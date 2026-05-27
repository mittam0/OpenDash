import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "opendash.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PASSWORD_SALT = "opendash_salt_2026"
DEFAULT_CONNECTOR_NAME = "main"
MAX_BLOCKS = 4
