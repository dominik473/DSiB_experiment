"""Etap 7: protokoly analiza sitowa + wskaznik piaskowy

Revision ID: fe30f910e3f3
Revises: 0da7d209ce6a
Create Date: 2025-10-11 15:02:10.746193

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe30f910e3f3'
down_revision = '0da7d209ce6a'
branch_labels = None
depends_on = None

def upgrade():
    # kolumny frakcji jak w Etapie 6 (te same nazwy: v_0_063 ... v_63)
    sitowe_cols = [
        ("v_0_063", sa.Float()),
        ("v_0_125", sa.Float()),
        ("v_0_25", sa.Float()),
        ("v_0_5", sa.Float()),
        ("v_1", sa.Float()),
        ("v_2", sa.Float()),
        ("v_4", sa.Float()),
        ("v_5_6", sa.Float()),
        ("v_8", sa.Float()),
        ("v_11_2", sa.Float()),
        ("v_16", sa.Float()),
        ("v_22_4", sa.Float()),
        ("v_32_5", sa.Float()),
        ("v_63", sa.Float()),
    ]

    # PROTOKÓŁ: Analiza sitowa (snapshot szeroki)
    op.create_table(
        "protokol_analiza_sitowa",
        sa.Column("id_protokol_analiza_sitowa", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_roboczy_analiza_sitowa", sa.Integer(), nullable=False),

        # meta + snapshot
        sa.Column("data", sa.Date(), server_default=sa.text("(DATE('now'))"), nullable=False),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("lokalizacja", sa.String(255), nullable=True),
        sa.Column("warstwa", sa.String(255), nullable=True),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("plukanie", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        *[sa.Column(n, t, nullable=True) for n, t in sitowe_cols],

        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_pas_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_roboczy_analiza_sitowa"], ["roboczy_analiza_sitowa.id_roboczy_analiza_sitowa"], name="fk_pas_ras", ondelete="RESTRICT"),
    )
    op.create_index("ix_pas_licznik", "protokol_analiza_sitowa", ["id_licznik_tech_prot"])

    # PROTOKÓŁ: Wskaźnik piaskowy (snapshot)
    op.create_table(
        "protokol_wskaznik_piaskowy",
        sa.Column("id_protokol_wskaznik_piaskowy", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_roboczy_wskaznik_piaskowy", sa.Integer(), nullable=False),

        # meta + snapshot
        sa.Column("data", sa.Date(), server_default=sa.text("(DATE('now'))"), nullable=False),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("lokalizacja", sa.String(255), nullable=True),
        sa.Column("warstwa", sa.String(255), nullable=True),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("wynik_1", sa.Float(), nullable=True),
        sa.Column("wynik_2", sa.Float(), nullable=True),
        sa.Column("wp_wynik", sa.Float(), nullable=True),

        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_pwp_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_roboczy_wskaznik_piaskowy"], ["roboczy_wskaznik_piaskowy.id_roboczy_wskaznik_piaskowy"], name="fk_pwp_rwp", ondelete="RESTRICT"),
    )
    op.create_index("ix_pwp_licznik", "protokol_wskaznik_piaskowy", ["id_licznik_tech_prot"])


def downgrade():
    op.drop_index("ix_pwp_licznik", table_name="protokol_wskaznik_piaskowy")
    op.drop_table("protokol_wskaznik_piaskowy")

    op.drop_index("ix_pas_licznik", table_name="protokol_analiza_sitowa")
    op.drop_table("protokol_analiza_sitowa")
