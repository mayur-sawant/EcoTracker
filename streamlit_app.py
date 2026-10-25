from pathlib import Path
import os
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


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return

    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export "):].strip()

        name, separator, value = line.partition("=")
        name = name.strip()
        if not separator or not name:
            raise ValueError(f"Invalid .env entry on line {line_number}.")

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        os.environ.setdefault(name, value)


load_env_file(BASE_DIR / ".env")


def get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        return api_key

    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except st.errors.StreamlitSecretNotFoundError:
        return ""


DATA_DIR = BASE_DIR / "data"

LOG_DIR = BASE_DIR / "logs"

IUCN_PATH = DATA_DIR / "iucn_red_list.csv"

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
# HEADER
# ==================================================

st.title("🌿 Eco-Tracker")
st.write(
    "AI-powered wildlife identification "
    "and conservation monitoring system."
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


    api_key = get_api_key()


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
                "🚨 Configure GEMINI_API_KEY in the environment or Streamlit secrets."
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

        # Display species info with container styling
        with st.container(border=True):
            st.markdown(
                f"### 🐾 {result['common_name']}"
            )
            st.markdown(
                f"*{result['scientific_name']}*"
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