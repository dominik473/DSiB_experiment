# app/models/core.py
from sqlalchemy import UniqueConstraint
from app.extensions import db  # <-- wspólny singleton z extensions.py


class Klient(db.Model):
    __tablename__ = "klienci"

    id_klienta = db.Column(db.Integer, primary_key=True)
    nazwa_skrocona = db.Column(db.String(128), nullable=False, unique=True)

    nazwa_firmy  = db.Column(db.String(255))
    adres        = db.Column(db.String(255))
    kod_pocztowy = db.Column(db.String(16))
    miejscowosc  = db.Column(db.String(128))
    nip          = db.Column(db.String(32))

    __table_args__ = (
        UniqueConstraint(
            "nazwa_firmy", "adres", "kod_pocztowy", "miejscowosc", "nip",
            name="uq_klienci_firma_adres_kod_miejsc_nip",
        ),
    )


class Inwestycja(db.Model):
    __tablename__ = "inwestycje"

    id_inwestycji = db.Column(db.Integer, primary_key=True)

    # unikat – index powstaje dzięki UNIQUE
    nr_inwestycji = db.Column(db.String(32), unique=True, nullable=True)

    # FK + indeks pod wyszukiwanie po kliencie
    id_klienta = db.Column(
        db.Integer,
        db.ForeignKey("klienci.id_klienta"),
        nullable=True,
        index=True,
    )

    pelna_nazwa_inwestycji = db.Column(db.String(255), nullable=False)
    status_crm = db.Column(db.String(32))

    __table_args__ = (
        UniqueConstraint(
            "id_klienta", "pelna_nazwa_inwestycji",
            name="uq_inwestycje_klient_pelna_nazwa",
        ),
    )

    klient = db.relationship("Klient", backref="inwestycje")
