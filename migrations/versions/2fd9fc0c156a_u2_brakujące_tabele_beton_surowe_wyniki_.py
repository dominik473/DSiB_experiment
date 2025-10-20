"""U2: brakujące tabele beton + surowe wyniki + rozszerzenie protokol_vss

Revision ID: 2fd9fc0c156a
Revises: 0bb3349da8c4
Create Date: 2025-10-12 12:06:01.721104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fd9fc0c156a'
down_revision = '0bb3349da8c4'
branch_labels = None
depends_on = None

def upgrade():
    # 1) ZLECENIE BETONOWANIE
    op.create_table(
        "zlecenie_betonowanie",
        sa.Column("id_zlecenie_betonowania", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_zlecenie", sa.Integer(), nullable=False),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("element", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["id_zlecenie"], ["zlecenia.id_zlecenie"], name="fk_zb_zlec", ondelete="CASCADE"),
    )
    op.create_index("ix_zb_zlec", "zlecenie_betonowanie", ["id_zlecenie"])

    # 2) BETONOWANIE – ZLECONE BADANIA
    op.create_table(
        "betonowanie_zlecone_badania",
        sa.Column("id_betonowanie_zlecone_badania", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_zlecenie_betonowania", sa.Integer(), nullable=False),
        sa.Column("id_recepty_beton", sa.Integer(), nullable=True),
        sa.Column("konsystencja", sa.String(64), nullable=True),
        sa.Column("powietrze", sa.Float(), nullable=True),
        sa.Column("klasa", sa.String(64), nullable=True),  # gdy brak recepty
        sa.Column("nasiakliwosc", sa.Float(), nullable=True),
        sa.Column("wodoszczelnosc", sa.Float(), nullable=True),
        sa.Column("mrozoodpornosc", sa.String(64), nullable=True),
        sa.Column("zlecona_suma_kostek", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["id_zlecenie_betonowania"], ["zlecenie_betonowanie.id_zlecenie_betonowania"], name="fk_bzb_zb", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_recepty_beton"], ["recepty_beton.id_recepty_beton"], name="fk_bzb_recepta", ondelete="SET NULL"),
    )
    op.create_index("ix_bzb_zb", "betonowanie_zlecone_badania", ["id_zlecenie_betonowania"])

    # 3) DODATKOWE ŚCISKANIA
    op.create_table(
        "zlecone_dodatkowe_sciskania",
        sa.Column("id_zlecone_dodatkowe_sciskania", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_betonowanie_zlecone_badania", sa.Integer(), nullable=False),
        sa.Column("zlecone_po_ilu_dniach", sa.Integer(), nullable=False),
        sa.Column("zlecone_ile_kostek", sa.Integer(), nullable=True),  # defaultowo 1 w logice
        sa.ForeignKeyConstraint(["id_betonowanie_zlecone_badania"], ["betonowanie_zlecone_badania.id_betonowanie_zlecone_badania"], name="fk_zds_bzb", ondelete="CASCADE"),
    )
    op.create_index("ix_zds_bzb", "zlecone_dodatkowe_sciskania", ["id_betonowanie_zlecone_badania"])

    # 4) SUROWE WYNIKI Z BETONOWANIA (opcjonalne – niezależnie od protokołów)
    op.create_table(
        "betonowanie_temperatura",
        sa.Column("id_betonowanie_temperatura", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_betonowanie", sa.Integer(), nullable=False),
        sa.Column("wynik_temperatura", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["id_betonowanie"], ["betonowanie.id_betonowanie"], name="fk_bt_beton", ondelete="CASCADE"),
    )
    op.create_table(
        "betonowanie_stozek",
        sa.Column("id_betonowanie_stozek", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_betonowanie", sa.Integer(), nullable=False),
        sa.Column("wynik_stozek", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["id_betonowanie"], ["betonowanie.id_betonowanie"], name="fk_bs_beton", ondelete="CASCADE"),
    )
    op.create_table(
        "betonowanie_powietrze",
        sa.Column("id_betonowanie_powietrze", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_betonowanie", sa.Integer(), nullable=False),
        sa.Column("wynik_powietrze", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["id_betonowanie"], ["betonowanie.id_betonowanie"], name="fk_bp_beton", ondelete="CASCADE"),
    )

    # 5) ROZDZIELENIE WYNIKÓW PROTOKOŁÓW
    op.create_table(
        "protokol_stozek_wyniki",
        sa.Column("id_protokol_stozek_wyniki", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_protokol_stozek", sa.Integer(), nullable=False),
        sa.Column("wynik_stozek", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["id_protokol_stozek"], ["protokol_stozek.id_protokol_stozek"], name="fk_psw_stozek", ondelete="CASCADE"),
    )
    op.create_index("ix_psw_stozek", "protokol_stozek_wyniki", ["id_protokol_stozek"])

    op.create_table(
        "protokol_powietrze_wyniki",
        sa.Column("id_protokol_powietrze_wyniki", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_protokol_powietrze", sa.Integer(), nullable=False),
        sa.Column("wynik_powietrze", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["id_protokol_powietrze"], ["protokol_powietrze.id_protokol_powietrze"], name="fk_ppw_pow", ondelete="CASCADE"),
    )
    op.create_index("ix_ppw_pow", "protokol_powietrze_wyniki", ["id_protokol_powietrze"])

    # 6) ROZSZERZENIE PROTOKOŁU VSS – krzywe
    add_cols = []
    # pierwotny 0.02..0.45
    for val in [0.02,0.05,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45]:
        name = f"pierwotny_{str(val).replace('0.', '0_')}".replace('.','_')
        add_cols.append(sa.Column(name, sa.Float(), nullable=True))
    # odciążenie 0.35..0.02
    for val in [0.35,0.25,0.15,0.05,0.02]:
        name = f"odciazenie_{str(val).replace('0.', '0_')}".replace('.','_')
        add_cols.append(sa.Column(name, sa.Float(), nullable=True))
    # wtórny 0.05..0.45
    for val in [0.05,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45]:
        name = f"wtorny_{str(val).replace('0.', '0_')}".replace('.','_')
        add_cols.append(sa.Column(name, sa.Float(), nullable=True))

    for col in add_cols:
        op.add_column("protokol_vss", col)

def downgrade():
    # VSS remove columns (SQLite: DROP COLUMN via batch recreate nie jest dostępny na skróty – zostawiamy bez dropów kolumn, by nie ryzykować utraty danych)
    # Jeśli konieczne, przygotujemy osobną migrację rekonstrukcyjną.

    op.drop_index("ix_ppw_pow", table_name="protokol_powietrze_wyniki")
    op.drop_table("protokol_powietrze_wyniki")

    op.drop_index("ix_psw_stozek", table_name="protokol_stozek_wyniki")
    op.drop_table("protokol_stozek_wyniki")

    op.drop_table("betonowanie_powietrze")
    op.drop_table("betonowanie_stozek")
    op.drop_table("betonowanie_temperatura")

    op.drop_index("ix_zds_bzb", table_name="zlecone_dodatkowe_sciskania")
    op.drop_table("zlecone_dodatkowe_sciskania")

    op.drop_index("ix_bzb_zb", table_name="betonowanie_zlecone_badania")
    op.drop_table("betonowanie_zlecone_badania")

    op.drop_index("ix_zb_zlec", table_name="zlecenie_betonowanie")
    op.drop_table("zlecenie_betonowanie")
