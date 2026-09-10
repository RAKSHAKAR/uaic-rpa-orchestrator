"""Test direct MX SMTP transmission to damcogroup-com.mail.protection.outlook.com:25."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

MX_HOST = "damcogroup-com.mail.protection.outlook.com"
PORT = 25
RECIPIENT = "priyer@test.com"
SENDER = "notifications@test.com"

print(f"Connecting to MX server {MX_HOST}:{PORT}...")
t0 = time.time()
try:
    server = smtplib.SMTP(MX_HOST, PORT, timeout=15)
    server.set_debuglevel(1)
    server.ehlo()
    print("STARTTLS...")
    server.starttls()
    server.ehlo()
    print(f"Connected and TLS ready in {(time.time() - t0)*1000:.1f}ms")
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "UAIC Orchestrator — Test Notification & Delivery Receipt"
    msg["From"] = f"UAIC Claim Alerts <{SENDER}>"
    msg["To"] = RECIPIENT
    msg["Disposition-Notification-To"] = SENDER
    msg["Return-Receipt-To"] = SENDER
    msg["X-Confirm-Reading-To"] = SENDER
    
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 24px;">
            <h2 style="color: #059669; margin-top: 0;">UAIC Orchestrator — Delivery Receipt Test</h2>
            <p>Hello,</p>
            <p>This is a live verified test notification from the UAIC Claim &amp; RPA Orchestrator notification engine.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background: #f1f5f9;"><td style="padding: 8px; font-weight: bold;">Recipient</td><td style="padding: 8px;">priyer@test.com</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Delivery Channel</td><td style="padding: 8px;">Direct MX (TLS Encrypted)</td></tr>
                <tr style="background: #f1f5f9;"><td style="padding: 8px; font-weight: bold;">Delivery Receipt</td><td style="padding: 8px;">Requested (Return-Receipt-To, Disposition-Notification-To)</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Status</td><td style="padding: 8px; color: #059669; font-weight: bold;">DELIVERED TO GATEWAY</td></tr>
            </table>
            <p style="color: #64748b; font-size: 12px; margin-top: 24px;">UAIC Insurance Group — Automated RPA &amp; Guidewire Cloud Orchestration</p>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText("This is a live test notification from the UAIC Orchestrator.", "plain"))
    msg.attach(MIMEText(html, "html"))
    
    print(f"Sending message to {RECIPIENT}...")
    resp = server.sendmail(SENDER, [RECIPIENT], msg.as_string())
    print("SUCCESS: sendmail response:", resp)
    server.quit()
    print("Direct MX delivery test PASSED!")
except Exception as e:
    print(f"FAILED direct MX delivery: {e}")
