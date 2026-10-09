# CivicPulse 🏙️
### Making Invisible Problems Visible – Sustainable Cities & Communities (UN SDG 11)

CivicPulse is an intelligent civic reporting platform designed to empower citizens in rural villages, towns, and tier-2/3 cities to report and track invisible, overlooked infrastructure breakdown (such as deep potholes, water pipeline bursts, uncollected garbage piles, broken streetlights, and live wire hazards).

---

## ✨ Features & Highlights

- 📸 **Citizen Problem Reporting & AI Classifier Mode**:
  - Image upload dropzone with immediate preview.
  - Modular AI vision analysis mode suggesting problem categories with confidence ratings.

- 🧮 **Rule-Based Severity Assessment Engine**:
  - Evaluates physical safety hazards, visible damage extent, and location context (main road vs public facility) to calculate transparent Low, Medium, High, or Critical severity levels.

- 🗺️ **Interactive Geographic Leaflet Map Explorer**:
  - Real-time map pins color-coded by severity level.
  - Dynamically synchronized search and filter controls (by Category, District, Severity, Status, or Real vs Demo Data).
  - Built-in GPS device geolocation auto-detector for instant coordinate capture.

- 🏛️ **Verified Public Authority Contact Directory**:
  - Mapped directory of **47+ verified official government department offices** across Andhra Pradesh, Telangana, Karnataka, Uttar Pradesh, Madhya Pradesh, West Bengal, Delhi NCR, Tamil Nadu, and Maharashtra.
  - Complete with direct officer designations, phone numbers, official emails, physical postal addresses, and Google Maps direction links.
  - Integrated 24x7 National & State Emergency Helpline counters (`1912` Power, `112` Emergency, `1969` Swachh Bharat, `1033` Highways).

- 📊 **Dynamic Civic Analytics Dashboard**:
  - Real-time Chart.js visual analytics for category breakdown, resolution statuses, severity distribution, and district heatmaps.

- 🛡️ **Jury Administrative Console**:
  - Authenticated admin panel to manage report lifecycle statuses (`Reported` → `Under Review` → `In Progress` → `Resolved`) and add new verified local authority contacts.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask framework
- **Database**: SQLite 3
- **Frontend**: HTML5, Vanilla CSS3 (Custom Modern Design System), Javascript (ES6+)
- **Mapping & Visualizations**: Leaflet.js, OpenStreetMap, Chart.js, FontAwesome 6

---

## 🚀 Quick Start Guide

### 1. Clone the repository
```bash
git clone https://github.com/Vyshnavi-2912/CivicPulse.git
cd CivicPulse
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & seed database
```bash
python database/init_db.py
python database/seed_authorities.py
```

### 4. Run application server
```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 🔑 Jury Admin Console Login
- **URL**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)
- **Username**: `admin`
- **Password**: `civicpulse2026`

---

## 📜 License & SDG Alignment
Aligned with **United Nations Sustainable Development Goal 11**: *Make cities and human settlements inclusive, safe, resilient, and sustainable.*
