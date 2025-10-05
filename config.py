# config.py
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Wczytaj .env (lokalnie) – w prod zwykle ustawiasz zmienne środowiskowe na hostingu
load_dotenv()

# Ścieżki bazowe
ROOT = Path(__file__).resolve().parent          # jeśli config.py leży w katalogu głównym projektu
INSTANCE_DIR = ROOT / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)  # upewnij się, że katalog istnieje

DB_PATH = (INSTANCE_DIR / "app.db").as_posix()   # absolutna ścieżka do bazy (format unixowy)

def _normalize_sqlite_uri(uri: str | None) -> str:
    """
    Zamień względne URI typu 'sqlite:///instance/app.db' na absolutne,
    aby uniknąć błędu 'unable to open database file' podczas migracji.
    """
    if not uri:
        return f"sqlite:///{DB_PATH}"
    if uri.startswith("sqlite:///") and not uri.startswith("sqlite:////"):
        rel = uri[len("sqlite:///"):]  # część po prefixie
        abs_path = (ROOT / rel).resolve().as_posix()
        return f"sqlite:///{abs_path}"
    return uri

def _calendar_id(value: str | None) -> str | None:
    """
    Przyjmij ID kalendarza jako e-mail. Jeśli ktoś wkleił pełny URL embedu,
    wyciągnij z niego parametr 'src'.
    """
    if not value:
        return None
    v = value.strip()
    if v.startswith("http"):
        qs = parse_qs(urlparse(v).query)
        srcs = qs.get("src", [])
        return srcs[0] if srcs else v
    return v

class Config:
    # --- Bezpieczeństwo ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # --- Baza danych ---
    _RAW_DB = os.getenv("DATABASE_URL")  # np. sqlite:///instance/app.db
    SQLALCHEMY_DATABASE_URI = _normalize_sqlite_uri(_RAW_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Kalendarze (ID = e-mail) ---
    CALENDAR_ID_1 = _calendar_id(os.getenv("CALENDAR_ID_1"))
    CALENDAR_ID_2 = _calendar_id(os.getenv("CALENDAR_ID_2"))
    CALENDAR_ID_3 = _calendar_id(os.getenv("CALENDAR_ID_3"))
    CALENDAR_ID_EDITABLE = _calendar_id(os.getenv("CALENDAR_ID_EDITABLE")) or CALENDAR_ID_3
    CALENDAR_TZ = os.getenv("CALENDAR_TZ", "Europe/Warsaw")
    CALENDAR_LOCALE = os.getenv("CALENDAR_LOCALE", "pl-PL")

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False

if __name__ == "__main__":
    # Szybki podgląd kluczowych wartości (do lokalnej diagnostyki)
    print("DB URI:", Config.SQLALCHEMY_DATABASE_URI)
    print("Instance dir:", INSTANCE_DIR)
    print("CAL1:", Config.CALENDAR_ID_1)
    print("CAL2:", Config.CALENDAR_ID_2)
    print("CAL3:", Config.CALENDAR_ID_3)
    print("CALEDIT:", Config.CALENDAR_ID_EDITABLE)
