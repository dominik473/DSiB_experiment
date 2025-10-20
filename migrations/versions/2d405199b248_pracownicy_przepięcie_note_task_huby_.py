from alembic import op
import sqlalchemy as sa

# --- Identyfikatory migracji ---
revision = "dsib_pracownicy_huby_drop_user_v1"
down_revision = "cleanup_drop_staging_add_idx"  # <- USTAW: wynik `flask db current`
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    # 1) PRACOWNICY (docelowa tabela użytkowników systemu)
    op.create_table(
        "pracownicy",
        sa.Column("id_pracownika", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("imie", sa.String(length=120), nullable=True),
        sa.Column("nazwisko", sa.String(length=120), nullable=True),
        sa.Column("data_urodzin", sa.Date(), nullable=True),       # jeśli chcesz: nullable=False
        sa.Column("data_zatrudnienia", sa.Date(), nullable=True),  # jeśli chcesz: nullable=False
        sa.Column("data_zwolnienia", sa.Date(), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("haslo", sa.String(length=255), nullable=True),
    )
    # Unikalność emaila (opcjonalnie None dopuszczalne, unikaty działają na nie-NULL)
    op.create_index("uq_pracownicy_email", "pracownicy", ["email"], unique=True)

    # 2) PRZEPIĘCIE FK w NOTE: user -> pracownicy
    # Istniejąca struktura: created_by_id INTEGER NOT NULL, FK -> user(id), indeksy ix_note_*
    # Użyjemy batch_alter_table, by SQLite sobie poradził z rekreacją.
    if dialect == "sqlite":
        recreate_kwargs = {"sqlite_autoincrement": True}
    else:
        recreate_kwargs = {}

    with op.batch_alter_table("note", recreate="always") as b:
        try:
            b.drop_constraint("fk_note_created_by", type_="foreignkey")
        except Exception:
            pass
        b.create_foreign_key(
            "fk_note_created_by_pracownicy",
            "pracownicy",
            local_cols=["created_by_id"],
            remote_cols=["id_pracownika"],
            ondelete="SET NULL",
        )

    # 3) PRZEPIĘCIE FK w TASK: user -> pracownicy (dla dwóch kolumn)
    with op.batch_alter_table("task", recreate="always") as b:
        for old_fk in ("fk_task_assigned_to", "fk_task_created_by"):
            try:
                b.drop_constraint(old_fk, type_="foreignkey")
            except Exception:
                pass
        b.create_foreign_key(
            "fk_task_assigned_to_pracownicy",
            "pracownicy",
            local_cols=["assigned_to_id"],
            remote_cols=["id_pracownika"],
            ondelete="SET NULL",
        )
        b.create_foreign_key(
            "fk_task_created_by_pracownicy",
            "pracownicy",
            local_cols=["created_by_id"],
            remote_cols=["id_pracownika"],
            ondelete="SET NULL",
        )

    # 4) HUB NUMERÓW PROTOKOŁÓW
    op.create_table(
        "licznik_tech_prot",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("data_wprowadzenia", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("nr_inwestycji", sa.String(length=64), nullable=False),
        sa.Column("data", sa.Date(), nullable=True),
        sa.Column("rok_iso", sa.Integer(), nullable=False),
        sa.Column("tydzien_iso", sa.Integer(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("nr_protokolu", sa.String(length=64), nullable=True),  # etykieta pomocnicza (opcjonalna)
        sa.Column("anulowany", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("faktura", sa.String(length=64), nullable=True),
    )
    op.create_unique_constraint(
        "uq_licznik_tech_prot_nr_rok_tydz_seq",
        "licznik_tech_prot",
        ["nr_inwestycji", "rok_iso", "tydzien_iso", "seq"],
    )

    # 5) HUB NUMERÓW KOSTEK
     # 6) DROP legacy USER (u Ciebie 0 rekordów)
    # Najpierw upewniliśmy się, że żadne FK już nie wskazują na 'user'.
    op.execute("DROP TABLE IF EXISTS user")


def downgrade():
    # Przywrócenie legacy user (minimalne, by zaspokoić FK)
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("surname", sa.String(length=120), nullable=True),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)


    op.drop_constraint("uq_licznik_tech_prot_nr_rok_tydz_seq", "licznik_tech_prot", type_="unique")
    op.drop_table("licznik_tech_prot")

    # Przywróć FK w task/note na user
    with op.batch_alter_table("task", recreate="always") as b:
        try:
            b.drop_constraint("fk_task_assigned_to_pracownicy", type_="foreignkey")
        except Exception:
            pass
        try:
            b.drop_constraint("fk_task_created_by_pracownicy", type_="foreignkey")
        except Exception:
            pass
        b.create_foreign_key(
            "fk_task_assigned_to", "user",
            local_cols=["assigned_to_id"], remote_cols=["id"], ondelete="SET NULL",
        )
        b.create_foreign_key(
            "fk_task_created_by", "user",
            local_cols=["created_by_id"], remote_cols=["id"], ondelete="SET NULL",
        )

    with op.batch_alter_table("note", recreate="always") as b:
        try:
            b.drop_constraint("fk_note_created_by_pracownicy", type_="foreignkey")
        except Exception:
            pass
        b.create_foreign_key(
            "fk_note_created_by", "user",
            local_cols=["created_by_id"], remote_cols=["id"], ondelete="SET NULL",
        )

    # Usuń pracownicy
    op.drop_index("uq_pracownicy_email", table_name="pracownicy")
    op.drop_table("pracownicy")
