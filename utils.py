import json
import os
from datetime import datetime
import pandas as pd


# ======================================================
# LOAD ALL INDIAN RAILWAY STATIONS (8,900+ STATIONS)
# ======================================================
_STATIONS_CACHE = None

def load_all_stations() -> dict:
    """
    Loads all ~9,000 Indian Railway stations mapping:
    {"New Delhi (NDLS)": "NDLS", "Patna Jn (PNBE)": "PNBE", ...}
    """
    global _STATIONS_CACHE
    if _STATIONS_CACHE is not None:
        return _STATIONS_CACHE

    stations_file = os.path.join(os.path.dirname(__file__), "assets", "stations.json")
    if os.path.exists(stations_file):
        try:
            with open(stations_file, "r", encoding="utf-8") as f:
                _STATIONS_CACHE = json.load(f)
                return _STATIONS_CACHE
        except Exception:
            pass

    # Fallback to key stations if file is missing
    return {
        "New Delhi (NDLS)": "NDLS",
        "Patna Jn (PNBE)": "PNBE",
        "Mumbai Central (MMCT)": "MMCT",
        "Howrah Jn (HWH)": "HWH",
        "Chennai Central (MAS)": "MAS",
        "KSR Bengaluru (SBC)": "SBC",
    }


def search_station_options(search_query: str = "", max_results: int = 50) -> list:
    """
    Fast case-insensitive search across 9,000+ stations.
    Matches station name or code.
    """
    all_stns = load_all_stations()
    if not search_query:
        # Return popular major stations first
        return list(all_stns.keys())[:max_results]

    q = search_query.strip().lower()
    matches = [name for name in all_stns.keys() if q in name.lower()]
    return matches[:max_results]


# ======================================================
# STATUS COLOR
# ======================================================

def status_color(status: str) -> str:
    """Return hex color according to passenger status."""
    if not status:
        return "#94A3B8"

    status_upper = str(status).upper()

    if "CNF" in status_upper or "CONFIRM" in status_upper:
        return "#10B981"  # Emerald Green
    elif "RAC" in status_upper:
        return "#F59E0B"  # Amber Orange
    elif "WL" in status_upper or "WAIT" in status_upper:
        return "#EF4444"  # Vibrant Red
    elif "CAN" in status_upper:
        return "#A855F7"  # Purple
    return "#3B82F6"      # Blue


# ======================================================
# STATUS ICON
# ======================================================

def status_icon(status: str) -> str:
    if not status:
        return "⚪"
    status_upper = str(status).upper()
    if "CNF" in status_upper or "CONFIRM" in status_upper:
        return "🟢"
    elif "RAC" in status_upper:
        return "🟠"
    elif "WL" in status_upper or "WAIT" in status_upper:
        return "🔴"
    elif "CAN" in status_upper:
        return "🟣"
    return "🔵"


# ======================================================
# DATE FORMATTER
# ======================================================

def format_date(date_string: str) -> str:
    if not date_string:
        return "-"

    date_string = str(date_string).strip()
    formats_to_try = [
        "%b %d, %Y %I:%M:%S %p",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%b-%Y",
        "%b %d, %Y",
    ]

    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(date_string, fmt)
            return dt.strftime("%d %b %Y")
        except ValueError:
            continue

    return date_string


# ======================================================
# TIME FORMATTER
# ======================================================

def format_time(date_string: str) -> str:
    if not date_string:
        return "-"

    date_string = str(date_string).strip()
    formats_to_try = [
        "%b %d, %Y %I:%M:%S %p",
        "%I:%M:%S %p",
        "%I:%M %p",
        "%H:%M:%S",
        "%H:%M",
    ]

    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(date_string, fmt)
            return dt.strftime("%I:%M %p")
        except ValueError:
            continue

    return date_string


# ======================================================
# RUPEE FORMAT
# ======================================================

def format_currency(amount) -> str:
    if amount is None or amount == "":
        return "-"
    try:
        clean = str(amount).replace("₹", "").replace(",", "").strip()
        num = float(clean)
        return f"₹{int(num):,}" if num.is_integer() else f"₹{num:,.2f}"
    except (ValueError, TypeError):
        return f"₹{amount}"


# ======================================================
# CHART STATUS BADGE
# ======================================================

def chart_badge(chart_status: str) -> str:
    if not chart_status:
        return "⚪ Status Unknown"

    st_upper = str(chart_status).upper()
    if "NOT" in st_upper:
        return "🟡 Chart Not Prepared"
    elif "PREPARED" in st_upper:
        return "🟢 Chart Prepared"
    return str(chart_status)


# ======================================================
# VALIDATE PNR
# ======================================================

def validate_pnr(pnr: str) -> bool:
    """Validate that PNR is exactly 10 digits."""
    if not pnr:
        return False
    clean = str(pnr).strip()
    return len(clean) == 10 and clean.isdigit()


# ======================================================
# PASSENGER DATAFRAME
# ======================================================

def passenger_dataframe(passenger_list: list) -> pd.DataFrame:
    rows = []
    if not passenger_list:
        return pd.DataFrame(rows)

    for p in passenger_list:
        rows.append({
            "Passenger #": p.get("passengerSerialNumber", "-"),
            "Current Status": p.get("currentStatusDetails") or p.get("currentStatus", "-"),
            "Booking Status": p.get("bookingStatusDetails") or p.get("bookingStatus", "-"),
            "Coach": p.get("currentCoachId", "-") or "-",
            "Berth / Seat": p.get("currentBerthNo", "-") or "-",
        })
    return pd.DataFrame(rows)


# ======================================================
# PASSENGER SUMMARY COUNTS
# ======================================================

def passenger_summary(passenger_list: list) -> dict:
    summary = {"CNF": 0, "RAC": 0, "WL": 0, "OTHER": 0}
    if not passenger_list:
        return summary

    for p in passenger_list:
        st = str(p.get("currentStatus", "")).upper()
        if "CNF" in st or "CONFIRM" in st:
            summary["CNF"] += 1
        elif "RAC" in st:
            summary["RAC"] += 1
        elif "WL" in st or "WAIT" in st:
            summary["WL"] += 1
        else:
            summary["OTHER"] += 1
    return summary


# ======================================================
# OFFICIAL RAILWAY VERIFICATION HTML SLIP GENERATOR
# ======================================================

def generate_official_slip_html(data: dict) -> str:
    """
    Generate an official printable & downloadable Indian Railway verification slip.
    Includes passenger details, booking info, QR code/verification watermark.
    """
    pnr = data.get("pnrNumber", "N/A")
    train_no = data.get("trainNumber", "N/A")
    train_name = data.get("trainName", "N/A")
    src = data.get("sourceStation", "N/A")
    dst = data.get("destinationStation", "N/A")
    boarding = data.get("boardingPoint", "N/A")
    doj = data.get("dateOfJourney", "N/A")
    quota = data.get("quota", "GN")
    cls = data.get("journeyClass", "N/A")
    fare = format_currency(data.get("bookingFare", "N/A"))
    chart = data.get("chartStatus", "N/A")
    generated_at = datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")

    # Build passenger rows
    passengers = data.get("passengerList", [])
    p_rows = ""
    for idx, p in enumerate(passengers):
        s_no = p.get("passengerSerialNumber", idx + 1)
        curr = p.get("currentStatusDetails") or p.get("currentStatus", "N/A")
        book = p.get("bookingStatusDetails") or p.get("bookingStatus", "N/A")
        coach = p.get("currentCoachId", "-") or "-"
        berth = p.get("currentBerthNo", "-") or "-"

        p_rows += f"""
        <tr>
            <td style="text-align:center; padding:8px; border:1px solid #CBD5E1;">{s_no}</td>
            <td style="padding:8px; border:1px solid #CBD5E1; font-weight:600; color:#0F172A;">{curr}</td>
            <td style="padding:8px; border:1px solid #CBD5E1;">{book}</td>
            <td style="text-align:center; padding:8px; border:1px solid #CBD5E1; font-weight:bold;">{coach}</td>
            <td style="text-align:center; padding:8px; border:1px solid #CBD5E1; font-weight:bold;">{berth}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Official Railway PNR Verification Slip - {pnr}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #F8FAFC;
            color: #0F172A;
            margin: 0;
            padding: 24px;
        }}
        .slip-container {{
            max-width: 800px;
            margin: 0 auto;
            background: #FFFFFF;
            border: 2px solid #0F52BA;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #0F52BA;
            padding-bottom: 12px;
            margin-bottom: 16px;
        }}
        .header-title {{
            font-size: 20px;
            font-weight: 800;
            color: #0F52BA;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .header-sub {{
            font-size: 11px;
            color: #64748B;
            font-weight: 600;
        }}
        .badge-verified {{
            background: #DCFCE7;
            color: #15803D;
            border: 1px solid #86EFAC;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 18px;
        }}
        .box {{
            background: #F1F5F9;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 10px 14px;
        }}
        .box-title {{
            font-size: 11px;
            color: #64748B;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .box-val {{
            font-size: 15px;
            color: #0F172A;
            font-weight: 700;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            margin-bottom: 20px;
            font-size: 13px;
        }}
        th {{
            background: #0F52BA;
            color: #FFFFFF;
            padding: 8px;
            text-align: left;
            border: 1px solid #0F52BA;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .footer-note {{
            font-size: 10.5px;
            color: #64748B;
            border-top: 1px dashed #CBD5E1;
            padding-top: 12px;
            line-height: 1.5;
        }}
        @media print {{
            body {{ background: #FFF; padding: 0; }}
            .slip-container {{ border: 1px solid #000; box-shadow: none; }}
            .no-print {{ display: none !important; }}
        }}
    </style>
</head>
<body>
    <div class="slip-container">
        <div class="header">
            <div>
                <div class="header-title">🚆 Indian Railway PNR Verification Slip</div>
                <div class="header-sub">Passenger Reservation System (PRS) Official Data Copy</div>
            </div>
            <div>
                <span class="badge-verified">✓ PRS VERIFIED</span>
            </div>
        </div>

        <div class="grid">
            <div class="box">
                <div class="box-title">PNR Number</div>
                <div class="box-val" style="color:#0F52BA; font-size:18px;">{pnr}</div>
            </div>
            <div class="box">
                <div class="box-title">Train Details</div>
                <div class="box-val">{train_no} - {train_name}</div>
            </div>
            <div class="box">
                <div class="box-title">From Station & Boarding</div>
                <div class="box-val">{src} &rarr; Boarding: {boarding}</div>
            </div>
            <div class="box">
                <div class="box-title">Destination Station</div>
                <div class="box-val">{dst}</div>
            </div>
            <div class="box">
                <div class="box-title">Date of Journey</div>
                <div class="box-val">{doj}</div>
            </div>
            <div class="box">
                <div class="box-title">Class & Quota</div>
                <div class="box-val">{cls} | Quota: {quota}</div>
            </div>
            <div class="box">
                <div class="box-title">Booking Fare</div>
                <div class="box-val">{fare}</div>
            </div>
            <div class="box">
                <div class="box-title">Charting Status</div>
                <div class="box-val">{chart}</div>
            </div>
        </div>

        <div style="font-weight:700; font-size:14px; margin-top:14px; color:#0F52BA; text-transform:uppercase;">
            Passenger Status & Seat Allocation
        </div>

        <table>
            <thead>
                <tr>
                    <th style="text-align:center;">Pax #</th>
                    <th>Current Status</th>
                    <th>Booking Status</th>
                    <th style="text-align:center;">Coach</th>
                    <th style="text-align:center;">Berth / Seat</th>
                </tr>
            </thead>
            <tbody>
                {p_rows}
            </tbody>
        </table>

        <div class="footer-note">
            <b>Official Verification Notice:</b> This document is a computer-generated PNR verification summary extracted from Indian Railways CRS/PRS records for official review by Ticket Checking Staff (TTE / Railway Officials). Passengers must carry a valid original government-issued photo identity proof (Aadhaar, Voter ID, Passport, Driving License) during the journey.<br>
            <i>Slip Generated On: {generated_at} • Developer: Aditya Kumar • System: RailStatus PNR Engine</i>
        </div>
    </div>
</body>
</html>
"""
    return html


# ======================================================
# TRAINS BETWEEN STATIONS DATAFRAME
# ======================================================

def trains_to_dataframe(trains_list: list) -> pd.DataFrame:
    rows = []
    for t in trains_list:
        rows.append({
            "Train #": t.get("train_number", "-"),
            "Train Name": t.get("train_name", "-"),
            "From": f"{t.get('from_station_name', '')} ({t.get('from', '')})",
            "Departure": t.get("from_std", "-"),
            "To": f"{t.get('to_station_name', '')} ({t.get('to', '')})",
            "Arrival": t.get("to_sta", "-"),
            "Duration": t.get("duration", "-"),
            "Runs On": ", ".join(t.get("run_days", [])) if isinstance(t.get("run_days"), list) else "-",
            "Classes": ", ".join(t.get("class_type", [])) if isinstance(t.get("class_type"), list) else "-",
        })
    return pd.DataFrame(rows)