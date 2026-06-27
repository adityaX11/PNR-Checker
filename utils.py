from datetime import datetime
import pandas as pd


# ======================================================
# STATUS COLOR
# ======================================================

def status_color(status: str) -> str:
    """
    Return color according to passenger status.
    """

    if not status:
        return "#9E9E9E"

    status = status.upper()

    if "CNF" in status or "CONFIRMED" in status:
        return "#00C853"      # Green

    elif "RAC" in status:
        return "#FF9800"      # Orange

    elif "WL" in status:
        return "#F44336"      # Red

    elif "CAN" in status:
        return "#9C27B0"      # Purple

    return "#2196F3"


# ======================================================
# STATUS ICON
# ======================================================

def status_icon(status: str) -> str:

    if not status:
        return "⚪"

    status = status.upper()

    if "CNF" in status:
        return "🟢"

    elif "RAC" in status:
        return "🟠"

    elif "WL" in status:
        return "🔴"

    return "🔵"


# ======================================================
# DATE FORMATTER
# ======================================================

def format_date(date_string):

    """
    Convert

    Jul 4, 2026 7:40:00 PM

    into

    04 Jul 2026
    """

    if not date_string:
        return "-"

    try:

        dt = datetime.strptime(
            date_string,
            "%b %d, %Y %I:%M:%S %p"
        )

        return dt.strftime("%d %b %Y")

    except:

        return date_string


# ======================================================
# TIME FORMATTER
# ======================================================

def format_time(date_string):

    if not date_string:
        return "-"

    try:

        dt = datetime.strptime(
            date_string,
            "%b %d, %Y %I:%M:%S %p"
        )

        return dt.strftime("%I:%M %p")

    except:

        return "-"


# ======================================================
# JOURNEY DURATION
# ======================================================

def calculate_duration(start, end):

    """
    Return journey duration.
    """

    try:

        start = datetime.strptime(
            start,
            "%b %d, %Y %I:%M:%S %p"
        )

        end = datetime.strptime(
            end,
            "%b %d, %Y %I:%M:%S %p"
        )

        diff = end - start

        hrs = diff.seconds // 3600

        mins = (diff.seconds % 3600) // 60

        days = diff.days

        if days > 0:
            return f"{days} Day {hrs} Hr {mins} Min"

        return f"{hrs} Hr {mins} Min"

    except:

        return "-"


# ======================================================
# RUPEE FORMAT
# ======================================================

def format_currency(amount):

    try:

        return f"₹ {int(amount):,}"

    except:

        return "-"


# ======================================================
# CHART STATUS
# ======================================================

def chart_badge(chart_status):

    if not chart_status:
        return "⚪ Unknown"

    chart_status = chart_status.upper()

    if "PREPARED" in chart_status:
        return "✅ Chart Prepared"

    if "NOT" in chart_status:
        return "🟡 Chart Not Prepared"

    return chart_status


# ======================================================
# PASSENGER DATAFRAME
# ======================================================

def passenger_dataframe(passenger_list):

    rows = []

    for p in passenger_list:

        rows.append({

            "Passenger": p["passengerSerialNumber"],

            "Current Status": p["currentStatusDetails"],

            "Booking Status": p["bookingStatusDetails"],

            "Coach": p["currentCoachId"],

            "Berth": p["currentBerthNo"]

        })

    return pd.DataFrame(rows)


# ======================================================
# STATUS COUNTS
# ======================================================

def passenger_summary(passenger_list):

    summary = {

        "CNF": 0,

        "RAC": 0,

        "WL": 0

    }

    for p in passenger_list:

        status = p["currentStatus"].upper()

        if "CNF" in status:

            summary["CNF"] += 1

        elif "RAC" in status:

            summary["RAC"] += 1

        elif "WL" in status:

            summary["WL"] += 1

    return summary


# ======================================================
# VALIDATE PNR
# ======================================================

def validate_pnr(pnr):

    if len(pnr) != 10:
        return False

    if not pnr.isdigit():
        return False

    return True


# ======================================================
# DOWNLOAD DATA
# ======================================================

def create_download_dataframe(data):

    rows = []

    rows.append({
        "Field": "PNR Number",
        "Value": data["pnrNumber"]
    })

    rows.append({
        "Field": "Train Name",
        "Value": data["trainName"]
    })

    rows.append({
        "Field": "Train Number",
        "Value": data["trainNumber"]
    })

    rows.append({
        "Field": "Source",
        "Value": data["sourceStation"]
    })

    rows.append({
        "Field": "Destination",
        "Value": data["destinationStation"]
    })

    rows.append({
        "Field": "Journey Date",
        "Value": data["dateOfJourney"]
    })

    rows.append({
        "Field": "Booking Fare",
        "Value": data["bookingFare"]
    })

    rows.append({
        "Field": "Chart Status",
        "Value": data["chartStatus"]
    })

    return pd.DataFrame(rows)