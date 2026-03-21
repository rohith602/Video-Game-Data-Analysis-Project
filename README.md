# Video Game Sales Analysis Dashboard

## Project Overview
A professional, full-stack data visualization platform built to analyze global video game sales trends across decades. This project transforms a dataset of over 16,500 records into 10 high-fidelity, interactive charts, providing deep insights into market dynamics, regional correlations, and genre evolution.

## Key Features
- **Advanced Data Pipeline**: Built with **Flask** and **Pandas**, featuring robust data cleaning and mathematical normalization.
- **Scientific Visualizations**: Includes 10 unique chart types ranging from standard line/bar plots to advanced **Log-Scale KDE**, **SymLog Scatter Plots**, and **Hexagonal Binning**.
- **OLED Dark Mode UI**: A premium, high-contrast interface designed for maximum visual clarity and modern aesthetics.
- **Statistical Rigor**: Implements custom bandwidth smoothing for density plots and logarithmic scaling to accurately visualize highly skewed sales data (e.g., handling extreme outliers like *Wii Sports*).
- **Optimized Performance**: Minimized full-stack architecture with programmatic UI rendering for lightning-fast analysis execution.

## Tech Stack
- **Backend**: Python, Flask, Pandas, NumPy, SciPy
- **Frontend**: HTML5, Vanilla CSS3 (Custom Grid System), JavaScript (ES6+)
- **DataViz**: Matplotlib (Custom OLED Theme)

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python app.py`
3. View the dashboard: Open `http://127.0.0.1:5000` in your browser.
