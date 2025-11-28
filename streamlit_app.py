# streamlit_app.py

import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import tempfile
from datetime import datetime
from fpdf import FPDF
from spark_app import run_full_pipeline_from_df, TARGET_COL, TIMESTAMP_COL
def inject_css():
    # Hardcoded Dark Theme Colors
    bg = "#000000"          # Pure black
    bg_elevated = "#121212" # Very dark gray for cards
    bg_deep = "#000000"
    text = "#ffffff"        # Pure white
    text_muted = "#a3a3a3"  # Light gray
    accent = "#00bcd4"      # Cyan accent
    accent_soft = "#000000"
    accent_alt = "#00e676"
    card_shadow = "none"

    st.markdown(
        f"""
        <style>
        /* ------------------ GLOBAL ------------------ */
        .stApp {{
            background-color: {bg};
            color: {text};
            font-family: "Courier New", Courier, monospace;
        }}
        .block-container {{
            padding-top: 3rem;
            padding-bottom: 3rem;
            padding-left: 4rem;
            padding-right: 4rem;
            max-width: 100%;
        }}
        h1, h2, h3, h4 {{
            color: {text} !important;
        }}
        p, label, span, div {{
            color: {text_muted} !important;
        }}

        /* ------------------ NAVBAR ------------------ */
        .ev-navbar {{
            width: 100%;
            border-radius: 18px;
            padding: 1.1rem 1.8rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(90deg, #0f172a, {accent});
            box-shadow: {card_shadow};
        }}
        .ev-navbar-left {{
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }}
        .ev-logo {{
            width: 38px;
            height: 38px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at 30% 0%, #38bdf8, #0ea5e9 40%, #0284c7 75%);
            box-shadow: 0 0 18px rgba(248,250,252,0.45);
            font-size: 1.4rem;
        }}
        
        .ev-title-main {{
            font-weight: 600;
            font-size: 1.2rem;
            color: {text} !important;
        }}
        .ev-title-sub {{
            font-size: 0.78rem;
            color: {text_muted} !important;
        }}
        .ev-chip {{
            font-size: 0.78rem;
            padding: 0.25rem 0.8rem;
            border-radius: 999px;
            background: {accent_soft};
            color: {accent} !important;
            font-weight: 600;
            border: 1px solid rgba(148,163,184,0.25);
        }}
        
        /* ------------------ CARDS ------------------ */
        .ev-card {{
            border-radius: 20px;
            padding: 1.6rem 1.8rem;
            background: {bg_elevated};
            box-shadow: {card_shadow};
            margin-top: 1.4rem;
        }}
        .ev-card-hero {{
            border-radius: 24px;
            padding: 1.7rem 2rem;
            background: linear-gradient(135deg, {bg_deep}, {accent_soft});
            box-shadow: {card_shadow};
            margin-top: 1.4rem;
            margin-bottom: 1.6rem;
        }}
        .ev-section-title {{
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: {text} !important;
        }}
        .ev-section-caption {{
            font-size: 0.88rem;
            color: {text_muted} !important;
        }}
        /* ------------------ METRIC CARDS ------------------ */
        .ev-metric-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0,1fr));
            gap: 1.1rem;
            margin-top: 1rem;
        }}
        .ev-metric-card {{
            border-radius: 16px;
            padding: 1rem 1.1rem;
            background: {bg_elevated};
            box-shadow: {card_shadow};
            border: 1px solid rgba(148,163,184,0.18);
        }}
        .ev-metric-label {{
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {text_muted} !important;
            margin-bottom: 0.3rem;
        }}
        .ev-metric-value {{
            font-size: 1.32rem;
            font-weight: 600;
            color: {text} !important;
        }}

        /* ------------------ BUTTONS ------------------ */
        .stButton>button, .stDownloadButton>button {{
            width: 100%;
            padding: 0.9rem 1.1rem;
            border-radius: 999px;
            border: none;
            font-weight: 500;
            font-size: 0.95rem;
            background: {accent};
            color: white !important;
            box-shadow: 0 14px 30px rgba(15,23,42,0.35);
        }}

        .stButton>button:hover, .stDownloadButton>button:hover {{
            filter: brightness(1.05);
            transform: translateY(-1px);
        }}

        /* Secondary button styling */
        .ev-secondary-btn>button {{
            background: transparent !important;
            color: {accent} !important;
            border: 1px solid rgba(148,163,184,0.6) !important;
            box-shadow: none !important;
        }}

        /* ------------------ TABLE / FILE UPLOADER ------------------ */
        section[data-testid="stFileUploader"] > div {{
            border-radius: 18px;
            background: {bg_elevated};
        }}

        /* ------------------ CHART CARDS ------------------ */
        .ev-chart-card {{
            border-radius: 18px;
            padding: 1.2rem 1.3rem;
            background: {bg_elevated};
            box-shadow: {card_shadow};
        }}

        /* Small badge */
        .ev-badge-soft {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background: {accent_soft};
            color: {accent};
            font-size: 0.75rem;
            font-weight: 500;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )

def generate_pdf_report(df, metrics, charts):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Water Bill Prediction Report", ln=True, align="C")

    pdf.ln(4)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        "This report summarizes Spark preprocessing and RandomForest predictions "
        "for Water Bill amounts based on the uploaded dataset.",
    )

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Model Performance", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"R² Score: {metrics['r2']:.4f}", ln=True)
    pdf.cell(0, 6, f"RMSE: {metrics['rmse']:.4f}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Dataset Overview", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"Rows: {len(df)}", ln=True)
    pdf.cell(0, 6, f"Columns: {len(df.columns)}", ln=True)
    import matplotlib.pyplot as plt
    import tempfile
    for title, fig in charts.items():
        pdf.add_page()
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, title, ln=True)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            fig.savefig(tmp.name, bbox_inches="tight")
            pdf.image(tmp.name, x=10, y=28, w=190)
        plt.close(fig)
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes

def plot_time_series(df):
    if TIMESTAMP_COL not in df.columns or TARGET_COL not in df.columns:
        return None
    df2 = df.copy()
    df2[TIMESTAMP_COL] = pd.to_datetime(df2[TIMESTAMP_COL])
    df2 = df2.sort_values(TIMESTAMP_COL)

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(df2[TIMESTAMP_COL], df2[TARGET_COL], label="Actual Bill", linewidth=1.2)
    if "Predicted_Bill_Amount" in df2.columns:
        ax.plot(
            df2[TIMESTAMP_COL],
            df2["Predicted_Bill_Amount"],
            linestyle="--",
            label="Predicted Bill",
            linewidth=1.1,
        )
    ax.set_title("Actual vs Predicted Bill Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amount")
    ax.legend()
    plt.xticks(rotation=25)
    plt.tight_layout()
    return fig

def plot_actual_vs_pred_scatter(df):
    if "Predicted_Bill_Amount" not in df.columns or TARGET_COL not in df.columns:
        return None
    fig, ax = plt.subplots(figsize=(4.5, 3.2))
    ax.scatter(df[TARGET_COL], df["Predicted_Bill_Amount"], alpha=0.4)
    ax.set_title("Actual vs Predicted (Scatter)")
    ax.set_xlabel("Actual Bill")
    ax.set_ylabel("Predicted Bill")
    plt.tight_layout()
    return fig

def plot_error_hist(df):
    if "Predicted_Bill_Amount" not in df.columns or TARGET_COL not in df.columns:
        return None
    errors = df["Predicted_Bill_Amount"] - df[TARGET_COL]
    fig, ax = plt.subplots(figsize=(4.5, 3.2))
    ax.hist(errors, bins=40)
    ax.set_title("Prediction Error Distribution")
    ax.set_xlabel("Error (Predicted - Actual)")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    return fig

def main():
    # Force simple dark theme
    inject_css()
    st.set_page_config(
        page_title="Water Bill Predictions",
        layout="wide",
    )

    # # --------------------------------------------------
    # # CLEAN FIXED NAVBAR (NO LEAKED CODE)
    # # --------------------------------------------------

    # col_nav = st.container()
    # with col_nav:

    #     navbar_html = f"""
    #     <style>
    #         .ev-navbar {{
    #             display: flex;
    #             justify-content: space-between;
    #             align-items: center;
    #             padding: 18px 30px;
    #             width: 100%;
    #             border-radius: 12px;
    #             background: {'#0d1117' if theme=='dark' else '#e9f5ff'};
    #             box-shadow: 0 3px 12px rgba(0,0,0,0.25);
    #         }}
    #         .ev-navbar-left {{
    #             display: flex;
    #             gap: 18px;
    #             align-items: center;
    #         }}
    #         .ev-logo {{
    #             font-size: 33px;
    #         }}
    #         .ev-title-main {{
    #             font-size: 21px;
    #             font-weight: 700;
    #             color: {'white' if theme=='dark' else '#000'};
    #         }}
    #         .ev-title-sub {{
    #             font-size: 13px;
    #             color: {'#9ca3af' if theme=='dark' else '#333'};
    #         }}
    #         .ev-navbar-right {{
    #             display: flex;
    #             align-items: center;
    #             gap: 20px;
    #         }}
    #         .ev-chip {{
    #             padding: 6px 14px;
    #             border-radius: 20px;
    #             font-size: 13px;
    #             background: {'#1f2937' if theme=='dark' else '#d0e7ff'};
    #             color: {'white' if theme=='dark' else '#003366'};
    #             font-weight: 600;
    #         }}
    #         .ev-theme-btn {{
    #             padding: 10px 20px;
    #             border-radius: 25px;
    #             border: none;
    #             background: #3ea8ff;
    #             color: black;
    #             font-size: 14px;
    #             font-weight: 600;
    #             cursor: pointer;
    #         }}
    #     </style>

    #     <div class="ev-navbar">

    #         <div class="ev-navbar-left">
    #             <div class="ev-logo">💧</div>
    #             <div>
    #                 <div class="ev-title-main">Water Bill Predictions</div>
    #                 <div class="ev-title-sub">Apache Spark · RandomForest · Streamlit Dashboard</div>
    #             </div>
    #         </div>

    #         <div class="ev-navbar-right">
    #             <div class="ev-chip">Big Data Ready</div>
    #             <div class="ev-chip">PDF Reports</div>
    #         </div>

    #     </div>
    #     """

    #     st.markdown(navbar_html, unsafe_allow_html=True)

    #     # THEME TOGGLE BUTTON
    #     toggle_label = "☀ Light Mode" if theme == "dark" else "🌙 Dark Mode"

    #     if st.button(toggle_label, key="real_theme_toggle"):
    #         st.session_state.theme = "light" if theme == "dark" else "dark"
    #         st.rerun()



    # HERO SECTION
    st.markdown(
        """
        <div class="ev-card-hero">
  <div style="max-width:100%;">
    <h2 style="margin-top:0.6rem; margin-bottom:0.3rem;">Water Bill Predictions System</h2>
    <p style="font-size:0.92rem;">
      A simple project that predicts water bills using uploaded CSV data and displays analytics with charts.
    </p>
  </div>
</div>

        """,
        unsafe_allow_html=True,
    )

    # ---------- DATA SOURCE CARD ----------
    # ---------- DATA SOURCE CARD ----------
    st.markdown(
        """
        <div class="ev-card">
          <div class="ev-section-title">1. Data Source</div>
          <div class="ev-section-caption">
            Using the built-in dataset (<code>dataset/Water_Consumption_And_Cost__2013_-_Feb_2023_.csv</code>).
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load local dataset directly
    df = None
    try:
        df = pd.read_csv("dataset/Water_Consumption_And_Cost__2013_-_Feb_2023_.csv")
        
        # Rename columns to match Water Bill terminology immediately
        rename_map = {
            "Service End Date": "Date_Time",
            "Current Charges": "Water_Bill_Amount",
            "Charging_Load_kW": "Water_Bill_Amount"
        }
        df = df.rename(columns=rename_map)
        
        st.success("Loaded local dataset: `dataset/Water_Consumption_And_Cost__2013_-_Feb_2023_.csv`")
        st.success("Loaded local dataset: `dataset/Water_Consumption_And_Cost__2013_-_Feb_2023_.csv`")
        # st.dataframe(df.head(), use_container_width=True) # Hidden as per request
    except Exception as e:
        st.error(f"Failed to load local dataset: {e}")
        return

    # ---------- RUN PIPELINE ----------
    st.markdown(
        """
        <div class="ev-card">
          <div class="ev-section-title">2. Run Spark + RandomForest Pipeline</div>
          <div class="ev-section-caption">
            Spark will clean timestamps and remove categorical columns, then a RandomForestRegressor will be trained 
            to predict <code>Water_Bill_Amount</code>. You’ll get metrics, processed data and visualizations.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Running Spark preprocessing and training RandomForest model…"):
        try:
            predicted_df, metrics = run_full_pipeline_from_df(df)
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            return

    st.success("Pipeline completed successfully ✅")

    # ---------- METRICS + DATA SUMMARY ----------
    rows, cols = predicted_df.shape

    st.markdown(
        f"""
        <div class="ev-metric-grid">
          <div class="ev-metric-card">
            <div class="ev-metric-label">Rows</div>
            <div class="ev-metric-value">{rows:,}</div>
          </div>
          <div class="ev-metric-card">
            <div class="ev-metric-label">Columns</div>
            <div class="ev-metric-value">{cols}</div>
          </div>
          <div class="ev-metric-card">
            <div class="ev-metric-label">R² Score</div>
            <div class="ev-metric-value">{metrics['r2']:.4f}</div>
          </div>
          <div class="ev-metric-card">
            <div class="ev-metric-label">RMSE</div>
            <div class="ev-metric-value">{metrics['rmse']:.4f}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- PROCESSED DATA ----------
    st.markdown(
        """
        <div class="ev-card" style="margin-top:1.8rem;">
          <div class="ev-section-title">3. Processed Data with Predictions</div>
          <div class="ev-section-caption">
            This table shows the Spark-cleaned dataset with the <code>Predicted_Bill_Amount</code> column added by the model.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(predicted_df.head(100), use_container_width=True)

    # ---------- CHARTS ----------
    # ---------- CHARTS ----------
    st.markdown(
        """
        <div class="ev-card" style="margin-top:1.8rem; margin-bottom:1.2rem;">
        <div class="ev-section-title">4. Visual Analytics</div>
        <div class="ev-section-caption">
            Time series, scatter and error-distribution views help you explain model behaviour in your viva.
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    charts = {}

    # TIME SERIES
    fig_ts = plot_time_series(predicted_df)
    if fig_ts:
        st.markdown('<div class="ev-chart-card">', unsafe_allow_html=True)
        st.pyplot(fig_ts)  # FIXED
        st.markdown("</div>", unsafe_allow_html=True)
        charts["Actual vs Predicted Bill Over Time"] = fig_ts

    # SCATTER
    fig_scatter = plot_actual_vs_pred_scatter(predicted_df)
    if fig_scatter:
        st.markdown('<div class="ev-chart-card" style="margin-top:1rem;">', unsafe_allow_html=True)
        st.pyplot(fig_scatter)  # FIXED
        st.markdown("</div>", unsafe_allow_html=True)
        charts["Actual vs Predicted Scatter"] = fig_scatter

    # ERROR HIST
    fig_err = plot_error_hist(predicted_df)
    if fig_err:
        st.markdown('<div class="ev-chart-card" style="margin-top:1rem;">', unsafe_allow_html=True)
        st.pyplot(fig_err)  # FIXED
        st.markdown("</div>", unsafe_allow_html=True)
        charts["Prediction Error Distribution"] = fig_err


    # Export section removed as per request


if __name__ == "__main__":
    main()
