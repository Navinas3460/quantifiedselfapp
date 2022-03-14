
from app import *
import numpy as np
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure



def valid_username(username):
    if username.isalnum():
        return True
    else:
        return False

@login_manager.user_loader
def load_user(user_id):
    return Users_Model.query.get(user_id)

@app.route('/', methods = ['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template("index.html")
    elif request.method == 'POST':
        username = request.form.get("inputUsername")
        if valid_username(username):
            user = Users_Model.query.filter_by(username=username).first()
            if user:
                if bcrypt.check_password_hash(user.password, request.form.get('inputPassword')):
                    login_user(user)
                    return redirect(f"/user/{user.username}/home")
                else:
                    error = "Your Password Is Wrong"
                    return render_template("index.html", error=error)
            else:
                error = "Username Not Found"
                return render_template("index.html", error=error)
        else:
            error = "Invalid Username. It must be alpha-numerical"
            return render_template("index.html", error=error)

@app.route("/user/create", methods=['GET', 'POST'])
def user_create():
    if request.method == 'GET':
        tra = Trackers_Model.query.all()
        return render_template("user_create.html", trackers=tra)
    else:
        tra = Trackers_Model.query.all()
        username = request.form.get("createUsername")
        hashedPassword = bcrypt.generate_password_hash(request.form.get("createPassword"))
        tracker_list = request.form.getlist("trackers")
        if username and valid_username(username):
            user = Users_Model(username=username, password=hashedPassword)
            for t in tracker_list:
                tracker = Trackers_Model.query.filter_by(tracker_id = t).one()
                user.trackers.append(tracker)
            try:
                db.session.add(user)
                db.session.commit()
                flash("account created")
                return redirect("/")
            except:
                db.session.rollback()
                error = "Username invalid or already exists. Username must be alpha-numerical"
                return(render_template("user_create.html", error=error, trackers=tra))
        else:
            error = "Username invalid or empty. Username must be alpha-numerical"
            return(render_template("user_create.html", error = error, trackers=tra))

@app.route("/user/logout")
@login_required
def user_logout():
    logout_user()
    return redirect("/")

@app.route("/user/<username>/home")
@login_required
def user_home(username):
    user_id = current_user.user_id
    enrolls = Enrollments_Model.query.filter_by(user_id=user_id).all()
    trackers = []
    logs = {}
    for e in enrolls:
        log = Logs_Model.query.filter_by(user_id=user_id, tracker_id=e.tracker_id).order_by(Logs_Model.log_id.desc()).first()
        tracker = Trackers_Model.query.filter_by(tracker_id=e.tracker_id).one()
        trackers.append(tracker)
        if log:
            logs[e.tracker_id] = log.timestamp,log.value
        else:
            logs[e.tracker_id] = None
        
    condition = False
    if trackers:
        condition = True
    tracker = Trackers_Model()
    loge = Logs_Model.query.filter_by(user_id=user_id).order_by(Logs_Model.log_id.desc()).all()
    i = 1
    log = []
    while i <= 3:
        log.append(loge[i])
        i += 1
    
    return render_template("user_home.html", username=username, trackers=trackers, condition=condition, logs=logs, tracker=tracker, log=log )



@app.route("/user/<username>/trackers")
@login_required
def user_trackers(username):
    user = Users_Model.query.filter_by(username=username).one()
    user_id = user.user_id
    enrolls = Enrollments_Model.query.filter_by(user_id=user_id).all()
    trackers = []
    for e in enrolls:
        tracker = Trackers_Model.query.filter_by(tracker_id=e.tracker_id).one()
        trackers.append(tracker)
    all_trackers = Trackers_Model.query.all()
    condition1 = False
    if trackers:
        condition1 = True
    available_trackers = []
    for t in all_trackers:
        if t not in trackers:
            available_trackers.append(t)
    condition2 = False
    if available_trackers:
        condition2 = True
    return render_template("user_trackers.html", username=username, trackers=trackers, condition1=condition1, condition2=condition2, available_trackers=available_trackers)

@app.route("/user/<username>/tracker/<int:tracker_id>/delete")
@login_required
def user_tracker_del(username, tracker_id):
    user = Users_Model.query.filter_by(username=username).one()
    user_id = user.user_id
    enrolls = Enrollments_Model.query.filter_by(user_id=user_id, tracker_id=tracker_id).all()
    try:
        for e in enrolls:
            db.session.delete(e)
        db.session.commit()
        return redirect(f"/user/{username}/trackers")
    except:
        db.session.rollback()
        raise

@app.route("/user/<username>/tracker/<int:tracker_id>")
@login_required
def user_tracker_info(username, tracker_id):
    tracker = Trackers_Model.query.filter_by(tracker_id=tracker_id).first()
    condition = False
    if tracker.tracker_type == "Numerical":
        condition = True

    return render_template("user_tracker_info.html", username=username, tracker=tracker, condition=condition)

@app.route("/plot_png/<int:tracker_id>")
@login_required
def plot_png(tracker_id):
    logs = Logs_Model.query.filter_by(tracker_id=tracker_id, user_id=current_user.user_id).all()
    timestamps = []
    values = []
    for log in logs:
        timestamps.append(log.timestamp)
        values.append(log.value)
    timestamps = np.array(timestamps)
    values = np.array(values)
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(timestamps, values)
    

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route("/user/<username>/tracker/<int:tracker_id>/add")
@login_required
def user_tracker_add(username, tracker_id):
    user = Users_Model.query.filter_by(username=username).one()
    user_id = user.user_id
    new_enroll = Enrollments_Model(user_id=user_id, tracker_id=tracker_id)
    try:
        db.session.add(new_enroll)
        db.session.commit()
        return redirect(f"/user/{username}/trackers")
    except:
        db.session.rollback()
        raise