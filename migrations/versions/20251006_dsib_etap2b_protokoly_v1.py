from alembic import op
import sqlalchemy as sa

# UWAGA: dokładnie te ID
revision = "dsib_etap2b_protokoly_v1"
down_revision = "dsib_etap2a_teren_v1"
branch_labels = None
depends_on = None

def upgrade():
    # --- Protokol VSS (1 badanie na dokument) ---
    op.create_table(
        "protokol_vss",
        sa.Column("id_protokol_vss", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_vss_roboczy_wyniki", sa.Integer(), nullable=False),

        sa.Column("data", sa.Date(), nullable=False, server_default=sa.text("(DATE('now'))")),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("lokalizacja", sa.String(255), nullable=True),
        sa.Column("warstwa", sa.String(255), nullable=True),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),

        sa.Column("E1", sa.Float(), nullable=True),
        sa.Column("E2", sa.Float(), nullable=True),

        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_vss_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_vss_roboczy_wyniki"], ["vss_roboczy_wyniki.id_vss_roboczy_wyniki"], name="fk_vss_roboczy", ondelete="RESTRICT"),
    )
    op.create_index("ix_protokol_vss_licznik", "protokol_vss", ["id_licznik_tech_prot"], unique=False)

    # --- Protokol LPD (wiele wyników) ---
    op.create_table(
        "protokol_lpd",
        sa.Column("id_protokol_lpd", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_lpd_roboczy", sa.Integer(), nullable=False),

        sa.Column("data", sa.Date(), nullable=False, server_default=sa.text("(DATE('now'))")),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("lokalizacja", sa.String(255), nullable=True),
        sa.Column("warstwa", sa.String(255), nullable=True),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),

        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_lpd_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_lpd_roboczy"], ["lpd_roboczy.id_lpd_roboczy"], name="fk_lpd_roboczy", ondelete="RESTRICT"),
    )
    op.create_index("ix_protokol_lpd_licznik", "protokol_lpd", ["id_licznik_tech_prot"], unique=False)

    op.create_table(
        "protokol_lpd_wyniki",
        sa.Column("id_protokol_lpd_wyniki", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_protokol_lpd", sa.Integer(), nullable=False),
        sa.Column("wynik", sa.Float(), nullable=False),
        sa.Column("kolejnosc", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["id_protokol_lpd"], ["protokol_lpd.id_protokol_lpd"], name="fk_lpdwyn_protokol", ondelete="CASCADE"),
    )
    op.create_index("ix_protokol_lpd_wyniki_protokol", "protokol_lpd_wyniki", ["id_protokol_lpd"])

    # --- Protokol SD (1 badanie, snapshot szeroki 0.1..6.0) ---
    wide_cols = [sa.Column(f"v_{str(x/10).replace('.', '_')}", sa.Float(), nullable=True) for x in range(1, 61)]
    op.create_table(
        "protokol_sd",
        sa.Column("id_protokol_sd", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_licznik_tech_prot", sa.Integer(), nullable=False),
        sa.Column("id_sd_roboczy_wyniki", sa.Integer(), nullable=False),

        sa.Column("data", sa.Date(), nullable=False, server_default=sa.text("(DATE('now'))")),
        sa.Column("obiekt", sa.String(255), nullable=True),
        sa.Column("lokalizacja", sa.String(255), nullable=True),
        sa.Column("warstwa", sa.String(255), nullable=True),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("uwagi", sa.Text(), nullable=True),

        *wide_cols,

        sa.ForeignKeyConstraint(["id_licznik_tech_prot"], ["licznik_tech_prot.id"], name="fk_sd_licznik", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["id_sd_roboczy_wyniki"], ["sd_roboczy_wyniki.id_sd_roboczy_wyniki"], name="fk_sd_roboczy", ondelete="RESTRICT"),
    )
    op.create_index("ix_protokol_sd_licznik", "protokol_sd", ["id_licznik_tech_prot"], unique=False)

def downgrade():
    op.drop_index("ix_protokol_sd_licznik", table_name="protokol_sd")
    op.drop_table("protokol_sd")

    op.drop_index("ix_protokol_lpd_wyniki_protokol", table_name="protokol_lpd_wyniki")
    op.drop_table("protokol_lpd_wyniki")

    op.drop_index("ix_protokol_lpd_licznik", table_name="protokol_lpd")
    op.drop_table("protokol_lpd")

    op.drop_index("ix_protokol_vss_licznik", table_name="protokol_vss")
    op.drop_table("protokol_vss")
