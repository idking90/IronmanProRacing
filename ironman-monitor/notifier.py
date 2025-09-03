import smtplib, os
from email.mime.text import MIMEText

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
ALERT_EMAIL = os.environ.get("ALERT_EMAIL")

def send_notification(file_name):
    if not (SMTP_USER and SMTP_PASS and ALERT_EMAIL):
        print("⚠️ Missing email environment variables in Render!")
        return

    msg = MIMEText(f"The monitored file '{file_name}' has changed.")
    msg["Subject"] = f"[Ironman Monitor] {file_name} updated"
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"✅ Notification sent to {ALERT_EMAIL}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")