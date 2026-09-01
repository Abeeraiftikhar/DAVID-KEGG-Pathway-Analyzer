import streamlit as st
import pandas as pd
import tempfile
import shutil
import io
import zipfile
from pathlib import Path

from backend.analysis import analyze_kegg
from backend.plots import create_plots


# ===================================================
# PAGE CONFIGURATION
# ===================================================

st.set_page_config(
    page_title="KEGG Enrichment Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===================================================
# SESSION STATE
# ===================================================

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

if "result" not in st.session_state:
    st.session_state.result = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "data" not in st.session_state:
    st.session_state.data = None

if "export_data" not in st.session_state:
    st.session_state.export_data = None

if "bar_chart_bytes" not in st.session_state:
    st.session_state.bar_chart_bytes = None

if "bubble_plot_bytes" not in st.session_state:
    st.session_state.bubble_plot_bytes = None

if "combined_figure_bytes" not in st.session_state:
    st.session_state.combined_figure_bytes = None

if "zip_bytes" not in st.session_state:
    st.session_state.zip_bytes = None


# ===================================================
# CUSTOM CSS
# ===================================================

st.markdown(
    """
    <style>

    /* =========================================
       MAIN APPLICATION
    ========================================= */

    .stApp {
        background-color: #F7F8FC;
        color: #1D2B44;
    }


    /* =========================================
       SIDEBAR
       EXACT DARK NAVY STYLE
    ========================================= */

    [data-testid="stSidebar"] {
        background-color: #171C36 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: #171C36 !important;
    }


    /* Sidebar text */

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #F3F5FA !important;
    }


    /* Sidebar title */

    .sidebar-title {
        font-size: 30px;
        font-weight: 800;
        color: #FFFFFF !important;
        line-height: 1.25;
        margin-top: 20px;
        margin-bottom: 10px;
    }


    /* Sidebar description */

    .sidebar-description {
        font-size: 15px;
        color: #B8C2D9 !important;
        line-height: 1.7;
        margin-bottom: 10px;
    }


    /* Sidebar footer */

    .sidebar-footer {
        color: #B8C2D9 !important;
        font-size: 14px;
        line-height: 1.7;
    }


    /* Sidebar divider */

    [data-testid="stSidebar"] hr {
        border-color: #39415D !important;
        margin-top: 28px;
        margin-bottom: 28px;
    }


    /* Sidebar radio buttons */

    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 7px;
    }


    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 10px 12px;
        border-radius: 8px;
        transition: 0.2s ease;
    }


    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background-color: #263B5C !important;
    }


    /* Navigation text */

    [data-testid="stSidebar"] [role="radiogroup"] label p {
        font-size: 15px !important;
        font-weight: 500;
    }


    /* =========================================
       MAIN CONTENT
    ========================================= */

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #1D2B44;
        margin-bottom: 8px;
    }


    .main-subtitle {
        font-size: 18px;
        color: #68758A;
        margin-bottom: 35px;
    }


    /* =========================================
       INFORMATION BOX
    ========================================= */

    .info-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE2EC;
        border-radius: 16px;
        padding: 25px 30px;
        margin-bottom: 30px;
    }


    /* =========================================
       SECTION HEADINGS
    ========================================= */

    .section-heading {
        font-size: 28px;
        font-weight: 750;
        color: #1D2B44;
        margin-top: 15px;
        margin-bottom: 15px;
    }


    /* =========================================
       METRICS
    ========================================= */

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #DCE2EC;
        border-radius: 12px;
        padding: 18px;
    }


    /* =========================================
       BUTTONS
    ========================================= */

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 18px;
    }


    /* =========================================
       FILE UPLOAD BOXES
    ========================================= */

    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 1px solid #DCE2EC;
        border-radius: 12px;
        padding: 15px;
    }


    /* =========================================
       FOOTER
    ========================================= */

    .footer {
        text-align: center;
        color: #788398;
        font-size: 14px;
        padding-top: 30px;
        padding-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ===================================================
# SIDEBAR
# ===================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            🧬 KEGG Enrichment<br>
            Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-description">
            Pathway enrichment analysis and visualization
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Navigation",
        [
            "📤 Upload & Overview",
            "📊 Analysis",
            "📥 Export",
            "ℹ️ About Us"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### BioCode Innovators")

    st.markdown(
        """
        <div class="sidebar-footer">
            Built for bioinformatics research and genomic insights.
        </div>
        """,
        unsafe_allow_html=True
    )


# ===================================================
# FUNCTION: RUN ANALYSIS
# ===================================================

def run_analysis(up_file, dn_file):

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_dir = Path(temp_dir)

        up_path = temp_dir / "upregulated.csv"
        dn_path = temp_dir / "downregulated.csv"

        # Save uploaded files

        up_path.write_bytes(
            up_file.getvalue()
        )

        dn_path.write_bytes(
            dn_file.getvalue()
        )


        # =============================================
        # RUN ANALYSIS
        # =============================================

        result = analyze_kegg(
            up_path,
            dn_path
        )

        df = result["data"]
        summary = result["summary"]

        export_df = result["export"]


        # =============================================
        # CREATE OUTPUT DIRECTORY
        # =============================================

        output_dir = temp_dir / "output"

        output_dir.mkdir(
            exist_ok=True
        )


        # =============================================
        # CREATE PLOTS
        # =============================================

        create_plots(
            df,
            summary,
            output_dir
        )


        # =============================================
        # FILE PATHS
        # =============================================

        bar_chart = (
            output_dir /
            "KEGG_Bar_Chart.png"
        )

        bubble_plot = (
            output_dir /
            "KEGG_Bubble_Plot.png"
        )

        combined_figure = (
            output_dir /
            "KEGG_Combined_Figure.png"
        )


        # =============================================
        # STORE RESULTS IN SESSION STATE
        # =============================================

        st.session_state.result = result

        st.session_state.data = df

        st.session_state.summary = summary

        st.session_state.export_data = export_df


        # =============================================
        # STORE CHART FILES
        # =============================================

        if bar_chart.exists():

            st.session_state.bar_chart_bytes = (
                bar_chart.read_bytes()
            )

        else:

            st.session_state.bar_chart_bytes = None


        if bubble_plot.exists():

            st.session_state.bubble_plot_bytes = (
                bubble_plot.read_bytes()
            )

        else:

            st.session_state.bubble_plot_bytes = None


        if combined_figure.exists():

            st.session_state.combined_figure_bytes = (
                combined_figure.read_bytes()
            )

        else:

            st.session_state.combined_figure_bytes = None


        # =============================================
        # CREATE ZIP FILE
        # =============================================

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zip_file:


            # Summary CSV

            csv_bytes = (
                export_df
                .to_csv(index=False)
                .encode("utf-8")
            )

            zip_file.writestr(
                "KEGG_All_Pathways_Summary.csv",
                csv_bytes
            )


            # Bar Chart

            if st.session_state.bar_chart_bytes:

                zip_file.writestr(
                    "KEGG_Bar_Chart.png",
                    st.session_state.bar_chart_bytes
                )


            # Bubble Plot

            if st.session_state.bubble_plot_bytes:

                zip_file.writestr(
                    "KEGG_Bubble_Plot.png",
                    st.session_state.bubble_plot_bytes
                )


            # Combined Figure

            if st.session_state.combined_figure_bytes:

                zip_file.writestr(
                    "KEGG_Combined_Figure.png",
                    st.session_state.combined_figure_bytes
                )


        zip_buffer.seek(0)

        st.session_state.zip_bytes = (
            zip_buffer.getvalue()
        )


        # =============================================
        # ANALYSIS COMPLETE
        # =============================================

        st.session_state.analysis_complete = True


# ===================================================
# PAGE 1
# UPLOAD & OVERVIEW
# ===================================================

if page == "📤 Upload & Overview":

    st.markdown(
        """
        <div class="main-title">
            🧬 KEGG Pathway Enrichment Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="main-subtitle">
            Upload DAVID enrichment results and generate KEGG pathway insights.
        </div>
        """,
        unsafe_allow_html=True
    )


    # =============================================
    # APPLICATION OVERVIEW
    # =============================================

    st.markdown(
        """
        <div class="section-heading">
            What this application does
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="info-card">

        <ul>
            <li>Filter <b>KEGG_PATHWAY</b> enrichment results</li>
            <li>Calculate −log₁₀(P-value)</li>
            <li>Separate Upregulated and Downregulated pathways</li>
            <li>Identify significant pathways using FDR</li>
            <li>Generate Bar Charts</li>
            <li>Generate Bubble Plots</li>
            <li>Generate Combined Figures</li>
            <li>Allow CSV and figure downloads</li>
        </ul>

        </div>
        """,
        unsafe_allow_html=True
    )


    # =============================================
    # UPLOAD SECTION
    # =============================================

    st.markdown(
        """
        <div class="section-heading">
            📁 Upload Input Files
        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    # =============================================
    # UPREGULATED FILE
    # =============================================

    with col1:

        up_file = st.file_uploader(
            "Upload Upregulated DAVID CSV File",
            type=["csv"],
            key="upregulated_file"
        )


    # =============================================
    # DOWNREGULATED FILE
    # =============================================

    with col2:

        dn_file = st.file_uploader(
            "Upload Downregulated DAVID CSV File",
            type=["csv"],
            key="downregulated_file"
        )


    st.write("")


    # =============================================
    # RUN ANALYSIS
    # =============================================

    if (
        up_file is not None
        and
        dn_file is not None
    ):

        if st.button(
            "🚀 Run KEGG Enrichment Analysis",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Analyzing KEGG pathways..."
                ):

                    run_analysis(
                        up_file,
                        dn_file
                    )

                st.success(
                    "Analysis completed successfully!"
                )


            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )


    else:

        st.info(
            "Please upload both Upregulated and Downregulated CSV files to begin."
        )


# ===================================================
# PAGE 2
# ANALYSIS
# ===================================================

elif page == "📊 Analysis":

    st.markdown(
        """
        <div class="main-title">
            📊 KEGG Analysis
        </div>
        """,
        unsafe_allow_html=True
    )


    if not st.session_state.analysis_complete:

        st.info(
            "Please upload your files and run the analysis first."
        )


    else:

        summary = st.session_state.summary

        display_df = st.session_state.export_data


        # =============================================
        # SUMMARY
        # =============================================

        st.markdown(
            """
            <div class="section-heading">
                Analysis Summary
            </div>
            """,
            unsafe_allow_html=True
        )


        m1, m2, m3, m4, m5 = st.columns(5)


        m1.metric(
            "Total Pathways",
            summary["total_pathways"]
        )


        m2.metric(
            "Upregulated",
            summary["upregulated"]
        )


        m3.metric(
            "Downregulated",
            summary["downregulated"]
        )


        m4.metric(
            "Significant FDR < 0.05",
            summary["significant_fdr"]
        )


        m5.metric(
            "Maximum −log₁₀(P)",
            f'{summary["max_neglog10p"]:.2f}'
        )


        st.write("")


        # =============================================
        # RESULTS TABLE
        # =============================================

        st.markdown(
            """
            <div class="section-heading">
                📋 KEGG Pathway Results
            </div>
            """,
            unsafe_allow_html=True
        )


        st.dataframe(
            display_df,
            use_container_width=True
        )


        # =============================================
        # VISUALIZATIONS
        # =============================================

        st.markdown(
            """
            <div class="section-heading">
                📈 KEGG Visualizations
            </div>
            """,
            unsafe_allow_html=True
        )


        tab1, tab2, tab3 = st.tabs(
            [
                "📊 Bar Chart",
                "🫧 Bubble Plot",
                "📈 Combined Figure"
            ]
        )


        # =============================================
        # BAR CHART
        # =============================================

        with tab1:

            if st.session_state.bar_chart_bytes:

                st.image(
                    st.session_state.bar_chart_bytes,
                    use_container_width=True
                )

                st.download_button(
                    label="⬇️ Download Bar Chart",
                    data=st.session_state.bar_chart_bytes,
                    file_name="KEGG_Bar_Chart.png",
                    mime="image/png",
                    key="download_bar"
                )

            else:

                st.warning(
                    "Bar chart was not generated."
                )


        # =============================================
        # BUBBLE PLOT
        # =============================================

        with tab2:

            if st.session_state.bubble_plot_bytes:

                st.image(
                    st.session_state.bubble_plot_bytes,
                    use_container_width=True
                )

                st.download_button(
                    label="⬇️ Download Bubble Plot",
                    data=st.session_state.bubble_plot_bytes,
                    file_name="KEGG_Bubble_Plot.png",
                    mime="image/png",
                    key="download_bubble"
                )

            else:

                st.warning(
                    "Bubble plot was not generated."
                )


        # =============================================
        # COMBINED FIGURE
        # =============================================

        with tab3:

            if st.session_state.combined_figure_bytes:

                st.image(
                    st.session_state.combined_figure_bytes,
                    use_container_width=True
                )

                st.download_button(
                    label="⬇️ Download Combined Figure",
                    data=st.session_state.combined_figure_bytes,
                    file_name="KEGG_Combined_Figure.png",
                    mime="image/png",
                    key="download_combined"
                )

            else:

                st.warning(
                    "Combined figure was not generated."
                )


# ===================================================
# PAGE 3
# EXPORT
# ===================================================

elif page == "📥 Export":

    st.markdown(
        """
        <div class="main-title">
            📥 Export Results
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="main-subtitle">
            Download your KEGG pathway analysis results and visualizations.
        </div>
        """,
        unsafe_allow_html=True
    )


    if not st.session_state.analysis_complete:

        st.info(
            "Run the KEGG enrichment analysis first to download results."
        )


    else:

        display_df = (
            st.session_state.export_data
        )


        # =============================================
        # CSV DOWNLOAD
        # =============================================

        st.markdown(
            """
            <div class="section-heading">
                📄 Summary Data
            </div>
            """,
            unsafe_allow_html=True
        )


        csv_data = (
            display_df
            .to_csv(index=False)
            .encode("utf-8")
        )


        st.download_button(
            label="⬇️ Download KEGG Summary CSV",
            data=csv_data,
            file_name="KEGG_All_Pathways_Summary.csv",
            mime="text/csv",
            use_container_width=True
        )


        st.write("")


        # =============================================
        # FIGURE DOWNLOADS
        # =============================================

        st.markdown(
            """
            <div class="section-heading">
                🖼️ Download Visualizations
            </div>
            """,
            unsafe_allow_html=True
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            if st.session_state.bar_chart_bytes:

                st.download_button(
                    "⬇️ Bar Chart",
                    data=st.session_state.bar_chart_bytes,
                    file_name="KEGG_Bar_Chart.png",
                    mime="image/png",
                    use_container_width=True,
                    key="export_bar"
                )


        with col2:

            if st.session_state.bubble_plot_bytes:

                st.download_button(
                    "⬇️ Bubble Plot",
                    data=st.session_state.bubble_plot_bytes,
                    file_name="KEGG_Bubble_Plot.png",
                    mime="image/png",
                    use_container_width=True,
                    key="export_bubble"
                )


        with col3:

            if st.session_state.combined_figure_bytes:

                st.download_button(
                    "⬇️ Combined Figure",
                    data=st.session_state.combined_figure_bytes,
                    file_name="KEGG_Combined_Figure.png",
                    mime="image/png",
                    use_container_width=True,
                    key="export_combined"
                )


        st.write("")
        st.write("")


        # =============================================
        # DOWNLOAD EVERYTHING
        # =============================================

        st.markdown(
            """
            <div class="section-heading">
                📦 Download Complete Analysis
            </div>
            """,
            unsafe_allow_html=True
        )


        st.download_button(
            label="⬇️ Download ALL Results (ZIP)",
            data=st.session_state.zip_bytes,
            file_name="KEGG_Enrichment_Results.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )


# ===================================================
# PAGE 4
# ABOUT US
# ===================================================

elif page == "ℹ️ About Us":

    st.markdown(
        """
        <div class="main-title">
            🧬 About BioCode Innovators
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="main-subtitle">
            Bridging biology and technology through modern computational solutions.
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="info-card">

        <h2>Our Mission</h2>

        <p>
        BioCode Innovators is dedicated to transforming biological data
        into meaningful insights. We support students, researchers, and
        professionals through practical tools, training, and real-world
        applications in bioinformatics, genomics, and data-driven life sciences.
        </p>

        <br>

        <h2>Focus Areas</h2>

        <ul>
            <li>🧬 Computational Biology</li>
            <li>📊 Data Analysis</li>
            <li>📈 Biological Data Visualization</li>
            <li>⚙️ Bioinformatics Tools</li>
            <li>🐍 Python for Biology</li>
            <li>📉 R for Biology</li>
        </ul>

        </div>
        """,
        unsafe_allow_html=True
    )


# ===================================================
# FOOTER
# ===================================================

st.markdown(
"""
<div style="text-align: center; color: #788398; font-size: 14px; line-height: 1.5;">

<div style="font-weight: 700; color: #171C36;">
🧬 Powered by BioCode Innovators
</div>

<div>
Developed with precision by Abeera Iftikhar
</div>

<br>

<div>
KEGG Enrichment Dashboard designed for pathway enrichment analysis,<br>
biological interpretation, KEGG pathway visualization, and modern<br>
bioinformatics research.
</div>

<br>

<div style="font-weight: 600;">
✨ Bridging Biology, Data Science, and Computational Intelligence
</div>

</div>
""",
unsafe_allow_html=True
)