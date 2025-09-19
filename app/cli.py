# app/cli.py
import click
from app.extensions import db
from app.models.user import User

def register_cli(app):
    @app.cli.command("create-user")
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--role", default="admin")
    def create_user(email, password, role):
        """Utwórz użytkownika w bazie."""
        with app.app_context():
            u = User(email=email.lower(), role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            click.echo(f"Utworzono użytkownika: {email} ({role})")
