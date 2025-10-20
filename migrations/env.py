import logging
from logging.config import fileConfig
import os
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- Logging / config ---
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")



# --- Ustal URL bazy ---
# Priorytet:
# 1) env var DSIB_SQLALCHEMY_URL (np. sqlite:///C:/.../DSiB.db)
# 2) domyślnie: sqlite:///<repo_root>/instance/DSiB.db
def _compute_default_sqlite_url() -> str:
    # env.py -> migrations -> <repo_root>
    repo_root = Path(__file__).resolve().parents[1].parent
    db_path = repo_root / "instance" / "DSiB.db"
    # absolutny path dla Windows
    return f"sqlite:///{db_path.as_posix()}"

SQLALCHEMY_URL = os.environ.get("DSIB_SQLALCHEMY_URL", _compute_default_sqlite_url())
config.set_main_option("sqlalchemy.url", SQLALCHEMY_URL)

# --- Nie ładujemy modeli aplikacji (żadnej refleksji) ---
target_metadata = None

logger.info("Using SQLALCHEMY_URL = %s", SQLALCHEMY_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        render_as_batch=True,  # ważne dla SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=None,   # brak refleksji modeli
            render_as_batch=True,   # SQLite-friendly ALTER TABLE
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
