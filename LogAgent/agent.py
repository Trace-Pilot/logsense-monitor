import os
import re
import psycopg2
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

LOG_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Logs"
)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": os.environ["LOGSENSE_DB_PASSWORD"]
}


# ============================================================
# MASK SENSITIVE INFORMATION
# ============================================================

def mask_sensitive_information(message):
    """
    Masks sensitive information before storing the log
    in PostgreSQL.

    Aadhaar:
        123456789012
        becomes
        1234XXXX9012

    PAN:
        ABCDE1234F
        becomes
        AXXXE23XXF
    """

    if not message:
        return message

    # --------------------------------------------------------
    # Aadhaar Number
    #
    # Supports:
    # 123456789012
    # 1234 5678 9012
    # 1234-5678-9012
    # --------------------------------------------------------

    def mask_aadhaar(match):

        value = re.sub(
            r"[\s-]",
            "",
            match.group(0)
        )

        return (
            value[:4]
            + "XXXX"
            + value[-4:]
        )

    aadhaar_pattern = (
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    )

    message = re.sub(
        aadhaar_pattern,
        mask_aadhaar,
        message
    )

    # --------------------------------------------------------
    # PAN Number
    #
    # Example:
    # ABCDE1234F
    #
    # Becomes:
    # AXXXE23XXF
    # --------------------------------------------------------

    def mask_pan(match):

        value = match.group(0).upper()

        return (
            value[0]
            + "XXX"
            + value[4]
            + value[5:7]
            + "XX"
            + value[9]
        )

    pan_pattern = (
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    )

    message = re.sub(
        pan_pattern,
        mask_pan,
        message,
        flags=re.IGNORECASE
    )

    return message


# ============================================================
# CREATE TABLE IF MISSING
# ============================================================

def create_logs_table(connection):

    with connection.cursor() as cursor:

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                severity VARCHAR(20) NOT NULL,
                application VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                source_file VARCHAR(255) NOT NULL,
                line_number INTEGER NOT NULL
            )
            """
        )


# ============================================================
# INSERT STRUCTURED LOG INTO DATABASE
# ============================================================

def insert_log(
    connection,
    timestamp,
    severity,
    application,
    message,
    file_name,
    line_number
):

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO logs
                (
                    timestamp,
                    severity,
                    application,
                    message,
                    source_file,
                    line_number
                )
                VALUES
                (%s, %s, %s, %s, %s, %s)
                """,
                (
                    timestamp,
                    severity,
                    application,
                    message,
                    file_name,
                    line_number
                )
            )

        return True

    except psycopg2.Error as error:

        print(f"Insert error: {error}")

        raise


# ============================================================
# PARSE ONE LOG LINE
# ============================================================

def parse_log_line(log_line):

    """
    Expected format:

    timestamp|severity|application|message

    Example:

    2026-09-01 17:00:10|INFO|CustomerService|Customer Aadhaar 123456789012 verified successfully
    """

    # --------------------------------------------------------
    # Split log into four parts
    # --------------------------------------------------------

    parts = log_line.split("|", 3)

    if len(parts) != 4:
        return None

    timestamp_text = parts[0].strip()
    severity = parts[1].strip().upper()
    application = parts[2].strip()
    message = parts[3].strip()

    # --------------------------------------------------------
    # Validate fields
    # --------------------------------------------------------

    if (
        timestamp_text == ""
        or severity == ""
        or application == ""
        or message == ""
    ):
        return None

    # --------------------------------------------------------
    # Validate timestamp
    # --------------------------------------------------------

    try:

        timestamp = datetime.strptime(
            timestamp_text,
            "%Y-%m-%d %H:%M:%S"
        )

    except ValueError:

        return None

    # --------------------------------------------------------
    # SECURITY STEP
    #
    # Mask sensitive information BEFORE the
    # message is passed to the database.
    # --------------------------------------------------------

    masked_message = mask_sensitive_information(
        message
    )

    return {
        "timestamp": timestamp,
        "severity": severity,
        "application": application,
        "message": masked_message
    }


# ============================================================
# PROCESS ONE LOG FILE
# ============================================================

def process_file(
    connection,
    file_path,
    file_name
):

    line_number = 0
    imported_count = 0
    skipped_count = 0

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as file:

            print(
                f"Reading: {file_path}"
            )

            for line in file:

                line_number += 1

                # ------------------------------------------------
                # Remove newline
                # ------------------------------------------------

                log_line = line.rstrip(
                    "\r\n"
                )

                # ------------------------------------------------
                # Ignore empty lines
                # ------------------------------------------------

                if log_line.strip() == "":
                    continue

                # ------------------------------------------------
                # Parse log
                # ------------------------------------------------

                parsed_log = parse_log_line(
                    log_line
                )

                # ------------------------------------------------
                # Invalid log
                # ------------------------------------------------

                if parsed_log is None:

                    skipped_count += 1

                    print(
                        f"Skipping invalid log at "
                        f"{file_name}, "
                        f"line {line_number}: "
                        f"{log_line}"
                    )

                    continue

                # ------------------------------------------------
                # Insert masked log
                # ------------------------------------------------

                insert_log(
                    connection,
                    parsed_log["timestamp"],
                    parsed_log["severity"],
                    parsed_log["application"],
                    parsed_log["message"],
                    file_name,
                    line_number
                )

                imported_count += 1

    except OSError as error:

        print(
            f"Cannot open: {file_path}"
        )

        print(
            f"Error: {error}"
        )

        raise

    print(
        f"Finished {file_name}: "
        f"{imported_count} imported, "
        f"{skipped_count} skipped"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "========================================"
    )

    print(
        "       LOGSENSE LOG AGENT"
    )

    print(
        "========================================"
    )

    print(
        "Agent is started."
    )

    # --------------------------------------------------------
    # Connect to PostgreSQL
    # --------------------------------------------------------

    try:

        print(
            "Creating database connection."
        )

        connection = psycopg2.connect(
            **DB_CONFIG
        )

        print(
            "Database connection established."
        )

    except psycopg2.Error as error:

        print(
            f"Database connection failed: "
            f"{error}"
        )

        return 1

    # --------------------------------------------------------
    # Start transaction
    # --------------------------------------------------------

    try:

        print(
            "Starting transaction."
        )

        # ----------------------------------------------------
        # Create table if necessary
        # ----------------------------------------------------

        create_logs_table(
            connection
        )

        # ----------------------------------------------------
        # Check log directory
        # ----------------------------------------------------

        if not os.path.isdir(
            LOG_DIRECTORY
        ):

            print(
                f"Cannot access directory: "
                f"{LOG_DIRECTORY}"
            )

            connection.rollback()

            return 1

        # ----------------------------------------------------
        # Read log files
        # ----------------------------------------------------

        files_found = 0

        for file_name in os.listdir(
            LOG_DIRECTORY
        ):

            full_path = os.path.join(
                LOG_DIRECTORY,
                file_name
            )

            # Ignore directories

            if os.path.isdir(
                full_path
            ):
                continue

            files_found += 1

            process_file(
                connection,
                full_path,
                file_name
            )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        connection.commit()

        print(
            "----------------------------------------"
        )

        print(
            f"Files processed: {files_found}"
        )

        print(
            "Log import completed successfully."
        )

        print(
            "----------------------------------------"
        )

    except Exception as error:

        print(
            "----------------------------------------"
        )

        print(
            f"Error occurred: {error}"
        )

        print(
            "Rolling back transaction."
        )

        print(
            "----------------------------------------"
        )

        connection.rollback()

        return 1

    finally:

        connection.close()

        print(
            "Database connection closed."
        )

    return 0


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()