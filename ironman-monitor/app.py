import os
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, MonitoredFile
from checker import check_file
from notifier import send_notification

def create_app():
    app = Flask(__name__)
    database_url = os.environ.get("DATABASE_URL", "sqlite:///monitor.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        if not MonitoredFile.query.first():
            db.session.add_all([
                MonitoredFile(name="Pro Calendar", url="https://www.ironman.com/community/pro-athletes"),
                MonitoredFile(name="Start List", url="https://www.ironman.com/community/pro-athletes")
            ])
            db.session.commit()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: run_checks(app), trigger="interval", hours=6)
    scheduler.start()

    @app.route("/")
    def index():
        files = MonitoredFile.query.all()
        return render_template("index.html", files=files)

    return app

def run_checks(app):
    with app.app_context():
        files = MonitoredFile.query.all()
        for f in files:
            changed = check_file(f)
            if changed:
                print(f"🔔 Change detected in {f.name}")
                send_notification(f.name)

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)