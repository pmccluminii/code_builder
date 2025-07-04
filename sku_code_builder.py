import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    xls = pd.ExcelFile("sku-permutation-generator.xlsm")
    df = xls.parse("Raw Data")
    return df

def parse_sku_elements(row):
    sku_order = row["SKU_Order"].split("|")
    sku_data = []
    for element in sku_order:
        options = row.get(element, "")
        labels = row.get(f"{element}_Label", "")
        if pd.isna(options):
            continue
        opt_list = str(options).split("|")
        label_list = str(labels).split("|") if isinstance(labels, str) else opt_list
        sku_data.append((element, list(zip(opt_list, label_list))))
    return sku_data, sku_order

def add_styling():
    st.markdown("""
    <style>
        div[role="radiogroup"] {
            flex-direction: row;
            gap: 15px;
        }
        input[type="radio"] + div {
            background: #dfeef6 !important;
            color: white !important;
            border-radius: 38px !important;
            padding: 8px 18px !important;
            cursor: pointer;
            user-select: none;
            transition: background 0.3s, color 0.3s;
        }
        input[type="radio"]:checked + div {
            background: #4CAF50 !important;
            color: white !important;
            font-weight: 600;
        }
        div[role="radiogroup"] > label > div:first-child {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        div[role="radiogroup"] label {
            margin-right: 0 !important;
            user-select: none;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Part Code Builder", layout="wide")
st.markdown("<h3 style='margin-bottom: 0.25rem;'>🔧 Product Part Code Builder</h3>", unsafe_allow_html=True)
add_styling()

df = load_data()
product_list = df["Product"].dropna().unique().tolist()
product_selection = st.selectbox("Choose a product:", product_list)

if product_selection:
    selected_row = df[df["Product"] == product_selection].iloc[0]
    model_code = selected_row["Model"]
    model_label = selected_row.get("Model_Label", model_code)

    st.markdown(f"<h4 style=''>SKU Options for {product_selection} ({model_label})</h4>", unsafe_allow_html=True)
    sku_elements, sku_order = parse_sku_elements(selected_row)

    if "sku_choice" not in st.session_state:
        st.session_state.sku_choice = {}

    # Initialize session state for radios if missing or invalid
    for element, options in sku_elements:
        radio_key = f"radio_{element}"
        opt_codes = [code for code, label in options]
        opt_labels = [label for code, label in options]

        default_code = st.session_state.sku_choice.get(element, opt_codes[0])
        code_to_label = dict(options)
        default_label = code_to_label.get(default_code, opt_labels[0])

        # Only set if key missing or invalid to avoid Streamlit warning
        if radio_key not in st.session_state or st.session_state[radio_key] not in opt_labels:
            st.session_state[radio_key] = default_label

    # Render radios and collect selected labels
    for element, options in sku_elements:
        st.markdown(f"<div style='font-weight:600; margin:0'>{element}</div>", unsafe_allow_html=True)

        opt_codes = [code for code, label in options]
        opt_labels = [label for code, label in options]

        radio_key = f"radio_{element}"

        selected_label = st.radio(
            label="",
            options=opt_labels,
            index=opt_labels.index(st.session_state[radio_key]),
            key=radio_key,
            horizontal=True,
        )

    # Sync sku_choice from radios' selected labels
    for element, options in sku_elements:
        radio_key = f"radio_{element}"
        selected_label = st.session_state.get(radio_key, None)
        if selected_label is not None:
            label_to_code = {label: code for code, label in options}
            st.session_state.sku_choice[element] = label_to_code[selected_label]

    if st.session_state.sku_choice:
        st.markdown("<hr style='margin-top: 0rem; margin-bottom: 0rem;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-bottom: 0rem;'>Current Part Code:</h4>", unsafe_allow_html=True)
        parts = [st.session_state.sku_choice.get(el, "--") for el in sku_order]
        full_code = "-".join([model_code if sku_order[0] != "Model" else ""] + parts).strip("-")
        st.code(full_code, language=None)

