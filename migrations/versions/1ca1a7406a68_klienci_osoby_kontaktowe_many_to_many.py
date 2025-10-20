"""klienci_osoby_kontaktowe_many_to_many

Revision ID: 1ca1a7406a68
Revises: 91802764043f
Create Date: 2025-10-20 13:54:15.218410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ca1a7406a68'
down_revision = '91802764043f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "osoba_kontaktowa_klient",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_osoby_kontaktowej", sa.Integer(), nullable=False),
        sa.Column("id_klienta", sa.Integer(), nullable=False),
        sa.Column("rola", sa.String(120)),
        sa.Column("stanowisko", sa.String(120)),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("od_kiedy", sa.Date()),
        sa.Column("do_kiedy", sa.Date()),
        sa.Column("uwagi", sa.Text()),
        sa.ForeignKeyConstraint(
            ["id_osoby_kontaktowej"], ["osoby_kontaktowe.id_osoby_kontaktowej"],
            name="fk_ok_rel_osoba", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["id_klienta"], ["klienci.id_klienta"],
            name="fk_ok_rel_klient", ondelete="CASCADE"
        ),
        sa.UniqueConstraint("id_osoby_kontaktowej", "id_klienta", name="uq_ok_rel_pair"),
    )

    # indeksy pomocnicze
    op.create_index("ix_ok_rel_osoba", "osoba_kontaktowa_klient", ["id_osoby_kontaktowej"])
    op.create_index("ix_ok_rel_klient", "osoba_kontaktowa_klient", ["id_klienta"])

    # backfill z kolumny osoby_kontaktowe.id_klienta (jeśli istnieje i nie-NULL)
    op.execute("""
    INSERT OR IGNORE INTO osoba_kontaktowa_klient (id_osoby_kontaktowej, id_klienta, is_primary)
    SELECT ok.id_osoby_kontaktowej, ok.id_klienta, 1
    FROM osoby_kontaktowe ok
    WHERE ok.id_klienta IS NOT NULL
    """)


def downgrade():
    op.drop_index("ix_ok_rel_klient", table_name="osoba_kontaktowa_klient")
    op.drop_index("ix_ok_rel_osoba", table_name="osoba_kontaktowa_klient")
    op.drop_table("osoba_kontaktowa_klient")
