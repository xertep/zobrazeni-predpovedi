import streamlit as st
from streamlit_extras.stylable_container import stylable_container
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
    ("CB", "Šumava a Novohradské hory"),
    ("HK", "Krkonoše"),
    ("LB", "Jizerské hory"),
    ("MT", "Beskydy"),
    ("OL", "Jeseníky a Králický Sněžník"),
    ("PL", "Český a Slavkovský les"),
    ("PU", "Orlické hory"),
    ("UL", "Krušné hory"),
    ("VY", "Žďárské vrchy"),
    ("ZL", "Javorníky a Bílé Karpaty"),
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

    output_lines = []

    if place_name:
        output_lines.append(f"**=== Předpověď {place_name} ===**\n")

    for pattern, headline_main, items, sender in all_data:
        if pattern in ["pCK2tx", "pCK3tx", "pCK4tx"] and not dalsi_dny_inserted:
            if not (morning_found and pattern == "pCK2tx"):
                output_lines.append("\n**=== Další dny ===**\n")
                dalsi_dny_inserted = True

        if evening_found and pattern == "pCK0tx":
            continue
        if morning_found and pattern == "pCK2tx":
            continue

        if pattern not in ["pCKntx", "pCK2tx", "pCK3tx", "pCK4tx", "pCRntx", "pCR2tx", "pCR3tx", "pCR4tx", "pCR5tx", "pCR8tx"] and headline_main:
            output_lines.append(f"**{headline_main}**\n")

        for item in items:
            h = item.get("headline")
            t = item.get("displayText")
            if h:
                output_lines.append(f"**{h}**")
            if t:
                t = t.replace("\xa0", " ")
                output_lines.append(t)

        if pattern == "pCK1tx" and sender:
            output_lines.append(f"\nMeteorolog: {sender}")

    for pattern, _, _, sender in reversed(all_data):
        if pattern == "pCK4tx" and sender:
            output_lines.append(f"\nMeteorolog: {sender}")
            break

    return "\n\n".join(output_lines)


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
                output_lines.append(f"**{headline_main}**\n")

            for item in items:
                h = item.get("headline")
                t = item.get("displayText")
                if h:
                    output_lines.append(f"**{h}**")
                if t:
                    t = t.replace("\xa0", " ")
                    output_lines.append(t)

        except Exception as e:
            st.error(f"Error loading {label} ({mountain_code}): {e}")

    if place_name:
        output_lines.insert(0, f"**=== Předpověď {place_name} ===**\n")
    if sender_name:
        output_lines.append(f"\nMeteorolog: {sender_name}")

    return "\n\n".join(output_lines)


# --- Streamlit page config ---
st.set_page_config(
    page_title="Předpovědi počasí ČHMÚ",
    page_icon="🌤️",
    layout="wide"
)

st.title("Předpovědi počasí ČHMÚ")

# --- Colors ---
main_region_colors = {"JM": "#ffc0cb", "ZL": "#98fb98", "VY": "#87ceeb", "CR": "#ffd700"}
other_region_colors = {
    "CB":"#eeeeee", "HK":"#eeeeee", "KV":"#eeeeee", "LB":"#eeeeee",
    "MS":"#eeeeee", "OL":"#eeeeee", "PH":"#eeeeee", "PL":"#eeeeee",
    "PU":"#eeeeee", "SC":"#eeeeee", "UL":"#eeeeee"
}

# --- Regions (Kraje) ---
st.markdown("### Kraje")
region_codes = ["JM","ZL","VY","CR","CB","HK","KV","LB","MS","OL","PH","PL","PU","SC","UL"]
selected_region = None

for row_idx, row in enumerate([region_codes[i:i+15] for i in range(0, len(region_codes), 15)]):
    cols = st.columns(len(row))
    for col_idx, (col, code) in enumerate(zip(cols, row)):
        color = main_region_colors.get(code, other_region_colors.get(code, "#eeeeee"))
        # unique key for each container
        container_key = f"region_container_{code}_{row_idx}_{col_idx}"
        with col:
            with stylable_container(
                container_key,
                css_styles=f"""
                button {{
                    background-color: {color};
                    color: black;
                    height: 80px;
                    width: 100%;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 16px;
                }}
                """
            ):
                if st.button(code, key=f"region_{code}"):
                    selected_region = code

# --- Mountains (Horské oblasti) ---
st.markdown("### Horské oblasti")
selected_mountain = None
mountain_codes = [code for code, _ in mountains]

for row_idx, row in enumerate([mountain_codes[i:i+10] for i in range(0, len(mountain_codes), 10)]):
    cols = st.columns(len(row))
    for col_idx, (col, code) in enumerate(zip(cols, row)):
        container_key = f"mountain_container_{code}_{row_idx}_{col_idx}"
        with col:
            with stylable_container(
                container_key,
                css_styles=f"""
                button {{
                    background-color: #eeeeee;
                    color: black;
                    height: 80px;
                    width: 100%;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 12px;
                }}
                """
            ):
                if st.button(code, key=f"mountain_{code}"):
                    selected_mountain = code

# --- Forecast output ---
forecast_placeholder = st.empty()

if selected_mountain:
    with st.spinner("Načítám data..."):
        forecast_placeholder.markdown(fetch_mountain(selected_mountain))
elif selected_region:
    with st.spinner("Načítám data..."):
        forecast_placeholder.markdown(fetch_region(selected_region))
