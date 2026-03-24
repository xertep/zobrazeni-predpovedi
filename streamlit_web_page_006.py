import streamlit as st
import requests
import re

BASE_URL = "https://opendata.chmi.cz/meteorology/weather/forecast/now/"

# Forecast types
REGION_FORECAST_TYPES = [
    ("pCK0tx", "Day 1"),
    ("pCKntx", "Night"),
    ("pCK1tx", "Day 2"),
    ("pCK2tx", "Day 3"),
    ("pCK3tx", "Day 4"),
    ("pCK4tx", "Day 5"),
]

CR_FORECAST_TYPES = [
    ("pCR8ts", "Meteorologická situace"),
    ("pCR0tx", "Dnes"),
    ("pCRntx", "Noc"),
    ("pCR1tx", "Zítra"),
    ("pCR2tx", "Pozítří"),
    ("pCR3tx", "3. den"),
    ("pCR4tx", "4. den"),
    ("pCR5tx", "5. den"),
    ("pCR8tx", "6.–8. den"),
]

MOUNTAIN_FORECAST_TYPES = [
    ("pCH1tx", "Day 1"),
    ("pCH2tx", "Day 2"),
]

mountains = [
    ("VY", "Žďárské vrchy"),
    ("ZL", "Javorníky a Bílé Karpaty"),
    ("CB", "Šumava a Novohradské hory"),
    ("HK", "Krkonoše"),
    ("LB", "Jizerské hory"),
    ("MT", "Beskydy"),
    ("OL", "Jeseníky a Králický Sněžník"),
    ("PL", "Český a Slavkovský les"),
    ("PU", "Orlické hory"),
    ("UL", "Krušné hory"),
]

# Colors
main_region_colors = {"JM": "pink", "ZL": "PaleGreen", "VY": "SkyBlue"}
other_region_colors = {
    "CB":"lightgrey", "HK":"lightgrey", "KV":"lightgrey", "LB":"lightgrey",
    "MS":"lightgrey", "OL":"lightgrey", "PH":"lightgrey", "PL":"lightgrey",
    "PU":"lightgrey", "SC":"lightgrey", "UL":"lightgrey"
}
cr_color = "gold"
mountain_color = "gray73"


def get_latest_file(pattern):
    response = requests.get(BASE_URL)
    html = response.text
    matches = re.findall(r'href="(web_' + pattern + r'(?:_[A-Z]{2,3})?[^"]+\.json)"', html)
    if not matches:
        return None
    matches.sort()
    return BASE_URL + matches[-1]


def fetch_region(region_code):
    sender_name = None
    place_name = None
    dalsi_dny_inserted = False
    evening_found = False
    morning_found = False
    all_data = []

    forecast_types = CR_FORECAST_TYPES if region_code == "CR" else REGION_FORECAST_TYPES
    full_pattern_prefix = "" if region_code == "CR" else f"_RP{region_code}"

    for pattern, label in forecast_types:
        full_pattern = f"{pattern}{full_pattern_prefix}"
        url = get_latest_file(full_pattern)
        if not url:
            continue
        try:
            data = requests.get(url).json()
            features = data.get("data", {}).get("features", [])
            if not features:
                continue
            props = features[0].get("properties", {})
            if not place_name:
                place_name = props.get("place", {}).get("name", "Česká republika" if region_code=="CR" else "")
            if not sender_name:
                sender_name = props.get("senderName", "")

            headline_main = props.get("headline-main", {}).get("headline", "")
            items = sorted(props.get("data", []), key=lambda x: x.get("displayOrder", 0))

            for item in items:
                h = item.get("headline", "")
                if h:
                    if "Počasí dnes večer a v noci (18-07):" in h:
                        evening_found = True
                    if "Počasí (06-22):" in h:
                        morning_found = True

            all_data.append((pattern, headline_main, items, props.get("senderName", "")))

        except Exception as e:
            st.error(f"Error loading {label}: {e}")

    # Build output with HTML for bold and spacing
    output_lines = []

    if place_name:
        output_lines.append(f'<b>=== Předpověď {place_name} ===</b><br>')

    for pattern, headline_main, items, sender in all_data:
        if pattern in ["pCK2tx", "pCK3tx", "pCK4tx"] and not dalsi_dny_inserted:
            if not (morning_found and pattern == "pCK2tx"):
                output_lines.append('<br><b>=== Další dny ===</b><br>')
                dalsi_dny_inserted = True

        if evening_found and pattern == "pCK0tx":
            continue
        if morning_found and pattern == "pCK2tx":
            continue

        if pattern not in ["pCKntx", "pCK2tx", "pCK3tx", "pCK4tx", "pCRntx", "pCR2tx", "pCR3tx", "pCR4tx", "pCR5tx", "pCR8tx"] and headline_main:
            output_lines.append(f'<br><b>{headline_main}</b><br>')

        for item in items:
            h = item.get("headline")
            t = item.get("displayText")
            if h:
                output_lines.append(f'<br><b>{h}</b><br>')
            if t:
                t = t.replace("\xa0", " ")
                output_lines.append(f'{t}<br>')

        if pattern == "pCK1tx" and sender:
            output_lines.append(f'<br>Meteorolog: {sender}<br>')

    for pattern, _, _, sender in reversed(all_data):
        if pattern == "pCK4tx" and sender:
            output_lines.append(f'<br>Meteorolog: {sender}<br>')
            break

    return "".join(output_lines)


def fetch_mountain(mountain_code):
    sender_name = None
    place_name = None
    output_lines = []

    for pattern, label in MOUNTAIN_FORECAST_TYPES:
        full_pattern = f"{pattern}_RP{mountain_code}"
        url = get_latest_file(full_pattern)
        if not url:
            continue
        try:
            data = requests.get(url).json()
            features = data.get("data", {}).get("features", [])
            if not features:
                continue
            props = features[0].get("properties", {})
            if not place_name:
                place_name = props.get("place", {}).get("name", "")
            if not sender_name:
                sender_name = props.get("senderName", "")

            headline_main = props.get("headline-main", {}).get("headline", "")
            items = sorted(props.get("data", []), key=lambda x: x.get("displayOrder", 0))

            if headline_main:
                output_lines.append(f'<br><b>{headline_main}</b><br>')

            for item in items:
                h = item.get("headline")
                t = item.get("displayText")
                if h:
                    output_lines.append(f'<br><b>{h}</b><br>')
                if t:
                    t = t.replace("\xa0", " ")
                    output_lines.append(f'{t}<br>')

        except Exception as e:
            st.error(f"Error loading {label} ({mountain_code}): {e}")

    if place_name:
        output_lines.insert(0, f'<b>=== Předpověď {place_name} ===</b><br>')
    if sender_name:
        output_lines.append(f'<br>Meteorolog: {sender_name}<br>')

    return "".join(output_lines)


# --- Streamlit UI ---
# Change browser tab title and favicon
st.set_page_config(
    page_title="Předpovědi počasí ČHMÚ",
    page_icon="🌤️",
    layout="wide"
)

st.title("Předpovědi počasí ČHMÚ")

# --- Regions (Kraje) ---
st.markdown("### Kraje")

region_codes = ["JM","ZL","VY","CR","CB","HK","KV","LB","MS","OL","PH","PL","PU","SC","UL"]
region_codes_cz = ["JM","ZL","VY","ČR","CB","HK","KV","LB","MS","OL","PH","PL","PU","SC","UL"]

selected_region = None

# Split into rows of 15 buttons
for row in [list(zip(region_codes, region_codes_cz))[i:i+15] for i in range(0, len(region_codes), 15)]:
    cols = st.columns(len(row))  # one column per code in this row
    for col, (code, label) in zip(cols, row):
        if col.button(label, key=f"region_{code}", use_container_width=True):
            selected_region = code

# --- Mountains (Horské oblasti) ---
st.markdown("### Horské oblasti")
selected_mountain = None

# Split mountains into rows of 10
for row in [mountains[i:i+10] for i in range(0, len(mountains), 10)]:
    cols = st.columns(len(row))
    for col, (code, _) in zip(cols, row):
        if col.button(code, key=f"mountain_{code}", use_container_width=True):
            selected_mountain = code

# --- Forecast output ---
forecast_placeholder = st.empty()

if selected_mountain:
    with st.spinner("Načítám data..."):
        forecast_html = fetch_mountain(selected_mountain)
        forecast_placeholder.markdown(forecast_html, unsafe_allow_html=True)
elif selected_region:
    with st.spinner("Načítám data..."):
        forecast_html = fetch_region(selected_region)
        forecast_placeholder.markdown(forecast_html, unsafe_allow_html=True)

