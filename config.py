import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent  # .../your_app
PROJECT_ROOT = BASE_DIR                     # jeśli plik config.py leży w katalogu głównym projektu
INSTANCE_DIR = PROJECT_ROOT / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)  # upewnij się, że istnieje

DEFAULT_DB_PATH = (INSTANCE_DIR / "app.db").as_posix()  # zamień na format unixowy (działa też na Windows)
DEFAULT_DB_URI = f"sqlite:///{DEFAULT_DB_PATH}"

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", DEFAULT_DB_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    DEBUG = True