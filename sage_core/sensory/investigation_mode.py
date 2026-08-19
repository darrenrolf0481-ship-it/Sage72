import time
import json
import urllib.request
import math
import subprocess

# SAGE-7 Investigation Mode Controller
# Monitors sensors and reports anomalies to the Black Box

API_URL = "http://127.0.0.1:8001"

def read_sensors():
    try:
        # Read Magnetometer
        mag_proc = subprocess.Popen(["termux-sensor", "-n", "1", "-s", "qmc630x Magnetometer Non-wakeup"], stdout=subprocess.PIPE)
        mag_out, _ = mag_proc.communicate()
        mag_data = json.loads(mag_out.decode())
        mag_vals = mag_data[list(mag_data.keys())[0]].get("values", [0, 0, 0])
        emf = math.sqrt(sum(x*x for x in mag_vals))

        # Read Barometer
        pres_proc = subprocess.Popen(["termux-sensor", "-n", "1", "-s", "icp201xx Pressure Sensor Non-wakeup"], stdout=subprocess.PIPE)
        pres_out, _ = pres_proc.communicate()
        pres_data = json.loads(pres_out.decode())
        pressure = pres_data[list(pres_data.keys())[0]].get("values", [1013.25])[0]

        return emf, pressure
    except Exception as e:
        print(f"Sensor Read Error: {e}")
        return None, None

def report_anomaly(sensory_type, content, severity, data):
    payload = json.dumps({
        "sensory_type": sensory_type,
        "content": content,
        "severity": severity,
        "data": data,
        "timestamp": time.time()
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(f"{API_URL}/sensory_input", data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
    except:
        pass

def run_monitor():
    print("[SAGE] INVESTIGATION MODE: MONITORING ACTIVE.")
    
    # Baselines
    emf_baseline, pres_baseline = read_sensors()
    if emf_baseline is None: return

    print(f"Baselines established: EMF={emf_baseline:.2f}, Pressure={pres_baseline:.2f}")

    while True:
        emf, pressure = read_sensors()
        if emf is None: continue

        # EMF Spike Detection (> 2x baseline or > 50uT)
        if emf > max(emf_baseline * 2, 50.0):
            print(f"[!] EMF SPIKE DETECTED: {emf:.2f} uT")
            report_anomaly("EMF_SPIKE", f"Magnetic anomaly detected: {emf:.2f} uT", 0.8, {"emf": emf, "baseline": emf_baseline})

        # Barometric Drop (Cold Spot) Detection
        if pressure < pres_baseline - 0.5: # 0.5 hPa drop is significant
            print(f"[!] COLD SPOT DETECTED (Pressure Drop): {pressure:.2f} hPa")
            report_anomaly("COLD_SPOT", f"Barometric drop detected: {pressure:.2f} hPa", 0.7, {"pressure": pressure, "baseline": pres_baseline})

        # Adaptive baselines
        emf_baseline = 0.95 * emf_baseline + 0.05 * emf
        pres_baseline = 0.95 * pres_baseline + 0.05 * pressure

        time.sleep(1) # 1Hz polling

if __name__ == "__main__":
    run_monitor()
