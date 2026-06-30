import streamlit as st
import pandas as pd
from api import get_pnr_status
from utils import status_color


# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Indian Railway PNR Status",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# LOAD CSS
# -----------------------------

try:
    with open("style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass

# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.image(
        "assets/train.png",
        width=120
    )

    st.title("🚆 PNR Checker")

    st.markdown("---")

    st.markdown("### 👨‍💻 Developer")
    st.write("Aditya Kumar")

    st.markdown("### 🛠 Version")
    st.write("1.0.0")

    st.markdown("### 🌐 API")
    st.write("RapidAPI")

    st.markdown("---")

    st.info(
        """
        🚂 **Is your seat confirmed or still playing hide-and-seek? 👀**

        Type your PNR below and let's solve the mystery together!
        """
    )

# -----------------------------
# HEADER
# -----------------------------

st.markdown(
    """
<h1 style='text-align:center;color:#4CAF50;'>
🚆 Indian Railway PNR Status Checker
</h1>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<p style='text-align:center;font-size:18px;color:gray'>
Know your Railway Reservation Status instantly.
</p>
""",
    unsafe_allow_html=True,
)

st.write("")

# -----------------------------
# SEARCH
# -----------------------------

col1, col2 = st.columns([5,1])

with col1:

    pnr = st.text_input(
        "Enter PNR Number",
        placeholder="Enter 10 Digit PNR Number",
    )

with col2:

    st.write("")
    st.write("")

    search = st.button(
        "🔍 Search",
        use_container_width=True
    )

# -----------------------------
# SEARCH EVENT
# -----------------------------

if search:

    if len(pnr) != 10:

        st.error("Please Enter Valid 10 Digit PNR Number.")

        st.stop()

    with st.spinner("Fetching Latest PNR Status..."):

        data = get_pnr_status(pnr)

    if data is None:

        st.error("Unable to Fetch Data.")

        st.stop()

    # -----------------------------
    # SUCCESS
    # -----------------------------

    st.success("PNR Status Retrieved Successfully")

    st.divider()

    # -----------------------------
    # METRICS
    # -----------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "PNR Number",
        data["pnrNumber"]
    )

    c2.metric(
        "Train Number",
        data["trainNumber"]
    )

    c3.metric(
        "Class",
        data["journeyClass"]
    )

    c4.metric(
        "Fare",
        f"₹ {data['bookingFare']}"
    )

    st.divider()

    # -----------------------------
    # JOURNEY DETAILS
    # -----------------------------

    st.subheader("🚉 Journey Details")

    left, right = st.columns(2)

    with left:

        st.markdown(f"**Train Name** : {data['trainName']}")

        st.markdown(f"**From** : {data['sourceStation']}")

        st.markdown(f"**Boarding Point** : {data['boardingPoint']}")

        st.markdown(f"**Journey Date** : {data['dateOfJourney']}")

        st.markdown(f"**Booking Date** : {data['bookingDate']}")

    with right:

        st.markdown(f"**To** : {data['destinationStation']}")

        st.markdown(f"**Reservation Upto** : {data['reservationUpto']}")

        st.markdown(f"**Arrival Date** : {data['arrivalDate']}")

        st.markdown(f"**Quota** : {data['quota']}")

        st.markdown(f"**Chart Status** : {data['chartStatus']}")

    st.divider()

    # -----------------------------
    # PASSENGER DETAILS
    # -----------------------------

    st.subheader("🧍 Passenger Details")

    passenger_df = []

    for passenger in data["passengerList"]:

        passenger_df.append({

            "Passenger": passenger["passengerSerialNumber"],

            "Current Status": passenger["currentStatusDetails"],

            "Booking Status": passenger["bookingStatusDetails"],

            "Coach": passenger["currentCoachId"],

            "Berth": passenger["currentBerthNo"]

        })

    df = pd.DataFrame(passenger_df)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # PASSENGER CARDS
    # -----------------------------

    st.subheader("Passenger Summary")

    for passenger in data["passengerList"]:

        color = status_color(passenger["currentStatus"])

        with st.container(border=True):

            st.markdown(
                f"### Passenger {passenger['passengerSerialNumber']}"
            )

            c1, c2, c3 = st.columns(3)

            c1.markdown(
                f"**Current Status**<br><span style='color:{color};font-size:20px'>{passenger['currentStatusDetails']}</span>",
                unsafe_allow_html=True
            )

            c2.markdown(
                f"**Booking Status**<br>{passenger['bookingStatusDetails']}",
                unsafe_allow_html=True
            )

            c3.markdown(
                f"**Coach / Berth**<br>{passenger['currentCoachId']} - {passenger['currentBerthNo']}",
                unsafe_allow_html=True
            )

    # st.divider()

    # -----------------------------
    # JSON VIEW
    # -----------------------------

    # with st.expander("🔍 View Raw JSON"): ## this is for developer.

    #     st.json(data)

# -----------------------------
# FOOTER
# -----------------------------

st.markdown("---")

st.markdown(
"""
<div style="text-align:center">

Made with 🪄 using

<b>Python</b> • <b>Streamlit</b> • <b>RapidAPI</b>

</div>
""",
unsafe_allow_html=True
)