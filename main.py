import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Magic bytes for common file types (add more as needed)
MAGIC_BYTES = {
    "jpg": (b"\xFF\xD8\xFF",),
    "png": (b"\x89PNG\r\n\x1a\n",),
    "gif": (b"GIF87a", b"GIF89a"),
    "pdf": (b"%PDF-",),
}


def setup_argparse():
    """
    Set up command-line arguments for the file-type-verifier tool.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Verifies file content against expected magic bytes or file signatures to detect file type mismatches."
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to the file to be verified."
    )
    parser.add_argument(
        "--expected-type",
        type=str,
        # The accepted values for --expected-type are the table's keys, taken
        # when the parser is built. Adding a type to MAGIC_BYTES extends the
        # command line by itself; there is no second list to keep in step.
        choices=MAGIC_BYTES.keys(),
        required=True,
        help="Expected file type (e.g., jpg, png, gif, pdf)."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )
    return parser.parse_args()


def verify_file_signature(file_path, expected_type):
    """
    Verify the file signature (magic bytes) against the expected type.

    Args:
        file_path (str): Path to the file to verify.
        expected_type (str): Expected file type.

    Returns:
        bool: True if the file matches the expected type, False otherwise.
    """
    try:
        path = Path(file_path)
        if not path.is_file():
            logging.error(f"The specified path '{file_path}' is not a valid file.")
            return False

        with path.open("rb") as file:
            signatures = MAGIC_BYTES.get(expected_type)
            if not signatures:
                logging.error(f"No magic bytes defined for the expected type: {expected_type}")
                return False

            # Only as many bytes as the longest signature for the expected type
            # are read, eight at most in the current table. Each candidate is then
            # compared against its own length of prefix, which is how the two GIF
            # variants share one entry despite both being six bytes.
            # A file shorter than its signature compares unequal on the slice and
            # fails cleanly, with no special empty or truncated case.
            file_signature = file.read(max(len(s) for s in signatures))
            if any(file_signature[:len(s)] == s for s in signatures):
                logging.info(f"File '{file_path}' matches the expected type: {expected_type}.")
                return True
            else:
                logging.warning(f"File '{file_path}' does not match the expected type: {expected_type}.")
                return False

    except Exception as e:
        logging.error(f"An error occurred while verifying the file: {e}")
        return False


def main():
    """
    Main function to execute the file-type-verifier tool.

    Example usage:
        python main.py /path/to/file --expected-type jpg
    """
    args = setup_argparse()

    # Enable verbose logging if specified
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    file_path = args.file
    expected_type = args.expected_type

    logging.debug(f"File path: {file_path}")
    logging.debug(f"Expected type: {expected_type}")

    # Verify file signature
    result = verify_file_signature(file_path, expected_type)

    # Mismatch, missing file, and read error all arrive here as the same
    # False and the same exit 1. Which of the three happened is in the log
    # line written at the point of failure, nowhere else.
    if not result:
        exit(1)  # Exit with error code if verification fails
    else:
        exit(0)  # Exit with success code if verification passes


if __name__ == "__main__":
    main()