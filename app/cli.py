# app/cli.py
import click
from app.extensions import db
from app.models.user import User, validate_staff_identity

def register_cli(app):
    @app.cli.command("create-user")
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--role", default="admin", type=click.Choice(["client", "staff", "admin"], case_sensitive=False))
    @click.option("--name", default="", help="Imię (wymagane dla staff/admin)")
    @click.option("--surname", default="", help="Nazwisko (wymagane dla staff/admin)")
    def create_user(email, password, role, name, surname):
        """Utwórz użytkownika w bazie."""
        with app.app_context():
            u = User(email=email.lower(), role=role.lower().strip())
            # uzupełnij imię/nazwisko, jeśli podano
            if name:
                u.name = name.strip()
            if surname:
                u.surname = surname.strip()

            u.set_password(password)

            # walidacja polityki: staff/admin muszą mieć name+surname
            validate_staff_identity(u)

            db.session.add(u)
            db.session.commit()
            click.echo(f"Utworzono użytkownika: {u.email} ({u.role})"
                       + (f" [{u.name} {u.surname}]" if (u.name or u.surname) else ""))
