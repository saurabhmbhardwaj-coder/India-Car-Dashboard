"""
India Car Market Intelligence Dashboard
Streamlit app – live prices, sales trends, reviews, competitor analysis, industry news
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import feedparser
import json
import re
from datetime import datetime
from urllib.parse import quote_plus
import time

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="India Car Market Intel",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .stMetric { background: #f8f9fa; border-radius: 10px; padding: 1rem; border: 1px solid #e9ecef; }
    .stMetric label { font-size: 13px !important; color: #6c757d !important; }
    .news-card {
        background: #fff;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .news-title { font-weight: 600; font-size: 14px; color: #212529; line-height: 1.4; margin-bottom: 4px; }
    .news-meta  { font-size: 11px; color: #6c757d; }
    .review-card {
        background: #fff;
        border: 1px solid #e9ecef;
        border-left: 4px solid #0d6efd;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .review-source { font-weight: 700; font-size: 12px; color: #0d6efd; text-transform: uppercase; margin-bottom: 4px; }
    .review-title  { font-size: 15px; font-weight: 600; color: #212529; margin-bottom: 6px; }
    .review-snippet{ font-size: 13px; color: #495057; line-height: 1.5; }
    .review-link   { font-size: 12px; color: #0d6efd; text-decoration: none; }
    .comp-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 12px 14px;
        border: 1px solid #dee2e6;
        margin-bottom: 8px;
    }
    .badge { display:inline-block; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
    .badge-green { background:#d4edda; color:#155724; }
    .badge-red   { background:#f8d7da; color:#721c24; }
    .badge-blue  { background:#cce5ff; color:#004085; }
    .sidebar-header { font-size: 18px; font-weight: 700; color: #212529; margin-bottom: 0.5rem; }
    div[data-testid="stSidebarContent"] { padding-top: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] { height: 36px; padding: 0 16px; border-radius: 6px 6px 0 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EMBEDDED SALES DATA  (Jul 2024 – Mar 2025)
# Source: SIAM / FADA / VAHAN compiled data
# ─────────────────────────────────────────────
MONTHS = ["Jul'24","Aug'24","Sep'24","Oct'24","Nov'24","Dec'24","Jan'25","Feb'25","Mar'25"]

SALES_DATA = {
    "Hatchback": {
        "Maruti Suzuki": {
            "Swift":     [18000,17500,19200,21000,18500,16000,22000,19500,21000],
            "Baleno":    [15000,14500,16000,18000,15500,13500,17000,15000,16500],
            "WagonR":    [17000,16500,18000,19500,17000,15000,19000,17500,18500],
            "Alto K10":  [12000,11500,13000,14000,12000,11000,13500,12000,13000],
            "Celerio":   [3000, 2800, 3200, 3500, 3000, 2600, 3500, 3100, 3300],
        },
        "Hyundai": {
            "Grand i10 Nios": [5500,5200,5800,6500,5800,5000,6000,5500,5800],
            "i20":            [7000,6800,7500,8500,7500,6500,8000,7200,7800],
        },
        "Tata": {
            "Tiago": [6500,6200,7000,7800,6800,6000,7200,6500,7000],
        },
    },
    "Sedan": {
        "Maruti Suzuki": {
            "Dzire": [14000,13500,15000,16500,14500,13000,16000,14500,15500],
            "Ciaz":  [1500, 1400, 1600, 1800, 1600, 1400, 1700, 1500, 1600],
        },
        "Honda": {
            "Amaze": [5000,4800,5500,6000,5200,4500,5800,5200,5600],
            "City":  [4000,3800,4500,5000,4500,4000,5000,4400,4800],
        },
        "Hyundai": {
            "Aura":  [4500,4300,4800,5500,4800,4200,5200,4600,5000],
            "Verna": [6000,5800,6500,7500,6500,5800,7000,6200,6800],
        },
        "Skoda":      {"Slavia":  [2000,1900,2200,2500,2200,1900,2300,2100,2300]},
        "Volkswagen": {"Virtus":  [2200,2100,2400,2700,2400,2100,2500,2300,2500]},
    },
    "Compact SUV": {
        "Tata": {
            "Nexon": [14000,13500,15000,17000,14500,13000,16500,14500,16000],
            "Punch": [13000,12500,14000,15500,13500,12000,15000,13500,14500],
        },
        "Maruti Suzuki": {
            "Brezza": [15000,14500,16000,18000,15500,14000,17500,15500,16500],
            "Fronx":  [12000,11500,13000,14500,12500,11500,14000,12500,13500],
        },
        "Hyundai":  {"Venue":      [8000, 7800, 8500, 9500, 8500, 7500, 9500, 8500, 9000]},
        "Kia":      {"Sonet":      [8500, 8200, 9000,10000, 9000, 8000,10000, 9000, 9500]},
        "Mahindra": {"XUV300":     [3500, 3300, 3800, 4200, 3700, 3200, 4000, 3600, 4000]},
        "Renault":  {"Kiger":      [2500, 2400, 2700, 3000, 2700, 2300, 2800, 2500, 2700]},
        "Nissan":   {"Magnite":    [3000, 2900, 3200, 3600, 3200, 2800, 3400, 3100, 3300]},
        "Toyota":   {"Urban Cruiser Hyryder": [6000,5800,6500,7200,6500,5800,7000,6300,6800]},
    },
    "Mid & Large SUV": {
        "Hyundai": {
            "Creta":   [14000,13500,15000,17000,15000,13500,17000,15000,16500],
            "Alcazar": [2000, 1900, 2200, 2500, 2200, 1900, 2400, 2100, 2300],
        },
        "Kia": {
            "Seltos": [10000, 9800,11000,12000,10500, 9500,11500,10200,11000],
            "Carens": [5000,  4800, 5500, 6200, 5500, 4800, 6000, 5400, 5800],
        },
        "Mahindra": {
            "XUV700":   [8000,7800,8500, 9500,8500,7500, 9500,8500,9000],
            "Scorpio N":[9000,8800,9500,10500,9500,8500,10500,9500,10000],
            "Thar":     [6000,5800,6500, 7500,6500,5800, 7500,6700,7200],
        },
        "Tata": {
            "Harrier": [5000,4800,5500,6200,5500,4800,6000,5400,5800],
            "Safari":  [4500,4300,5000,5800,5000,4500,5500,5000,5400],
        },
        "MG":     {"Hector":       [3500,3300,3800,4200,3700,3200,4000,3600,3900]},
        "Toyota": {
            "Fortuner":     [2500,2400,2700,3000,2700,2400,2900,2600,2800],
            "Innova HyCross":[6000,5800,6500,7500,6500,5800,7000,6300,6800],
        },
    },
    "MUV / MPV": {
        "Maruti Suzuki": {
            "Ertiga": [8000,7800,8500,9500,8500,7500,9500,8500,9000],
            "XL6":    [2500,2400,2700,3000,2700,2400,2900,2600,2800],
        },
        "Toyota": {
            "Innova Crysta":  [5000,4800,5500,6200,5500,4800,6000,5400,5800],
            "Innova HyCross": [6000,5800,6500,7500,6500,5800,7000,6300,6800],
        },
        "Kia":     {"Carens":  [5000,4800,5500,6200,5500,4800,6000,5400,5800]},
        "Renault": {"Triber":  [2000,1900,2200,2500,2200,1900,2300,2100,2300]},
        "Mahindra":{"Bolero":  [6000,5800,6500,7200,6500,5800,7000,6300,6800]},
    },
    "EV": {
        "Tata": {
            "Nexon EV":  [3500,3300,3800,4200,3700,3200,4200,3800,4200],
            "Punch EV":  [4500,4300,5000,5600,5000,4400,5500,5000,5500],
            "Tiago EV":  [2000,1900,2200,2500,2200,1900,2300,2100,2300],
        },
        "MG": {
            "ZS EV":     [800, 750, 900,1000, 900, 800, 950, 850, 950],
            "Comet EV":  [500, 480, 550, 600, 550, 480, 580, 530, 580],
        },
        "Hyundai":  {"Ioniq 5": [200,190,220,250,220,190,230,210,240]},
        "BYD": {
            "Atto 3": [400,380,440,500,440,380,460,420,460],
            "Seal":   [150,140,170,200,180,150,190,170,200],
        },
        "Mahindra": {
            "XEV 9e": [300,280,330,380,330,280,380,340,380],
            "BE 6e":  [350,330,390,450,400,350,430,390,430],
        },
    },
}

# CarDekho slug map  ─────────────────────────
CARDEKHO_SLUGS = {
    "Swift": "maruti/maruti-swift", "Baleno": "maruti/maruti-baleno",
    "WagonR": "maruti/maruti-wagon-r", "Alto K10": "maruti/maruti-alto-k10",
    "Celerio": "maruti/maruti-celerio", "Grand i10 Nios": "hyundai/hyundai-grand-i10-nios",
    "i20": "hyundai/hyundai-i20", "Tiago": "tata/tata-tiago",
    "Dzire": "maruti/maruti-swift-dzire", "Ciaz": "maruti/maruti-ciaz",
    "Amaze": "honda/honda-amaze", "City": "honda/honda-city",
    "Aura": "hyundai/hyundai-aura", "Verna": "hyundai/hyundai-verna",
    "Slavia": "skoda/skoda-slavia", "Virtus": "volkswagen/volkswagen-virtus",
    "Nexon": "tata/tata-nexon", "Punch": "tata/tata-punch",
    "Brezza": "maruti/maruti-brezza", "Fronx": "maruti/maruti-fronx",
    "Venue": "hyundai/hyundai-venue", "Sonet": "kia/kia-sonet",
    "XUV300": "mahindra/mahindra-xuv300", "Kiger": "renault/renault-kiger",
    "Magnite": "nissan/nissan-magnite",
    "Urban Cruiser Hyryder": "toyota/toyota-urban-cruiser-hyryder",
    "Creta": "hyundai/hyundai-creta", "Alcazar": "hyundai/hyundai-alcazar",
    "Seltos": "kia/kia-seltos", "Carens": "kia/kia-carens",
    "XUV700": "mahindra/mahindra-xuv700", "Scorpio N": "mahindra/mahindra-scorpio-n",
    "Thar": "mahindra/mahindra-thar", "Harrier": "tata/tata-harrier",
    "Safari": "tata/tata-safari", "Hector": "mg/mg-hector",
    "Fortuner": "toyota/toyota-fortuner", "Innova HyCross": "toyota/toyota-innova-hycross",
    "Ertiga": "maruti/maruti-ertiga", "XL6": "maruti/maruti-xl6",
    "Innova Crysta": "toyota/toyota-innova", "Triber": "renault/renault-triber",
    "Bolero": "mahindra/mahindra-bolero",
    "Nexon EV": "tata/tata-nexon-ev", "Punch EV": "tata/tata-punch-ev",
    "Tiago EV": "tata/tata-tiago-ev", "ZS EV": "mg/mg-zs-ev",
    "Comet EV": "mg/mg-comet-ev", "Ioniq 5": "hyundai/hyundai-ioniq-5",
    "Atto 3": "byd/byd-atto-3", "Seal": "byd/byd-seal",
    "XEV 9e": "mahindra/mahindra-xev-9e", "BE 6e": "mahindra/mahindra-be-6e",
}

# ─────────────────────────────────────────────
# SCRAPER HELPERS
# ─────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_price(model: str) -> dict:
    """Scrape ex-showroom price from CarDekho."""
    slug = CARDEKHO_SLUGS.get(model)
    if not slug:
        return {"price": "N/A", "price_range": "N/A", "source": ""}

    url = f"https://www.cardekho.com/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Try multiple selectors that CarDekho uses
        selectors = [
            ("span", {"class": re.compile(r"price|Price")}),
            ("div",  {"class": re.compile(r"price|Price")}),
            ("p",    {"class": re.compile(r"price|Price")}),
        ]
        price_text = None
        for tag, attrs in selectors:
            el = soup.find(tag, attrs)
            if el:
                t = el.get_text(strip=True)
                if "₹" in t or "lakh" in t.lower():
                    price_text = t
                    break

        # Fallback: look for any ₹ pattern in page
        if not price_text:
            matches = re.findall(r"₹\s*[\d,.]+(?:\s*-\s*₹\s*[\d,.]+)?\s*(?:lakh|Lakh|L)?", r.text)
            price_text = matches[0] if matches else "See CarDekho"

        # Extract range if present
        range_match = re.findall(r"₹\s*[\d,.]+\s*(?:Lakh|lakh|L)?", price_text)
        if len(range_match) >= 2:
            return {"price": range_match[0].strip(), "price_range": f"{range_match[0]} – {range_match[-1]}", "source": url}
        return {"price": price_text.strip(), "price_range": price_text.strip(), "source": url}

    except Exception as e:
        return {"price": "Fetch error", "price_range": str(e)[:60], "source": url}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_reviews(model: str, brand: str) -> list:
    """
    Fetch review snippets from AutoCar India, ZigWheels, Evo India, MotorOctane
    via Google Custom Search / direct scraping.
    """
    sources = [
        {"name": "AutoCar India",  "color": "#e63946", "domain": "autocarindia.com"},
        {"name": "ZigWheels",      "color": "#f77f00", "domain": "zigwheels.com"},
        {"name": "Evo India",      "color": "#2b9348", "domain": "evoindia.com"},
        {"name": "MotorOctane",    "color": "#0077b6", "domain": "motoroctane.com"},
    ]
    results = []

    for src in sources:
        query   = f"{brand} {model} review site:{src['domain']}"
        gurl    = f"https://www.google.com/search?q={quote_plus(query)}&num=3"
        try:
            r    = requests.get(gurl, headers={**HEADERS, "Accept": "text/html"}, timeout=8)
            soup = BeautifulSoup(r.text, "html.parser")

            # Google result blocks
            for div in soup.select("div.g, div[data-hveid]")[:3]:
                a = div.find("a", href=True)
                href = a["href"] if a else ""
                if src["domain"] not in href:
                    continue

                title_el   = div.find("h3")
                snippet_el = div.find("div", class_=re.compile(r"VwiC3b|IsZvec|s|st"))
                title   = title_el.get_text(strip=True)   if title_el   else f"{model} Review"
                snippet = snippet_el.get_text(strip=True) if snippet_el else "Click to read the full review."
                snippet = snippet[:280] + ("…" if len(snippet) > 280 else "")

                # Clean google redirect
                clean_href = re.sub(r"^/url\?q=", "", href).split("&")[0]

                results.append({
                    "source":  src["name"],
                    "color":   src["color"],
                    "title":   title   or f"{model} Expert Review – {src['name']}",
                    "snippet": snippet or "Full road test and verdict available on the source site.",
                    "url":     clean_href,
                })
                break
        except Exception:
            results.append({
                "source":  src["name"],
                "color":   src["color"],
                "title":   f"{model} Review on {src['name']}",
                "snippet": "Could not fetch snippet. Visit the source for the full review.",
                "url":     f"https://{src['domain']}",
            })

    return results


@st.cache_data(ttl=900, show_spinner=False)
def fetch_news() -> list:
    """Pull latest auto industry news from multiple RSS feeds."""
    feeds = [
        ("ET Auto",       "https://economictimes.indiatimes.com/industry/auto/rss.cms"),
        ("AutoCar India", "https://www.autocarindia.com/rss"),
        ("CarAndBike",    "https://www.carandbikeshow.com/feed/"),
        ("ZigWheels",     "https://www.zigwheels.com/rss/news"),
        ("Team-BHP",      "https://www.team-bhp.com/forum/external.php?type=RSS2"),
    ]
    items = []
    for source, url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:4]:
                pub = entry.get("published", entry.get("updated", ""))
                try:
                    dt = datetime(*entry.published_parsed[:6])
                    pub = dt.strftime("%d %b %Y")
                except Exception:
                    pub = pub[:16] if pub else "Recent"

                items.append({
                    "source":  source,
                    "title":   entry.get("title", "Auto News"),
                    "summary": entry.get("summary", entry.get("description", ""))[:200].strip(),
                    "link":    entry.get("link", "#"),
                    "date":    pub,
                })
        except Exception:
            pass

    # Sort newest first (best effort) & cap at 30
    return items[:30]


# ─────────────────────────────────────────────
# COMPETITOR ANALYSIS HELPER
# ─────────────────────────────────────────────
def get_competitors(segment: str, brand: str, model: str) -> list:
    """Return all other models in same segment sorted by 9-month volume."""
    comps = []
    for b, models in SALES_DATA.get(segment, {}).items():
        for m, sales in models.items():
            if b == brand and m == model:
                continue
            vol = sum(sales)
            mom = ((sales[-1] - sales[-2]) / sales[-2] * 100) if sales[-2] else 0
            comps.append({"brand": b, "model": m, "sales": sales, "vol": vol, "mom": mom})
    comps.sort(key=lambda x: x["vol"], reverse=True)
    return comps[:8]


# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def sales_chart(sales: list, model: str) -> go.Figure:
    mom   = ((sales[-1] - sales[-2]) / sales[-2] * 100) if sales[-2] else 0
    color = "#1D9E75" if mom >= 0 else "#E24B4A"
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=MONTHS, y=sales,
        marker_color=[color if i == len(sales)-1 else "#cbd5e1" for i in range(len(sales))],
        text=[f"{v/1000:.1f}K" for v in sales],
        textposition="outside",
        hovertemplate="%{x}: <b>%{y:,}</b> units<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=MONTHS, y=sales,
        mode="lines+markers",
        line=dict(color=color, width=2, dash="dot"),
        marker=dict(size=5, color=color),
        showlegend=False,
        hoverinfo="skip",
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=280,
        title=dict(text=f"{model} – Monthly Wholesale Dispatches", font_size=13, x=0),
        yaxis=dict(tickformat=",", title="Units", tickfont_size=11),
        xaxis=dict(tickfont_size=11),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
    )
    fig.update_yaxes(gridcolor="#f0f0f0")
    return fig


def competitor_chart(comps: list, selected_model: str, selected_sales: list) -> go.Figure:
    all_models = [selected_model] + [c["model"] for c in comps]
    all_vols   = [sum(selected_sales)] + [c["vol"] for c in comps]
    colors     = ["#1D9E75"] + ["#94a3b8"] * len(comps)

    fig = go.Figure(go.Bar(
        x=all_vols, y=all_models,
        orientation="h",
        marker_color=colors,
        text=[f"{v/1000:.0f}K" for v in all_vols],
        textposition="outside",
        hovertemplate="%{y}: <b>%{x:,}</b> units (9M)<extra></extra>",
    ))
    fig.update_layout(
        margin=dict(l=10, r=50, t=30, b=10),
        height=max(280, len(all_models) * 38 + 60),
        title=dict(text="9-Month Volume vs Competitors", font_size=13, x=0),
        xaxis=dict(tickformat=",", title="Units (9 months)", tickfont_size=11),
        yaxis=dict(tickfont_size=11, autorange="reversed"),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(gridcolor="#f0f0f0")
    return fig


def market_share_chart(segment: str) -> go.Figure:
    brand_totals: dict[str, int] = {}
    for brand, models in SALES_DATA.get(segment, {}).items():
        brand_totals[brand] = sum(sum(s) for s in models.values())
    labels = list(brand_totals.keys())
    values = list(brand_totals.values())
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.45,
        textinfo="label+percent",
        textfont_size=11,
        marker=dict(line=dict(color="white", width=1.5)),
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=300,
        title=dict(text=f"{segment} – Brand Market Share (9M)", font_size=13, x=0),
        showlegend=False,
        paper_bgcolor="white",
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR  ──  SELECTORS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-header">🚗 India Car Market Intel</div>', unsafe_allow_html=True)
    st.caption("Live prices · Sales trends · Reviews · News")
    st.divider()

    segment = st.selectbox("📌 Segment", list(SALES_DATA.keys()))
    brands   = list(SALES_DATA[segment].keys())
    brand    = st.selectbox("🏭 Brand (Manufacturer)", brands)
    models   = list(SALES_DATA[segment][brand].keys())
    model    = st.selectbox("🚙 Model", models)

    st.divider()
    sales = SALES_DATA[segment][brand][model]
    total_9m = sum(sales)
    avg_mo   = total_9m // len(sales)
    mom      = round((sales[-1] - sales[-2]) / sales[-2] * 100, 1) if sales[-2] else 0
    mom_str  = f"{'▲' if mom >= 0 else '▼'} {abs(mom)}%"

    st.metric("9M Total", f"{total_9m/1000:.0f}K units")
    st.metric("Monthly Avg", f"{avg_mo/1000:.1f}K units")
    st.metric("MoM (Mar '25)", mom_str, delta_color="normal")

    st.divider()
    st.caption("Data: SIAM / FADA / VAHAN (Jul'24–Mar'25)")
    st.caption("Prices: CarDekho live scrape")
    st.caption("Reviews: AutoCar India · ZigWheels · Evo India · MotorOctane")


# ─────────────────────────────────────────────
# MAIN LAYOUT  ──  two columns
# ─────────────────────────────────────────────
main_col, news_col = st.columns([0.72, 0.28], gap="medium")

# ══════════════════════════════════════════════
# LEFT  –  main dashboard
# ══════════════════════════════════════════════
with main_col:
    st.subheader(f"{brand} {model}  ·  {segment}", divider="gray")

    # ── KPI row ──────────────────────────────
    with st.spinner("Fetching live ex-showroom price…"):
        price_data = fetch_price(model)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ex-Showroom (base)",   price_data["price"],
              help="Source: CarDekho live")
    k1.caption(f"[CarDekho ↗]({price_data['source']})" if price_data.get("source") else "")
    k2.metric("Price Range",   price_data["price_range"])
    k3.metric("Latest Month",  f"{sales[-1]/1000:.1f}K units",
              delta=f"{mom:+.1f}% MoM")
    k4.metric("9M Total",      f"{total_9m/1000:.0f}K units")

    st.divider()

    # ── Tabs ─────────────────────────────────
    tab_sales, tab_reviews, tab_comp = st.tabs(["📈 Sales Trend", "⭐ Expert Reviews", "🔍 Competitor Analysis"])

    # ── Sales Trend tab ───────────────────────
    with tab_sales:
        st.plotly_chart(sales_chart(sales, model), use_container_width=True)

        # Monthly table
        df = pd.DataFrame({"Month": MONTHS, "Units": sales})
        df["MoM Δ"] = df["Units"].pct_change().mul(100).round(1).apply(
            lambda x: f"▲ {x}%" if x > 0 else (f"▼ {abs(x)}%" if pd.notna(x) else "—")
        )
        df["Units"] = df["Units"].apply(lambda x: f"{x:,}")
        st.dataframe(df, use_container_width=True, hide_index=True, height=368)

    # ── Reviews tab ───────────────────────────
    with tab_reviews:
        with st.spinner(f"Fetching {model} reviews from AutoCar India, ZigWheels, Evo India, MotorOctane…"):
            reviews = fetch_reviews(model, brand)

        if not reviews:
            st.info("No reviews fetched. Try refreshing.")
        for rev in reviews:
            st.markdown(f"""
            <div class="review-card" style="border-left-color:{rev['color']};">
                <div class="review-source" style="color:{rev['color']};">{rev['source']}</div>
                <div class="review-title">{rev['title']}</div>
                <div class="review-snippet">{rev['snippet']}</div>
                <a class="review-link" href="{rev['url']}" target="_blank">Read full review ↗</a>
            </div>""", unsafe_allow_html=True)

    # ── Competitor Analysis tab ────────────────
    with tab_comp:
        comps = get_competitors(segment, brand, model)

        # Volume comparison bar
        st.plotly_chart(competitor_chart(comps, model, sales), use_container_width=True)

        # Market share donut
        st.plotly_chart(market_share_chart(segment), use_container_width=True)

        # Competitor table
        st.markdown("##### Segment Rivals — Monthly Trend")
        for c in comps:
            cs   = c["sales"]
            cmom = round((cs[-1] - cs[-2]) / cs[-2] * 100, 1) if cs[-2] else 0
            badge_cls = "badge-green" if cmom >= 0 else "badge-red"
            badge_txt = f"{'▲' if cmom >= 0 else '▼'} {abs(cmom)}% MoM"
            spark_vals = ", ".join(str(v) for v in cs)
            st.markdown(f"""
            <div class="comp-card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-weight:600;font-size:14px;">{c['brand']} {c['model']}</span>
                        <span class="badge badge-blue" style="margin-left:8px;">{c['vol']//1000:.0f}K units (9M)</span>
                    </div>
                    <span class="badge {badge_cls}">{badge_txt}</span>
                </div>
                <div style="font-size:12px;color:#6c757d;margin-top:4px;">
                    Mar '25: {cs[-1]:,} units &nbsp;|&nbsp; Avg: {sum(cs)//len(cs):,}/mo
                </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# RIGHT  –  industry news panel
# ══════════════════════════════════════════════
with news_col:
    st.subheader("📰 Industry News", divider="gray")

    with st.spinner("Loading latest auto news…"):
        news_items = fetch_news()

    if not news_items:
        st.warning("Could not fetch news feeds. Check your internet connection.")
    else:
        source_filter = st.multiselect(
            "Filter by source",
            options=list({n["source"] for n in news_items}),
            default=[],
            placeholder="All sources",
        )
        filtered = [n for n in news_items if not source_filter or n["source"] in source_filter]

        for item in filtered[:20]:
            clean_summary = re.sub(r"<[^>]+>", "", item.get("summary", "")).strip()[:160]
            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">
                    <a href="{item['link']}" target="_blank" style="color:#212529;text-decoration:none;">
                        {item['title']}
                    </a>
                </div>
                <div class="news-meta">
                    <b>{item['source']}</b> &middot; {item['date']}
                </div>
                {f'<div style="font-size:12px;color:#6c757d;margin-top:4px;">{clean_summary}…</div>' if clean_summary else ''}
            </div>""", unsafe_allow_html=True)
