# RhuCus Skating Scorer

RhuCus is a figure skating scoring app built with Streamlit. It allows you to enter, score, and manage skating programs for one or multiple skaters, including full competition management and protocol sheet export.

## Features

- Add and manage multiple skaters and their unique programs
- Score elements with GOE, edge calls, and deductions
- Per-skater PCS and deduction management
- Competition mode for multi-skater events
- Results page with sortable scores and downloadable protocol sheets (PDF/CSV)
- Touch-friendly UI and progress bars for scoring
- Works fully offline; can be packaged as a desktop app

## Setup

1. **Clone or download this repository**
2. **Install dependencies:**

   ```bash
   pip3 install -r requirements.txt
   ```

   For desktop mode, also install:

   ```bash
   pip3 install pywebview
   ```

3. **Run the app:**

   ```bash
   streamlit run skating_scorer.py
   ```

   The app will open in your browser at <http://localhost:8501>

## Usage

- **Coach Mode:** Enter and score a single program.
- **Competition Mode:** Add multiple skaters, assign programs, and score each skater independently.
- **Results:** View and export all skaters' scores and protocol sheets.
- **Offline/Desktop:** Use with PyInstaller and pywebview to create a native desktop app (see code comments for details).

## Export & Protocol Sheets

- Download protocol sheets as PDF or CSV from the Results page.
- Each skater’s protocol includes their name and detailed scoring breakdown.

## Customization

- Edit `config.toml` to change the app’s color theme.

---

Made with ❤️ by a code nerd on ice.
