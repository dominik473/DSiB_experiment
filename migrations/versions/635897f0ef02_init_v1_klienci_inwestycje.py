"""init v1: klienci + inwestycje"""

from alembic import op
import sqlalchemy as sa

# --- revision identifiers ---
revision = "635897f0ef02"
down_revision = "b31f811ee37b"
branch_labels = None
depends_on = None

# zmień, jeśli masz inną nazwę tabeli z użytkownikami
USER_TBL = "user"


def upgrade():
    # --- Tabela: klienci ---
    op.create_table(
        "klienci",
        sa.Column("id_klienta", sa.Integer(), primary_key=True),
        sa.Column("nazwa_skrocona", sa.String(length=128), nullable=False),
        sa.Column("nazwa_firmy", sa.String(length=255), nullable=True),
        sa.Column("adres", sa.String(length=255), nullable=True),
        sa.Column("kod_pocztowy", sa.String(length=16), nullable=True),
        sa.Column("miejscowosc", sa.String(length=128), nullable=True),
        sa.Column("nip", sa.String(length=32), nullable=True),
        sa.UniqueConstraint("nazwa_skrocona", name="uq_klienci_nazwa_skrocona"),
        sa.UniqueConstraint(
            "nazwa_firmy",
            "adres",
            "kod_pocztowy",
            "miejscowosc",
            "nip",
            name="uq_klienci_firma_adres_kod_miejsc_nip",
        ),
    )

    # --- Tabela: inwestycje ---
    op.create_table(
        "inwestycje",
        sa.Column("id_inwestycji", sa.Integer(), primary_key=True),
        sa.Column("nr_inwestycji", sa.String(length=32), nullable=True, unique=True),
        # staging do importu; usuniemy później osobną migracją
        sa.Column("nazwa_skrocona_klienta", sa.String(length=128), nullable=True),
        sa.Column("id_klienta", sa.Integer(), nullable=True),
        sa.Column("pelna_nazwa_inwestycji", sa.String(length=255), nullable=False),
        sa.Column("status_crm", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_klienta"],
            ["klienci.id_klienta"],
            name="fk_inwestycje_klient",
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint(
            "id_klienta",
            "pelna_nazwa_inwestycji",
            name="uq_inwestycje_klient_pelna_nazwa",
        ),
    )

    # --- Modyfikacje istniejących tabel: note ---
    with op.batch_alter_table("note", schema=None) as batch_op:
        batch_op.create_index("ix_note_created_at", ["created_at"], unique=False)
        batch_op.create_foreign_key(
            "fk_note_created_by",
            USER_TBL,
            ["created_by_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # --- Modyfikacje istniejących tabel: task ---
    with op.batch_alter_table("task", schema=None) as batch_op:
        batch_op.create_index("ix_task_created_at", ["created_at"], unique=False)
        batch_op.create_index("ix_task_done", ["done"], unique=False)
        batch_op.create_index("ix_task_due_at", ["due_at"], unique=False)
        batch_op.create_foreign_key(
            "fk_task_assigned_to",
            USER_TBL,
            ["assigned_to_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_task_created_by",
            USER_TBL,
            ["created_by_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():
    # --- Cofnięcie zmian w task ---
    with op.batch_alter_table("task", schema=None) as batch_op:
        try:
            batch_op.drop_constraint("fk_task_assigned_to", type_="foreignkey")
        except Exception:
            pass
        try:
            batch_op.drop_constraint("fk_task_created_by", type_="foreignkey")
        except Exception:
            pass
        try:
            batch_op.drop_index("ix_task_created_at")
        except Exception:
            pass
        try:
            batch_op.drop_index("ix_task_done")
        except Exception:
            pass
        try:
            batch_op.drop_index("ix_task_due_at")
        except Exception:
            pass

    # --- Cofnięcie zmian w note ---
    with op.batch_alter_table("note", schema=None) as batch_op:
        try:
            batch_op.drop_constraint("fk_note_created_by", type_="foreignkey")
        except Exception:
            pass
        try:
            batch_op.drop_index("ix_note_created_at")
        except Exception:
            pass

    # --- Drop: inwestycje, klienci ---
    try:
        op.drop_table("inwestycje")
    except Exception:
        pass
    try:
        op.drop_table("klienci")
    except Exception:
        pass
