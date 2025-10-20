"""drop kontaktowe i user

Revision ID: 7f78ea6af45d
Revises: 1ca1a7406a68
Create Date: 2025-10-20 14:52:51.274130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f78ea6af45d'
down_revision = '1ca1a7406a68'
branch_labels = None
depends_on = None


def upgrade():
    for tbl in [
        "osoba_kontaktowa_klient",
        "osoba_kontaktowa_inwestycja",
        "osoby_kontaktowe",
        "user",
    ]:
        try:
            op.execute(f"DROP TABLE IF EXISTS {tbl}")
            print(f"✅ dropped {tbl}")
        except Exception as e:
            print(f"⚠️ error dropping {tbl}: {e}")


def downgrade():
    # nie odtwarzamy — struktury zostaną odtworzone w nowym etapie
    pass