from alembic import op
import sqlalchemy as sa

# Id migracji
revision = "dsib_etap2a_teren_v1"
down_revision = "dsib_pracownicy_huby_drop_user_v1"   # np. dsib_pracownicy_huby_drop_user_v1
branch_labels = None
depends_on = None

def upgrade():
    # 1) ZLECENIA (luźny „request”/wyjazd)
    op.create_table(
        "zlecenia",
        sa.Column("id_zlecenie", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("id_kontaktu", sa.Integer(), nullable=True),        # na przyszłość (użytkownicy/klienci)
        sa.Column("id_inwestycji", sa.Integer(), nullable=True),
        sa.Column("id_pracownika", sa.Integer(), nullable=True),      # autor/zleceniobiorca (zalogowany)
        sa.Column("miejsce", sa.String(255), nullable=True),          # jeśli brak inwestycji
        sa.Column("czas_realizacji", sa.DateTime(), nullable=True),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_inwestycji"], ["inwestycje.id_inwestycji"], name="fk_zlecenia_inwestycje", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_pracownika"], ["pracownicy.id_pracownika"], name="fk_zlecenia_pracownik", ondelete="SET NULL"),
    )
    op.create_index("ix_zlecenia_inwestycja", "zlecenia", ["id_inwestycji"])
    op.create_index("ix_zlecenia_pracownik_czas", "zlecenia", ["id_pracownika", "czas_realizacji"])

    # 2) ROBOCZY PROTOKÓŁ (nagłówek dnia/wyjazdu)
    op.create_table(
        "roboczy_protokol",
        sa.Column("id_roboczy_protokol", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_pracownika", sa.Integer(), nullable=True),
        sa.Column("id_zlecenie", sa.Integer(), nullable=True),
        sa.Column("id_inwestycji", sa.Integer(), nullable=True),  # może być ustawiane niezależnie od zlecenia
        sa.Column("data", sa.Date(), server_default=sa.text("(DATE('now'))"), nullable=False),
        sa.Column("zalacznik_path", sa.String(512), nullable=True),  # jeśli zamiast pól załączamy foto/pdf
        sa.ForeignKeyConstraint(["id_pracownika"], ["pracownicy.id_pracownika"], name="fk_robo_pracownik", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_zlecenie"], ["zlecenia.id_zlecenie"], name="fk_robo_zlecenie", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["id_inwestycji"], ["inwestycje.id_inwestycji"], name="fk_robo_inwestycja", ondelete="SET NULL"),
    )
    op.create_index("ix_robo_inwestycja", "roboczy_protokol", ["id_inwestycji"])

    # 3) ROBOCZY GRUNTU IN SITU (kontekst punktu)
    op.create_table(
        "roboczy_gruntu_insitu",
        sa.Column("id_roboczy_gruntu_insitu", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_protokol", sa.Integer(), nullable=False),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("lokalizacja", sa.String(255), nullable=True),
        sa.Column("warstwa", sa.String(255), nullable=False),
        sa.Column("material", sa.String(255), nullable=False),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_roboczy_protokol"], ["roboczy_protokol.id_roboczy_protokol"], name="fk_rg_insitu_robo", ondelete="CASCADE"),
    )
    op.create_index("ix_rg_insitu_robo", "roboczy_gruntu_insitu", ["id_roboczy_protokol"])

    # 4) VSS ro-bocze wyniki (1 punkt na dokument docelowo, ale roboczo trzymamy punkty tutaj)
    op.create_table(
        "vss_roboczy_wyniki",
        sa.Column("id_vss_roboczy_wyniki", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_gruntu_insitu", sa.Integer(), nullable=False),
        sa.Column("E1", sa.Float(), nullable=True),
        sa.Column("E2", sa.Float(), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_roboczy_gruntu_insitu"], ["roboczy_gruntu_insitu.id_roboczy_gruntu_insitu"], name="fk_vss_rg_insitu", ondelete="CASCADE"),
    )
    op.create_index("ix_vss_rg", "vss_roboczy_wyniki", ["id_roboczy_gruntu_insitu"])

    # 5) LPD ro-bocze (nagłówek pojedynczego pomiaru)
    op.create_table(
        "lpd_roboczy",
        sa.Column("id_lpd_roboczy", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_gruntu_insitu", sa.Integer(), nullable=False),
        sa.Column("odczyt_evd", sa.Float(), nullable=True),   # jeśli chcesz nagłówkowy odczyt
        sa.Column("punkt_opis", sa.String(255), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["id_roboczy_gruntu_insitu"], ["roboczy_gruntu_insitu.id_roboczy_gruntu_insitu"], name="fk_lpd_rg_insitu", ondelete="CASCADE"),
    )
    op.create_index("ix_lpd_rg", "lpd_roboczy", ["id_roboczy_gruntu_insitu"])

    op.create_table(
        "lpd_roboczy_wyniki",
        sa.Column("id_lpd_roboczy_wyniki", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_lpd_roboczy", sa.Integer(), nullable=False),
        sa.Column("wynik", sa.Float(), nullable=False),
        sa.Column("kolejnosc", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["id_lpd_roboczy"], ["lpd_roboczy.id_lpd_roboczy"], name="fk_lpd_wyniki_lpd", ondelete="CASCADE"),
    )
    op.create_index("ix_lpd_wyniki_lpd", "lpd_roboczy_wyniki", ["id_lpd_roboczy"])

    # 6) SD ro-bocze — snapshot szeroki (0.1 … 6.0 co 0.1 m)
    op.create_table(
        "sd_roboczy_wyniki",
        sa.Column("id_sd_roboczy_wyniki", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_roboczy_gruntu_insitu", sa.Integer(), nullable=False),
        sa.Column("punkt_opis", sa.String(255), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),

        # kolumny 0.1 ... 6.0 – liczby zmiennoprzecinkowe
        # (możesz je ograniczyć do np. NUMERIC(6,2) jeśli wolisz)
        *[sa.Column(f"v_{str(x/10).replace('.', '_')}", sa.Float(), nullable=True) for x in range(1, 61)],

        sa.ForeignKeyConstraint(["id_roboczy_gruntu_insitu"], ["roboczy_gruntu_insitu.id_roboczy_gruntu_insitu"], name="fk_sd_rg_insitu", ondelete="CASCADE"),
    )
    op.create_index("ix_sd_rg", "sd_roboczy_wyniki", ["id_roboczy_gruntu_insitu"])


def downgrade():
    op.drop_index("ix_sd_rg", table_name="sd_roboczy_wyniki")
    op.drop_table("sd_roboczy_wyniki")

    op.drop_index("ix_lpd_wyniki_lpd", table_name="lpd_roboczy_wyniki")
    op.drop_table("lpd_roboczy_wyniki")

    op.drop_index("ix_lpd_rg", table_name="lpd_roboczy")
    op.drop_table("lpd_roboczy")

    op.drop_index("ix_vss_rg", table_name="vss_roboczy_wyniki")
    op.drop_table("vss_roboczy_wyniki")

    op.drop_index("ix_rg_insitu_robo", table_name="roboczy_gruntu_insitu")
    op.drop_table("roboczy_gruntu_insitu")

    op.drop_index("ix_robo_inwestycja", table_name="roboczy_protokol")
    op.drop_table("roboczy_protokol")

    op.drop_index("ix_zlecenia_pracownik_czas", table_name="zlecenia")
    op.drop_index("ix_zlecenia_inwestycja", table_name="zlecenia")
    op.drop_table("zlecenia")
