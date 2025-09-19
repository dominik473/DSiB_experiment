import click
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

@app.cli.command("create-user")
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--role", default="admin")
def create_user(email, password, role):
    u = User(email=email.lower(), role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    click.echo(f"Utworzono użytkownika: {email} ({role})")

@app.cli.command("seed-demo")
def seed_demo():
    from app.extensions import db
    from app.models.user import User
    from app.models.task import Task
    from app.models.note import Note
    from datetime import datetime, timedelta

    u = User.query.filter_by(email="admin@example.com").first()
    if not u:
        u = User(email="admin@example.com", role="admin"); u.set_password("admin123")
        db.session.add(u); db.session.commit()

    # Tasks
    if Task.query.count() == 0:
        db.session.add_all([
            Task(assignee_id=u.id, text="Oddzwonić do klienta A", due_at=datetime.utcnow()+timedelta(days=1)),
            Task(assignee_id=u.id, text="Przygotować protokół #128", due_at=datetime.utcnow()+timedelta(days=2)),
            Task(assignee_id=u.id, text="Zamówić odczynniki", done=True),
        ])

    # Notes
    if Note.query.count() == 0:
        db.session.add_all([
            Note(user_id=u.id, title="Spotkanie z klientem A", body="Ustalić zakres badań i terminy.", tag="Klienci"),
            Note(user_id=u.id, title="Faktury wrzesień", body="Wysłać faktury do InżPol i MaxBud.", tag="Finanse"),
            Note(user_id=u.id, title="Protokół #128 korekta", body="Sprawdzić wartości graniczne.", tag="Protokoły"),
        ])

    db.session.commit()
    print("Seed OK.")




if __name__ == "__main__":
    app.run()
