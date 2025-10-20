"""U1: uzytkownicy (klienci) + relacje i FK do zlecen

Revision ID: 0bb3349da8c4
Revises: fe30f910e3f3
Create Date: 2025-10-12 12:03:46.358055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bb3349da8c4'
down_revision = 'fe30f910e3f3'
branch_labels = None
depends_on = None


def upgrade():
    # 1) UŻYTKOWNICY (klienccy)
    op.create_table(
        "uzytkownicy",
        sa.Column("id_uzytkownika", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_klienta", sa.Integer(), nullable=False),
        sa.Column("imie", sa.String(120), nullable=False),
        sa.Column("nazwisko", sa.String(120), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("haslo", sa.String(255), nullable=False),
        sa.Column("aktywny", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["id_klienta"], ["klienci.id_klienta"], name="fk_uzyt_klient", ondelete="CASCADE"),
    )
    op.create_index("uq_uzyt_email", "uzytkownicy", ["email"], unique=True)
    op.create_index("ix_uzyt_klient", "uzytkownicy", ["id_klienta"])

    # 2) Telefony użytkownika (osobna tabela – nie ruszamy istniejących 'telefony' dla 'osoby_kontaktowe')
    op.create_table(
        "telefony_uzytkownika",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_uzytkownika", sa.Integer(), nullable=False),
        sa.Column("nr_telefonu", sa.String(32), nullable=False),
        sa.Column("typ", sa.String(20), nullable=True),           # mobile/office/home/other
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.CheckConstraint("nr_telefonu <> ''", name="ck_tu_not_empty"),
        sa.ForeignKeyConstraint(["id_uzytkownika"], ["uzytkownicy.id_uzytkownika"], name="fk_tu_user", ondelete="CASCADE"),
    )
    op.create_index("uq_tu_nr", "telefony_uzytkownika", ["nr_telefonu"], unique=True)
    op.create_index("ix_tu_user", "telefony_uzytkownika", ["id_uzytkownika", "is_primary"])

    # 3) Mapowanie użytkownik ↔ inwestycja (wiele-do-wielu)
    op.create_table(
        "uzytkownik_inwestycja",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_uzytkownika", sa.Integer(), nullable=False),
        sa.Column("id_inwestycji", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_uzytkownika"], ["uzytkownicy.id_uzytkownika"], name="fk_ui_user", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_inwestycji"], ["inwestycje.id_inwestycji"], name="fk_ui_inv", ondelete="CASCADE"),
        sa.UniqueConstraint("id_uzytkownika", "id_inwestycji", name="uq_ui_pair"),
    )
    op.create_index("ix_ui_inv", "uzytkownik_inwestycja", ["id_inwestycji"])

    # 4) Dodanie FK do 'zlecenia' (batch recreate, bo SQLite)
    with op.batch_alter_table("zlecenia", recreate="always") as b:
        b.add_column(sa.Column("id_uzytkownika", sa.Integer(), nullable=True))
        b.create_foreign_key("fk_zlecenia_uzytkownik", "uzytkownicy", ["id_uzytkownika"], ["id_uzytkownika"], ondelete="SET NULL")

def downgrade():
    with op.batch_alter_table("zlecenia", recreate="always") as b:
        b.drop_constraint("fk_zlecenia_uzytkownik", type_="foreignkey")
        b.drop_column("id_uzytkownika")

    op.drop_index("ix_ui_inv", table_name="uzytkownik_inwestycja")
    op.drop_table("uzytkownik_inwestycja")

    op.drop_index("ix_tu_user", table_name="telefony_uzytkownika")
    op.drop_index("uq_tu_nr", table_name="telefony_uzytkownika")
    op.drop_table("telefony_uzytkownika")

    op.drop_index("ix_uzyt_klient", table_name="uzytkownicy")
    op.drop_index("uq_uzyt_email", table_name="uzytkownicy")
    op.drop_table("uzytkownicy")
