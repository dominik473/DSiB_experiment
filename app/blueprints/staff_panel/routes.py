from flask import render_template, redirect, request, url_for, current_app
from flask_login import login_required, current_user
from . import bp
from app.models.task import Task
from app.models.note import Note

@bp.route("/dashboard")
@login_required
def dashboard():

    # Google calender
    cfg = current_app.config

    # KPI
    total_tasks = Task.query.filter_by(assignee_id=current_user.id).count()
    open_tasks = Task.query.filter_by(assignee_id=current_user.id, done=False).count()
    recent_notes = Note.query.order_by(Note.updated_at.desc()).limit(5).all()

    # Nadchodzące (najbliższe 5 zadań z terminem)
    upcoming = (Task.query
                .filter(Task.assignee_id == current_user.id, Task.done.is_(False), Task.due_at.isnot(None))
                .order_by(Task.due_at.asc())
                .limit(5).all())

    # Lista zadań (ostatnie 10)
    tasks = (Task.query
             .filter_by(assignee_id=current_user.id)
             .order_by(Task.done.asc(), Task.created_at.desc())
             .limit(10).all())

    return render_template("staff_panel/dashboard.html",
                           kpi={"tasks": total_tasks, "open": open_tasks, "notes": len(recent_notes)},
                           upcoming=upcoming,
                           tasks=tasks,
                           notes=recent_notes,
                           cal1=cfg["CALENDAR_ID_1"],
                           cal2=cfg["CALENDAR_ID_2"],
                           cal3=cfg["CALENDAR_ID_3"],
                           cal_edit=cfg["CALENDAR_ID_EDITABLE"])

@bp.post("/tasks/<int:task_id>/toggle")
@login_required
def toggle_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.assignee_id != current_user.id and current_user.role != "admin":
        return "Forbidden", 403
    t.done = not t.done
    from app.extensions import db
    db.session.commit()
    # wracamy do strony, z której przyszliśmy (dashboard lub /tasks)
    return redirect(request.referrer or url_for("staff.dashboard"))


@bp.route("/notes")
@login_required
def notes():
    notes = [
        {"id": 1, "title": "Spotkanie z klientem A", "body": "Ustalić zakres badań i terminy dostaw próbek.", "tag": "Klienci"},
        {"id": 2, "title": "Protokół #128 korekta", "body": "Sprawdzić wartości graniczne – błąd w wierszu 23.", "tag": "Protokoły"},
        {"id": 3, "title": "Faktury wrzesień", "body": "Wysłać faktury do InżPol i MaxBud.", "tag": "Finanse"},
    ]
    return render_template("staff_panel/notes.html", notes=notes)

@bp.route("/notes/<int:note_id>")
@login_required
def note_details(note_id: int):
    # Na razie mock (później: pobierz z DB)
    note = {
        "id": note_id,
        "title": "Spotkanie z klientem A",
        "body": "Ustalić zakres badań:\n• rodzaj próbek: beton C30/37\n• terminy dostaw: pon/śr\n• dokumenty: protokół Vss, LPD\n\nDodatkowo: przygotować ofertę.",
        "tag": "Klienci",
        "createdAt": "2025-09-06 10:30",
        "updatedAt": "2025-09-06 13:05",
    }
    attachments = ["protokol_vss.pdf", "zdjecie_1.jpg", "oferta.docx"]
    return render_template("staff_panel/note_details.html", note=note, attachments=attachments)

@bp.route("/tasks")
@login_required
def tasks():
    tasks = [
        {"id": 1, "text": "Oddzwonić do klienta A w sprawie terminów", "done": False},
        {"id": 2, "text": "Dodać protokół Vss z budowy X", "done": False},
        {"id": 3, "text": "Zlecić badanie ściskania próbkom #21-#30", "done": True},
        {"id": 4, "text": "Wystawić fakturę dla InżPol (wrzesień)", "done": False},
        {"id": 5, "text": "Ustalić wizytę w laboratorium – wt 10:00", "done": False},
    ]
    return render_template("staff_panel/tasks.html", tasks=tasks)
