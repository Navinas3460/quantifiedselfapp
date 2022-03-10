from app import *

@app.route("/user/<username>/logs")
@login_required
def user_logs(username):
    user = Users_Model.query.filter_by(username=username).one()
    logs = Logs_Model.query.filter_by(user_id=user.user_id).order_by(Logs_Model.tracker_id).all()
    tracker = Trackers_Model()
    return render_template("user_logs.html", user=user, logs=logs, tracker=tracker, username=username)

@app.route("/user/<username>/logs/<int:tracker_id>/add", methods=['GET', 'POST'])
@login_required
def user_log_add(username, tracker_id):
    if request.method=='GET':
        now = datetime.now()
        now = now.strftime("%d/%m/%Y %I:%M %p")
        tracker = Trackers_Model.query.filter_by(tracker_id=tracker_id).first()
        if tracker.tracker_type == "Multiple Choice":
            s = Selectable_Values_Model.query.filter_by(tracker_id=tracker_id).first()
            choices = s.selectables.split(",")
            return render_template("user_log_add.html", username=username, tracker=tracker, now=now, condition=False, choices=choices)
        return render_template("user_log_add.html", username=username, tracker=tracker, now=now, condition=True)
    elif request.method=='POST':
        value = request.form.get('value')
        note = request.form.get('note')
        timestamp = request.form.get('datetime')
        log = Logs_Model(value=value, note=note, timestamp=timestamp, tracker_id=tracker_id, user_id=current_user.user_id)
        try:
            db.session.add(log)
            db.session.commit()
            return redirect(f"/user/{username}/logs")
        except:
            db.session.rollback()
            return 'Error'

@app.route("/user/<username>/logs/<int:log_id>/edit", methods=['GET', 'POST'])
@login_required
def user_log_edit(username, log_id):
    if request.method == 'GET':
        log = Logs_Model.query.filter_by(log_id=log_id).one()
        tracker = Trackers_Model.query.filter_by(tracker_id=log.tracker_id).first()
        if tracker.tracker_type == "Multiple Choice":
            s = Selectable_Values_Model.query.filter_by(tracker_id=log.tracker_id).first()
            choices = s.selectables.split(",")
            return render_template("user_log_edit.html", condition=False, username=username, tracker=tracker, choices=choices, log=log)
        return render_template("user_log_edit.html",condition=True, username=username, tracker=tracker, log=log)
    elif request.method == 'POST':
        log = Logs_Model.query.filter_by(log_id=log_id).one()
        value = request.form.get("logvalue")
        when = request.form.get("datetime")
        note = request.form.get("note")
        log.value = value
        log.timestamp = when
        log.note = note
        try:
            db.session.commit()
            return redirect(f"/user/{username}/logs")
        except:
            db.session.rollback()
            return "ERROR"

@app.route("/user/<username>/logs/<int:log_id>/delete")
@login_required
def user_log_del(username, log_id):
    log = Logs_Model.query.filter_by(log_id=log_id).first()
    try:
        db.session.delete(log)
        db.session.commit()
        return redirect(f"/user/{username}/logs")
    except:
        db.session.rollback()
        raise
    