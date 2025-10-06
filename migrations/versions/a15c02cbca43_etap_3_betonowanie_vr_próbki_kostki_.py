from alembic import op
import sqlalchemy as sa

revision = "dsib_etap3_beton_v1"
down_revision = "dsib_etap2b_protokoly_v1"
branch_labels = None
depends_on = None

def upgrade():
    # --- Betonowanie fizyczne (z wyjazdu) ---
    op.create_table(
        "betonowanie",
        sa.Column("id_betonowanie", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_protokol", sa.Integer(), nullable=True),
        sa.Column("godz_przyjazdu", sa.Time(), nullable=True),
        sa.Column("id_recepty_beton", sa.Integer(), nullable=True),
        sa.Column("klasa", sa.String(64), nullable=True),
        sa.Column("konsystencja", sa.String(64), nullable=True),
        sa.Column("powietrze", sa.Float(), nullable=True),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("element", sa.String(255), nullable=True),
        sa.Column("zlecona_suma_kostek", sa.Integer(), nullable=True),
        sa.Column("godz_odjazdu", sa.Time(), nullable=True),
        sa.ForeignKeyConstraint(["id_roboczy_protokol"], ["roboczy_protokol.id_roboczy_protokol"], name="fk_beton_robo", ondelete="SET NULL"),
    )

    # --- Betonowanie VR (nie było nas na miejscu) ---
    op.create_table(
        "betonowanie_vr",
        sa.Column("id_betonowanie_vr", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_zlecenie", sa.Integer(), nullable=True),
        sa.Column("id_inwestycji", sa.Integer(), nullable=True),
        sa.Column("data", sa.Date(), nullable=False, server_default=sa.text("(DATE('now'))")),
        sa.Column("id_recepty_beton", sa.Integer(), nullable=True),
        sa.Column("klasa", sa.String(64), nullable=True),
        sa.Column("konsystencja", sa.String(64), nullable=True),
        sa.Column("powietrze", sa.Float(), nullable=True),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("element", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["id_inwestycji"], ["inwestycje.id_inwestycji"], name="fk_betonvr_inwestycja", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_zlecenie"], ["zlecenia.id_zlecenie"], name="fk_betonvr_zlecenie", ondelete="SET NULL"),
    )

    # --- Beton próbki ---
    op.create_table(
        "beton_probka",
        sa.Column("id_beton_probka", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_betonowanie", sa.Integer(), nullable=True),
        sa.Column("id_betonowanie_vr", sa.Integer(), nullable=True),
        sa.Column("id_licznik_tech_kostki", sa.Integer(), nullable=True),
        sa.Column("nr_kostki", sa.String(64), nullable=True),
        sa.Column("ilosc_kostek_10", sa.Integer(), nullable=True),
        sa.Column("ilosc_kostek_15", sa.Integer(), nullable=True),
        sa.Column("nasiakliwosc", sa.Float(), nullable=True),
        sa.Column("wodoszczelnosc", sa.Float(), nullable=True),
        sa.Column("mrozoodpornosc", sa.String(64), nullable=True),
        sa.Column("suma_kostek", sa.Integer(), nullable=True),

        # CHECK-i muszą być w CREATE TABLE na SQLite:
        sa.CheckConstraint(
            "( (id_betonowanie IS NOT NULL) <> (id_betonowanie_vr IS NOT NULL) )",
            name="ck_probka_xor_beton"
        ),
        sa.CheckConstraint(
            "(suma_kostek = COALESCE(ilosc_kostek_10,0) + COALESCE(ilosc_kostek_15,0))",
            name="ck_probka_suma"
        ),

        sa.ForeignKeyConstraint(["id_betonowanie"], ["betonowanie.id_betonowanie"], name="fk_probka_beton",
                                ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_betonowanie_vr"], ["betonowanie_vr.id_betonowanie_vr"], name="fk_probka_betonvr",
                                ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_licznik_tech_kostki"], ["licznik_tech_kostki.id"], name="fk_probka_kostki",
                                ondelete="SET NULL"),
    )

    # --- Kostki ściskanie ---
    op.create_table(
        "kostki_sciskanie",
        sa.Column("id_kostki_sciskanie", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_beton_probka", sa.Integer(), nullable=False),
        sa.Column("id_pracownika", sa.Integer(), nullable=True),
        sa.Column("data_pomiaru", sa.Date(), server_default=sa.text("(DATE('now'))")),
        sa.Column("po_ilu_dniach", sa.Integer(), nullable=True),
        sa.Column("wymiar", sa.String(32), nullable=True),
        sa.Column("wynik_1", sa.Float(), nullable=True),
        sa.Column("wynik_2", sa.Float(), nullable=True),
        sa.Column("wynik_3", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["id_beton_probka"], ["beton_probka.id_beton_probka"], name="fk_kostki_probka", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_pracownika"], ["pracownicy.id_pracownika"], name="fk_kostki_pracownik", ondelete="SET NULL"),
    )

    # --- Protokół stożek ---
    op.create_table(
        "protokol_stozek",
        sa.Column("id_protokol_stozek", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_betonowanie", sa.Integer(), nullable=True),
        sa.Column("id_betonowanie_vr", sa.Integer(), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_stozek_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_betonowanie"], ["betonowanie.id_betonowanie"], name="fk_stozek_beton", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_betonowanie_vr"], ["betonowanie_vr.id_betonowanie_vr"], name="fk_stozek_betonvr", ondelete="SET NULL"),
    )

    # --- Protokół powietrze ---
    op.create_table(
        "protokol_powietrze",
        sa.Column("id_protokol_powietrze", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_betonowanie", sa.Integer(), nullable=True),
        sa.Column("id_betonowanie_vr", sa.Integer(), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_powietrze_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_betonowanie"], ["betonowanie.id_betonowanie"], name="fk_powietrze_beton", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_betonowanie_vr"], ["betonowanie_vr.id_betonowanie_vr"], name="fk_powietrze_betonvr", ondelete="SET NULL"),
    )

    # --- Protokół ściskanie beton ---
    op.create_table(
        "protokol_sciskanie_beton",
        sa.Column("id_protokol_sciskanie_beton", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_kostki_sciskanie", sa.Integer(), nullable=False),
        sa.Column("id_beton_probka", sa.Integer(), nullable=True),
        sa.Column("id_pracownika", sa.Integer(), nullable=True),
        sa.Column("data", sa.Date(), server_default=sa.text("(DATE('now'))")),
        sa.Column("po_ilu_dniach", sa.Integer(), nullable=True),
        sa.Column("wymiar", sa.String(32), nullable=True),
        sa.Column("wynik_1", sa.Float(), nullable=True),
        sa.Column("wynik_2", sa.Float(), nullable=True),
        sa.Column("wynik_3", sa.Float(), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_scisk_beton_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_kostki_sciskanie"], ["kostki_sciskanie.id_kostki_sciskanie"], name="fk_scisk_beton_kostki", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_beton_probka"], ["beton_probka.id_beton_probka"], name="fk_scisk_beton_probka", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_pracownika"], ["pracownicy.id_pracownika"], name="fk_scisk_beton_pracownik", ondelete="SET NULL"),
    )


def downgrade():
    op.drop_table("protokol_sciskanie_beton")
    op.drop_table("protokol_powietrze")
    op.drop_table("protokol_stozek")
    op.drop_table("kostki_sciskanie")
    op.drop_constraint("ck_probka_suma", "beton_probka", type_="check")
    op.drop_constraint("ck_probka_xor_beton", "beton_probka", type_="check")
    op.drop_table("beton_probka")
    op.drop_table("betonowanie_vr")
    op.drop_table("betonowanie")
