import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Magic bytes for common file types (add more as needed)
MAGIC_BYTES = {
    "jpg": b"\xFF\xD8\xFF",
    "png": b"\x89PNG\r\n\x1a\n",
    "gif": b"GIF87a",
    "pdf": b"%PDF-",
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
            magic_bytes = MAGIC_BYTES.get(expected_type)
            if not magic_bytes:
                logging.error(f"No magic bytes defined for the expected type: {expected_type}")
                return False

            file_signature = file.read(len(magic_bytes))
            if file_signature == magic_bytes:
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

    if not result:
        exit(1)  # Exit with error code if verification fails
    else:
        exit(0)  # Exit with success code if verification passes


if __name__ == "__main__":
    main()