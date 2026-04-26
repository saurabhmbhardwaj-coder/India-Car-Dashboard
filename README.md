# 🚗 India Car Market Intelligence Dashboard

A real-time Streamlit dashboard for Indian automotive market research — built for consultants, strategists, and market researchers.

---

## 🔍 What It Does

| Feature | Details |
|---|---|
| **Segment → Brand → Model selector** | 6 segments, 13+ brands, 40+ models |
| **Live Ex-Showroom Price** | Scraped from CarDekho in real-time |
| **Monthly Sales Trend** | Jul 2024 – Mar 2025 wholesale dispatch data (SIAM/FADA/VAHAN) |
| **Expert Reviews** | Live snippets from AutoCar India, ZigWheels, Evo India, MotorOctane |
| **Competitor Analysis** | Volume comparison, market share donut, rival benchmarking |
| **Industry News** | Live RSS from ET Auto, AutoCar India, CarAndBike, ZigWheels, Team-BHP |

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/india-car-dashboard.git
cd india-car-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub (public or private)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select this repo → set **Main file**: `app.py`
4. Click **Deploy** — live in ~2 minutes ✅

---

## 📁 File Structure

```
india-car-dashboard/
├── app.py              ← entire app (single file)
├── requirements.txt    ← Python dependencies
└── README.md
```

---

## 📊 Data Sources

- **Sales data**: SIAM monthly wholesale dispatches + FADA retail registration data + VAHAN dashboard (compiled Jul 2024–Mar 2025)
- **Prices**: CarDekho live scrape (cached 1 hr)
- **Reviews**: Google search → AutoCar India, ZigWheels, Evo India, MotorOctane
- **News**: RSS feeds — ET Auto, AutoCar India, CarAndBike, ZigWheels, Team-BHP

> ⚠️ Sales figures are indicative wholesale dispatch data. Always validate against primary SIAM/FADA sources before strategic use.

---

## 🧩 Segments Covered

- Hatchback
- Sedan
- Compact SUV
- Mid & Large SUV
- MUV / MPV
- EV

---

## 🛠 Built With

- [Streamlit](https://streamlit.io) — UI framework
- [Plotly](https://plotly.com) — charts
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — web scraping
- [feedparser](https://feedparser.readthedocs.io) — RSS parsing
- [Pandas](https://pandas.pydata.org) — data tables

---

## 👤 Author

Built by [@saurabhmbhardwaj](https://www.linkedin.com/in/saurabhmbhardwaj/) as part of a market strategy and GTM consulting portfolio.

---

## ⚖️ Disclaimer

This tool is for research and educational purposes. Prices and sales figures are indicative. Always verify with primary sources (SIAM, FADA, VAHAN, OEM press releases) before making business decisions.
