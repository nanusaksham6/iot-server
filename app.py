import os
import random
import time
import threading
from datetime import timedelta
from functools import wraps

from flask import Flask, jsonify, render_template, request, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Loads the .env file that sits next to this script.
# That file holds your secrets and is NEVER uploaded to GitHub.
load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------
# 1. SECRET KEY  -  read from .env, never written in the code
# ---------------------------------------------------------------
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise RuntimeError("SECRET_KEY missing. Create a .env file first.")

# ---------------------------------------------------------------
# 2. COOKIE / SESSION HARDENING
# ---------------------------------------------------------------
IS_PRODUCTION = os.environ.get('FLASK_ENV', 'development') == 'production'

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,        # JavaScript cannot read the cookie (blocks XSS theft)
    SESSION_COOKIE_SAMESITE='Lax',       # Blocks cross-site request forgery
    SESSION_COOKIE_SECURE=IS_PRODUCTION,  # HTTPS-only once deployed
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),  # Auto logout after 30 min
    MAX_CONTENT_LENGTH=16 * 1024,        # Rejects oversized request bodies
)

# ---------------------------------------------------------------
# 3. CREDENTIALS  -  password stored as a hash, not plain text
# ---------------------------------------------------------------
MASTER_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@vibratech.io')
_raw_password = os.environ.get('ADMIN_PASSWORD')
if not _raw_password:
    raise RuntimeError("ADMIN_PASSWORD missing. Create a .env file first.")
MASTER_PASSWORD_HASH = generate_password_hash(_raw_password)
del _raw_password  # Remove the plain password from memory

# ---------------------------------------------------------------
# 4. BRUTE-FORCE LOCKOUT
#    5 wrong attempts from one IP  ->  locked for 5 minutes
# ---------------------------------------------------------------
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300
_failed_attempts = {}          # { ip: [count, first_attempt_time] }
_attempts_lock = threading.Lock()


def is_locked_out(ip):
    with _attempts_lock:
        record = _failed_attempts.get(ip)
        if not record:
            return False
        count, first_time = record
        if time.time() - first_time > LOCKOUT_SECONDS:
            _failed_attempts.pop(ip, None)
            return False
        return count >= MAX_ATTEMPTS


def register_failure(ip):
    with _attempts_lock:
        count, first_time = _failed_attempts.get(ip, [0, time.time()])
        if time.time() - first_time > LOCKOUT_SECONDS:
            count, first_time = 0, time.time()
        _failed_attempts[ip] = [count + 1, first_time]


def clear_failures(ip):
    with _attempts_lock:
        _failed_attempts.pop(ip, None)


# ---------------------------------------------------------------
# 5. LOGIN DECORATOR  -  put @login_required on any protected route
# ---------------------------------------------------------------
def login_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if not session.get('user_logged_in'):
            abort(403)
        return view_function(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------
# 6. SECURITY HEADERS  -  added to every single response
# ---------------------------------------------------------------
@app.after_request
def apply_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'            # Blocks clickjacking
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "frame-ancestors 'none'"
    )
    if IS_PRODUCTION:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Cache-Control'] = 'no-store'
    return response


# ---------------------------------------------------------------
# TELEMETRY SIMULATION  (unchanged logic, thread-safe now)
# ---------------------------------------------------------------
_telemetry_lock = threading.Lock()
motor3_start_time = time.time()
motor1_temp = 38.5
motor2_temp = 46.2
motor3_temp = 37.0

VALID_ASSETS = ('motor_01', 'motor_02', 'motor_03')


def get_scada_telemetry(asset_name):
    global motor3_start_time, motor1_temp, motor2_temp, motor3_temp

    with _telemetry_lock:
        current_time_str = time.strftime("%H:%M:%S")

        if asset_name == "motor_01":
            motor1_temp = max(36.5, min(41.0, motor1_temp + random.uniform(-0.1, 0.1)))
            vibration_rms = round(random.uniform(1.1, 1.9), 2)
            rpm_velocity = random.randint(1440, 1460)
            status = "Normal"
            health = random.randint(94, 99)
            rul_hours = random.randint(520, 580)
            confidence = round(random.uniform(92.1, 95.8), 1)
            temperature = motor1_temp

        elif asset_name == "motor_02":
            motor2_temp = max(44.0, min(52.5, motor2_temp + random.uniform(-0.15, 0.2)))
            vibration_rms = round(random.uniform(4.8, 6.2), 2)
            rpm_velocity = random.randint(1320, 1380)
            status = "Critical"
            health = random.randint(32, 45)
            rul_hours = random.randint(12, 48)
            confidence = round(random.uniform(86.4, 89.9), 1)
            temperature = motor2_temp

        else:
            elapsed_seconds = time.time() - motor3_start_time
            if elapsed_seconds < 60:
                motor3_temp = max(36.0, min(39.5, motor3_temp + random.uniform(-0.1, 0.1)))
                vibration_rms = round(random.uniform(1.2, 1.8), 2)
                rpm_velocity = random.randint(1445, 1465)
                status = "Normal"
                health = random.randint(95, 98)
                rul_hours = random.randint(600, 650)
                confidence = round(random.uniform(94.0, 96.5), 1)
            else:
                motor3_temp = max(42.0, min(54.0, motor3_temp + random.uniform(0.05, 0.25)))
                vibration_rms = round(random.uniform(4.2, 5.9), 2)
                rpm_velocity = random.randint(1340, 1395)
                status = "Critical"
                health = random.randint(25, 48)
                rul_hours = random.randint(15, 75)
                confidence = round(random.uniform(88.2, 91.4), 1)
            temperature = motor3_temp

        fft_harmonics = [
            round(random.uniform(5, 45 if status == "Normal" else 180), 1)
            for _ in range(10)
        ]
        fft_harmonics[0] = 210.5 if status == "Normal" else 245.0
        base_freq = 5.0 if status == "Normal" else 12.4

        return {
            "timestamp": current_time_str,
            "temperature": round(temperature, 1),
            "rpm": rpm_velocity,
            "vibration": vibration_rms,
            "fft": fft_harmonics,
            "peak_freq": base_freq,
            "status": status,
            "health": health,
            "rul": rul_hours,
            "confidence": confidence
        }


# ---------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------
@app.route('/')
def home():
    if session.get('user_logged_in'):
        return render_template('index.html', user_email=session.get('user_email'))
    return render_template('index.html', show_login=True)


@app.route('/api/auth/login', methods=['POST'])
def process_login():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()

    if is_locked_out(client_ip):
        return jsonify({
            "status": "error",
            "message": "Too many failed attempts. Try again in 5 minutes."
        }), 429

    req_data = request.get_json(silent=True) or {}
    email = str(req_data.get('email', ''))[:120]
    password = str(req_data.get('password', ''))[:200]

    if email == MASTER_EMAIL and check_password_hash(MASTER_PASSWORD_HASH, password):
        session.clear()               # Stops session-fixation attacks
        session.permanent = True      # Enables the 30-minute timeout
        session['user_logged_in'] = True
        session['user_email'] = MASTER_EMAIL
        clear_failures(client_ip)
        return jsonify({"status": "success"})

    register_failure(client_ip)
    time.sleep(0.5)  # Slows down automated guessing
    # Same message for wrong email and wrong password, so attackers
    # cannot find out which email addresses are valid.
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.route('/api/auth/logout', methods=['POST'])
def system_logout_endpoint():
    session.clear()
    return jsonify({"status": "success"})


@app.route('/api/telemetry')
@login_required
def telemetry_stream():
    asset = request.args.get('asset', 'motor_01')
    if asset not in VALID_ASSETS:
        return jsonify({"error": "Bad request vector"}), 400
    return jsonify(get_scada_telemetry(asset))


# ---------------------------------------------------------------
# ERROR HANDLERS  -  never leak stack traces to the user
# ---------------------------------------------------------------
@app.errorhandler(403)
def forbidden(_):
    return jsonify({"error": "Forbidden"}), 403


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(_):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # debug is ON only on your laptop, never in production
    app.run(host='127.0.0.1', port=5000, debug=not IS_PRODUCTION)
