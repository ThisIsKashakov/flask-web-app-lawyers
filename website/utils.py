import random
import string
from datetime import datetime
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Storage settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 8 * 1024 * 1024))  # Default 8MB
STORAGE_LIMIT = int(os.getenv("STORAGE_LIMIT", 30 * 1024 * 1024 * 1024))  # Default 30GB

# Security settings
FORBIDDEN_CHARS = [
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
        forbidden_chars = FORBIDDEN_CHARS

    allowed_chars = [
        char
        for char in string.ascii_letters + string.digits + string.punctuation
        if char not in forbidden_chars
    ]
    password = "".join(random.choices(allowed_chars, k=length))
    return password


# Список опасных SQL паттернов
SQL_PATTERNS = [
    r"(?i)((%27)|('))\s*((%6F)|o|(%4F))((%72)|r|(%52))",  # 'or
    r"(?i)((%27)|('))\s*((%61)|a|(%41))((%6E)|n|(%4E))((%64)|d|(%44))",  # 'and
    r"(?i)((%3D)|(=))[^\n]*((%27)|(')|(--)|(\%3B)|(;))",  # ='...
    r"(?i)((%27)|('))..*?((%27)|('))..",  # '...'
    r"(?i)/\*.*?\*/",  # /* ... */
    r"(?i);\s*$",  # Statement ending with ;
    r"(?i)--",  # SQL comment
    r"(?i)UNION\s+SELECT",  # UNION SELECT
    r"(?i)(ALTER|CREATE|DELETE|DROP|EXEC(UTE)?|INSERT|MERGE|SELECT|UPDATE|UNION)",  # SQL commands
]


def has_sql_injection(input_string):
    """Проверяет строку на наличие паттернов SQL-инъекций"""
    return any(re.search(pattern, input_string) for pattern in SQL_PATTERNS)


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


def is_valid_email(email):
    """
    Проверяет, что строка соответствует формату email

    Args:
        email: Строка для проверки

    Returns:
        bool: True если формат корректный, False в противном случае
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


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
