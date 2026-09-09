# =============================================================================
#  IoT SCADA Telemetry Server
#  Copyright (c) 2026 Saksham (github.com/nanusaksham6). All rights reserved.
#
#  Original author : Saksham
#  Institution     : Thapar Institute of Engineering and Technology
#  Repository      : https://github.com/nanusaksham6/iot-server
#  First published : 9 September 2026
#
#  Licensed under the terms in LICENSE. Unauthorised copying, redistribution,
#  or academic submission of this file by any other individual is prohibited.
# =============================================================================





















import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from scipy.signal import butter, filtfilt
from scipy.fft import fft, fftfreq

# ============================
# Connect to PostgreSQL
# ============================

engine = create_engine(
    "postgresql://postgres:1234@localhost:5432/iot_db"
)

# ============================
# Read vibration data
# ============================

df = pd.read_sql(
    "SELECT * FROM vibration_data ORDER BY id",
    engine
)

print(df.head())
print("\nTotal Samples:", len(df))

# ============================
# Original Signal
# ============================

signal = df["vibration"].values

# ============================
# Low Pass Filter (Butterworth)
# ============================

b, a = butter(
    N=3,
    Wn=0.2,
    btype="low"
)

filtered_signal = filtfilt(b, a, signal)

# ============================
# LPF Graph
# ============================

plt.figure(figsize=(12,6))

plt.plot(signal, label="Original Signal")
plt.plot(filtered_signal, label="Filtered Signal", linewidth=3)

plt.title("Low Pass Filter on Vibration Data")
plt.xlabel("Sample Number")
plt.ylabel("Vibration")
plt.grid(True)
plt.legend()

plt.show()

# ============================
# FFT
# ============================

N = len(filtered_signal)

sampling_rate = 1.0

fft_values = fft(filtered_signal)

frequencies = fftfreq(N, d=1/sampling_rate)

positive_freq = frequencies[:N//2]
positive_fft = np.abs(fft_values[:N//2])

# ============================
# FFT Graph
# ============================

plt.figure(figsize=(12,6))

plt.plot(positive_freq, positive_fft, color="red")

plt.title("FFT Spectrum of Filtered Vibration Signal")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.show()