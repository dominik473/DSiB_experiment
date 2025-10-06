"""cleanup: drop nazwa_skrocona_klienta + add index"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "cleanup_drop_staging_add_idx"
down_revision = "635897f0ef02"  # <-- PODSTAW poprz. revision, np. "635897f0ef02"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table_name)]
    return column_name in cols

def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    idx_names = {ix["name"] for ix in insp.get_indexes(table_name)}
    return index_name in idx_names

def upgrade():
    # 1) Usuń kolumnę staging, jeśli istnieje
    if _has_column("inwestycje", "nazwa_skrocona_klienta"):
        with op.batch_alter_table("inwestycje") as batch_op:
            batch_op.drop_column("nazwa_skrocona_klienta")

    # 2) Dodaj indeks po id_klienta (jeśli go nie ma)
    if not _has_index("inwestycje", "ix_inwestycje_id_klienta"):
        op.create_index(
            "ix_inwestycje_id_klienta",
            "inwestycje",
            ["id_klienta"],
            unique=False,
        )

def downgrade():
    # 1) Usuń indeks (jeśli istnieje)
    if _has_index("inwestycje", "ix_inwestycje_id_klienta"):
        op.drop_index("ix_inwestycje_id_klienta", table_name="inwestycje")

    # 2) Przywróć kolumnę staging (jako nullable), jeśli nie istnieje
    if not _has_column("inwestycje", "nazwa_skrocona_klienta"):
        with op.batch_alter_table("inwestycje") as batch_op:
            batch_op.add_column(sa.Column("nazwa_skrocona_klienta", sa.String(length=128), nullable=True))
