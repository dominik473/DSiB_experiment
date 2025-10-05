from flask import render_template, redirect, request, url_for, current_app, abort, flash
from flask_login import login_required, current_user
from . import bp
from app.extensions import db
from app.models.task import Task
from app.models.note import Note
from app.models.user import User

@bp.route("/dashboard")
@login_required
def dashboard():
    cfg = current_app.config
    total_tasks = Task.query.filter_by(assigned_to_id=current_user.id).count()
    open_tasks = Task.query.filter_by(assigned_to_id=current_user.id, done=False).count()
    recent_notes = Note.query.order_by(Note.updated_at.desc()).limit(5).all()
    upcoming = (Task.query
                .filter(Task.assigned_to_id == current_user.id, Task.done.is_(False), Task.due_at.isnot(None))
                .order_by(Task.due_at.asc()).limit(5).all())
    tasks = (Task.query
             .filter_by(assigned_to_id=current_user.id)
             .order_by(Task.done.asc(), Task.created_at.desc()).limit(10).all())
    return render_template("staff_panel/dashboard.html",
                           kpi={"tasks": total_tasks, "open": open_tasks, "notes": len(recent_notes)},
                           upcoming=upcoming, tasks=tasks, notes=recent_notes,
                           cal1=cfg.get("CALENDAR_ID_1"), cal2=cfg.get("CALENDAR_ID_2"),
                           cal3=cfg.get("CALENDAR_ID_3"), cal_edit=cfg.get("CALENDAR_ID_EDITABLE"))

@bp.route("/tasks")
@login_required
def tasks():
    tasks = (Task.query
             .filter_by(assigned_to_id=current_user.id)
             .order_by(Task.done.asc(), Task.created_at.desc()).all())
    return render_template("staff_panel/tasks.html", tasks=tasks)

@bp.post("/tasks/<int:task_id>/toggle")
@login_required
def toggle_task(task_id: int):
    t = Task.query.get_or_404(task_id)
    if t.assigned_to_id != current_user.id and current_user.role != "admin":
        return "Forbidden", 403
    t.done = not t.done
    db.session.commit()
    return redirect(request.referrer or url_for("staff.dashboard"))

@bp.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        assigned_to_id = request.form.get("assigned_to_id")
        if not text or not assigned_to_id:
            flash("Uzupełnij treść i wybierz adresata.", "warning")
            return redirect(url_for("staff.create_task"))
        t = Task(text=text, created_by_id=current_user.id, assigned_to_id=int(assigned_to_id))
        db.session.add(t); db.session.commit()
        flash("Zadanie utworzone.", "success")
        return redirect(url_for("staff.tasks"))
    users = User.query.order_by(User.name.asc().nullslast(), User.surname.asc().nullslast()).all()
    return render_template("staff_panel/task_form.html", users=users)

@bp.route("/notes")
@login_required
def notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template("staff_panel/notes.html", notes=notes)

@bp.route("/notes/<int:note_id>")
@login_required
def note_details(note_id: int):
    note = Note.query.get_or_404(note_id)
    return render_template("staff_panel/note_details.html", note=note, attachments=[])

@bp.route("/notes/create", methods=["GET", "POST"])
@login_required
def create_note():
    if current_user.role not in {"staff", "admin"}:
        abort(403)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not title or not body:
            flash("Uzupełnij tytuł i treść.", "warning")
            return redirect(url_for("staff.create_note"))
        n = Note(title=title, body=body, created_by_id=current_user.id)
        db.session.add(n); db.session.commit()
        flash("Notatka utworzona.", "success")
        return redirect(url_for("staff.notes"))
    return render_template("staff_panel/note_form.html")
