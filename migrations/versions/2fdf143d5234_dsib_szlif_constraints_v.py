"""dsib_szlif_constraints_v

Revision ID: 2fdf143d5234
Revises: fc50f98e7bc0
Create Date: 2025-10-13 11:57:19.752662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fdf143d5234'
down_revision = 'fc50f98e7bc0'
branch_labels = None
depends_on = None

def upgrade():
    # Klienci: unikalność skrótu
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_klienci_nazwa_skrocona ON klienci(nazwa_skrocona)")
    # Jeśli chcesz szeroką sygnaturę i jej jeszcze nie masz:
    # op.execute(\"CREATE UNIQUE INDEX IF NOT EXISTS uq_klienci_firma_adres_kod_miejsc_nip ON klienci(nazwa_firmy, adres, kod_pocztowy, miejscowosc, nip)\")

    # Użytkownicy (klienccy): prosty CHECK na niepusty email
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_uzyt_email ON uzytkownicy(email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_uzyt_aktywny ON uzytkownicy(aktywny)")
    op.execute("DROP INDEX IF EXISTS ck_uzyt_email_not_empty")  # zapobiega duplikatom

    # Telefony (osoby_kontaktowe)

    op.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_tel_len_ins
        BEFORE INSERT ON telefony
        WHEN length(NEW.nr_telefonu) < 5
        BEGIN
          SELECT RAISE(ABORT, 'nr_telefonu too short');
        END;""")
    op.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_tel_len_upd
        BEFORE UPDATE OF nr_telefonu ON telefony
        WHEN length(NEW.nr_telefonu) < 5
        BEGIN
          SELECT RAISE(ABORT, 'nr_telefonu too short');
        END;""")

    # Telefony użytkownika
    op.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_tu_len_ins
        BEFORE INSERT ON telefony_uzytkownika
        WHEN length(NEW.nr_telefonu) < 5
        BEGIN
          SELECT RAISE(ABORT, 'nr_telefonu too short');
        END;""")
    op.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_tu_len_upd
        BEFORE UPDATE OF nr_telefonu ON telefony_uzytkownika
        WHEN length(NEW.nr_telefonu) < 5
        BEGIN
          SELECT RAISE(ABORT, 'nr_telefonu too short');
        END;""")

    # Beton_probka: nieujemne wartości
    with op.batch_alter_table("beton_probka", recreate="always") as b:
        b.create_check_constraint(
            "ck_probka_nonneg",
            "COALESCE(ilosc_kostek_10,0) >= 0 AND COALESCE(ilosc_kostek_15,0) >= 0 AND COALESCE(suma_kostek,0) >= 0"
        )

    # Zlecone_dodatkowe_sciskania: dni i ilość > 0
    with op.batch_alter_table("zlecone_dodatkowe_sciskania", recreate="always") as b:
        b.create_check_constraint("ck_zds_days_pos", "zlecone_po_ilu_dniach > 0")
        b.create_check_constraint("ck_zds_count_pos", "COALESCE(zlecone_ile_kostek,1) > 0")

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_tu_len_upd;")
    op.execute("DROP TRIGGER IF EXISTS trg_tu_len_ins;")
    op.execute("DROP TRIGGER IF EXISTS trg_tel_len_upd;")
    op.execute("DROP TRIGGER IF EXISTS trg_tel_len_ins;")
