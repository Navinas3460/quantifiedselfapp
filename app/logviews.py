from app import *

tracker_types = {'Numerical': float, 'Multiple Choice': str, 'Boolean': str, 'Time Duration': float}
allowed_bools = {'true':'True', 'false':'False', '0':'False', '1':'True'}

@app.route("/user/<username>/logs")
@login_required
def user_logs(username):
    user = Users_Model.query.filter_by(username=username).first()
    logs = Logs_Model.query.filter_by(user_id=user.user_id).all()
    condition = False
    if logs:
        condition = True
    tracker = Trackers_Model()
    return render_template("user_logs.html", user=user, logs=logs, tracker=tracker, username=username, condition=condition)

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
            return render_template("user_log_add.html", username=current_user.username, tracker=tracker, now=now, condition=False, choices=choices)
        return render_template("user_log_add.html", username=current_user.username, tracker=tracker, now=now, condition=True)
    elif request.method=='POST':
        now = datetime.now()
        now = now.strftime("%d/%m/%Y %I:%M %p")
        value = request.form.get('value')
        tracker = Trackers_Model.query.filter_by(tracker_id=tracker_id).first()
        if tracker.tracker_type == "Boolean":
            if value.lower() in allowed_bools:
                value = allowed_bools[value.lower()]
            else:
                error = "Boolean value is not allowed. Try 'true or false' or '1 or 0'"
                raise InputError(400, "LOG002", error, "user_log_add.html", tracker=tracker, username=current_user.username, condition=True, now=now)
        elif tracker.tracker_type == "Numerical" or tracker.tracker_type == "Time Duration":
            value = float(value)
        if type(value) != tracker_types[tracker.tracker_type]:
            error = "Your value doesn't match the tracker type"
            if tracker.tracker_type == "Multiple Choice":
                s = Selectable_Values_Model.query.filter_by(tracker_id=tracker_id).first()
                choices = s.selectables.split(",")
                raise InputError(400, "LOG001", error, "user_log_add.html", username=current_user.username, tracker=tracker, now=now, condition=False, choices=choices)
            raise InputError(400, "LOG002", error, "user_log_add.html", tracker=tracker, username=current_user.username, condition=True, now=now)
        note = request.form.get('note')
        timestamp = request.form.get('datetime')
        log = Logs_Model(value=value, note=note, timestamp=timestamp, tracker_id=tracker_id, user_id=current_user.user_id)
        try:
            db.session.add(log)
            db.session.commit()
            return redirect(f"/user/{username}/logs")
        except:
            db.session.rollback()
            raise ServerError(500, "LOG003", "<h1>SERVER ERROR</h1>")

@app.route("/user/<username>/logs/<int:log_id>/edit", methods=['GET', 'POST'])
@login_required
def user_log_edit(username, log_id):
    if request.method == 'GET':
        log = Logs_Model.query.filter_by(log_id=log_id).one()
        tracker = Trackers_Model.query.filter_by(tracker_id=log.tracker_id).first()
        if tracker.tracker_type == "Multiple Choice":
            s = Selectable_Values_Model.query.filter_by(tracker_id=log.tracker_id).first()
            choices = s.selectables.split(",")
            return render_template("user_log_edit.html", condition=False, username=current_user.username, tracker=tracker, choices=choices, log=log)
        return render_template("user_log_edit.html",condition=True, username=current_user.username, tracker=tracker, log=log)
    elif request.method == 'POST':
        log = Logs_Model.query.filter_by(log_id=log_id).one()
        value = request.form.get("logvalue")
        when = request.form.get("datetime")
        note = request.form.get("note")

        tracker = Trackers_Model.query.filter_by(tracker_id=log.tracker_id).first()
        if tracker.tracker_type == "Boolean":
            if value.lower() in allowed_bools:
                value = allowed_bools[value.lower()]
            else:
                error = "Boolean value is not allowed. Try 'true or false' or '1 or 0'"
                raise InputError(400, "LOG005", error, "user_log_edit.html", username=current_user.username, tracker=tracker, condition=True, log=log)
        if type(value) != tracker_types[tracker.tracker_type]:
            error = "Your value doesn't match the tracker type"
            if tracker.tracker_type == "Multiple Choice":
                s = Selectable_Values_Model.query.filter_by(tracker_id=log.tracker_id).first()
                choices = s.selectables.split(",")
                raise InputError(400, "LOG004", error, "user_log_edit.html", username=current_user.username, tracker=tracker, condition=False, choices=choices, log=log)
            raise InputError(400, "LOG005", error, "user_log_edit.html", username=current_user.username, tracker=tracker, condition=True, log=log)
        log.value = value
        log.timestamp = when
        log.note = note
        try:
            db.session.commit()
            return redirect(f"/user/{username}/logs")
        except:
            db.session.rollback()
            raise ServerError(500, "LOG006", "<h1>SERVER ERROR</h1>")

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
        raise ServerError(500, "LOG007", "<h1>SERVER ERROR</h1>")
    