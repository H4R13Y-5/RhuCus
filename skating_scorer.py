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

# Ensure 'page' is initialized in session state before any access
if 'page' not in st.session_state:
    st.session_state.page = 'Coach'

def toggle_sidebar():
    st.session_state.sidebar_state = (
        "expanded" if st.session_state.sidebar_state == "collapsed" else "collapsed"
    )
    st.rerun()

st.sidebar.button("Toggle Sidebar", on_click=toggle_sidebar, key="toggle_sidebar_button")

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

# --------------------------
# Navigation Buttons: Coach, Prediction, Glossary
# --------------------------
nav_cols = st.columns([1, 1, 1])
with nav_cols[0]:
    if st.button("Coach", key="nav_coach_col"):
        st.session_state.page = "Coach"
with nav_cols[1]:
    if st.button("Prediction", key="nav_prediction_col"):
        st.session_state.page = "Prediction"
with nav_cols[2]:
    if st.button("Glossary", key="nav_glossary_col"):
        st.session_state.page = "Glossary"

# Ensure 'page' is initialized
if 'page' not in st.session_state:
    st.session_state.page = "Coach"

# Display the selected page
st.write(f"**Current Page:** {st.session_state.page}")

# --------------------------
# Show page content based on current page
# --------------------------
st.markdown(f"<div class='main-title'>⛸️ {st.session_state.page} Mode</div>", unsafe_allow_html=True)

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

if st.session_state.page == "Coach":
    if st.session_state.current < len(st.session_state.program):
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
            for col in protocol_df.columns:
                pdf.cell(40, 10, col, border=1)
            pdf.ln()
            for _, row in protocol_df.iterrows():
                for item in row:
                    pdf.cell(40, 10, str(item), border=1)
                pdf.ln()
            pdf_file = "protocol_sheet.pdf"
            pdf.output(pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button("📄", f, file_name="protocol_sheet.pdf", mime="application/pdf")

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
            suggestions = [option for option in options if option.startswith(input_text.upper())]
            return suggestions[:10]

        user_input = st.text_input(
            "Enter element codes (e.g., 3A, 2T+2T):",
            key="element_autocomplete"
        )

        all_element_options = list(base_values.keys())
        autocomplete_options = autocomplete_suggestions(user_input, all_element_options)

        # Display clickable suggestions below the text input
        if autocomplete_options:
            st.markdown("**Suggestions:**", unsafe_allow_html=True)
            sugg_cols = st.columns(len(autocomplete_options))
            for i, suggestion in enumerate(autocomplete_options):
                with sugg_cols[i]:
                    if st.button(suggestion, key=f"suggestion_{suggestion}"):
                        st.session_state.element_autocomplete = suggestion
                        st.experimental_rerun()

        if st.button("Add Elements"):
            if user_input:
                input_list = [item.strip().upper() for item in user_input.split(",")]
                invalid_elements = [item for item in input_list if item not in base_values]
                valid_elements = [item for item in input_list if item in base_values]
                if invalid_elements:
                    st.error(f"Invalid element(s): {', '.join(invalid_elements)}. Please check your input.")
                if valid_elements:
                    st.session_state.program.extend(valid_elements)
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

        if st.session_state.program:
            st.write("Program: " + ", ".join(st.session_state.program))

        if start_clicked:
            if st.session_state.program:
                st.session_state.current = 0
                st.rerun()  # Transition to scoring mode
            else:
                st.error("Please add elements to the program before starting.")

    # Fix the PCS check to avoid TypeError
    if st.session_state.pcs == 0:
        st.warning("You have not adjusted the PCS scores. Please adjust them in the sidebar before proceeding.")
        st.stop()  # Stop further execution until PCS scores are adjusted

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
        pdf.cell(40, 10, str(row["GOE"]), border=1)
        pdf.cell(40, 10, f"{row['Final Score']:.2f}", border=1)
        pdf.cell(40, 10, str(row["Edge Call"]), border=1)
        pdf.ln()
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

elif st.session_state.page == "Prediction":
    # Prediction Mode Content
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
    **Edge Calls:** `Q`, `U`, `e`, `!` indicating unclear or wrong takeoffs.
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
