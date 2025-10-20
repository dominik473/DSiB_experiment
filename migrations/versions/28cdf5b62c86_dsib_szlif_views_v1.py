""" dsib_szlif_views_v1

Revision ID: 28cdf5b62c86
Revises: 2fdf143d5234
Create Date: 2025-10-13 12:00:31.193590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28cdf5b62c86'
down_revision = '2fdf143d5234'
branch_labels = None
depends_on = None


def upgrade():
    # v_protokoly — rozszerzona o wszystkie protokoły
    op.execute("DROP VIEW IF EXISTS v_protokoly;")
    op.execute("""
    CREATE VIEW v_protokoly AS
    SELECT 'VSS' AS typ, id_protokol_vss AS id, id_licznik_tech_prot AS id_nr, data, obiekt, lokalizacja, warstwa, material
      FROM protokol_vss
    UNION ALL
    SELECT 'LPD', id_protokol_lpd, id_licznik_tech_prot, data, obiekt, lokalizacja, warstwa, material
      FROM protokol_lpd
    UNION ALL
    SELECT 'SD', id_protokol_sd, id_licznik_tech_prot, data, obiekt, lokalizacja, warstwa, material
      FROM protokol_sd
    UNION ALL
    SELECT 'STABIL_SCISK', id_protokol_stabil_sciskanie, id_licznik_tech_prot, data, NULL, NULL, NULL, NULL
      FROM protokol_stabil_sciskanie
    UNION ALL
    SELECT 'ANALIZA_SIT', id_protokol_analiza_sitowa, id_licznik_tech_prot, data, obiekt, lokalizacja, warstwa, material
      FROM protokol_analiza_sitowa
    UNION ALL
    SELECT 'WSK_PIASK', id_protokol_wskaznik_piaskowy, id_licznik_tech_prot, data, obiekt, lokalizacja, warstwa, material
      FROM protokol_wskaznik_piaskowy
    UNION ALL
    SELECT 'STOZEK', id_protokol_stozek, id_licznik_tech_prot, NULL, NULL, NULL, NULL, NULL
      FROM protokol_stozek
    UNION ALL
    SELECT 'POWIETRZE', id_protokol_powietrze, id_licznik_tech_prot, NULL, NULL, NULL, NULL, NULL
      FROM protokol_powietrze
    UNION ALL
    SELECT 'SCISK_BETON', id_protokol_sciskanie_beton, id_licznik_tech_prot, data, NULL, NULL, NULL, NULL
      FROM protokol_sciskanie_beton;
    """)

    # v_beton_przeglad — przegląd betonowań
    op.execute("DROP VIEW IF EXISTS v_beton_przeglad;")
    op.execute("""
    CREATE VIEW v_beton_przeglad AS
    SELECT b.id_betonowanie AS id, 'BETON' AS zrodlo, b.obiekt, b.element, b.klasa, b.konsystencja, b.powietrze, b.zlecona_suma_kostek
      FROM betonowanie b
    UNION ALL
    SELECT vr.id_betonowanie_vr, 'BETON_VR', vr.obiekt, vr.element, vr.klasa, vr.konsystencja, vr.powietrze, NULL
      FROM betonowanie_vr vr;
    """)

def downgrade():
    # Przy downgrade odtwarzamy wersje minimalne (lub kasujemy, jeśli wolisz czystość)
    op.execute("DROP VIEW IF EXISTS v_beton_przeglad;")
    op.execute("DROP VIEW IF EXISTS v_protokoly;")
