from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

db = SQLAlchemy()

class Users_Model(db.Model, UserMixin):
  __tablename__ = "Users"
  user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  username = db.Column(db.String, nullable=False, unique=True)
  password = db.Column(db.String, nullable=False)
  trackers = db.relationship("Trackers_Model", secondary="Enrollments")
  def get_id(self):
      return (self.user_id)

class Trackers_Model(db.Model):
  __tablename__ = "Trackers"
  tracker_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  tracker_name = db.Column(db.String, nullable=False, unique=True)
  tracker_type = db.Column(db.String, nullable=False)
  tracker_desc = db.Column(db.String)

class Enrollments_Model(db.Model):
    __tablename__ = "Enrollments"
    enroll_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"), primary_key=True, nullable=False)
    tracker_id = db.Column(db.Integer, db.ForeignKey("Trackers.tracker_id"), primary_key=True, nullable=False)

class Logs_Model(db.Model):
  __tablename__ = "Logs"
  log_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  value = db.Column(db.String, nullable=False)
  note = db.Column(db.String)
  timestamp = db.Column(db.String, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"), primary_key=True, nullable=False)
  tracker_id = db.Column(db.Integer, db.ForeignKey("Trackers.tracker_id"), primary_key=True, nullable=False)

class Selectable_Values_Model(db.Model):
  __tablename__ = "Selectable_Values"
  value_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  selectables = db.Column(db.String, nullable=False)
  tracker_id = db.Column(db.Integer, db.ForeignKey("Trackers.tracker_id"), primary_key=True, nullable=False)
