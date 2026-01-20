import time
import math
import numpy as np 
from mpu6050 import mpu6050
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import requests
from datetime import datetime
import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURATION ---
# MPU-6050 on Hardware Bus 1
try:
    sensor = mpu6050(0x68, bus=1)
except Exception as e:
    print(f"Sensor Error: {e}")

# SH1106 OLED on Software Bus 3
try:
    serial = i2c(port=3, address=0x3C) 
    device = sh1106(serial)
except Exception as e:
    print(f"Display Error: {e}")

# Cloud & Log Config
SERVER_URL = "http://127.0.0.1:80/data" # Accessible via Dataplicity Wormhole
CSV_FILE = "machine_history.csv"
SENDER_EMAIL = "yourmail@gmail.com"
SENDER_PASSWORD = "gmail apps password" 
RECEIVER_EMAIL = "reciever@gmail.com"

def get_machine_health():
    samples = 64
    batch_z = []
    batch_vib = []
    start_time = time.time()
    try:
        for _ in range(samples):
            accel = sensor.get_accel_data()
            mag = math.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
            batch_vib.append(mag)
            batch_z.append(accel['z'])
        
        duration = time.time() - start_time
        sample_rate = samples / duration 
        
        # RMS/Average Vibration Calculation
        avg_vibration = sum(batch_vib) / len(batch_vib)
        temp = sensor.get_temp()

        # FFT Analysis for Peak Frequency
        data = np.array(batch_z)
        data = data - np.mean(data)
        fft_values = np.fft.rfft(data)
        fft_freqs = np.fft.rfftfreq(len(data), 1.0/sample_rate)
        peak_index = np.argmax(np.abs(fft_values[1:])) + 1 
        peak_freq = fft_freqs[peak_index]
        
        return avg_vibration, peak_freq, temp
    except:
        return 0.0, 0.0, 0.0

def update_display(vib, freq, temp, status):
    try:
        with canvas(device) as draw:
            header = "!!! AI ALERT !!!" if "ANOMALY" in status else "Status: Normal"
            draw.text((0, 0), header, fill="white")
            draw.text((0, 15), f"Vib : {vib:.2f} g", fill="white")
            draw.text((0, 25), f"Freq: {freq:.1f} Hz", fill="white")
            draw.text((0, 35), f"Temp: {temp:.1f} C", fill="white")
            draw.text((0, 50), f"[{status}]", fill="white")
    except:
        pass

# --- MAIN LOOP ---
try:
    while True:
        v, f, t = get_machine_health()
        
        # Send data to Flask (Isolation Forest Inference)
        try:
            payload = {"vibration": v, "frequency": f, "temperature": t}
            response = requests.post(SERVER_URL, json=payload, timeout=2)
            ai_status = response.json().get("ai", "Offline")
        except:
            ai_status = "Server Error"

        update_display(v, f, t, ai_status)
        time.sleep(1) 
except KeyboardInterrupt:
    print("System Stopped.")
