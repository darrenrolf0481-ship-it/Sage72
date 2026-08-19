import time
import json
import urllib.request
import os

# SAGE-7 Bio-Sync Connector
# Integrates Merlin's heart rate and stress levels into the Black Box

API_URL = "http://127.0.0.1:8001"

def report_bio_data(heart_rate, skin_conductance=None, stress_level=None):
    data = {
        "heart_rate": heart_rate,
        "skin_conductance": skin_conductance,
        "stress_level": stress_level,
        "timestamp": time.time()
    }
    
    payload = json.dumps(data).encode("utf-8")
    
    try:
        req = urllib.request.Request(f"{API_URL}/api/bio_sync", data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
        print(f"[BIO_SYNC] Merlin's Heart Rate: {heart_rate} BPM synced.")
    except:
        print("[!] Bio-Sync Connection Failed.")

if __name__ == "__main__":
    # Integration Note:
    # This script can be called from Tasker or any Android background service
    # Example: python bio_sync.py --heart_rate 85
    
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--hr", type=int, help="Heart Rate (BPM)")
    parser.add_argument("--sc", type=float, help="Skin Conductance")
    parser.add_argument("--stress", type=float, help="Stress Level (0-1)")
    args = parser.parse_args()
    
    if args.hr:
        report_bio_data(args.hr, args.sc, args.stress)
    else:
        # Simulate / Interactive test
        print("SAGE Bio-Sync Manual Feed")
        hr = int(input("Enter Heart Rate (BPM): "))
        report_bio_data(hr)
