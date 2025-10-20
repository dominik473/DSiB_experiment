"""hotfix: create licznik_tech_kostki

Revision ID: 4278c31e78b7
Revises: e1042e7f9ae4
Create Date: 2025-10-13 12:07:51.907038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4278c31e78b7'
down_revision = '2fd9fc0c156a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "licznik_tech_kostki",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("seq", sa.Integer(), nullable=True),
        sa.Column("nr_kostki", sa.String(120), nullable=True),
        sa.Column("status_vr", sa.String(50), nullable=True)  # np. 'VR' / NULL
    )
    # (opcjonalnie) unikat numeru, jeśli chcesz
    # op.create_index("uq_licznik_kostki_nr", "licznik_tech_kostki", ["nr_kostki"], unique=True)

def downgrade():
    # jeśli dodałeś/aś indeks unikatowy, najpierw go skasuj:
    # op.drop_index("uq_licznik_kostki_nr", table_name="licznik_tech_kostki")
    op.drop_table("licznik_tech_kostki")
