"""Etap 4: meta (linki notatek/zadań, komentarze, checklisty, słowniki, widoki)

Revision ID: 251f37337d62
Revises: dsib_etap3_beton_v1
Create Date: 2025-10-11 14:21:28.203556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dsib_etap4_meta_v1"
down_revision = 'dsib_etap3_beton_v1'
branch_labels = None
depends_on = None


# do użycia w CHECK-ach
NOTE_TARGETS = "('klient','inwestycja','zlecenie','roboczy_protokol','rg_insitu','protokol_vss','protokol_lpd','protokol_sd','betonowanie','betonowanie_vr','beton_probka','protokol_stozek','protokol_powietrze','protokol_sciskanie_beton')"
TASK_TARGETS = NOTE_TARGETS

def upgrade():
    # 1) NOTE LINKS (polimorficzne)
    op.create_table(
        "note_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(f"target_type IN {NOTE_TARGETS}", name="ck_note_links_target_type"),
        sa.ForeignKeyConstraint(["note_id"], ["note.id"], name="fk_note_links_note", ondelete="CASCADE"),
    )
    op.create_index("ix_note_links_note", "note_links", ["note_id"])
    op.create_index("ix_note_links_target", "note_links", ["target_type", "target_id"])

    # 2) TASK LINKS (polimorficzne)
    op.create_table(
        "task_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(f"target_type IN {TASK_TARGETS}", name="ck_task_links_target_type"),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], name="fk_task_links_task", ondelete="CASCADE"),
    )
    op.create_index("ix_task_links_task", "task_links", ["task_id"])
    op.create_index("ix_task_links_target", "task_links", ["target_type", "target_id"])

    # 3) NOTE COMMENTS
    op.create_table(
        "note_comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("author_kind", sa.String(20), nullable=False),  # 'staff' | 'client'
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("author_kind IN ('staff','client')", name="ck_note_comments_author_kind"),
        sa.ForeignKeyConstraint(["note_id"], ["note.id"], name="fk_note_comments_note", ondelete="CASCADE"),
    )
    op.create_index("ix_note_comments_note", "note_comments", ["note_id", "created_at"])

    # 4) TASK CHECKLIST
    op.create_table(
        "task_checklist",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("item_text", sa.String(255), nullable=False),
        sa.Column("is_done", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], name="fk_task_checklist_task", ondelete="CASCADE"),
    )
    op.create_index("ix_task_checklist_task", "task_checklist", ["task_id", "order_index"])

    # 5) SŁOWNIKI (lekkie)
    op.create_table(
        "slownik_materialow",
        sa.Column("id_material", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nazwa", sa.String(120), nullable=False, unique=True),
        sa.Column("opis", sa.String(255), nullable=True),
    )
    op.create_table(
        "slownik_klas_betonu",
        sa.Column("id_klasa", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("symbol", sa.String(50), nullable=False, unique=True),  # np. C25/30
        sa.Column("opis", sa.String(255), nullable=True),
    )
    op.create_table(
        "slownik_typow_badan",
        sa.Column("id_typ", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("kod", sa.String(50), nullable=False, unique=True),  # np. 'VSS','LPD','SD','STOZEK'
        sa.Column("nazwa", sa.String(120), nullable=False),
    )

    # 6) WIDOKI (SQLite: zwykły CREATE VIEW)
    op.execute("""
    CREATE VIEW IF NOT EXISTS v_labownik AS
    SELECT rp.id_roboczy_protokol,
           rp.data,
           rp.id_inwestycji,
           i.nr_inwestycji,
           rg.id_roboczy_gruntu_insitu,
           rg.obiekt, rg.lokalizacja, rg.warstwa, rg.material
    FROM roboczy_protokol rp
    LEFT JOIN inwestycje i ON i.id_inwestycji = rp.id_inwestycji
    LEFT JOIN roboczy_gruntu_insitu rg ON rg.id_roboczy_protokol = rp.id_roboczy_protokol;
    """)

    op.execute("""
    CREATE VIEW IF NOT EXISTS v_protokoly AS
    SELECT 'VSS' AS typ, pv.id_protokol_vss AS id, pv.id_licznik_tech_prot AS id_nr, pv.data, pv.obiekt, pv.lokalizacja, pv.warstwa, pv.material
      FROM protokol_vss pv
    UNION ALL
    SELECT 'LPD', pl.id_protokol_lpd, pl.id_licznik_tech_prot, pl.data, pl.obiekt, pl.lokalizacja, pl.warstwa, pl.material
      FROM protokol_lpd pl
    UNION ALL
    SELECT 'SD', psd.id_protokol_sd, psd.id_licznik_tech_prot, psd.data, psd.obiekt, psd.lokalizacja, psd.warstwa, psd.material
      FROM protokol_sd psd
    UNION ALL
    SELECT 'STOZEK', pst.id_protokol_stozek, pst.id_licznik_tech_prot, NULL, NULL, NULL, NULL, NULL
      FROM protokol_stozek pst
    UNION ALL
    SELECT 'POWIETRZE', pp.id_protokol_powietrze, pp.id_licznik_tech_prot, NULL, NULL, NULL, NULL, NULL
      FROM protokol_powietrze pp
    UNION ALL
    SELECT 'SCISK_BETON', psb.id_protokol_sciskanie_beton, psb.id_licznik_tech_prot, psb.data, NULL, NULL, NULL, NULL
      FROM protokol_sciskanie_beton psb;
    """)

    op.execute("""
    CREATE VIEW IF NOT EXISTS v_beton_przeglad AS
    SELECT b.id_betonowanie AS id, 'BETON' AS zrodlo, b.obiekt, b.element, b.klasa, b.konsystencja, b.powietrze, b.zlecona_suma_kostek
      FROM betonowanie b
    UNION ALL
    SELECT vr.id_betonowanie_vr, 'BETON_VR', vr.obiekt, vr.element, vr.klasa, vr.konsystencja, vr.powietrze, NULL
      FROM betonowanie_vr vr;
    """)

def downgrade():
    op.execute("DROP VIEW IF EXISTS v_beton_przeglad;")
    op.execute("DROP VIEW IF EXISTS v_protokoly;")
    op.execute("DROP VIEW IF EXISTS v_labownik;")

    op.drop_table("slownik_typow_badan")
    op.drop_table("slownik_klas_betonu")
    op.drop_table("slownik_materialow")

    op.drop_index("ix_task_checklist_task", table_name="task_checklist")
    op.drop_table("task_checklist")

    op.drop_index("ix_note_comments_note", table_name="note_comments")
    op.drop_table("note_comments")

    op.drop_index("ix_task_links_target", table_name="task_links")
    op.drop_index("ix_task_links_task", table_name="task_links")
    op.drop_table("task_links")

    op.drop_index("ix_note_links_target", table_name="note_links")
    op.drop_index("ix_note_links_note", table_name="note_links")
    op.drop_table("note_links")
