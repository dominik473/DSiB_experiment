from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# Identyfikatory migracji
revision = "b31f811ee37b"
down_revision = "922e469d2f06"

def _pragma_columns(conn, table_name: str):
    # Zwraca listę nazw kolumn tabeli
    return [r[1] for r in conn.exec_driver_sql(f'PRAGMA table_info("{table_name}")').fetchall()]

def _first_user_id(conn):
    row = conn.exec_driver_sql('SELECT id FROM "user" ORDER BY id LIMIT 1').fetchone()
    return row[0] if row else None

def upgrade():
    conn = op.get_bind()

    # --- sprzątanie po przerwanych recreate
    conn.exec_driver_sql("DROP TABLE IF EXISTS _alembic_tmp_note")
    conn.exec_driver_sql("DROP TABLE IF EXISTS _alembic_tmp_task")

    # =========================
    # USER: add name, surname (jeśli brak)
    # =========================
    user_cols = _pragma_columns(conn, "user")
    with op.batch_alter_table("user") as b:
        if "name" not in user_cols:
            b.add_column(sa.Column("name", sa.String(120)))
        if "surname" not in user_cols:
            b.add_column(sa.Column("surname", sa.String(120)))

    # =========================
    # NOTE: created_by_id + backfill; drop tag/user_id
    # =========================
    note_cols = _pragma_columns(conn, "note")

    # 1) dodaj kolumnę created_by_id (NULLABLE) jeśli brak
    if "created_by_id" not in note_cols:
        op.add_column("note", sa.Column("created_by_id", sa.Integer(), nullable=True))
        # backfill z user_id (jeśli istnieje)
        try:
            conn.exec_driver_sql("UPDATE note SET created_by_id = user_id WHERE created_by_id IS NULL")
        except Exception:
            pass

    # 2) uzupełnij NULL na istniejącego usera (jeśli jest jakikolwiek)
    seed_uid = _first_user_id(conn)
    if seed_uid is not None:
        conn.execute(
            text("UPDATE note SET created_by_id = :uid WHERE created_by_id IS NULL"),
            {"uid": seed_uid},
        )

    # 3) FK + indeks (w try/except, bo mogły już istnieć)
    try:
        op.create_index("ix_note_created_by_id", "note", ["created_by_id"], unique=False)
    except Exception:
        pass
    try:
        op.create_foreign_key(
            "fk_note_created_by_id_user", "note", "user",
            ["created_by_id"], ["id"], ondelete="RESTRICT"
        )
    except Exception:
        pass

    # 4) zdecyduj czy wolno już wymusić NOT NULL
    nulls_count = conn.exec_driver_sql(
        "SELECT COUNT(*) FROM note WHERE created_by_id IS NULL"
    ).fetchone()[0]

    # odśwież listę kolumn przed recreate
    note_cols = _pragma_columns(conn, "note")
    conn.exec_driver_sql("DROP TABLE IF EXISTS _alembic_tmp_note")

    with op.batch_alter_table("note", recreate="always") as b:
        # Tag do usunięcia (jeśli jeszcze istnieje)
        if "tag" in note_cols:
            try:
                b.drop_column("tag")
            except Exception:
                pass
        # user_id do usunięcia (przeszliśmy na created_by_id)
        if "user_id" in note_cols:
            b.drop_column("user_id")
        # created_by_id: NOT NULL tylko, jeśli brak NULL-i
        if nulls_count == 0:
            b.alter_column("created_by_id", existing_type=sa.Integer(), nullable=False)
        # w przeciwnym razie pozostaje NULLABLE i uzupełnisz dane później

    # =========================
    # TASK: assigned_to_id / created_by_id + backfill; drop assignee_id
    # =========================
    task_cols = _pragma_columns(conn, "task")

    # assigned_to_id – jeżeli nie ma, dodaj i skopiuj z assignee_id
    if "assigned_to_id" not in task_cols:
        op.add_column("task", sa.Column("assigned_to_id", sa.Integer(), nullable=True))
        try:
            conn.exec_driver_sql("UPDATE task SET assigned_to_id = assignee_id WHERE assigned_to_id IS NULL")
        except Exception:
            pass
        try:
            op.create_index("ix_task_assigned_to_id", "task", ["assigned_to_id"], unique=False)
        except Exception:
            pass
        try:
            op.create_foreign_key(
                "fk_task_assigned_to_id_user", "task", "user",
                ["assigned_to_id"], ["id"], ondelete="RESTRICT"
            )
        except Exception:
            pass

    # created_by_id – jeżeli nie ma, dodaj i wypełnij (np. najstarszym userem)
    task_cols = _pragma_columns(conn, "task")
    if "created_by_id" not in task_cols:
        op.add_column("task", sa.Column("created_by_id", sa.Integer(), nullable=True))
        try:
            op.create_index("ix_task_created_by_id", "task", ["created_by_id"], unique=False)
        except Exception:
            pass
        try:
            op.create_foreign_key(
                "fk_task_created_by_id_user", "task", "user",
                ["created_by_id"], ["id"], ondelete="RESTRICT"
            )
        except Exception:
            pass

        if seed_uid is not None:
            conn.execute(
                text("UPDATE task SET created_by_id = :uid WHERE created_by_id IS NULL"),
                {"uid": seed_uid},
            )

    # sprawdź czy można już wymusić NOT NULL
    task_assigned_nulls = conn.exec_driver_sql(
        "SELECT COUNT(*) FROM task WHERE assigned_to_id IS NULL"
    ).fetchone()[0]
    task_created_nulls = conn.exec_driver_sql(
        "SELECT COUNT(*) FROM task WHERE created_by_id IS NULL"
    ).fetchone()[0]

    # zrób recreate i usuń assignee_id, NOT NULL tylko gdy realnie brak NULL-i
    task_cols = _pragma_columns(conn, "task")
    conn.exec_driver_sql("DROP TABLE IF EXISTS _alembic_tmp_task")

    with op.batch_alter_table("task", recreate="always") as b:
        if task_assigned_nulls == 0:
            b.alter_column("assigned_to_id", existing_type=sa.Integer(), nullable=False)
        if task_created_nulls == 0:
            b.alter_column("created_by_id", existing_type=sa.Integer(), nullable=False)
        if "assignee_id" in task_cols:
            b.drop_column("assignee_id")

def downgrade():
    conn = op.get_bind()

    # cofnięcie zmian w TASK (przywrócenie assignee_id, usunięcie nowych kolumn/constraintów)
    task_cols = _pragma_columns(conn, "task")
    with op.batch_alter_table("task", recreate="always") as b:
        if "assignee_id" not in task_cols:
            b.add_column(sa.Column("assignee_id", sa.Integer(), nullable=True))
        # kopiuj z assigned_to_id, jeśli istnieje
        if "assigned_to_id" in task_cols:
            try:
                conn.exec_driver_sql("UPDATE task SET assignee_id = assigned_to_id")
            except Exception:
                pass
        # usuń nowe kolumny
        if "created_by_id" in task_cols:
            b.drop_column("created_by_id")
        if "assigned_to_id" in task_cols:
            b.drop_column("assigned_to_id")

    # cofnięcie zmian w NOTE (przywrócenie user_id/tag, usunięcie created_by_id)
    note_cols = _pragma_columns(conn, "note")
    with op.batch_alter_table("note", recreate="always") as b:
        if "user_id" not in note_cols:
            b.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        if "created_by_id" in note_cols:
            # spróbuj przepisać z powrotem
            try:
                conn.exec_driver_sql("UPDATE note SET user_id = created_by_id")
            except Exception:
                pass
            b.drop_column("created_by_id")
        if "tag" not in note_cols:
            b.add_column(sa.Column("tag", sa.String(length=50), nullable=True))

    # cofnięcie zmian w USER (name/surname)
    user_cols = _pragma_columns(conn, "user")
    with op.batch_alter_table("user") as b:
        if "surname" in user_cols:
            b.drop_column("surname")
        if "name" in user_cols:
            b.drop_column("name")
