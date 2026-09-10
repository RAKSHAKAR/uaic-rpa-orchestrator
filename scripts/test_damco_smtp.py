"""Test SMTP connectivity and authentication with Office 365 for priyer@test.com."""
import smtplib
import ssl
import time

HOST = "smtp.office365.com"
PORT = 587
USER = "priyer@test.com"
PASSWORDS = ["Welcome@8876", "World@8876"]

print(f"Connecting to {HOST}:{PORT}...")
t0 = time.time()
try:
    server = smtplib.SMTP(HOST, PORT, timeout=15)
    server.ehlo()
    print("EHLO 1 successful. Starting TLS...")
    context = ssl.create_default_context()
    server.starttls(context=context)
    server.ehlo()
    print(f"TLS established in {(time.time() - t0)*1000:.1f}ms.")
    
    auth_success = False
    working_password = None
    for pwd in PASSWORDS:
        print(f"\nAttempting LOGIN with password: {pwd[:3]}*** ...")
        try:
            code, resp = server.login(USER, pwd)
            print(f"SUCCESS: Login accepted! Code: {code}, Response: {resp.decode('utf-8', errors='ignore')}")
            auth_success = True
            working_password = pwd
            break
        except smtplib.SMTPAuthenticationError as e:
            print(f"AUTH FAILED: {e.smtp_code} - {e.smtp_error.decode('utf-8', errors='ignore') if isinstance(e.smtp_error, bytes) else e.smtp_error}")
        except Exception as e:
            print(f"Error during login: {e}")
            
    if auth_success:
        print(f"\nVerified working credentials for {USER}!")
    else:
        print("\nNeither password succeeded for direct SMTP AUTH.")
    
    server.quit()
except Exception as e:
    print(f"Connection failed: {e}")
