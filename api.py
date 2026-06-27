# import requests # pyright: ignore[reportMissingModuleSource]

# url = "https://irctc-indian-railway-pnr-status.p.rapidapi.com/getPNRStatus/6833824029"

# headers = {
#     'x-rapidapi-key': "2d0c4d6d54msh52b141af57c4d0ep1bdc3ejsnb455e696e232",
#     'x-rapidapi-host': "irctc-indian-railway-pnr-status.p.rapidapi.com",
#     'Content-Type': "application/json"
# }

# pnr = str(input("Enter PNR Number: "))

# params = {
#     "pnrNumber": pnr
# }

# response = requests.get(url, headers=headers, params=params)

# # print(response.status_code)
# # print(response.text)

# if response.status_code == 200:
#     data = response.json()["data"]
#     # print(data)
#     print("PNR Number:", data["pnrNumber"])
#     print("Train Number:", data["trainNumber"])
#     print("Journey Date:", data["dateOfJourney"])
#     print("Arrival Time:", data["arrivalDate"])
#     print("Booking Date:", data["bookingDate"])
#     print("Train Name:", data["trainName"])
#     print("From Station:", data["sourceStation"])
#     print("To Station:", data["destinationStation"])
#     print("Boarding Point:", data["boardingPoint"])
#     print("Reservation Upto:", data["reservationUpto"])
#     print("Journey Class:", data["journeyClass"])
#     print("Total Passengers:", data["numberOfpassenger"])
#     print("Charting Status:", data["chartStatus"])
#     print("Booking Charge :", data["bookingFare"])
#     print("Quota:", data["quota"])

#     print("----------------------------------------")
#     print("\nPassenger Status:")
#     for passenger in data["passengerList"]:
#         print("Passenger Number:", passenger["passengerSerialNumber"])
#         print("Current Status:", passenger["currentStatus"])
#         print("Booking Status:", passenger["bookingStatus"])
#         print("Coach Position:", passenger["currentCoachId"])
#         print("Current Berth Number:", passenger["currentBerthNo"])
#         print("Booking status:", passenger["bookingStatusDetails"])
#         print("Current status:", passenger["currentStatusDetails"])


# else:
#     print("Error:", response.status_code, response.text)

import requests # type: ignore
import streamlit as st # type: ignore


# -----------------------------
# API Configuration
# -----------------------------

BASE_URL = "https://irctc-indian-railway-pnr-status.p.rapidapi.com/getPNRStatus/"


# -----------------------------
# Get PNR Status
# -----------------------------

@st.cache_data(show_spinner=False, ttl=300)
def get_pnr_status(pnr: str):
    """
    Fetch PNR Status from RapidAPI.

    Parameters
    ----------
    pnr : str

    Returns
    -------
    dict | None
    """

    headers = {
        "x-rapidapi-key": st.secrets["RAPID_API_KEY"],
        "x-rapidapi-host": "irctc-indian-railway-pnr-status.p.rapidapi.com",
        "Content-Type": "application/json",
    }

    params = {
        "pnrNumber": pnr
    }

    try:

        url = BASE_URL + pnr

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        # HTTP Error
        response.raise_for_status()

        json_data = response.json()

        # API returned success
        if json_data.get("success"):

            return json_data.get("data")

        # API returned failure
        st.error(json_data.get("message", "Unable to fetch PNR Status"))

        return None

    except requests.exceptions.Timeout:

        st.error("⏳ Request Timed Out")

    except requests.exceptions.ConnectionError:

        st.error("🌐 Internet Connection Error")

    except requests.exceptions.HTTPError as e:

        st.error(f"HTTP Error : {e}")

    except requests.exceptions.RequestException as e:

        st.error(str(e))

    except Exception as e:

        st.error(f"Unexpected Error : {e}")

    return None