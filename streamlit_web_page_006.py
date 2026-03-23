# --- Streamlit UI ---
st.title("Předpovědi počasí ČHMÚ")

# Order EXACTLY as you want
region_codes = [
    "JM", "ZL", "VY", "CB", "HK", "KV", "LB",
    "MS", "OL", "PH", "PL", "PU", "SC", "UL", "CR"
]

mountain_codes = [code for code, _ in mountains]


# --- Color logic ---
def get_color(code, is_mountain=False):
    if is_mountain:
        return "#eeeeee"

    if code == "JM":
        return "#f8c8dc"  # soft pink
    elif code == "ZL":
        return "#cfeccf"  # soft green
    elif code == "VY":
        return "#cfe8f7"  # soft blue
    elif code == "CR":
        return "#f7e7a9"  # soft gold
    else:
        return "#eeeeee"  # grey


# --- Card grid ---
def card_grid(items, cols_per_row, key_prefix, is_mountain=False):
    selected = None
    rows = [items[i:i+cols_per_row] for i in range(0, len(items), cols_per_row)]

    for row in rows:
        cols = st.columns(len(row))

        for i, code in enumerate(row):
            color = get_color(code, is_mountain)

            with cols[i]:
                # Card background
                st.markdown(f"""
                    <div style="
                        background-color:{color};
                        padding:12px;
                        border-radius:14px;
                        text-align:center;
                        margin-bottom:6px;
                    ">
                """, unsafe_allow_html=True)

                # Clickable button
                if st.button(code, key=f"{key_prefix}_{code}"):
                    selected = code

                st.markdown("</div>", unsafe_allow_html=True)

    return selected


# --- UI Layout ---
st.markdown("### Kraje")
selected_region = card_grid(region_codes, 5, "region")

st.markdown("### Horské oblasti")
selected_mountain = card_grid(mountain_codes, 5, "mountain", is_mountain=True)


# --- Output ---
st.markdown("---")

if selected_mountain:
    st.markdown(fetch_mountain(selected_mountain))
elif selected_region:
    st.markdown(fetch_region(selected_region))
