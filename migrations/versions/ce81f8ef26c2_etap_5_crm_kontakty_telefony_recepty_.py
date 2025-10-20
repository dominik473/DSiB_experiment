"""Etap 5: CRM (kontakty/telefony) + recepty (beton/MMA)

Revision ID: ce81f8ef26c2
Revises: dsib_etap4_meta_v1
Create Date: 2025-10-11 14:41:24.641422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce81f8ef26c2'
down_revision = "dsib_etap4_meta_v1"
branch_labels = None
depends_on = None

def upgrade():
    # 1) OSOBY KONTAKTOWE (po stronie klienta)
    op.create_table(
        "osoby_kontaktowe",
        sa.Column("id_osoby_kontaktowej", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_klienta", sa.Integer(), nullable=False),
        sa.Column("imie", sa.String(120), nullable=False),
        sa.Column("nazwisko", sa.String(120), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("stanowisko", sa.String(120), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["id_klienta"], ["klienci.id_klienta"], name="fk_ok_klient", ondelete="CASCADE"),
    )
    # unikalny email (SQLite pozwoli na wiele NULL, ale pojedyncze nie-NULL będą unikalne)
    op.create_index("uq_ok_email", "osoby_kontaktowe", ["email"], unique=True)
    op.create_index("ix_ok_klient", "osoby_kontaktowe", ["id_klienta"])

    # 2) TELEFONY (unikatowy numer, przypięty do osoby)
    op.create_table(
        "telefony",
        sa.Column("id_telefonu", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_osoby_kontaktowej", sa.Integer(), nullable=False),
        sa.Column("nr_telefonu", sa.String(32), nullable=False),
        sa.Column("typ", sa.String(20), nullable=True),          # 'mobile' | 'office' | 'home' | 'other'
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.ForeignKeyConstraint(["id_osoby_kontaktowej"], ["osoby_kontaktowe.id_osoby_kontaktowej"], name="fk_tel_ok", ondelete="CASCADE"),
        sa.CheckConstraint("nr_telefonu <> ''", name="ck_tel_not_empty"),
    )
    op.create_index("uq_tel_nr", "telefony", ["nr_telefonu"], unique=True)
    op.create_index("ix_tel_ok", "telefony", ["id_osoby_kontaktowej", "is_primary"])

    # 3) Relacja kontakt ↔ inwestycja (unikalna para)
    op.create_table(
        "osoba_kontaktowa_inwestycja",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_osoby_kontaktowej", sa.Integer(), nullable=False),
        sa.Column("id_inwestycji", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_osoby_kontaktowej"], ["osoby_kontaktowe.id_osoby_kontaktowej"], name="fk_okinv_ok", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_inwestycji"], ["inwestycje.id_inwestycji"], name="fk_okinv_inv", ondelete="CASCADE"),
        sa.UniqueConstraint("id_osoby_kontaktowej", "id_inwestycji", name="uq_okinv_pair"),
    )
    op.create_index("ix_okinv_inv", "osoba_kontaktowa_inwestycja", ["id_inwestycji"])

    # 4) RECEPTY BETON
    op.create_table(
        "recepty_beton",
        sa.Column("id_recepty_beton", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nr_recepty_beton", sa.String(120), nullable=False),
        sa.Column("producent", sa.String(255), nullable=True),
        sa.Column("konsystencja", sa.String(64), nullable=True),
        sa.Column("powietrze", sa.Float(), nullable=True),
        # klasa: albo jako tekst, albo FK do słownika klas
        sa.Column("id_klasa_betonu", sa.Integer(), nullable=True),
        sa.Column("nasiakliwosc", sa.Float(), nullable=True),
        sa.Column("wodoszczelnosc", sa.Float(), nullable=True),
        sa.Column("mrozoodpornosc", sa.String(64), nullable=True),
        sa.Column("zalacznik_path", sa.String(512), nullable=True),  # ścieżka do PDF/obrazu

        # co najmniej JEDNO z (producent, zalacznik_path) musi istnieć
        sa.CheckConstraint("(producent IS NOT NULL) OR (zalacznik_path IS NOT NULL)", name="ck_recepty_beton_src"),
        sa.ForeignKeyConstraint(["id_klasa_betonu"], ["slownik_klas_betonu.id_klasa"], name="fk_rb_klasa", ondelete="SET NULL"),
    )
    op.create_index("uq_rb_nr", "recepty_beton", ["nr_recepty_beton"], unique=True)
    op.create_index("ix_rb_klasa", "recepty_beton", ["id_klasa_betonu"])

    # 5) RECEPTY MMA
    op.create_table(
        "recepty_mma",
        sa.Column("id_recepty_mma", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nazwa_recepty_mma", sa.String(255), nullable=False),
        sa.Column("gestosc_objetosciowa", sa.Float(), nullable=True),
        sa.Column("gestosc", sa.Float(), nullable=True),
    )
    op.create_index("uq_rmma_nazwa", "recepty_mma", ["nazwa_recepty_mma"], unique=True)


def downgrade():
    op.drop_index("uq_rmma_nazwa", table_name="recepty_mma")
    op.drop_table("recepty_mma")

    op.drop_index("ix_rb_klasa", table_name="recepty_beton")
    op.drop_index("uq_rb_nr", table_name="recepty_beton")
    op.drop_table("recepty_beton")

    op.drop_index("ix_okinv_inv", table_name="osoba_kontaktowa_inwestycja")
    op.drop_table("osoba_kontaktowa_inwestycja")

    op.drop_index("ix_tel_ok", table_name="telefony")
    op.drop_index("uq_tel_nr", table_name="telefony")
    op.drop_table("telefony")

    op.drop_index("ix_ok_klient", table_name="osoby_kontaktowe")
    op.drop_index("uq_ok_email", table_name="osoby_kontaktowe")
    op.drop_table("osoby_kontaktowe")
