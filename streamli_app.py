from pathlib import Path
import tempfile

import streamlit as st

from src.species_detector import SpeciesDetector
from src.iucn_database import IUCNDatabase
from src.location import validate_location
from src.logger import EcoLogger
from src.tracker import EcoTracker


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

LOG_DIR = BASE_DIR / "logs"

IUCN_PATH = DATA_DIR / "iucn_species.csv"

LOG_PATH = LOG_DIR / "eco_tracker.log"


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(

    page_title="Eco-Tracker",

    page_icon="🌿",

    layout="wide"

)


# ==================================================
# CSS
# ==================================================

st.markdown(
    """
    <style>

    .hero {

        padding: 35px;

        border-radius: 22px;

        background:
        linear-gradient(
            135deg,
            #064e3b,
            #166534
        );

        color: white;

        margin-bottom: 30px;

    }


    .hero h1 {

        font-size: 45px;

        margin-bottom: 8px;

    }


    .hero p {

        font-size: 17px;

        opacity: 0.9;

    }


    .info-card {

        background: white;

        padding: 25px;

        border-radius: 18px;

        border: 1px solid #d1d5db;

        margin-bottom: 20px;

    }


    .species-name {

        font-size: 32px;

        font-weight: 800;

    }


    .scientific-name {

        font-size: 18px;

        font-style: italic;

        color: #4b5563;

    }


    .metric-card {

        padding: 20px;

        border-radius: 15px;

        background: #f0fdf4;

        border: 1px solid #bbf7d0;

    }


    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">

        <h1>🌿 Eco-Tracker</h1>

        <p>
        AI-powered wildlife identification
        and conservation monitoring system.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header("🌿 Eco-Tracker")

    st.write(
        """
        Upload an animal or bird image and
        Eco-Tracker will identify the species
        and check its conservation information.
        """
    )

    st.divider()

    page = st.radio(

        "Navigation",

        [
            "🔍 Species Detection",
            "📜 Logs"
        ]

    )


# ==================================================
# LOGGER
# ==================================================

logger = EcoLogger(
    LOG_PATH
)


# ==================================================
# LOG PAGE
# ==================================================

if page == "📜 Logs":

    st.header("📜 Eco-Tracker Logs")

    st.write(
        "View previous detection activity."
    )


    logs = logger.read_logs()


    st.text_area(

        "Log file",

        logs,

        height=500

    )


    if st.button(
        "🔄 Refresh Logs"
    ):

        st.rerun()


# ==================================================
# DETECTION PAGE
# ==================================================

else:

    st.header("🔍 Identify Wildlife")


    # ----------------------------------------------
    # API KEY
    # ----------------------------------------------

    api_key = st.text_input(

        "Gemini API Key",

        type="password",

        help="Enter your Google Gemini API key."

    )


    # ----------------------------------------------
    # IMAGE
    # ----------------------------------------------

    uploaded_file = st.file_uploader(

        "Upload an animal or bird image",

        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ]

    )


    # ----------------------------------------------
    # IMAGE PREVIEW
    # ----------------------------------------------

    if uploaded_file:

        st.image(

            uploaded_file,

            caption="Uploaded Image",

            width=400

        )


    # ----------------------------------------------
    # LOCATION
    # ----------------------------------------------

    st.subheader("📍 Location")

    location_enabled = st.checkbox(
        "Add location information"
    )


    latitude = None

    longitude = None


    if location_enabled:

        col1, col2 = st.columns(2)


        with col1:

            latitude = st.number_input(

                "Latitude",

                min_value=-90.0,

                max_value=90.0,

                value=0.0,

                format="%.6f"

            )


        with col2:

            longitude = st.number_input(

                "Longitude",

                min_value=-180.0,

                max_value=180.0,

                value=0.0,

                format="%.6f"

            )


    st.divider()


    # ----------------------------------------------
    # ANALYZE
    # ----------------------------------------------

    if st.button(

        "🔎 Identify Species",

        type="primary",

        use_container_width=True

    ):

        # ==========================================
        # VALIDATION
        # ==========================================

        if not api_key:

            st.error(
                "🚨 Please enter your Gemini API key."
            )

            st.stop()


        if uploaded_file is None:

            st.error(
                "🚨 Please upload an animal image."
            )

            st.stop()


        if location_enabled:

            valid, message = validate_location(
                latitude,
                longitude
            )


            if not valid:

                st.error(
                    f"🚨 {message}"
                )

                st.stop()


        # ==========================================
        # SAVE TEMP IMAGE
        # ==========================================

        suffix = Path(
            uploaded_file.name
        ).suffix


        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(
                uploaded_file.getbuffer()
            )

            image_path = Path(
                temp_file.name
            )


        # ==========================================
        # INITIALIZE SYSTEM
        # ==========================================

        try:

            detector = SpeciesDetector(
                api_key
            )


            database = IUCNDatabase(
                IUCN_PATH
            )


            tracker = EcoTracker(

                detector,

                database,

                logger

            )


            # ======================================
            # ANALYSIS
            # ======================================

            with st.spinner(
                "🤖 AI is identifying the species..."
            ):

                result = tracker.analyze(

                    image_path,

                    latitude,

                    longitude

                )


        except Exception as error:

            logger.log(
                f"ERROR: {str(error)}"
            )

            st.error(
                f"🚨 Detection failed: {error}"
            )

            st.stop()


        # ==========================================
        # RESULTS
        # ==========================================

        st.success(
            "✅ Species identification completed."
        )


        st.markdown(
            f"""
            <div class="info-card">

                <div class="species-name">

                    🐾 {result["common_name"]}

                </div>

                <div class="scientific-name">

                    {result["scientific_name"]}

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ==========================================
        # METRICS
        # ==========================================

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "🤖 AI Confidence",
                result["confidence"]
            )


        with col2:

            st.metric(
                "🌍 Conservation Status",
                result["status"]
            )


        with col3:

            st.metric(
                "🐾 Global Population",
                f"{result['population']:,}"
                if isinstance(
                    result["population"],
                    (int, float)
                )
                else result["population"]
            )


        # ==========================================
        # CONSERVATION ALERT
        # ==========================================

        status = result["status"]


        if status == "Critically Endangered":

            st.error(
                "🚨 CRITICAL ALERT: "
                "This species is critically endangered. "
                "Immediate conservation attention is required."
            )


        elif status == "Endangered":

            st.error(
                "🚨 ALERT: "
                "This species is endangered."
            )


        elif status == "Vulnerable":

            st.warning(
                "⚠️ WARNING: "
                "This species is vulnerable."
            )


        elif status == "Near Threatened":

            st.warning(
                "⚠️ NOTICE: "
                "This species is near threatened."
            )


        elif status == "Least Concern":

            st.success(
                "✅ This species is currently classified "
                "as Least Concern."
            )


        else:

            st.info(
                "ℹ️ Conservation information was not "
                "found in the local IUCN dataset."
            )


        # ==========================================
        # LOCATION
        # ==========================================

        if result["location"]:

            st.subheader("📍 Detection Location")


            st.write(
                f"Latitude: "
                f"{result['location']['latitude']}"
            )


            st.write(
                f"Longitude: "
                f"{result['location']['longitude']}"
            )


            map_data = {

                "latitude": [
                    result["location"]["latitude"]
                ],

                "longitude": [
                    result["location"]["longitude"]
                ]

            }


            st.map(map_data)