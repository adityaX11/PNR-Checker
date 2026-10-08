import os
from datetime import date, timedelta
import streamlit as st
import pandas as pd

from api import (
    get_pnr_status,
    get_trains_between_stations,
    get_train_fare,
)
from utils import (
    status_color,
    status_icon,
    validate_pnr,
    chart_badge,
    format_currency,
    passenger_dataframe,
    passenger_summary,
    generate_official_slip_html,
    trains_to_dataframe,
    load_all_stations,
)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="RailStatus | Indian Railway PNR & All-India Train Search",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# LOAD CSS (Glassmorphism & Responsive)
# -----------------------------
try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    if os.path.exists("assets/train.png"):
        st.image("assets/train.png", width=90)

    st.markdown("### 🚆 **RailStatus Portal**")
    st.caption("Live IRCTC Services Dashboard")

    st.markdown("---")

    st.markdown(
        """
        <div class="sidebar-badge">
            <span style="color:#94A3B8;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Developer</span><br>
            <strong style="color:#F8FAFC;font-size:1.05rem;">Aditya Kumar</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-badge">
            <span style="color:#94A3B8;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Stations Database</span><br>
            <span style="color:#34D399;font-size:0.9rem;font-weight:600;">8,989+ All-India Stations</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-badge">
            <span style="color:#94A3B8;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Tech Stack</span><br>
            <span style="color:#CBD5E1;font-size:0.9rem;">Python • Streamlit • RapidAPI • Pandas</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-badge">
            <span style="color:#94A3B8;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">License</span><br>
            <span style="color:#10B981;font-size:0.9rem;font-weight:600;">MIT Open Source</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.info(
        "💡 **Fare Lookup:** Click 'Check Fare Prices' under any train to see real-time Sleeper, 3rd AC, 2nd AC, and 1st AC ticket fares!"
    )


# -----------------------------
# HERO / HEADER SECTION
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; padding: 1.2rem 0 0.8rem 0;">
        <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(59,130,246,0.12); border:1px solid rgba(59,130,246,0.3); padding:6px 16px; border-radius:9999px; margin-bottom:12px;">
            <span style="font-size:0.85rem; color:#60A5FA; font-weight:600;">⚡ All-India Real-Time Railway Hub</span>
        </div>
        <h1 style="font-size: clamp(1.8rem, 4vw, 2.8rem); font-weight:800; background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 8px 0;">
            RailStatus Navigator
        </h1>
        <p style="color:#94A3B8; font-size: clamp(0.95rem, 2vw, 1.15rem); max-width:660px; margin: 0 auto;">
            Check live IRCTC PNR status, download official TTE verification slips, search trains across 8,900+ stations in India, and view berth fares.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# MAIN APP NAVIGATION TABS
# -----------------------------
tab_pnr, tab_trains = st.tabs(["🎫 Check PNR Status", "🚉 Trains Between Stations & Fare Calculator"])


# =============================================================================
# TAB 1: PNR STATUS CHECKER & DOWNLOAD VERIFICATION SLIP
# =============================================================================
with tab_pnr:
    st.markdown("#### Enter 10-Digit PNR Number")

    search_container = st.container()
    with search_container:
        c_input, c_btn = st.columns([4, 1.2], gap="small")

        with c_input:
            pnr_input = st.text_input(
                "PNR Number",
                placeholder="Enter 10-digit PNR Number (e.g. 6833824029)",
                max_chars=10,
                label_visibility="collapsed",
                key="pnr_field",
            )

        with c_btn:
            pnr_searched = st.button("Check Status 🔍", use_container_width=True, key="pnr_search_button")

    if pnr_searched:
        clean_pnr = pnr_input.strip()

        if not validate_pnr(clean_pnr):
            st.error("⚠️ Please enter a valid 10-digit numerical PNR number.")
            st.stop()

        with st.spinner("Connecting to Railway servers & fetching live PNR details..."):
            data, err = get_pnr_status(clean_pnr)

        if err:
            st.error(f"❌ {err}")
            st.stop()

        if not data or not isinstance(data, dict):
            st.warning("⚠️ No data returned for this PNR. Please double-check the number or try again later.")
            st.stop()

        st.session_state["current_pnr_data"] = data

    # Render results if available in session state
    if "current_pnr_data" in st.session_state:
        data = st.session_state["current_pnr_data"]
        chart_info = chart_badge(data.get("chartStatus", ""))
        passengers = data.get("passengerList", [])
        summary = passenger_summary(passengers)
        pnr_val = data.get("pnrNumber", "PNR")

        st.markdown("---")

        # Top row: Status Banner & Download Button
        banner_col, download_col = st.columns([3, 1.4], gap="medium")

        with banner_col:
            if summary["CNF"] > 0 and summary["WL"] == 0 and summary["RAC"] == 0:
                st.success(f"🎉 **All Seats Confirmed!** ({summary['CNF']} Confirmed) • {chart_info}")
            elif summary["RAC"] > 0:
                st.info(f"ℹ️ **RAC Booking**: Reservation Against Cancellation • {chart_info}")
            elif summary["WL"] > 0:
                st.warning(f"⏳ **Waitlist Status**: {summary['WL']} Passenger(s) in Waitlist • {chart_info}")
            else:
                st.success(f"Status Retrieved • {chart_info}")

        with download_col:
            slip_html = generate_official_slip_html(data)
            st.download_button(
                label="📥 Download Official Verification Slip",
                data=slip_html,
                file_name=f"RailStatus_Verification_PNR_{pnr_val}.html",
                mime="text/html",
                use_container_width=True,
                help="Official printer-friendly PRS slip formatted for inspection by TTE / Railway checking officials.",
            )

        # KEY METRICS
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("PNR Number", pnr_val)
        m2.metric("Train Number", data.get("trainNumber", "-"))
        m3.metric("Class / Quota", f"{data.get('journeyClass', '-')} ({data.get('quota', '-')})")
        m4.metric("Booking Fare", format_currency(data.get("bookingFare", "-")))

        st.write("")

        # JOURNEY DETAILS
        st.markdown("### 🚉 **Journey Overview**")
        j_col1, j_col2 = st.columns(2, gap="medium")

        with j_col1:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="journey-item">
                        <span class="journey-label">🚆 Train Name</span>
                        <span class="journey-value">{data.get('trainName', '-')}</span>
                    </div>
                    <div class="journey-item">
                        <span class="journey-label">🚩 Source Station</span>
                        <span class="journey-value">{data.get('sourceStation', '-')}</span>
                    </div>
                    <div class="journey-item">
                        <span class="journey-label">📍 Boarding Point</span>
                        <span class="journey-value">{data.get('boardingPoint', '-')}</span>
                    </div>
                    <div class="journey-item">
                        <span class="journey-label">📅 Date of Journey</span>
                        <span class="journey-value">{data.get('dateOfJourney', '-')}</span>
                    </div>
                    <div class="journey-item">
                        <span class="journey-label">📝 Booking Date</span>
                        <span class="journey-value">{data.get('bookingDate', '-')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with j_col2:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="journey-item">
                        <span class="journey-label">🏁 Destination Station</span>
                        <span class="journey-value">{data.get('destinationStation', '-')}</span>
                    </div>
                    <div class="journey-item">
                        <span class="journey-label">🎯 Reservation Upto</span>
                        <span class="journey-value">{data.get('reservationUpto', '-')}</span>
                    </div>
                    <div class="journey-item">
                        <span class="journey-label">⏰ Arrival Date</span>
                        <span class="journey-value">{data.get('arrivalDate', '-')}</span>
                    </div>
                    <div class="journey-item">
                        <span class="journey-label">📋 Chart Status</span>
                        <span class="journey-value">{data.get('chartStatus', '-')}</span>
                    </div>
                    <div class="journey-item">
                        <span class="journey-label">👥 Total Passengers</span>
                        <span class="journey-value">{data.get('numberOfpassenger', len(passengers))}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        # PASSENGER SUMMARY CARDS
        st.markdown("### 🧍 **Passenger Breakdown**")
        if passengers:
            card_cols = st.columns(min(len(passengers), 3) if len(passengers) > 0 else 1)

            for idx, passenger in enumerate(passengers):
                col_target = card_cols[idx % len(card_cols)]
                curr_st = passenger.get("currentStatus", "")
                curr_details = passenger.get("currentStatusDetails", curr_st) or "-"
                book_details = passenger.get("bookingStatusDetails", "-") or "-"
                coach = passenger.get("currentCoachId", "-") or "-"
                berth = passenger.get("currentBerthNo", "-") or "-"
                col = status_color(curr_st)
                icon = status_icon(curr_st)

                with col_target:
                    st.markdown(
                        f"""
                        <div class="glass-card" style="margin-bottom: 12px; border-left: 4px solid {col};">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <span style="font-weight:700; font-size:1.05rem;">Passenger {passenger.get('passengerSerialNumber', idx + 1)}</span>
                                <span style="font-size:1.1rem;">{icon}</span>
                            </div>
                            <div style="margin: 6px 0;">
                                <span style="color:#94A3B8; font-size:0.8rem; text-transform:uppercase;">Current Status</span>
                                <div style="color:{col}; font-weight:700; font-size:1.15rem; font-family:var(--font-mono);">{curr_details}</div>
                            </div>
                            <div style="margin: 6px 0;">
                                <span style="color:#94A3B8; font-size:0.8rem; text-transform:uppercase;">Booking Status</span>
                                <div style="color:#E2E8F0; font-size:0.95rem;">{book_details}</div>
                            </div>
                            <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.06); display:flex; justify-content:space-between;">
                                <span><b style="color:#94A3B8;">Coach:</b> {coach}</span>
                                <span><b style="color:#94A3B8;">Berth:</b> {berth}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with st.expander("📊 View Passenger Details Table", expanded=False):
                df_pass = passenger_dataframe(passengers)
                st.dataframe(df_pass, use_container_width=True, hide_index=True)


# =============================================================================
# TAB 2: TRAINS BETWEEN STATIONS & BERTH FARE PRICES (ALL INDIA 8,900+ STATIONS)
# =============================================================================
with tab_trains:
    st.markdown("#### 🔍 Search Any Station in India (8,900+ Stations Database)")
    st.caption("Search by city name, junction name, or railway station code (e.g. New Delhi, Patna, Bangalore, NDLS, PNBE)")

    # Load complete dictionary of all Indian stations
    all_stations_dict = load_all_stations()
    station_display_list = list(all_stations_dict.keys())

    # Find sensible defaults
    default_from_code = "NDLS"
    default_to_code = "PNBE"

    from_default_index = 0
    to_default_index = 1

    for idx, name in enumerate(station_display_list):
        if "(NDLS)" in name:
            from_default_index = idx
        elif "(PNBE)" in name:
            to_default_index = idx

    s1, s2, s3, s4 = st.columns([2.8, 2.8, 2, 1.4], gap="small")

    with s1:
        chosen_from = st.selectbox(
            "Origin Station (From)",
            options=station_display_list,
            index=from_default_index,
            help="Type to search any of 8,900+ stations across India",
        )
        origin_code = all_stations_dict[chosen_from]

    with s2:
        chosen_to = st.selectbox(
            "Destination Station (To)",
            options=station_display_list,
            index=to_default_index,
            help="Type to search any of 8,900+ stations across India",
        )
        destination_code = all_stations_dict[chosen_to]

    with s3:
        journey_date_val = st.date_input(
            "Travel Date",
            value=date.today() + timedelta(days=1),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=120),
        )

    with s4:
        st.write("")
        st.write("")
        search_trains_btn = st.button("Search Trains 🚆", use_container_width=True, key="search_trains_main_btn")

    if search_trains_btn:
        if origin_code == destination_code:
            st.error("⚠️ Origin and Destination cannot be the same station!")
            st.stop()

        formatted_journey_date = journey_date_val.strftime("%Y-%m-%d")

        with st.spinner(f"Querying all direct trains from {chosen_from} to {chosen_to} on {journey_date_val.strftime('%d %b %Y')}..."):
            train_results, t_err = get_trains_between_stations(origin_code, destination_code, formatted_journey_date)

        if t_err:
            st.error(f"❌ {t_err}")
            st.stop()

        st.session_state["train_search_results"] = {
            "trains": train_results,
            "origin_name": chosen_from,
            "origin_code": origin_code,
            "dest_name": chosen_to,
            "dest_code": destination_code,
            "date": journey_date_val.strftime("%d %b %Y"),
        }

    # Display Train Results & Fare Price Checkers
    if "train_search_results" in st.session_state:
        res = st.session_state["train_search_results"]
        trains = res["trains"]
        orig_code = res["origin_code"]
        dst_code = res["dest_code"]

        st.markdown("---")
        st.markdown(
            f"### 🚆 Available Trains: **{res['origin_name']} &rarr; {res['dest_name']}** on **{res['date']}** "
            f"<span style='color:#60A5FA; font-size:1.1rem;'>({len(trains)} trains found)</span>",
            unsafe_allow_html=True,
        )

        if not trains:
            st.warning("No direct trains found for this route on the selected date. Please check alternate stations or dates.")
        else:
            view_mode = st.radio(
                "Display View:",
                ["Card View (with Fare Calculator)", "Table View"],
                horizontal=True,
                label_visibility="collapsed",
            )

            if view_mode == "Table View":
                df_trains = trains_to_dataframe(trains)
                st.dataframe(df_trains, use_container_width=True, hide_index=True)
            else:
                for idx, t in enumerate(trains):
                    t_num = t.get("train_number", "-")
                    t_name = t.get("train_name", "-")
                    f_name = t.get("from_station_name", orig_code)
                    t_dst_name = t.get("to_station_name", dst_code)
                    dep = t.get("from_std", "-")
                    arr = t.get("to_sta", "-")
                    duration = t.get("duration", "-")
                    classes = t.get("class_type", [])
                    run_days = t.get("run_days", [])

                    class_badges_html = "".join([f"<span class='badge-class'>{c}</span>" for c in classes])
                    days_text = " • ".join(run_days) if isinstance(run_days, list) else "-"

                    st.markdown(
                        f"""
                        <div class="train-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                                <div>
                                    <span style="font-weight:800; font-size:1.15rem; color:#FFFFFF;">{t_name}</span>
                                    <span style="background:rgba(59,130,246,0.25); color:#60A5FA; padding:2px 8px; border-radius:6px; font-family:var(--font-mono); font-size:0.85rem; font-weight:700; margin-left:8px;">#{t_num}</span>
                                </div>
                                <div>
                                    <span style="color:#94A3B8; font-size:0.85rem;">Runs: </span>
                                    <span style="color:#34D399; font-weight:600; font-size:0.85rem;">{days_text}</span>
                                </div>
                            </div>
                            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:12px; margin-top:14px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.06);">
                                <div>
                                    <div style="color:#94A3B8; font-size:0.75rem; text-transform:uppercase;">Departure</div>
                                    <div style="font-weight:700; font-size:1.1rem; color:#F8FAFC;">{dep}</div>
                                    <div style="font-size:0.82rem; color:#CBD5E1;">{f_name}</div>
                                </div>
                                <div>
                                    <div style="color:#94A3B8; font-size:0.75rem; text-transform:uppercase;">Duration</div>
                                    <div style="font-weight:700; font-size:1.05rem; color:#60A5FA;">⏱ {duration}</div>
                                </div>
                                <div>
                                    <div style="color:#94A3B8; font-size:0.75rem; text-transform:uppercase;">Arrival</div>
                                    <div style="font-weight:700; font-size:1.1rem; color:#F8FAFC;">{arr}</div>
                                    <div style="font-size:0.82rem; color:#CBD5E1;">{t_dst_name}</div>
                                </div>
                                <div>
                                    <div style="color:#94A3B8; font-size:0.75rem; text-transform:uppercase; margin-bottom:4px;">Classes Available</div>
                                    <div>{class_badges_html if class_badges_html else '<span style=\"color:#94A3B8;\">-</span>'}</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Interactive Berth & Class Fare Expander
                    with st.expander(f"💰 View Berth Fares for Train #{t_num} ({t_name})"):
                        fare_btn_key = f"fetch_fare_{t_num}_{idx}"
                        if st.button("Check Live Ticket Prices 🎫", key=fare_btn_key):
                            with st.spinner(f"Fetching official fare breakdown for #{t_num}..."):
                                fare_list, f_err = get_train_fare(t_num, orig_code, dst_code)
                            st.session_state[f"fare_data_{t_num}"] = (fare_list, f_err)

                        if f"fare_data_{t_num}" in st.session_state:
                            f_data, f_error = st.session_state[f"fare_data_{t_num}"]
                            if f_error:
                                st.warning(f"Could not load fare details: {f_error}")
                            elif f_data:
                                fare_cols = st.columns(min(len(f_data), 5) if len(f_data) > 0 else 1)
                                for c_idx, c_item in enumerate(f_data):
                                    c_target = fare_cols[c_idx % len(fare_cols)]
                                    c_name = c_item.get("class_name", c_item.get("class_type", "-"))
                                    c_type = c_item.get("class_type", "")
                                    c_fare = c_item.get("fare", 0)

                                    with c_target:
                                        st.markdown(
                                            f"""
                                            <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:10px 14px; text-align:center;">
                                                <div style="color:#94A3B8; font-size:0.75rem; font-weight:600; text-transform:uppercase;">{c_name} ({c_type})</div>
                                                <div style="color:#34D399; font-weight:800; font-size:1.35rem; font-family:var(--font-mono); margin-top:4px;">
                                                    {f'₹{c_fare}' if c_fare > 0 else 'N/A'}
                                                </div>
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                        )
                            else:
                                st.info("No fare information available for this train.")


# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; padding: 1rem 0; color:#94A3B8; font-size:0.9rem;">
        Developed by <b>Aditya Kumar</b> • Powered by <b>Python</b> & <b>Streamlit</b> • Open Source (MIT)
    </div>
    """,
    unsafe_allow_html=True,
)