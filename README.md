# IoT SCADA Telemetry Server

A real-time predictive maintenance dashboard for industrial motors. Streams live sensor telemetry, detects fault signatures through FFT vibration analysis, and predicts Remaining Useful Life (RUL) using trained regression models.

Built as a final-year project at Thapar Institute of Engineering and Technology.

---

## Problem

Unplanned motor failure in industrial plants causes expensive downtime. Traditional maintenance is either reactive (fix after breakdown) or calendar-based (replace parts that are still healthy). Both waste money.

This system monitors motors continuously and flags degradation before failure occurs.

---

## Features

- **Live telemetry stream** — temperature, RPM, and vibration RMS updated in real time
- **FFT harmonic analysis** — 10-band frequency decomposition to identify fault signatures
- **RUL prediction** — estimates remaining operating hours with a confidence score
- **Multi-asset monitoring** — tracks three motors independently with per-asset health scoring
- **Degradation simulation** — motor_03 demonstrates a healthy-to-critical transition over time
- **Secure authentication** — hashed credentials, session management, brute-force lockout

---

## Machine Learning

Three regression models were trained and compared for RUL prediction:

| Model | File |
|---|---|
| Linear Regression | `ml_linear_reg.pkl` |
| Random Forest | `ml_rf_reg.pkl` |
| Gradient Boosting | `ml_gb_reg.pkl` |

Features used: vibration RMS, temperature, RPM, and dominant frequency peak.

---

## Security

Security was treated as a first-class requirement, not an afterthought:

- Passwords stored as **scrypt hashes**, never plain text
- Secrets loaded from environment variables via `.env` — no credentials in source control
- **Brute-force protection** — 5 failed attempts per IP triggers a 5-minute lockout
- **Session hardening** — HttpOnly, SameSite, Secure cookies with a 30-minute timeout
- **Session fixation prevention** — session ID regenerated on login
- **Security headers** — CSP, X-Frame-Options, HSTS, nosniff on every response
- **No user enumeration** — identical error responses for invalid email and invalid password
- Debug mode disabled in production builds

---

## Tech Stack

**Backend:** Python, Flask
**ML:** scikit-learn, NumPy
**Messaging:** MQTT (publisher/subscriber)
**Frontend:** HTML, CSS, JavaScript
**Security:** Werkzeug password hashing, python-dotenv

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Dashboard (redirects to login if unauthenticated) |
| POST | `/api/auth/login` | Authenticate and create session |
| POST | `/api/auth/logout` | Destroy session |
| GET | `/api/telemetry?asset=motor_01` | Live telemetry for a given asset (auth required) |

---

## Setup

```bash
# Clone the repository
git clone https://github.com/nanusaksham6/iot-server.git
cd iot-server

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root: