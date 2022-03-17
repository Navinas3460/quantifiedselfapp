from app import *

def valid_name(name):
    if name.isalnum():
        return True
    else:
        return False

tracker_types = ['Numerical', 'Multiple Choice', 'Boolean', 'Time Duration']

@app.route("/trackers")
@login_required
def trackers_dashboard():
    trackers = Trackers_Model.query.all()
    return render_template("tracker_dashboard.html", trackers=trackers, username=current_user.username)

@app.route("/trackers/<int:tracker_id>/edit", methods=['GET', 'POST'])
def tracker_edit(tracker_id):
    if request.method == 'GET':
        tracker = Trackers_Model.query.filter_by(tracker_id=tracker_id).one()
        selectable_values = None
        if tracker.tracker_type == "Multiple Choice":
            try:
                selectable_values = Selectable_Values_Model.query.filter_by(tracker_id=tracker_id).one()
            except:
                pass
        return render_template("tracker_edit.html", tracker=tracker, selectable_values = selectable_values, username=current_user.username)
    elif request.method == 'POST':
        new_name = request.form['trackerName']
        new_desc = request.form['trackerDesc']
        tracker = Trackers_Model.query.filter_by(tracker_id=tracker_id).one()
        if valid_name(new_name):
            tracker.tracker_name = new_name
            tracker.tracker_desc = new_desc
            try:
                db.session.commit()
                return redirect("/trackers")
            except:
                db.session.rollback()
                error = "<h1>Could not edit tracker. SERVER ERROR </h1>"
                raise ServerError(500, "TRACKER001", error)
        else:
            error = "Invalid Name"
            raise InputError(400, "TRACKER002", html_page="tracker_edit.html", error_message=error, tracker=tracker, username=current_user.username)

@app.route("/trackers/<int:tracker_id>/delete")
def tracker_del(tracker_id):
    try:
        tracker = Trackers_Model.query.filter_by(tracker_id=tracker_id).one()
        enrolls = Enrollments_Model.query.filter_by(tracker_id=tracker_id).all()
        for e in enrolls:
            db.session.delete(e)
        db.session.delete(tracker)
        db.session.commit()
        return redirect("/trackers")
    except:
        db.session.rollback()
        error = "<h1>Something wrong happened. Server Error</h1>"
        raise ServerError(500, "TRACKER003", error_message=error)
    
@app.route("/trackers/create", methods=['GET', 'POST'])
def tracker_create():
    global tracker_types
    if request.method=="GET":
        return render_template("tracker_create.html", username=current_user.username)
    elif request.method=='POST':
        new_tracker_name = request.form.get("trackerName")
        if not valid_name(new_tracker_name):
            error="Invalid name"
            raise InputError(400, "TRACKER004", html_page="tracker_create.html", error_message=error, username=current_user.username)
        new_tracker_type = request.form.get("trackerType")
        if new_tracker_type not in tracker_types:
            error = 'Tracker Not Valid'
            raise InputError(400, "TRACKER005", error, html_page="tracker_create.html", username=current_user.username)
        
        new_tracerk_desc = request.form.get("trackerDesc")

        new_tracker = Trackers_Model(tracker_name=new_tracker_name, tracker_type=new_tracker_type, tracker_desc=new_tracerk_desc)
        try:
            db.session.add(new_tracker)
            db.session.commit()
            tracker = Trackers_Model.query.filter_by(tracker_name = new_tracker_name).one()
            if new_tracker_type == "Multiple Choice":
                return redirect(f"/trackers/create/{tracker.tracker_id}/selectables")
            return redirect("/trackers")
        except:
            db.session.rollback()
            error = "Invalid Inputs"
            raise InputError(400, "TRACKER006", error, "tracker_create.html", username=current_user.username)

@app.route("/trackers/create/<int:tracker_id>/selectables", methods=['GET', 'POST'])
def tracker_selectables(tracker_id):
    if request.method == 'GET':
        tracker = Trackers_Model.query.filter_by(tracker_id = tracker_id).one()
        return render_template("tracker_selectables.html", tracker=tracker)
    elif request.method == 'POST':
        selectables = request.form.get("trackerChoices")
        selectable_values = Selectable_Values_Model(tracker_id=tracker_id,selectables=selectables)
        try:
            logs = Logs_Model.query.filter_by(tracker_id=tracker_id).all()
            selectables = Selectable_Values_Model.query.filter_by(tracker_id=tracker_id).one()
            for l in logs:
                db.session.delete(l)
            db.session.delete(selectables)
            db.session.commit()
        except:
            db.session.rollback()
            pass
        try:
            db.session.add(selectable_values)
            db.session.commit()
            return redirect("/trackers")
        except:
            db.session.rollback()
            raise ServerError(500, "TRACKER007", "<h1>Server Error</h1>")