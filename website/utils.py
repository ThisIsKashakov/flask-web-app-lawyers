import random
import string
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Storage settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 8 * 1024 * 1024))  # Default 8MB
STORAGE_LIMIT = int(os.getenv("STORAGE_LIMIT", 30 * 1024 * 1024 * 1024))  # Default 30GB

ALLOWED_EXTENSIONS = {
    "txt",
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "zip",
    "rar",
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_random_password(length=12, forbidden_chars=None):
    if forbidden_chars is None:
        forbidden_chars = [
            ";",
            "--",
            "'",
            '"',
            "=",
            "<",
            ">",
            "|",
            "&",
            "$",
            "@",
            "%",
            "^",
            "*",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            "`",
            "~",
        ]

    allowed_chars = [
        char
        for char in string.ascii_letters + string.digits + string.punctuation
        if char not in forbidden_chars
    ]
    password = "".join(random.choices(allowed_chars, k=length))
    return password


def has_sql_injection(input_string):
    forbidden_chars = [
        ";",
        "--",
        "'",
        '"',
        "=",
        "<",
        ">",
        "|",
        "&",
        "$",
        "@",
        "%",
        "^",
        "*",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        "`",
        "~",
    ]
    return any(char in input_string for char in forbidden_chars)


def is_number(value):
    if isinstance(value, str):
        return value.isdigit()
    return False


def is_valid_range(str, max):
    return len(str) > 0 and len(str) <= max


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M:%S")
        return True
    except ValueError:
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False


def is_file_size_allowed(file, max_size):
    """Check if file size is under the maximum allowed size"""
    file.seek(0, 2)  # Seek to end of file
    file_size = file.tell()  # Get current position (file size)
    file.seek(0)  # Reset file position
    return file_size <= max_size


def get_directory_size(directory):
    """Calculate total size of a directory in bytes"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size


def get_storage_stats(directory):
    """Get storage statistics"""
    used_space = get_directory_size(directory)
    free_space = STORAGE_LIMIT - used_space
    return {
        "total": STORAGE_LIMIT,
        "used": used_space,
        "free": free_space,
        "usage_percent": (used_space / STORAGE_LIMIT) * 100,
    }


def is_storage_available(directory, file_size):
    """Check if there's enough storage space for new file"""
    stats = get_storage_stats(directory)
    return stats["free"] >= file_size
