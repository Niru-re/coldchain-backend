"""ColdChain 360 - Real-Time Telematics GPS Ingestion Simulator.

Periodically pings the FastAPI backend API with live moving GPS coordinates,
realistic reefer temperatures, speeds, and heading angles.

Usage:
    python backend/scripts/simulate_telematics.py [--interval 2] [--host http://localhost:8000]
"""

import sys
import time
import math
import argparse
from typing import Dict, List, Tuple
import urllib.request
import urllib.error
import json

# Major Freight Corridors (lat, lng)
TRUCK_ROUTES: Dict[str, List[Tuple[float, float]]] = {
    "CC-REEFER-01": [
        (16.9902, 73.3120),  # Ratnagiri Orchard
        (17.7120, 73.3890),  # Khed Bypass
        (18.5204, 73.8567),  # Pune Bio-Cluster
        (18.9894, 73.1175),  # Panvel Hub
        (19.0896, 72.8656),  # Mumbai Cargo BOM
    ],
    "CC-REEFER-02": [
        (19.9975, 73.7898),  # Nashik Agro
        (19.6750, 73.4830),  # Igatpuri
        (19.2967, 73.0631),  # Bhiwandi Hub
        (18.9499, 72.9511),  # JNPT Port
    ],
    "CC-REEFER-03": [
        (18.5204, 73.8567),  # Pune
        (18.7557, 73.4091),  # Lonavala
        (18.7880, 73.3440),  # Khopoli Expressway
        (19.0330, 73.0297),  # Navi Mumbai
        (19.2967, 73.0631),  # Bhiwandi
    ],
    "CC-REEFER-04": [
        (18.9500, 72.9500),  # Nhava Sheva
        (18.9894, 73.1175),  # Panvel
        (18.7880, 73.3440),  # Expressway
        (18.5204, 73.8567),  # Pune Bio Park
    ],
    "CC-REEFER-05": [
        (21.1458, 79.0882),  # Nagpur Central
        (20.7002, 77.0082),  # Karanja Lad
        (19.8762, 75.3433),  # Aurangabad
        (19.6750, 73.4830),  # Igatpuri
        (19.0760, 72.8777),  # Mumbai
    ],
}


def send_patch(url: str, data: dict) -> bool:
    """Send HTTP PATCH request using standard library."""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        return False


def main():
    parser = argparse.ArgumentParser(description="ColdChain 360 Telematics Ingestion Simulator")
    parser.add_argument("--interval", type=float, default=2.0, help="Ping interval in seconds (default: 2.0)")
    parser.add_argument("--host", type=str, default="http://localhost:8000", help="FastAPI backend URL")
    args = parser.parse_args()

    api_base = f"{args.host.rstrip('/')}/api/v1/fleet/trucks"

    print("=" * 65)
    print("  COLDCHAIN 360 - LIVE TELEMATICS INGESTION ENGINE")
    print(f"  Target Backend : {api_base}")
    print(f"  Ping Interval  : {args.interval}s")
    print("=" * 65)

    progress: Dict[str, float] = {truck_id: i * 0.4 for i, truck_id in enumerate(TRUCK_ROUTES)}

    iteration = 0
    try:
        while True:
            iteration += 1
            print(f"\n[Tick #{iteration}] Ingesting live GPS pings...")

            for truck_id, pts in TRUCK_ROUTES.items():
                N = len(pts) - 1
                curr_prog = progress[truck_id]
                next_prog = curr_prog + 0.04
                if next_prog >= N:
                    next_prog = 0.0

                progress[truck_id] = next_prog

                seg_idx = min(int(next_prog), N - 1)
                t = next_prog - seg_idx
                p1 = pts[seg_idx]
                p2 = pts[seg_idx + 1]

                lat = round(p1[0] + (p2[0] - p1[0]) * t, 5)
                lng = round(p1[1] + (p2[1] - p1[1]) * t, 5)

                speed = round(64.0 + math.sin(time.time() + seg_idx) * 6.0, 1)
                temp = round(3.8 + math.sin(time.time() * 0.5) * 0.4, 2)

                payload = {
                    "latitude": lat,
                    "longitude": lng,
                    "current_temperature": temp,
                    "status": "En Route",
                    "current_location": f"Corridor Section KM {int(next_prog * 45)} (Live GPS)",
                }

                url = f"{api_base}/{truck_id}"
                success = send_patch(url, payload)
                status_symbol = "✓" if success else "✗ (backend offline)"
                print(f"  [{status_symbol}] {truck_id}: Lat={lat}, Lng={lng}, Speed={speed}km/h, Temp={temp}°C")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\nTelematics simulator stopped cleanly.")


if __name__ == "__main__":
    main()
