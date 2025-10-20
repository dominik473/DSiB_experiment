"""Etap 6: stabilizacja + pobrania/analizy lab + protokol stabil sciskanie

Revision ID: 0da7d209ce6a
Revises: ce81f8ef26c2
Create Date: 2025-10-11 14:47:51.001828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0da7d209ce6a'
down_revision = 'ce81f8ef26c2'
branch_labels = None
depends_on = None

def upgrade():
    # 1) STABILIZACJA – pobranie próbek ze stabilizacji
    op.create_table(
        "stabil_pobranie",
        sa.Column("id_stabil_pobranie", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_protokol", sa.Integer(), nullable=False),
        sa.Column("nr_probki_stabil", sa.String(120), nullable=True),
        sa.Column("czy_z_recepty", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("klasa_stabil", sa.String(64), nullable=True),
        sa.Column("ile_probek", sa.Integer(), nullable=True),
        sa.Column("lokalizacja", sa.String(255), nullable=True),
        sa.Column("warstwa", sa.String(255), nullable=True),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_roboczy_protokol"], ["roboczy_protokol.id_roboczy_protokol"], name="fk_stabil_pob_robo", ondelete="CASCADE"),
    )
    op.create_index("ix_stabil_pob_robo", "stabil_pobranie", ["id_roboczy_protokol"])

    # 2) STABILIZACJA – ściskanie (wyniki)
    op.create_table(
        "stabil_sciskanie",
        sa.Column("id_stabil_sciskanie", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_stabil_pobranie", sa.Integer(), nullable=False),
        sa.Column("id_pracownika", sa.Integer(), nullable=True),
        sa.Column("data_pomiaru", sa.Date(), server_default=sa.text("(DATE('now'))")),
        sa.Column("po_ilu_dniach", sa.Integer(), nullable=True),
        sa.Column("wymiar", sa.String(32), nullable=True),
        sa.Column("wynik_1_stabil", sa.Float(), nullable=True),
        sa.Column("wynik_2_stabil", sa.Float(), nullable=True),
        sa.Column("wynik_3_stabil", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["id_stabil_pobranie"], ["stabil_pobranie.id_stabil_pobranie"], name="fk_stabil_sc_pob", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_pracownika"], ["pracownicy.id_pracownika"], name="fk_stabil_sc_prac", ondelete="SET NULL"),
    )
    op.create_index("ix_stabil_sc_pob", "stabil_sciskanie", ["id_stabil_pobranie"])

    # 3) LAB – ROB. POBRANIE MATERIAŁU (inne niż stabilizacja)
    op.create_table(
        "roboczy_pobranie_materialu",
        sa.Column("id_roboczy_pobranie_materialu", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_protokol", sa.Integer(), nullable=False),
        sa.Column("nr_probki_materialu", sa.String(120), nullable=True),
        sa.Column("opis", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_roboczy_protokol"], ["roboczy_protokol.id_roboczy_protokol"], name="fk_rpm_robo", ondelete="CASCADE"),
    )
    op.create_index("ix_rpm_robo", "roboczy_pobranie_materialu", ["id_roboczy_protokol"])

    # 4) LAB – ROB. ANALIZA SITOWA (snapshot szeroki; nazwy kolumn bez kropek)
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
    op.create_table(
        "roboczy_analiza_sitowa",
        sa.Column("id_roboczy_analiza_sitowa", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_protokol", sa.Integer(), nullable=False),
        sa.Column("plukanie", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        *[sa.Column(n, t, nullable=True) for n, t in sitowe_cols],
        sa.ForeignKeyConstraint(["id_roboczy_protokol"], ["roboczy_protokol.id_roboczy_protokol"], name="fk_ras_robo", ondelete="CASCADE"),
    )
    op.create_index("ix_ras_robo", "roboczy_analiza_sitowa", ["id_roboczy_protokol"])

    # 5) LAB – ROB. WSKAŹNIK PIASKOWY
    op.create_table(
        "roboczy_wskaznik_piaskowy",
        sa.Column("id_roboczy_wskaznik_piaskowy", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_protokol", sa.Integer(), nullable=False),
        sa.Column("wynik_1", sa.Float(), nullable=True),
        sa.Column("wynik_2", sa.Float(), nullable=True),
        sa.Column("wp_wynik", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["id_roboczy_protokol"], ["roboczy_protokol.id_roboczy_protokol"], name="fk_rwp_robo", ondelete="CASCADE"),
    )
    op.create_index("ix_rwp_robo", "roboczy_wskaznik_piaskowy", ["id_roboczy_protokol"])

    # 6) PROTOKOL – STABIL ŚCISKANIE (finalny dokument)
    op.create_table(
        "protokol_stabil_sciskanie",
        sa.Column("id_protokol_stabil_sciskanie", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_stabil_sciskanie", sa.Integer(), nullable=False),
        sa.Column("id_pracownika", sa.Integer(), nullable=True),

        # snapshot kluczowych danych (dokument nie zmienia się po korektach roboczych)
        sa.Column("nr_probki_stabil", sa.String(120), nullable=True),
        sa.Column("klasa_stabil", sa.String(64), nullable=True),
        sa.Column("lokalizacja", sa.String(255), nullable=True),
        sa.Column("warstwa", sa.String(255), nullable=True),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("po_ilu_dniach", sa.Integer(), nullable=True),
        sa.Column("wymiar", sa.String(32), nullable=True),
        sa.Column("wynik_1_stabil", sa.Float(), nullable=True),
        sa.Column("wynik_2_stabil", sa.Float(), nullable=True),
        sa.Column("wynik_3_stabil", sa.Float(), nullable=True),
        sa.Column("data", sa.Date(), server_default=sa.text("(DATE('now'))")),

        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_pss_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_stabil_sciskanie"], ["stabil_sciskanie.id_stabil_sciskanie"], name="fk_pss_scisk", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_pracownika"], ["pracownicy.id_pracownika"], name="fk_pss_prac", ondelete="SET NULL"),
    )
    op.create_index("ix_pss_licznik", "protokol_stabil_sciskanie", ["id_licznik_tech_prot"])
    op.create_index("ix_pss_scisk", "protokol_stabil_sciskanie", ["id_stabil_sciskanie"])


def downgrade():
    op.drop_index("ix_pss_scisk", table_name="protokol_stabil_sciskanie")
    op.drop_index("ix_pss_licznik", table_name="protokol_stabil_sciskanie")
    op.drop_table("protokol_stabil_sciskanie")

    op.drop_index("ix_rwp_robo", table_name="roboczy_wskaznik_piaskowy")
    op.drop_table("roboczy_wskaznik_piaskowy")

    op.drop_index("ix_ras_robo", table_name="roboczy_analiza_sitowa")
    op.drop_table("roboczy_analiza_sitowa")

    op.drop_index("ix_rpm_robo", table_name="roboczy_pobranie_materialu")
    op.drop_table("roboczy_pobranie_materialu")

    op.drop_index("ix_stabil_sc_pob", table_name="stabil_sciskanie")
    op.drop_table("stabil_sciskanie")

    op.drop_index("ix_stabil_pob_robo", table_name="stabil_pobranie")
    op.drop_table("stabil_pobranie")
