import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
from Levenshtein import distance as levenshtein_distance
import uuid
import json
import io

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

# Ensure 'page' is initialized in session state before any access
if 'page' not in st.session_state:
    st.session_state.page = 'Coach'

def toggle_sidebar():
    st.session_state.sidebar_state = (
        "expanded" if st.session_state.sidebar_state == "collapsed" else "collapsed"
    )
    st.rerun()

# --------------------------
# Custom Styling (your palette)
# --------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #55464e;
        background-color: #55364e !important;
        color: #222222; /* Changed from #ffffff to dark for light mode */
    }
    .css-1d391kg {
        background-color: #55364e !important;
        color: #222222 !important; /* Changed from #ffffff to dark for light mode */
            
    }
    .custom-header button {
        border-radius: 5px; /* Rectangular shape */
        width: auto; /* Adjust width to fit text */
        height: auto; /* Adjust height to fit text */
        padding: 10px 20px; /* Add padding for clarity */
        font-size: 1rem; /* Adjust font size for readability */
        text-align: center;
        margin: 0.3rem;
        font-weight: bold;
        border: 2px solid #55364e;
        background-color: #55364e !important;
            
            
    }
    .custom-header button:hover {
        background-color: #55364e;
        color: #aa9400; /* Gold color for hover effect */
        background-color: #55364e !important;
    }
    .main-title {
        color: #aa9400;
        font-size: 2.5rem;
        font-weight: bold;
        margin-top: 1rem; /* Added margin for spacing */
        text-align: center; /* Center the title */
        margin-bottom: 1rem; /* Added margin for spacing */ 
    }
    .sub-header {
        color: #55364e;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 1rem;
        background-color: #55364e !important;
        padding: 0.5rem;
    }
    .footer {
        margin-top: 3rem;
        padding: 1rem 0;
        border-top: 2px solid #aa9400;
        text-align: center;
        font-size: 0.9rem;
        color: ##dddfff; /* Light gray for footer text */
        background-color: #55364e; /* Dark background for footer */
        background-color: #55364e !important;
        
        
    }
    .score-container {
        background-color: #f4f4f4; /* Light gray for visibility in light mode */
        border: 3px solid #aa9400;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        width: 150px;
        display: inline-block;
        vertical-align: top;
        color: #808080; /* Gray text for contrast */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out;
    }
    .score-label {
        font-size: 1.5rem;
        color: #aa9400; /* Gold color for labels */
        font-weight: bold;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .big-score {
        font-size: 3rem;
        font-weight: bold;
        color: #55364e ; /* Dark color for contrast */
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* GOE Buttons Styling */
    .goe-button { 
        background-color: #55364e !important;
            
        font-size: 1.5rem;
        padding: 10px 15px;
        margin: 5px;
        border-radius: 8px;
        border: 2px solid #55364e;
        background-color: #fff; /* White background for visibility */
        color: #55364e; /* Dark text for contrast */
        transition: background-color 0.3s ease, color 0.3s ease;
        cursor: pointer;
    }
    .goe-button-positive {
        background-color: #4CAF50; /* Green */
        color: Black; /* Black text for contrast */
        border: 2px solid #4CAF50; /* Green border */
    }
    .goe-button-positive:hover {
        background-color: #45a049; /* Darker green on hover */
        color: white; /* White text on hover */ 
    }
    .goe-button-negative {
        background-color: #f44336; /* Red */ 
        color:Black; /* Black text for contrast */
        border: 2px solid #f44336; /* Red border */ 
    }
    .goe-button-negative:hover {   
        background-color: #da190b; /* Darker red on hover */
        color: white; /* White text on hover */ 
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

    .stButton button {
        border-radius: 0; /* Removed circular styling */
        width: auto; /* Adjust width to fit text */
        height: auto; /* Adjust height to fit text */
        font-size: 1rem; /* Adjust font size for readability */
        text-align: center;
        padding: 10px;
        overflow: hidden; /* Ensure text does not overflow */
        white-space: nowrap; /* Prevent text wrapping */
    }

.stDownloadButton button {
        border-radius: 0; /* Removed squircle styling */
        width: auto; /* Adjust width to fit text */
        height: auto; /* Adjust height to fit text */
        font-size: 0.9rem; /* Adjust font size for readability */
        text-align: center;
        padding: 5px;
        overflow: hidden; /* Ensure text does not overflow */
        white-space: nowrap; /* Prevent text wrapping */
    }

.nav-button-container button {
        border-radius: 0; /* Removed rectangular styling */
        width: auto; /* Adjust width to fit text */
        height: auto; /* Adjust height to fit text */
        padding: 10px 20px; /* Add padding for clarity */
        font-size: 1rem; /* Adjust font size for readability */
        text-align: center;
        margin: 0.3rem;
        font-weight: bold;
        border: 2px solid #55364e;
    }
    .nav-button-container button:hover {
        background-color: #45a049 !important; /* Darker green on hover */
    }
    </style>
""", unsafe_allow_html=True)

# Inject custom CSS for a touch-friendly UI
st.markdown("""
<style>
body, .stApp { background-color: #2a2a2a; color: #fff; }
.main-title { color: #FFB703; font-size: 2.5rem; font-weight: bold; text-align: center; }
.current-element { background: #FFB703; color: #000; padding: 15px; border-radius: 12px; font-size: 1.8rem; text-align: center; margin: 1rem 0; }
.big-button { font-size: 2rem; padding: 25px 20px; margin: 0.5rem; border-radius: 12px; text-align: center; width: 100%; }
.big-button-positive { background: #219EBC; color: white; border: none; }
.big-button-negative { background: #E63946; color: white; border: none; }
.fixed-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: #55364e; display: flex; justify-content: space-around; padding: 0.5rem 0; z-index: 9999; }
.fixed-nav button { flex: 1; margin: 0 0.3rem; padding: 1rem; font-size: 1.2rem; font-weight: bold; border: none; border-radius: 0; color: #fff; background: #55364e; }
.fixed-nav button:hover { background: #45a049; }
</style>
""", unsafe_allow_html=True)

# --- Mobile Optimization: Add responsive CSS for larger buttons and better layout ---
st.markdown('''
<style>
@media only screen and (max-width: 600px) {
  .stButton button, .stDownloadButton button {
    font-size: 1.3rem !important;
    padding: 18px 10px !important;
    min-width: 90vw !important;
    margin-bottom: 10px !important;
  }
  .stTextInput input {
    font-size: 1.2rem !important;
    padding: 12px !important;
  }
  .stSelectbox div[data-baseweb="select"] {
    font-size: 1.1rem !important;
  }
  .stDataFrame, .stTable {
    font-size: 1.1rem !important;
  }
}
</style>
''', unsafe_allow_html=True)

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
    if 'edge_call' not in st.session_state:
        st.session_state.edge_call = {}
    if 'edge_calls' not in st.session_state:
        st.session_state.edge_calls = {}

initialize_state()

# --- Competition Mode and Skater Management ---
if 'competition_mode' not in st.session_state:
    st.session_state.competition_mode = False
if 'skaters' not in st.session_state:
    st.session_state.skaters = {}
if 'selected_skater' not in st.session_state:
    st.session_state.selected_skater = ''
if 'competition_scoring' not in st.session_state:
    st.session_state.competition_scoring = None

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
st.session_state.pcs = sum(st.sidebar.slider(field, 0.0, 10.0, 0.0, 0.25) * 2.0 for field in pcs_fields)

st.sidebar.subheader("Display Options")
st.session_state.show_program_sheet = st.sidebar.checkbox("Show Planned Program Sheet")
# Ensure the program is cleared and session state is updated
if st.sidebar.button("Clear Program", key="clear_program_sidebar"):
    if st.session_state.competition_mode:
        st.session_state.skaters[st.session_state.selected_skater]['program'] = []
        st.session_state.skaters[st.session_state.selected_skater]['scores'] = []
        st.session_state.skaters[st.session_state.selected_skater]['tes'] = 0
        st.session_state.skaters[st.session_state.selected_skater]['current'] = 0
    else:
        st.session_state.program = []
        st.session_state.scores = []
        st.session_state.tes = 0
        st.session_state.current = 0
    st.sidebar.success("Program has been cleared and reset!")

# --- Download CSV at Bottom of Sidebar ---
if st.session_state.page == "Coach" and st.session_state.current >= len(st.session_state.program):
    protocol_df = pd.DataFrame(st.session_state.scores, columns=["Element", "GOE", "Score", "Edge Call"])
    protocol_df["Base Value"] = protocol_df["Element"].apply(
        lambda x: sum(base_values[part] for part in x.split("+") if part in base_values)
    )
    protocol_df["Final Score"] = protocol_df["Base Value"] * (1 + protocol_df["GOE"] / 10)
    protocol_df = protocol_df[["Element", "Base Value", "GOE", "Final Score", "Edge Call"]]
    csv = protocol_df.to_csv(index=False).encode('utf-8')
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.download_button("⬇️ Download CSV", csv, file_name="protocol.csv", mime="text/csv")

# --- Tabs Navigation ---
tab_labels = ["Coach", "Prediction", "Skater Management", "Competition", "Results"]
tabs = st.tabs(tab_labels)

# --------------------------
# Autocomplete Suggestions
# --------------------------
def autocomplete_suggestions(input_text, options):
    if not input_text:
        return []
    input_upper = input_text.upper()
    # If input is valid, return no suggestions
    if input_upper in options:
        return []
    # For short inputs (<=3 chars), prioritize substring matches
    if len(input_upper) <= 3:
        substr_matches = [option for option in options if input_upper in option]
        if substr_matches:
            return substr_matches[:3]
    # Otherwise, return 3 closest options by Levenshtein distance
    distances = [(option, levenshtein_distance(input_upper, option)) for option in options]
    distances.sort(key=lambda x: x[1])
    return [option for option, _ in distances[:3]]

# Coach Tab
with tabs[0]:
    # --- Coach Page Content ---
    st.markdown(f"<div class='main-title'>⛸️ Coach Mode</div>", unsafe_allow_html=True)

    # Display live scores (TSS, TES, PCS) at the top of the page, TSS first, no deductions
    st.markdown("""
    <div style='display: flex; justify-content: space-around; align-items: center; margin-bottom: 20px;'>
        <div class='score-container'>
            <div class='score-label'>TSS</div>
            <div class='big-score'>{:.2f}</div>
        </div>
        <div class='score-container'>
            <div class='score-label'>TES</div>
            <div class='big-score'>{:.2f}</div>
        </div>
        <div class='score-container'>
            <div class='score-label'>PCS</div>
            <div class='big-score'>{:.2f}</div>
        </div>
    </div>
    """.format(
        st.session_state.tes + st.session_state.pcs - st.session_state.deductions,
        st.session_state.tes,
        st.session_state.pcs
    ), unsafe_allow_html=True)

    if st.session_state.current < len(st.session_state.program):
        # Progress bar for scoring
        st.progress((st.session_state.current) / len(st.session_state.program), text=f"Element {st.session_state.current+1} of {len(st.session_state.program)}")
        # Display live scores (TSS, PCS, TES) at the top only
        st.markdown(f"<div class='current-element'>{st.session_state.program[st.session_state.current]}</div>", unsafe_allow_html=True)

        # Updated to handle combos as single elements with one GOE
        columns = st.columns(11)  # Create 11 columns for -5 to +5
        for i, val in enumerate(range(-5, 6)):
            display_val = f"+{val}" if val > 0 else str(val)  # Add '+' for positive values
            with columns[i]:
                if st.button(display_val, key=f"goe_{val}_{st.session_state.current}", help="Click to select GOE", use_container_width=True):
                    current_element = st.session_state.program[st.session_state.current]
                    if "+" in current_element:  # Handle combos
                        elements = current_element.split("+")
                        base_score = sum(base_values[element] for element in elements)  # Sum base values of combo elements
                    else:
                        base_score = base_values[current_element]

                    score = base_score * (1 + val / 10)  # Apply single GOE to total base score
                    edge_call = st.session_state.edge_calls.get(current_element, '')
                    st.session_state.scores.append((current_element, val, score, edge_call))
                    st.session_state.tes += score
                    st.session_state.current += 1
                    st.rerun()

        # Adjusted Edge Call Buttons Layout to include 2-character spacing between buttons
        call_cols = st.columns(6, gap="medium")  # Create 6 columns with medium gaps for horizontal layout
        for i, call in enumerate(["e", "!", "Q", "U", "D", "V"]):
            with call_cols[i]:
                if st.button(call, key=f"edge_{call}"):
                    st.session_state.edge_calls[st.session_state.program[st.session_state.current]] = call
                    st.rerun()

        if st.button("End Program"):
            st.session_state.current = len(st.session_state.program)
            st.success("Program ended! You can review the scores.")

            # Stop scoring by disabling GOE and edge call inputs
            st.markdown("<div class='sub-header'>Scoring has been completed.</div>", unsafe_allow_html=True)

            # Display final scores prominently
            st.markdown("""
                <div style='display: flex; justify-content: space-around; align-items: center;'>
                    <div class='score-container'>
                        <div class='score-label'>TES</div>
                        <div class='big-score'>{:.2f}</div>
                    </div>
                    <div class='score-container'>
                        <div class='score-label'>PCS</div>
                        <div class='big-score'>{:.2f}</div>
                    </div>
                    <div class='score-container'>
                        <div class='score-label'>TSS</div>
                        <div class='big-score'>{:.2f}</div>
                    </div>
                </div>
            """.format(st.session_state.tes, st.session_state.pcs, st.session_state.tes + st.session_state.pcs - st.session_state.deductions), unsafe_allow_html=True)

            # Provide export options
            protocol_df = pd.DataFrame(st.session_state.scores, columns=["Element", "GOE", "Score", "Edge Call"])
            csv = protocol_df.to_csv(index=False).encode('utf-8')
            st.sidebar.download_button("⬇️ Download CSV", csv, file_name="protocol.csv", mime="text/csv")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(40, 10, "Element", border=1)
            pdf.cell(40, 10, "Base Value", border=1)
            pdf.cell(40, 10, "GOE", border=1)
            pdf.cell(40, 10, "Final Score", border=1)
            pdf.cell(40, 10, "Edge Call", border=1)
            pdf.ln()
            for _, row in protocol_df.iterrows():
                pdf.cell(40, 10, str(row["Element"]), border=1)
                pdf.cell(40, 10, f"{row['Base Value']:.2f}", border=1)
                pdf.cell(40, 10, f"{row['GOE']:.2f}", border=1)
                pdf.cell(40, 10, f"{row['Final Score']:.2f}", border=1)
                pdf.cell(40, 10, str(row["Edge Call"]), border=1)
                pdf.ln()
            # Add summary (TSS, TES, PCS) to the PDF after the table
            pdf.ln(10)
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(0, 10, "Summary", ln=1)
            pdf.set_font("Arial", size=12)
            pdf.cell(60, 10, f"TES: {st.session_state.tes:.2f}", ln=1)
            pdf.cell(60, 10, f"PCS: {st.session_state.pcs:.2f}", ln=1)
            tss = st.session_state.tes + st.session_state.pcs - st.session_state.deductions
            pdf.cell(60, 10, f"TSS: {tss:.2f}", ln=1)
            pdf_file = "protocol_sheet.pdf"
            pdf.output(pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button("📄", f, file_name="protocol_sheet.pdf", mime="application/pdf")

            # Submit Score button for results
            if 'results' not in st.session_state:
                st.session_state.results = {}
            if st.button("Submit Score", key="submit_score_button"):
                skater_name = st.session_state.skater_name if not st.session_state.competition_mode else st.session_state.selected_skater
                st.session_state.results[skater_name] = {
                    'TES': st.session_state.tes,
                    'PCS': st.session_state.pcs,
                    'Deductions': st.session_state.deductions,
                    'TSS': tss,
                    'protocol': protocol_df.copy()
                }
                st.success(f"Score submitted for {skater_name}!")

            # Allow program reset
            if st.button("Reset Program", key="reset_program_end_button"):
                st.session_state.program = []
                st.session_state.current = 0
                st.session_state.scores = []
                st.session_state.tes = 0.0
                st.session_state.edge_calls = {}
                st.success("Program has been reset.")
    else:
        # --- Element Entry Section with Click-to-Autofill Suggestions ---
        def autocomplete_suggestions(input_text, options):
            if not input_text:
                return []
            input_upper = input_text.upper()
            # If input is valid, return no suggestions
            if input_upper in options:
                return []
            # Otherwise, return 3 closest options by Levenshtein distance
            distances = [(option, levenshtein_distance(input_upper, option)) for option in options]
            distances.sort(key=lambda x: x[1])
            return [option for option, _ in distances[:3]]

        user_input = st.text_input(
            "Enter element codes (e.g., 3A, 2T+2T):",
            key="element_autocomplete"
        )

        all_element_options = list(base_values.keys())
        autocomplete_options = autocomplete_suggestions(user_input, all_element_options)

        if autocomplete_options:
            st.markdown("**Did you mean?**", unsafe_allow_html=True)
            sugg_cols = st.columns(len(autocomplete_options))
            for i, suggestion in enumerate(autocomplete_options):
                with sugg_cols[i]:
                    if st.button(suggestion, key=f"suggestion_coach_{i}_{suggestion}"):
                        st.session_state.element_autocomplete = suggestion
                        st.rerun()

        if st.session_state.competition_mode:
            if st.session_state.selected_skater and st.session_state.selected_skater in st.session_state.skaters:
                program_list = st.session_state.skaters[st.session_state.selected_skater]['program']
                if program_list:
                    st.markdown('**Current Program for ' + st.session_state.selected_skater + ':**')
                    for idx, elem in enumerate(program_list):
                        col1, col2 = st.columns([6, 1])
                        with col1:
                            st.write(elem)
                        with col2:
                            if st.button('❌', key=f'del_elem_{st.session_state.selected_skater}_{idx}'):
                                program_list.pop(idx)
                                st.rerun()
                if st.button("Add Elements"):
                    if user_input:
                        input_list = [item.strip().upper() for item in user_input.split(",")]
                        valid_elements = []
                        invalid_elements = []
                        for item in input_list:
                            parts = [p.strip() for p in item.split("+")]
                            if 1 <= len(parts) <= 3 and all(part in base_values for part in parts):
                                valid_elements.append("+".join(parts))
                            else:
                                invalid_elements.append(item)
                        if invalid_elements:
                            st.error(f"Invalid element(s): {', '.join(invalid_elements)}. Please check your input.")
                        if valid_elements:
                            program_list.extend(valid_elements)
                            st.success(f"Added element(s): {', '.join(valid_elements)}")
                    else:
                        st.error("Please enter a valid element code.")
                col_start, spacer, col_reset = st.columns([1, 0.1, 1])
                with col_start:
                    start_clicked = st.button("Start Program", key=f"start_program_col_{st.session_state.selected_skater}")
                with col_reset:
                    reset_clicked = st.button("❌", key=f"reset_program_col_{st.session_state.selected_skater}")
                if reset_clicked:
                    st.session_state.skaters[st.session_state.selected_skater]['program'] = []
                    st.session_state.skaters[st.session_state.selected_skater]['current'] = 0
                    st.session_state.skaters[st.session_state.selected_skater]['scores'] = []
                    st.session_state.skaters[st.session_state.selected_skater]['tes'] = 0.0
                    st.session_state.skaters[st.session_state.selected_skater]['edge_calls'] = {}
                    st.success("Program has been reset.")
                if program_list:
                    st.write("Program: " + ", ".join(program_list))
                if start_clicked:
                    if program_list:
                        st.session_state.skaters[st.session_state.selected_skater]['current'] = 0
                        st.session_state.program = program_list
                        st.session_state.current = 0
                        st.session_state.scores = []
        if autocomplete_options:
            st.markdown("**Did you mean?**", unsafe_allow_html=True)
            sugg_cols = st.columns(len(autocomplete_options))
            for i, suggestion in enumerate(autocomplete_options):
                with sugg_cols[i]:
                    if st.button(suggestion, key=f"suggestion_coach_{i}_{suggestion}"):
                        st.session_state.element_autocomplete = suggestion
                        st.rerun()

        if st.session_state.competition_mode:
            if st.session_state.selected_skater and st.session_state.selected_skater in st.session_state.skaters:
                program_list = st.session_state.skaters[st.session_state.selected_skater]['program']
                # Show program with delete buttons for this skater
                if program_list:
                    st.markdown('**Current Program for ' + st.session_state.selected_skater + ':**')
                    for idx, elem in enumerate(program_list):
                        col1, col2 = st.columns([6, 1])
                        with col1:
                            st.write(elem)
                        with col2:
                            if st.button('❌', key=f'del_elem_{st.session_state.selected_skater}_{idx}'):
                                program_list.pop(idx)
                                st.rerun()
                if st.button("Add Elements"):
                    if user_input:
                        input_list = [item.strip().upper() for item in user_input.split(",")]
                        valid_elements = []
                        invalid_elements = []
                        for item in input_list:
                            parts = [p.strip() for p in item.split("+")]
                            if 1 <= len(parts) <= 3 and all(part in base_values for part in parts):
                                valid_elements.append("+".join(parts))
                            else:
                                invalid_elements.append(item)
                        if invalid_elements:
                            st.error(f"Invalid element(s): {', '.join(invalid_elements)}. Please check your input.")
                        if valid_elements:
                            program_list.extend(valid_elements)
                            st.success(f"Added element(s): {', '.join(valid_elements)}")
                    else:
                        st.error("Please enter a valid element code.")
                col_start, spacer, col_reset = st.columns([1, 0.1, 1])
                with col_start:
                    start_clicked = st.button("Start Program", key=f"start_program_col_{st.session_state.selected_skater}")
                with col_reset:
                    reset_clicked = st.button("❌", key=f"reset_program_col_{st.session_state.selected_skater}")
                if reset_clicked:
                    st.session_state.skaters[st.session_state.selected_skater]['program'] = []
                    st.session_state.skaters[st.session_state.selected_skater]['current'] = 0
                    st.session_state.skaters[st.session_state.selected_skater]['scores'] = []
                    st.session_state.skaters[st.session_state.selected_skater]['tes'] = 0.0
                    st.session_state.skaters[st.session_state.selected_skater]['edge_calls'] = {}
                    st.success("Program has been reset.")
                if program_list:
                    st.write("Program: " + ", ".join(program_list))
                if start_clicked:
                    if program_list:
                        st.session_state.skaters[st.session_state.selected_skater]['current'] = 0
                        st.session_state.program = program_list
                        st.session_state.current = 0
                        st.session_state.scores = []
                        st.session_state.tes = 0.0
                        st.session_state.edge_calls = {}
                        st.rerun()  # Transition to scoring mode
                    else:
                        st.error("Please add elements to the program before starting.")
            else:
                st.info("Please select a skater to edit their program.")
        else:
            if 'program' not in st.session_state:
                st.session_state.program = []
            program_list = st.session_state.program

            # Show program with delete buttons
            if program_list:
                st.markdown('**Current Program:**')
                for idx, elem in enumerate(program_list):
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        st.write(elem)
                    with col2:
                        if st.button('❌', key=f'del_elem_{idx}'):
                            program_list.pop(idx)
                            st.rerun()

            if st.button("Add Elements"):
                if user_input:
                    input_list = [item.strip().upper() for item in user_input.split(",")]
                    valid_elements = []
                    invalid_elements = []
                    for item in input_list:
                        parts = [p.strip() for p in item.split("+")]
                        if 1 <= len(parts) <= 3 and all(part in base_values for part in parts):
                            valid_elements.append("+".join(parts))
                        else:
                            invalid_elements.append(item)
                    if invalid_elements:
                        st.error(f"Invalid element(s): {', '.join(invalid_elements)}. Please check your input.")
                    if valid_elements:
                        program_list.extend(valid_elements)
                        st.success(f"Added element(s): {', '.join(valid_elements)}")
                else:
                    st.error("Please enter a valid element code.")

            col_start, spacer, col_reset = st.columns([1, 0.1, 1])
            with col_start:
                start_clicked = st.button("Start Program", key="start_program_col")
            with col_reset:
                reset_clicked = st.button("❌", key="reset_program_col")

            if reset_clicked:
                st.session_state.program = []
                st.session_state.current = 0
                st.session_state.scores = []
                st.session_state.tes = 0.0
                st.session_state.edge_calls = {}
                st.success("Program has been reset.")

            if program_list:
                st.write("Program: " + ", ".join(program_list))

            if start_clicked:
                if program_list:
                    st.session_state.current = 0
                    st.rerun()  # Transition to scoring mode
                else:
                    st.error("Please add elements to the program before starting.")

        # Fix the PCS check to avoid TypeError
        if st.session_state.pcs == 0:
            st.warning("You have not adjusted the PCS scores. Please adjust them in the sidebar before proceeding.")

        st.success("All GOE's have been entered! Here is the protocol sheet:")

        # Generate protocol sheet DataFrame
        protocol_df = pd.DataFrame(st.session_state.scores, columns=["Element", "GOE", "Score", "Edge Call"])
        protocol_df["Base Value"] = protocol_df["Element"].apply(
            lambda x: sum(base_values[part] for part in x.split("+") if part in base_values)
        )
        protocol_df["Final Score"] = protocol_df["Base Value"] * (1 + protocol_df["GOE"] / 10)
        protocol_df = protocol_df[["Element", "Base Value", "GOE", "Final Score", "Edge Call"]]

        # Display protocol sheet using Streamlit's built-in table functionality
        st.dataframe(protocol_df.style.set_properties(**{'text-align': 'center'}))

        # Calculate TSS, TES, PCS, and deductions
        tes = float(protocol_df["Final Score"].sum())
        pcs = float(st.session_state.pcs)
        deductions = float(st.session_state.deductions)
        tss = tes + pcs - deductions

        # Display TSS, TES, PCS, and deductions
        st.markdown(f"""
        <div style='margin-top: 20px;'>
            <h3>Summary</h3>
            <p><strong>TES:</strong> {tes:.2f}</p>
            <p><strong>PCS:</strong> {pcs:.2f}</p>
            <p><strong>Deductions:</strong> {deductions:.2f}</p>
            <p><strong>TSS:</strong> {tss:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

        # Provide download options for the protocol sheet
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(40, 10, "Element", border=1)
        pdf.cell(40, 10, "Base Value", border=1)
        pdf.cell(40, 10, "GOE", border=1)
        pdf.cell(40, 10, "Final Score", border=1)
        pdf.cell(40, 10, "Edge Call", border=1)
        pdf.ln()
        for _, row in protocol_df.iterrows():
            pdf.cell(40, 10, str(row["Element"]), border=1)
            pdf.cell(40, 10, f"{row['Base Value']:.2f}", border=1)
            pdf.cell(40, 10, f"{row['GOE']:.2f}", border=1)
            pdf.cell(40, 10, f"{row['Final Score']:.2f}", border=1)
            pdf.cell(40, 10, str(row["Edge Call"]), border=1)
            pdf.ln()
        # Add summary (TSS, TES, PCS) to the PDF after the table
        pdf.ln(10)
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, "Summary", ln=1)
        pdf.set_font("Arial", size=12)
        pdf.cell(60, 10, f"TES: {tes:.2f}", ln=1)
        pdf.cell(60, 10, f"PCS: {pcs:.2f}", ln=1)
        pdf.cell(60, 10, f"TSS: {tss:.2f}", ln=1)
        pdf_file = "protocol_sheet.pdf"
        pdf.output(pdf_file)

        # Place PDF download, Rerun, and Reset buttons on the same row
        col_pdf, col_rerun, col_reset = st.columns([1, 1, 1], gap="large")
        with col_pdf:
            with open(pdf_file, "rb") as f:
                st.download_button("📄", f, file_name="protocol_sheet.pdf", mime="application/pdf")
        with col_rerun:
            if st.button("Rerun Program", key="rerun_program_button"):
                st.session_state.current = 0
                st.session_state.scores = []
                st.session_state.tes = 0.0
                st.session_state.edge_calls = {}
                st.rerun()
        with col_reset:
            if st.button("❌", key="reset_program_button"):
                st.session_state.program = []
                st.session_state.current = 0
                st.session_state.scores = []
                st.session_state.tes = 0.0
                st.session_state.edge_calls = {}
                st.success("Program has been reset.")

# Prediction Tab
with tabs[1]:
    # --- Prediction Page Content ---
    st.markdown(f"<div class='main-title'>⛸️ Prediction Mode</div>", unsafe_allow_html=True)
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

# Skater Management Tab
with tabs[2]:
    st.markdown("<div class='main-title'>⛸️ Skater Management</div>", unsafe_allow_html=True)
    new_skater = st.text_input("Add Skater Name", key="add_skater_mgmt")
    categories = ["Mens", "Ladies"]
    adult_levels = [
        "Adult Pre-Bronze", "Adult Bronze", "Adult Silver", "Adult Gold", "Adult Masters"
    ]
    levels = [
        "Basic Novice", "Intermediate Novice", "Advanced Novice", "Junior", "Senior"
    ] + adult_levels
    programs = ["Free Skating", "Short Program", "Rhythm Dance", "Artistic"]
    selected_category = st.selectbox("Select Category", categories, key="select_category_mgmt")
    selected_level = st.selectbox("Select Level", levels, key="select_level_mgmt")
    selected_program = st.selectbox("Select Program Type", programs, key="select_program_mgmt")
    if st.button("Add Skater", key="add_skater_btn_mgmt"):
        if new_skater and new_skater not in st.session_state.skaters:
            st.session_state.skaters[new_skater] = {
                'category': selected_category,
                'level': selected_level,
                'program_type': selected_program,
                'program': [],
                'scores': [],
                'tes': 0.0,
                'pcs': 0.0,
                'deductions': 0,
                'current': 0,
                'edge_calls': {}
            }
            st.session_state.selected_skater = new_skater
            st.success(f"Skater {new_skater} added successfully!")
            st.rerun()
        elif new_skater in st.session_state.skaters:
            st.warning("Skater already exists.")
        else:
            st.warning("Please enter a valid name.")
    # Skater selection and program setup
    if st.session_state.skaters:
        skater_list = list(st.session_state.skaters.keys())
        selected = st.selectbox("Select Skater", skater_list, index=skater_list.index(st.session_state.selected_skater) if st.session_state.selected_skater in skater_list else 0, key="select_skater_mgmt")
        st.session_state.selected_skater = selected
        skater = st.session_state.selected_skater
        if skater:
            skater_info = st.session_state.skaters[skater]
            st.markdown(f"**Category:** {skater_info['category']}  ")
            st.markdown(f"**Level:** {skater_info['level']}  ")
            st.markdown(f"**Program Type:** {skater_info['program_type']}  ")
            # Program Entry
            user_input = st.text_input(f"Enter element codes for {skater} (e.g., 3A, 2T+2T):", key=f"element_autocomplete_mgmt_{skater}")
            program_list = skater_info['program']
            all_element_options = list(base_values.keys())
            autocomplete_options = autocomplete_suggestions(user_input, all_element_options)
            if autocomplete_options:
                st.markdown("**Did you mean?**", unsafe_allow_html=True)
                sugg_cols = st.columns(len(autocomplete_options))
                for i, suggestion in enumerate(autocomplete_options):
                    with sugg_cols[i]:
                        # Unique key for each suggestion button
                        if st.button(suggestion, key=f"suggestion_mgmt_{skater}_{i}_{suggestion}"):
                            st.session_state[f"element_autocomplete_mgmt_{skater}"] = suggestion
                            st.rerun()
            if program_list:
                st.markdown('**Current Program:**')
                for idx, elem in enumerate(program_list):
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        st.write(elem)
                    with col2:
                        if st.button('❌', key=f'del_elem_mgmt_{skater}_{idx}'):
                            program_list.pop(idx)
                            st.rerun()
            if st.button("Add Elements", key=f"add_elements_mgmt_{skater}"):
                if user_input:
                    input_list = [item.strip().upper() for item in user_input.split(",")]
                    valid_elements = []
                    invalid_elements = []
                    for item in input_list:
                        parts = [p.strip() for p in item.split("+")]
                        if 1 <= len(parts) <= 3 and all(part in base_values for part in parts):
                            valid_elements.append("+".join(parts))
                        else:
                            invalid_elements.append(item)
                    if invalid_elements:
                        st.error(f"Invalid element(s): {', '.join(invalid_elements)}. Please check your input.")
                    if valid_elements:
                        program_list.extend(valid_elements)
                        st.success(f"Added element(s): {', '.join(valid_elements)}")
                else:
                    st.error("Please enter a valid element code.")
            if st.button("Reset Program", key=f"reset_program_mgmt_{skater}"):
                skater_info['program'] = []
                skater_info['current'] = 0
                skater_info['scores'] = []
                skater_info['tes'] = 0.0
                skater_info['edge_calls'] = {}
                st.success("Program has been reset.")

# Competition Tab
with tabs[3]:
    # --- Competition Page Content ---
    st.markdown("<div class='main-title'>⛸️ Competition Mode</div>", unsafe_allow_html=True)
    # Only scoring for already-added skaters
    if st.session_state.skaters:
        skater_list = list(st.session_state.skaters.keys())
        selected = st.selectbox("Select Skater", skater_list, index=skater_list.index(st.session_state.selected_skater) if st.session_state.selected_skater in skater_list else 0, key="select_skater_comp")
        st.session_state.selected_skater = selected
        skater = st.session_state.selected_skater
        if skater:
            skater_info = st.session_state.skaters[skater]
            program_list = skater_info['program']
            col_start, col_reset = st.columns([1, 1])
            with col_start:
                if st.button("Start Scoring", key=f"start_scoring_comp_{skater}"):
                    if program_list:
                        st.session_state.competition_scoring = skater
                        skater_info['current'] = 0
                        skater_info['scores'] = []
                        skater_info['tes'] = 0.0
                        skater_info['edge_calls'] = {}
                        st.session_state.page = "Competition"
                        st.rerun()
                    else:
                        st.error("Please add elements to the program before starting.")
            with col_reset:
                if st.button("Reset Program", key=f"reset_program_comp_{skater}"):
                    skater_info['program'] = []
                    skater_info['current'] = 0
                    skater_info['scores'] = []
                    skater_info['tes'] = 0.0
                    skater_info['edge_calls'] = {}
                    st.success("Program has been reset.")
    # Scoring Mode
    if st.session_state.competition_scoring:
        skater = st.session_state.competition_scoring
        skater_info = st.session_state.skaters[skater]
        program_list = skater_info['program']
        current = skater_info['current']
        scores = skater_info['scores']
        tes = skater_info['tes']
        edge_calls = skater_info['edge_calls']

        st.markdown(f"### Scoring: {skater}")
        st.progress((current) / len(program_list) if program_list else 0, text=f"Element {current+1} of {len(program_list)}")

        if current < len(program_list):
            st.markdown(f"<div class='current-element'>{program_list[current]}</div>", unsafe_allow_html=True)
            columns = st.columns(11)
            for i, val in enumerate(range(-5, 6)):
                display_val = f"+{val}" if val > 0 else str(val)
                with columns[i]:
                    if st.button(display_val, key=f"goe_{val}_{skater}_{current}"):
                        element = program_list[current]
                        if "+" in element:
                            elements = element.split("+")
                            base_score = sum(base_values[e] for e in elements)
                        else:
                            base_score = base_values[element]
                        score = base_score * (1 + val / 10)
                        edge_call = edge_calls.get(element, '')
                        scores.append((element, val, score, edge_call))
                        tes += score
                        skater_info['current'] = current + 1
                        skater_info['scores'] = scores
                        skater_info['tes'] = tes
                        skater_info['edge_calls'] = edge_calls
                        st.rerun()

            call_cols = st.columns(6)
            for i, call in enumerate(["e", "!", "Q", "U", "D", "V"]):
                with call_cols[i]:
                    if st.button(call, key=f"edge_{call}_{skater}_{current}"):
                        edge_calls[program_list[current]] = call
                        skater_info['edge_calls'] = edge_calls
                        st.rerun()

        else:
            st.success("Program ended! You can review the scores.")
            protocol_df = pd.DataFrame(scores, columns=["Element", "GOE", "Score", "Edge Call"])
            protocol_df["Base Value"] = protocol_df["Element"].apply(
                lambda x: sum(base_values[part] for part in x.split("+") if part in base_values)
            )
            protocol_df["Final Score"] = protocol_df["Base Value"] * (1 + protocol_df["GOE"] / 10)
            protocol_df = protocol_df[["Element", "Base Value", "GOE", "Final Score", "Edge Call"]]
            st.dataframe(protocol_df.style.set_properties(**{'text-align': 'center'}))
            tes = float(protocol_df["Final Score"].sum())
            pcs = float(st.session_state.pcs)
            deductions = float(st.session_state.deductions)
            tss = tes + pcs - deductions
            st.markdown(f"""
            <div style='margin-top: 20px;'>
                <h3>Summary</h3>
                <p><strong>TES:</strong> {tes:.2f}</p>
                <p><strong>PCS:</strong> {pcs:.2f}</p>
                <p><strong>Deductions:</strong> {deductions:.2f}</p>
                <p><strong>TSS:</strong> {tss:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Submit Score", key=f"submit_score_{skater}"):
                if 'results' not in st.session_state:
                    st.session_state.results = {}
                st.session_state.results[skater] = {
                    'TES': tes,
                    'PCS': pcs,
                    'Deductions': deductions,
                    'TSS': tss,
                    'protocol': protocol_df.copy()
                }
                skater_info['current'] = 0
                skater_info['scores'] = []
                skater_info['tes'] = 0.0
                skater_info['edge_calls'] = {}
                st.session_state.competition_scoring = None
                st.success(f"Score submitted for {skater}!")
                st.rerun()

# Results Tab
with tabs[4]:
    st.markdown(f"<div class='main-title'>⛸️ Results</div>", unsafe_allow_html=True)
    if 'results' in st.session_state and st.session_state.results:
        # Prepare results DataFrame with category and level
        results_data = [
            {
                'Skater': skater,
                'Category': st.session_state.skaters[skater]['category'] if skater in st.session_state.skaters else '',
                'Level': st.session_state.skaters[skater]['level'] if skater in st.session_state.skaters else '',
                'TSS': data['TSS'],
                'TES': data['TES'],
                'PCS': data['PCS'],
                'Deductions': data['Deductions'],
                'protocol': data['protocol']
            }
            for skater, data in st.session_state.results.items()
        ]
        results_df = pd.DataFrame(results_data)
        # Group by Category and Level
        grouped = results_df.groupby(['Category', 'Level'])
        for (cat, lvl), group in grouped:
            group_sorted = group.sort_values(by='TSS', ascending=False).reset_index(drop=True)
            st.markdown(f"### {cat} - {lvl}")
            st.dataframe(group_sorted[['Skater', 'TSS', 'TES', 'PCS', 'Deductions']].style.format({'TSS': '{:.2f}', 'TES': '{:.2f}', 'PCS': '{:.2f}', 'Deductions': '{:.2f}'}))
            # Leaderboard
            st.markdown(f"**Leaderboard:** 🏆")
            for idx, row in group_sorted.iterrows():
                st.markdown(f"{idx+1}. **{row['Skater']}** — TSS: {row['TSS']:.2f}")
            # Protocol sheets
            for idx, row in group_sorted.iterrows():
                with st.expander(f"Protocol Sheet for {row['Skater']}"):
                    st.dataframe(row['protocol'].style.format({'Base Value': '{:.2f}', 'GOE': '{:.2f}', 'Final Score': '{:.2f}'}))
                    if st.button(f"Download Protocol Sheet for {row['Skater']}", key=f"download_pdf_{cat}_{lvl}_{row['Skater']}"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", style="B", size=14)
                        pdf.cell(0, 10, f"Protocol Sheet: {row['Skater']}", ln=1, align='C')
                        pdf.set_font("Arial", size=12)
                        pdf.cell(40, 10, "Element", border=1)
                        pdf.cell(40, 10, "Base Value", border=1)
                        pdf.cell(40, 10, "GOE", border=1)
                        pdf.cell(40, 10, "Final Score", border=1)
                        pdf.cell(40, 10, "Edge Call", border=1)
                        pdf.ln()
                        for _, prow in row['protocol'].iterrows():
                            pdf.cell(40, 10, str(prow["Element"]), border=1)
                            pdf.cell(40, 10, f"{prow['Base Value']:.2f}", border=1)
                            pdf.cell(40, 10, f"{prow['GOE']:.2f}", border=1)
                            pdf.cell(40, 10, f"{prow['Final Score']:.2f}", border=1)
                            pdf.cell(40, 10, str(prow["Edge Call"]), border=1)
                            pdf.ln()
                        pdf.ln(10)
                        pdf.set_font("Arial", style="B", size=12)
                        pdf.cell(0, 10, "Summary", ln=1)
                        pdf.set_font("Arial", size=12)
                        pdf.cell(60, 10, f"TES: {row['TES']:.2f}", ln=1)
                        pdf.cell(60, 10, f"PCS: {row['PCS']:.2f}", ln=1)
                        pdf.cell(60, 10, f"TSS: {row['TSS']:.2f}", ln=1)
                        pdf_file = f"protocol_sheet_{cat}_{lvl}_{row['Skater']}.pdf"
                        pdf.output(pdf_file)
                        with open(pdf_file, "rb") as f:
                            st.download_button(f"📄 Download PDF for {row['Skater']}", f, file_name=pdf_file, mime="application/pdf")
    else:
        st.info("No results submitted yet. Score and submit at least one skater to see results here.")

# --------------------------
# Footer (unchanged)
# --------------------------
st.markdown("""
    <div class='footer'>
        ⛸️ Rhubarb & Custard Skating Scorer — lovingly made by a code nerd on ice. ✨<br>
    </div>
""", unsafe_allow_html=True)
