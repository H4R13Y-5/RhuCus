import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
from Levenshtein import distance as levenshtein_distance
import uuid

st.set_page_config(
    page_title="My Skating App",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------
# Sidebar toggle and page config
# --------------------------
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "collapsed"

def toggle_sidebar():
    st.session_state.sidebar_state = (
        "expanded" if st.session_state.sidebar_state == "collapsed" else "collapsed"
    )
    st.experimental_rerun()

st.sidebar.button(
    "Toggle Sidebar",
    on_click=toggle_sidebar,
    key="toggle_sidebar_button"
)

# --------------------------
# Custom Styling (your palette)
# --------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #6f6f6f;
        color: #ffffff;
    }
    .css-1d391kg {
        background-color: #55364e !important;
        color: #ffffff;
    }
    .custom-header button {
        background-color: #aa9400;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        font-weight: bold;
        border: 2px solid #55364e;
    }
    .custom-header button:hover {
        background-color: #55364e;
        color: #aa9400;
    }
    .main-title {
        color: #aa9400;
        font-size: 2.5rem;
        font-weight: bold;
        margin-top: 1rem;
    }
    .sub-header {
        color: #55364e;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .footer {
        margin-top: 3rem;
        padding: 1rem 0;
        border-top: 2px solid #aa9400;
        text-align: center;
        font-size: 0.9rem;
        color: #ddd;
    }
    .score-container {
        background-color: #55364e;
        border: 3px solid #aa9400;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        width: 150px;
        display: inline-block;
        vertical-align: top;
        color: #ffffff;
    }
    .score-label {
        font-size: 1.5rem;
        color: #aa9400;
        font-weight: bold;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .big-score {
        font-size: 3rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* GOE Buttons Styling */
    .goe-button {
        font-size: 1.5rem;
        padding: 10px 15px;
        margin: 5px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
    }
    .goe-button-positive {
        background-color: #4CAF50; /* Green */
        color: white;
    }
    .goe-button-positive:hover {
        background-color: #45a049;
    }
    .goe-button-negative {
        background-color: #f44336; /* Red */
        color: white;
    }
    .goe-button-negative:hover {
        background-color: #da190b;
    }

    /* Mobile Responsiveness */
    @media only screen and (max-width: 768px) {
        .stApp {
            padding: 10px;
        }
        .score-container {
            width: 100%;
            margin: 10px 0;
        }
        .big-score {
            font-size: 2rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------
# Base Values (your scoring elements)
# --------------------------
base_values = {
    #Jumps#
    "1A": 1.1, "2A": 3.3, "3A": 8.0, "4A": 12.5, #Axel#
    "1T": 0.4, "2T": 1.3, "3T": 4.2, "4T": 9.5, #Toe Loop#
    "1S": 0.4, "2S": 1.3, "3S": 4.1, "4S": 8.8, #Salchow#
    "1LO": 0.5, "2LO": 1.7, "3LO": 4.9, "4LO": 9.7, #Loop#
    "1F": 0.5, "2F": 1.8, "3F": 5.3, "4F": 10.3, #Flip#
    "1LZ": 0.6, "2LZ": 2.1, "3LZ": 5.9, "4LZ": 11.0, #Lutz#

    #Base Spins#
    "USP": 1.0,"USP1": 1.0, "USP2": 1.5, "USP3": 2.0, "USP4": 2.5, #Upright Spin#
    "LSP": 1.2, "LSP1": 1.2, "LSP2": 1.8, "LSP3": 2.3, "LSP4": 2.7, #Layback Spin#
    "CSP": 1.5, "CSP1": 1.5, "CSP2": 2.0, "CSP3": 2.5, "CSP4": 3.0, #Camel Spin#
    "SSP": 1.2, "SSP1": 1.2, "SSP2": 1.8, "SSP3": 2.3, "SSP4": 2.7, #Sit Spin#

    #Spins with variations#
    #Flying Spins#
    "FUSP": 1.3, "FUSP1": 1.3, "FUSP2": 1.8, "FUSP3": 2.4, "FUSP4": 2.9, #Flying Spin#
    "FLSP": 1.5, "FLSP1": 1.5, "FLSP2": 2.0, "FLSP3": 2.6, "FLSP4": 3.2, #Flying Layback Spin#
    "FCSP": 1.8, "FCSP1": 1.8, "FCSP2": 2.4, "FCSP3": 3.0, "FCSP4": 3.6, #Flying Camel Spin#
    "FSSP": 1.5, "FSSP1": 1.5, "FSSP2": 2.0, "FSSP3": 2.5, "FSSP4": 3.0, #Flying Sit Spin#

    #change of foot spins#
    "CLSP": 1.4, "CLSP1": 1.4, "CLSP2": 2.0, "CLSP3": 2.5, "CLSP4": 3.1, #Change of Foot Layback Spin#
    "CCSP": 1.7, "CCSP1": 1.7, "CCSP2": 2.3, "CCSP3": 2.9, "CCSP4": 3.5, #Change of Foot Camel Spin#
    "CSSP": 1.4, "CSSP1": 1.4, "CSSP2": 2.0, "CSSP3": 2.5, "CSSP4": 3.1, #Change of Foot Sit Spin#
    "CUSP": 1.2, "CUSP1": 1.2, "CUSP2": 1.7, "CUSP3": 2.3, "CUSP4": 2.8, #Change of Foot Upright Spin#

    #Flying Change of Foot Spins#
    "FCLSP": 1.6, "FCLSP1": 1.6, "FCLSP2": 2.2, "FCLSP3": 2.8, "FCLSP4": 3.4, #Flying Change of Foot Layback Spin#
    "FCUSP": 1.5, "FCUSP1": 1.5, "FCUSP2": 2.0, "FCUSP3": 2.5, "FCUSP4": 3.0, #Flying Change of Foot Spin#
    "FCCSP": 2.0, "FCCSP1": 2.0, "FCCSP2": 2.5, "FCCSP3": 3.0, "FCCSP4": 3.6, #Flying Change of Foot Camel Spin#
    "FCSSP": 1.7, "FCSSP1": 1.7, "FCSSP2": 2.3, "FCSSP3": 2.9, "FCSSP4": 3.5, #Flying Change of Foot Sit Spin#

    #Combination Spins#
    "COSP": 1.5, "COSP1": 1.5, "COSP2": 2.0, "COSP3": 2.5, "COSP4": 3.0, #Combination Spin#
    "CCOSP": 1.6, "CCOSP1": 1.6, "CCOSP2": 2.2, "CCOSP3": 2.8, "CCOSP4": 3.4, #Change of Foot Combination Spin#
    "FCOSP": 1.7, "FCOSP1": 1.7, "FCOSP2": 2.3, "FCOSP3": 2.9, "FCOSP4": 3.5, #Flying Combination Spin#
    "FCCOSP": 1.8, "FCCOSP1": 1.8, "FCCOSP2": 2.4, "FCCOSP3": 3.0, "FCCOSP4": 3.6, #Flying Change of Foot Combination Spin#

    #Sequences#
    "STSQ1": 1.8, "STSQ2": 2.6, "STSQ3": 3.3, "STSQ4": 3.9,     #Step Sequence#
    "CHSQ1": 3.0, "CHSQ2": 3.5, "CHSQ3": 4.0, "CHSQ4": 4.5,    #Choreo Sequence#
}

# --------------------------
# Session State Setup
# --------------------------
def initialize_state():
    defaults = {
        'program': [],
        'scores': [],
        'tes': 0,
        'pcs': 0.0,
        'deductions': 0,
        'current': 0,
        'predicted_scores': pd.DataFrame(columns=["Element", "Predicted Base Value"]),
        'show_program_sheet': False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

initialize_state()

# --------------------------
# Sidebar: Deductions and PCS Sliders
# --------------------------
st.sidebar.subheader("Deductions")
falls_deductions = st.sidebar.number_input("Number of Falls (-1 each)", min_value=0, max_value=10, value=0)
time_violation = int(st.sidebar.checkbox("Time Violation (-1)"))
costume_violation = int(st.sidebar.checkbox("Costume Violation (-1)"))
illegal_element = 2 * int(st.sidebar.checkbox("Illegal Element (-2)"))
st.session_state.deductions = falls_deductions + time_violation + costume_violation + illegal_element

st.sidebar.subheader("Program Components (x2.0)")
pcs_fields = ["Skating Skills", "Transitions", "Performance", "Composition", "Interpretation"]
st.session_state.pcs = sum(st.sidebar.slider(field, 0.0, 10.0, 7.5, 0.25) * 2.0 for field in pcs_fields)

st.sidebar.subheader("Display Options")
st.session_state.show_program_sheet = st.sidebar.checkbox("Show Planned Program Sheet")
# Ensure the program is cleared and session state is updated
if st.sidebar.button("Clear Program", key="clear_program_sidebar"):
    st.session_state.program = []
    st.session_state.scores = []
    st.session_state.tes = 0
    st.session_state.current = 0
    st.sidebar.success("Program has been cleared and reset!")

# --------------------------
# Navigation Buttons (Fixed)
# --------------------------
if 'page' not in st.session_state:
    st.session_state.page = "Coach Mode"

st.markdown("<div class='custom-header'>", unsafe_allow_html=True)
header_cols = st.columns(3)
with header_cols[0]:
    if st.button("Coach Mode"):
        st.session_state.page = "Coach Mode"
with header_cols[1]:
    if st.button("Prediction Mode"):
        st.session_state.page = "Prediction Mode"
with header_cols[2]:
    if st.button("Glossary"):
        st.session_state.page = "Glossary"
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# Show page content based on current page
# --------------------------
if st.session_state.page == "Coach Mode":
    st.markdown("<div class='main-title'>⛸️ Coach Mode</div>", unsafe_allow_html=True)
    st.subheader("Enter Program Elements")
    col1, col2 = st.columns([3, 1])
    with col1:
        # Add both text input and dropdown for element codes
        new_element_text = st.text_input("Element Code (e.g., 2A, 3T+2Lo):", key="element_input_text")
        new_element_dropdown = st.selectbox("Or select from dropdown:", options=list(base_values.keys()), key="element_input_dropdown")
        new_element = new_element_text if new_element_text else new_element_dropdown
    with col2:
        if st.button("Add to Program", key="add_program_btn"):
            if new_element:
                elements = [e.strip() for e in new_element.split("+") if e.strip()]
                if all(e in base_values for e in elements):
                    if len(elements) <= 3:
                        st.session_state.program.append(new_element)
                        st.success(f"Added {new_element}")
                    else:
                        st.error("Too many elements in a combination! Max is 3.")
                else:
                    missing = [e for e in elements if e not in base_values]
                    suggestions = [
                        min(base_values.keys(), key=lambda x: levenshtein_distance(e, x))
                        for e in missing
                    ]
                    st.error(f"Invalid elements: {', '.join(missing)}. Did you mean: {', '.join(suggestions)}?")
            else:
                st.error("Please enter an element code.")

    if st.session_state.program:
        st.write(f"**Program Order:** {', '.join(st.session_state.program)}")
        if st.session_state.current < len(st.session_state.program):
            current_element = st.session_state.program[st.session_state.current]
            st.subheader(f"Scoring Element {st.session_state.current+1}: {current_element}")

            # GOE Buttons
            st.markdown("**Select GOE (Grade of Execution):**")
            cols = st.columns(11)
            for i, val in enumerate(range(-5, 6)):
                with cols[i]:
                    if st.button(f"{val}", key=f"goe_{val}_{st.session_state.current}", help=f"GOE: {val}", use_container_width=True):
                       # Retrieve the base value of the current element
                            base = sum(base_values.get(e, 0) for e in current_element.split("+"))

                            # Retrieve the edge call and apply penalty if present
                            edge_call = st.session_state.edge_call.get(current_element, "")  # Get edge call (if any)
                            edge_penalties = {">": 0.7, ">>": 0.5, "e": 0.8, "!": 0.5}  # Define penalty values
                            penalty = edge_penalties.get(edge_call, 0)  # Get penalty for the edge call

                            # Adjust base value by applying the penalty
                            adjusted_base_value = round(base * (1 - penalty), 2)

                            # Calculate final score with GOE
                            score = round(adjusted_base_value * (1 + val / 10), 2)
                            st.session_state.tes += score

                            # Add score details, including edge call
                            st.session_state.scores.append((current_element, val, base, adjusted_base_value, score, edge_call))
                            st.session_state.current += 1

            # Edge Calls
            st.markdown("**Edge Calls:**")
            edge_calls = st.columns(4)
            edge_labels = ["Q", "U", "e", "!"]
            for idx, label in enumerate(edge_labels):
                with edge_calls[idx]:
                    if st.button(label, key=f"edge_call_{label}_{st.session_state.current}"):
                        st.session_state.program[st.session_state.current] += f" {label}"
                        st.success(f"Added edge call: {label}")

            # Display Scores with styling
            tss = st.session_state.tes + st.session_state.pcs + st.session_state.deductions
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='score-container'><div class='score-label'>TES</div><div class='big-score'>{st.session_state.tes:.2f}</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='score-container'><div class='score-label'>PCS</div><div class='big-score'>{st.session_state.pcs:.2f}</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='score-container'><div class='score-label'>TSS</div><div class='big-score'>{tss:.2f}</div></div>", unsafe_allow_html=True)

    # Protocol Sheet Export (CSV & PDF)
    def generate_pdf(dataframe, filename):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt="Protocol Sheet", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", style="B", size=12)
        for column in dataframe.columns:
            pdf.cell(40, 10, str(column), border=1, align="C")
        pdf.ln()
        pdf.set_font("Arial", size=12)
        for _, row in dataframe.iterrows():
            for item in row:
                pdf.cell(40, 10, str(item) if pd.notna(item) else "", border=1, align="C")
            pdf.ln()
        pdf.output(filename)

    if st.session_state.scores:
        protocol_df = pd.DataFrame(st.session_state.scores, columns=["Element", "GOE", "Base Value", "Final Score"])
        totals = pd.DataFrame({
            "Element": ["TES", "PCS", "Deductions", "TSS"],
            "Final Score": [
                st.session_state.tes,
                st.session_state.pcs,
                st.session_state.deductions,
                st.session_state.tes + st.session_state.pcs + st.session_state.deductions
            ]
        })
        full_df = pd.concat([protocol_df, pd.DataFrame([{}]), totals], ignore_index=True)
        st.write(full_df)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_data = full_df.to_csv(index=False).encode('utf-8')
        st.download_button(f"Download Protocol Sheet ({timestamp})", csv_data, f"protocol_sheet_{timestamp}.csv")
        # PDF export
        pdf_filename = f"protocol_sheet_{timestamp}.pdf"
        if st.button("Download Protocol Sheet as PDF"):
            generate_pdf(full_df, pdf_filename)
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button("Download PDF", pdf_file, file_name=pdf_filename, mime="application/pdf")
    else:
        st.warning("No scored elements available. Please score some elements in Coach Mode.")

elif st.session_state.page == "Prediction Mode":
    # Prediction Mode Content
    st.markdown("<div class='main-title'>📊 Prediction Mode</div>", unsafe_allow_html=True)
    st.subheader("Prediction Program Builder")
    program_pred = st.multiselect("Select your program elements:", options=list(base_values.keys()))
    if st.button("Predict Scores", key="predict_scores"):
        if program_pred:
            pred_scores = [(code, base_values.get(code, 0)) for code in program_pred]
            st.session_state.predicted_scores = pd.DataFrame(pred_scores, columns=["Element", "Predicted Base Value"])
        else:
            st.warning("Select elements to predict scores.")
    if not st.session_state.predicted_scores.empty:
        pred_total = st.session_state.predicted_scores["Predicted Base Value"].sum()
        st.write(st.session_state.predicted_scores)
        st.write(f"**Predicted TES:** {pred_total:.2f}")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_data = st.session_state.predicted_scores.to_csv(index=False).encode('utf-8')
        st.download_button(f"Download Predictions ({timestamp})", csv_data, f"predicted_scores_{timestamp}.csv", "text/csv")

elif st.session_state.page == "Glossary":
    # Glossary Content
    st.markdown("<div class='main-title'>📖 Glossary</div>", unsafe_allow_html=True)
    st.write("""
    **GOE (Grade of Execution):** Performance bonus/penalty (-5 to +5) applied to base element values.
    **TES (Technical Element Score):** Sum of all scored technical elements.
    **PCS (Program Component Score):** Judges' artistic scores on:
    - Skating Skills
    - Transitions
    - Performance
    - Composition
    - Interpretation
    **TSS (Total Segment Score):** TES + PCS + Deductions.
    **Edge Calls:** `>`, `>>`, `e`, `!` indicating unclear or wrong takeoffs.
    **Combos:** Multiple jumps linked by `+` (max 3).
    **Deductions:** Penalties for falls, violations, illegal moves.
    """)

# --------------------------
# Footer (unchanged)
# --------------------------
st.markdown("""
    <div class='footer'>
        ⛸️ Rhubarb & Custard Skating Scorer — lovingly made by a code nerd on ice. ✨
    </div>
""", unsafe_allow_html=True)
