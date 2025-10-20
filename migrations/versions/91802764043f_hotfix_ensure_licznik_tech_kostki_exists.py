"""hotfix: ensure licznik_tech_kostki exists

Revision ID: 91802764043f
Revises: 4278c31e78b7
Create Date: 2025-10-20 07:49:44.024113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91802764043f'
down_revision = "e1042e7f9ae4"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS licznik_tech_kostki (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seq INTEGER,
        nr_kostki VARCHAR(120),
        status_vr VARCHAR(50)
    )
    """)

def downgrade():
    # nic nie ruszamy (bezpiecznie)
    pass