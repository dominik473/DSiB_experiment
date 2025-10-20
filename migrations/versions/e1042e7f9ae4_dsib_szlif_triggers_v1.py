"""dsib_szlif_triggers_v1

Revision ID: e1042e7f9ae4
Revises: 28cdf5b62c86
Create Date: 2025-10-13 12:01:48.624486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1042e7f9ae4'
down_revision = '28cdf5b62c86'
branch_labels = None
depends_on = None

def upgrade():
    # Jeśli ma być dokładnie jeden wynik na protokół, użyjemy UNIQUE INDEX 1:1
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_psw_one ON protokol_stozek_wyniki(id_protokol_stozek);")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_ppw_one ON protokol_powietrze_wyniki(id_protokol_powietrze);")

    # (Świadomie nie tworzymy triggerów modyfikujących NEW.* — SQLite nie wspiera „SET NEW.col”)
    # Logika przeliczania 'suma_kostek' zostaje w aplikacji + CHECK w tabeli 'beton_probka'.

def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_ppw_one;")
    op.execute("DROP INDEX IF EXISTS uq_psw_one;")
