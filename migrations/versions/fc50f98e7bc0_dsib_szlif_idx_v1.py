"""dsib_szlif_idx_v1

Revision ID: fc50f98e7bc0
Revises: 2fd9fc0c156a
Create Date: 2025-10-13 11:53:31.700842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc50f98e7bc0'
down_revision = '4278c31e78b7'
branch_labels = None
depends_on = None


def upgrade():
    def upgrade():
        stmts = [
            # Klienci / Inwestycje
            "CREATE INDEX IF NOT EXISTS ix_inwestycje_klient ON inwestycje (id_klienta)",
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_inwestycje_nr ON inwestycje (nr_inwestycji)",

            # Zlecenia
            "CREATE INDEX IF NOT EXISTS ix_zlecenia_pracownik_czas ON zlecenia (id_pracownika, czas_realizacji)",
            "CREATE INDEX IF NOT EXISTS ix_zlecenia_inwestycja ON zlecenia (id_inwestycji)",
            "CREATE INDEX IF NOT EXISTS ix_zlecenia_uzytkownik ON zlecenia (id_uzytkownika)",

            # Robocze (teren)
            "CREATE INDEX IF NOT EXISTS ix_rginsitu_robo ON roboczy_gruntu_insitu (id_roboczy_protokol)",
            "CREATE INDEX IF NOT EXISTS ix_vss_robo ON vss_roboczy_wyniki (id_roboczy_gruntu_insitu)",
            "CREATE INDEX IF NOT EXISTS ix_lpd_robo ON lpd_roboczy (id_roboczy_gruntu_insitu)",
            "CREATE INDEX IF NOT EXISTS ix_sd_robo ON sd_roboczy_wyniki (id_roboczy_gruntu_insitu)",

            # Protokoły
            "CREATE INDEX IF NOT EXISTS ix_pvss_nr ON protokol_vss (id_licznik_tech_prot)",
            "CREATE INDEX IF NOT EXISTS ix_plpd_nr ON protokol_lpd (id_licznik_tech_prot)",
            "CREATE INDEX IF NOT EXISTS ix_psd_nr ON protokol_sd (id_licznik_tech_prot)",
            "CREATE INDEX IF NOT EXISTS ix_pss_nr ON protokol_stabil_sciskanie (id_licznik_tech_prot)",
            "CREATE INDEX IF NOT EXISTS ix_pas_nr ON protokol_analiza_sitowa (id_licznik_tech_prot)",
            "CREATE INDEX IF NOT EXISTS ix_pwp_nr ON protokol_wskaznik_piaskowy (id_licznik_tech_prot)",
            "CREATE INDEX IF NOT EXISTS ix_psto_nr ON protokol_stozek (id_licznik_tech_prot)",
            "CREATE INDEX IF NOT EXISTS ix_ppow_nr ON protokol_powietrze (id_licznik_tech_prot)",
            "CREATE INDEX IF NOT EXISTS ix_pscb_nr ON protokol_sciskanie_beton (id_licznik_tech_prot)",

            # Beton
            "CREATE INDEX IF NOT EXISTS ix_beton_probka_beton ON beton_probka (id_betonowanie)",
            "CREATE INDEX IF NOT EXISTS ix_beton_probka_betonvr ON beton_probka (id_betonowanie_vr)",
            "CREATE INDEX IF NOT EXISTS ix_kostki_probka ON kostki_sciskanie (id_beton_probka)",

            # CRM / Użytkownicy
            "CREATE INDEX IF NOT EXISTS ix_ok_email_notnull ON osoby_kontaktowe (email)",
            "CREATE INDEX IF NOT EXISTS ix_uzyt_aktywny ON uzytkownicy (aktywny)",
        ]
        for s in stmts:
            op.execute(s)


def downgrade():
    stmts = [
        "DROP INDEX IF EXISTS ix_uzyt_aktywny",
        "DROP INDEX IF EXISTS ix_ok_email_notnull",
        "DROP INDEX IF EXISTS ix_kostki_probka",
        "DROP INDEX IF EXISTS ix_beton_probka_betonvr",
        "DROP INDEX IF EXISTS ix_beton_probka_beton",
        "DROP INDEX IF EXISTS ix_pscb_nr",
        "DROP INDEX IF EXISTS ix_ppow_nr",
        "DROP INDEX IF EXISTS ix_psto_nr",
        "DROP INDEX IF EXISTS ix_pwp_nr",
        "DROP INDEX IF EXISTS ix_pas_nr",
        "DROP INDEX IF EXISTS ix_pss_nr",
        "DROP INDEX IF EXISTS ix_psd_nr",
        "DROP INDEX IF EXISTS ix_plpd_nr",
        "DROP INDEX IF EXISTS ix_pvss_nr",
        "DROP INDEX IF EXISTS ix_sd_robo",
        "DROP INDEX IF EXISTS ix_lpd_robo",
        "DROP INDEX IF EXISTS ix_vss_robo",
        "DROP INDEX IF EXISTS ix_rginsitu_robo",
        "DROP INDEX IF EXISTS ix_zlecenia_uzytkownik",
        "DROP INDEX IF EXISTS ix_zlecenia_inwestycja",
        "DROP INDEX IF EXISTS ix_zlecenia_pracownik_czas",
        "DROP INDEX IF EXISTS ix_inwestycje_nr",
        "DROP INDEX IF EXISTS ix_inwestycje_klient",
    ]
    for s in stmts:
        op.execute(s)
