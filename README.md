# 🚆 Indian Railway PNR Status & All-India Train Search Portal

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45%2B-FF4B4B?logo=streamlit&logoColor=white)
![Stations](https://img.shields.io/badge/Stations-8%2C989%2B-success)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=adityakumar.pnr-checker)

A modern, responsive, glassmorphic web application designed to check real-time Indian Railway (IRCTC) PNR reservation status, generate official verification slips for Railway inspection, search trains across **all 8,989+ Indian stations**, and calculate live berth ticket fares (Sleeper, 3AC, 2AC, 1AC).

---

## 🌟 Key Features

- **Live PNR Tracking**: Instant fetch of live booking and confirmation status, coach & berth allocations, and charting status.
- **Official PNR Verification Slip**: One-click download of a computer-generated, printer-friendly PRS verification slip for TTE / Railway ticket checking inspection.
- **All-India Station Coverage (8,989+ Stations)**: Complete nationwide station search across every junction, city, and halt station in India.
- **Trains Between Stations**: Search all available direct trains between any two stations with departure/arrival times, travel duration, running days, and coach classes.
- **Live Berth Price / Fare Calculator**: Instant fare breakdown for each train across classes including **Sleeper (SL)**, **Third AC (3A)**, **Second AC (2A)**, and **First AC (1A)**.
- **Automatic Key Rotation & Failover Pool**: Built-in support for multiple RapidAPI keys. If one key reaches rate limits (`HTTP 429`), the app automatically switches to the next available key without interrupting the user.
- **Smart Multi-Tier Caching**: High-efficiency TTL caching (12 hours for train routes, 6 hours for fares, 10 minutes for PNRs) reduces external API calls by over 75%.
- **Glassmorphic UI**: Sleek dark aesthetic with frosted-glass containers, luminous highlights, and fluid responsive design across mobile and desktop.
- **Visual Passenger Cards**: Color-coded badges for Confirmed (CNF), RAC, and Waitlist (WL) passengers.
- **Multi-View Modes**: Switch between sleek card view and comprehensive table view for train search results.

---

## 🛠 Tech Stack & Tools

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3 |
| **Frontend & UI Framework** | Streamlit |
| **Styling** | Custom Glassmorphic CSS3 (Backdrop-filter, Flexbox, CSS Grid) |
| **Data Handling** | Pandas & JSON |
| **Stations Database** | Datameet Indian Railways All-Stations Dataset (8,989+ Stations) |
| **Networking & HTTP** | Requests |
| **Data Provider** | RapidAPI (IRCTC Indian Railway APIs) |

---

## 🔑 RapidAPI Key Pool Setup

To prevent rate limit errors, you can provide multiple RapidAPI keys in `.streamlit/secrets.toml` or Streamlit Cloud Secrets:

```toml
# Provide a single key or multiple keys as a list:
RAPID_API_KEYS = [
    "YOUR_PRIMARY_RAPIDAPI_KEY",
    "YOUR_BACKUP_RAPIDAPI_KEY_2",
    "YOUR_BACKUP_RAPIDAPI_KEY_3"
]
```

Or as a comma-separated string:
```toml
RAPID_API_KEY = "KEY_1, KEY_2, KEY_3"
```

---

## 👨‍💻 Developer

- **Aditya Kumar**

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
