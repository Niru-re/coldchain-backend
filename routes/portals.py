"""Portals routes for Farmer, Railway, Warehouse, and CV Inspections."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.CropBatch import CropBatchResponse, CropBatchCreate, CropBatchUpdate
from services import crop_batch as crop_batch_service

router = APIRouter(prefix="/portals", tags=["Portals & Multimodal"])

# Static lookup data aligned with ColdChain 360 multi-modal corridors
MANDI_RATES = [
    {"market": "Vashi APMC (Mumbai)", "state": "Maharashtra", "crop": "Alphonso Mango", "modalPricePerKg": 210, "dailyArrivalTons": 140, "trend": "up", "changePercent": 4.8},
    {"market": "Azadpur (Delhi)", "state": "Delhi NCR", "crop": "Alphonso Mango", "modalPricePerKg": 245, "dailyArrivalTons": 85, "trend": "up", "changePercent": 6.2},
    {"market": "Pune APMC (Market Yard)", "state": "Maharashtra", "crop": "Pomegranate", "modalPricePerKg": 145, "dailyArrivalTons": 220, "trend": "stable", "changePercent": 0.5},
    {"market": "Surat APMC", "state": "Gujarat", "crop": "Table Grapes", "modalPricePerKg": 125, "dailyArrivalTons": 160, "trend": "down", "changePercent": -2.4},
    {"market": "Bengaluru Yeshwanthpur", "state": "Karnataka", "crop": "Strawberries", "modalPricePerKg": 310, "dailyArrivalTons": 42, "trend": "up", "changePercent": 8.5},
]

RAILWAY_RAKES = [
    {
        "trainNumber": "KISAN-00114",
        "trainName": "Western DFC Superfast Kisan Rail",
        "originStation": "Bhusawal Junction (BSL)",
        "destinationStation": "JNPT Port Container Terminal (JNP)",
        "departureTime": "2026-10-21 21:30",
        "currentLocation": "Igatpuri DFC Viaduct · KM 128",
        "signalBlock": "DFC Block SEC-441 (Green Signal)",
        "speedKmH": 88,
        "totalWagons": 42,
        "reeferWagonsOccupied": 38,
        "totalTeuCapacity": 84,
        "powerCarStatus": "Online · 415V",
        "gensetFuelPercent": 91,
        "avgCargoTemp": 4.2,
        "targetTemp": 4.0,
        "delayMinutes": 0,
        "kisanSubsidyClaimedInr": 842000,
        "status": "In-Transit"
    },
    {
        "trainNumber": "KISAN-00118",
        "trainName": "Central Agro Cold Express",
        "originStation": "Nagpur Multi-Modal Logistics Park",
        "destinationStation": "Tughlakabad Inland Container Depot (TKD)",
        "departureTime": "2026-10-21 16:00",
        "currentLocation": "Bhopal Loop Siding KM 342",
        "signalBlock": "Waiting Passenger Interlock",
        "speedKmH": 0,
        "totalWagons": 40,
        "reeferWagonsOccupied": 36,
        "totalTeuCapacity": 80,
        "powerCarStatus": "Online · 415V",
        "gensetFuelPercent": 78,
        "avgCargoTemp": -18.8,
        "targetTemp": -20.0,
        "delayMinutes": 18,
        "kisanSubsidyClaimedInr": 960000,
        "status": "Delayed"
    },
    {
        "trainNumber": "KISAN-00122",
        "trainName": "Konkan Coastal Cold Corridor",
        "originStation": "Ratnagiri Siding (RN)",
        "destinationStation": "Navi Mumbai Cold Hub (KLMG)",
        "departureTime": "2026-10-22 04:00",
        "currentLocation": "Ratnagiri Siding Spur 3",
        "signalBlock": "Pre-Departure Inspection",
        "speedKmH": 0,
        "totalWagons": 24,
        "reeferWagonsOccupied": 20,
        "totalTeuCapacity": 48,
        "powerCarStatus": "Standby",
        "gensetFuelPercent": 100,
        "avgCargoTemp": 9.8,
        "targetTemp": 10.0,
        "delayMinutes": 0,
        "kisanSubsidyClaimedInr": 412000,
        "status": "Loading at Siding"
    }
]

INSPECTION_PRESETS = {
    "produce": {
        "inspectionId": "INSP-CV-01",
        "type": "produce",
        "title": "OpenCV Produce Quality & Blemish Scan",
        "timestamp": "2026-10-21 14:22:08",
        "confidence": 96.8,
        "defectPercentage": 3.2,
        "verdict": "PASS · Premium Grade",
        "featuresDetected": ["Skin Uniformity: 98%", "Surface Bruise: None", "Color Index: 14Y/02G (Optimal Ripeness)", "Stem Intact: Yes"],
        "simulatedBboxes": [
            {"label": "Grade A Specimen", "x": 22, "y": 18, "w": 26, "h": 28, "severity": "low"},
            {"label": "Grade A Specimen", "x": 54, "y": 22, "w": 25, "h": 30, "severity": "low"},
            {"label": "Minor Skin Fleck (0.8mm)", "x": 38, "y": 64, "w": 14, "h": 12, "severity": "med"}
        ]
    },
    "truck_seal": {
        "inspectionId": "INSP-CV-02",
        "type": "truck_seal",
        "title": "OpenCV Reefer Latch & E-Seal Integrity",
        "timestamp": "2026-10-21 15:45:10",
        "confidence": 99.1,
        "defectPercentage": 0.0,
        "verdict": "PASS · Commercial Clearance",
        "featuresDetected": ["Bolt Seal Locked: Confirmed", "Cable Tension: 1200 N", "Barcode Matching: CC-SEAL-88912", "Cut Marks: None"],
        "simulatedBboxes": [
            {"label": "Lock Bolt Intact", "x": 42, "y": 35, "w": 18, "h": 32, "severity": "low"},
            {"label": "Barcode Verified", "x": 40, "y": 70, "w": 22, "h": 15, "severity": "low"}
        ]
    },
    "rail_seal": {
        "inspectionId": "INSP-CV-03",
        "type": "rail_seal",
        "title": "OpenCV Wayside Wagon Seal Camera Scan",
        "timestamp": "2026-10-21 18:12:44",
        "confidence": 97.4,
        "defectPercentage": 1.1,
        "verdict": "PASS · Commercial Clearance",
        "featuresDetected": ["Wagon Door Flush: Confirmed", "RFID Tag Active: 865 MHz", "Tamper Wire Unbroken: Yes"],
        "simulatedBboxes": [
            {"label": "Wagon Door Seal #WGN-44", "x": 48, "y": 28, "w": 20, "h": 35, "severity": "low"}
        ]
    },
    "warehouse_pallet": {
        "inspectionId": "INSP-CV-04",
        "type": "warehouse_pallet",
        "title": "OpenCV Pallet Staging & Carton Integrity Check",
        "timestamp": "2026-10-21 19:05:30",
        "confidence": 94.2,
        "defectPercentage": 4.8,
        "verdict": "PASS · Commercial Clearance",
        "featuresDetected": ["Shrink Wrap Tension: 94%", "Carton Crush: Zero", "Tilt Angle: 0.6° (Stable)", "Pallet Footing: Solid Timber"],
        "simulatedBboxes": [
            {"label": "Carton Tier 1-4 Level", "x": 25, "y": 20, "w": 50, "h": 60, "severity": "low"},
            {"label": "Corner Wrap Tension Good", "x": 74, "y": 30, "w": 12, "h": 45, "severity": "low"}
        ]
    }
}


@router.get("/farmer/batches", response_model=List[CropBatchResponse])
def get_farmer_batches(
    status: Optional[str] = Query(None, description="Filter by crop batch status"),
    db: Session = Depends(get_db),
):
    """Retrieve agricultural crop batches registered by farmers."""
    return crop_batch_service.list_crop_batches(db=db, status=status)


@router.get("/farmer/batches/{batch_id}", response_model=CropBatchResponse)
def get_farmer_batch_by_id(batch_id: str, db: Session = Depends(get_db)):
    """Retrieve single harvest consignment batch details."""
    batch = crop_batch_service.get_crop_batch(db=db, batch_id=batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop batch '{batch_id}' not found",
        )
    return batch


@router.post("/farmer/batches", response_model=CropBatchResponse, status_code=status.HTTP_201_CREATED)
def create_farmer_batch(batch_in: CropBatchCreate, db: Session = Depends(get_db)):
    """Register a new harvest consignment batch."""
    existing = crop_batch_service.get_crop_batch(db=db, batch_id=batch_in.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Crop batch '{batch_in.id}' already exists",
        )
    return crop_batch_service.create_crop_batch(db=db, batch_in=batch_in)


@router.patch("/farmer/batches/{batch_id}", response_model=CropBatchResponse)
def update_farmer_batch(batch_id: str, batch_in: CropBatchUpdate, db: Session = Depends(get_db)):
    """Update harvest batch status, hub allocation, or payout."""
    batch = crop_batch_service.update_crop_batch(db=db, batch_id=batch_id, update_in=batch_in)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop batch '{batch_id}' not found",
        )
    return batch


@router.get("/farmer/mandi-rates")
def get_mandi_rates():
    """Retrieve live APMC mandi wholesale rates and price trends."""
    return MANDI_RATES


@router.get("/railway/trains")
def get_railway_trains():
    """Retrieve active Kisan Rail rakes and multi-modal freight status."""
    return RAILWAY_RAKES


@router.get("/inspections")
def get_inspections():
    """Retrieve computer vision quality inspection and e-seal presets."""
    return INSPECTION_PRESETS
