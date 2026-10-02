"""

app_integrated.py



Coconut Grading AI - Full Integration



Includes:

\- Authentication

\- Database

\- Analytics

\- Caching

\- CSV / JSON / Text exports

\- YOLO detection

\- OpenVINO detection

\- Single image analysis

\- Bulk image analysis

\- Maturity grading

\- Market valuation

\- Analysis history

"""



import streamlit as st

from PIL import Image, ImageDraw
import numpy as np

from pathlib import Path



# ============================================================

# OPENVINO DETECTOR

# ============================================================



from utils.openvino_detector import (

    load_openvino_model,

    detect_coconuts_openvino,

)



# ============================================================

# EXISTING UTILITIES

# ============================================================



from utils import (

    # Detection

    load_yolo_model,

    detect_coconuts,

    resolve_model_path,



    # Grading

    calculate_grade_and_summary,



    # Pricing

    load_price_model,

    predict_market_price,

    calculate_market_valuation,

    DEFAULT_MARKET_RATES,



    # Configuration

    get_config,

    ensure_directories,



    # Validation

    validate_image,

    validate_confidence_threshold,

    validate_market_rates,



    # Database / Authentication

    Database,

    AuthManager,



    # Image processing

    ImageProcessor,



    # Reports

    ReportGenerator,



    # Analytics

    Analytics,



    # Logging

    LoggingManager,



    # Performance

    PerformanceMonitor,



    # Cache

    Cache,

    ModelCache,

)





# ============================================================

# INITIALIZATION

# ============================================================



config = get_config()

ensure_directories()





# ============================================================

# DATABASE

# ============================================================



db = Database(config.DB_PATH)





# ============================================================

# AUTHENTICATION

# ============================================================



auth_manager = AuthManager(db)





# ============================================================

# LOGGING

# ============================================================



logger = LoggingManager(

    config.LOG_DIR,

    level=config.LOG_LEVEL,

)





# ============================================================

# CACHE

# ============================================================



model_cache = ModelCache(

    ttl_seconds=config.CACHE_TTL

)



general_cache = Cache(

    ttl_seconds=config.CACHE_TTL

)





# ============================================================

# REPORT GENERATOR

# ============================================================



report_gen = ReportGenerator(

    config.EXPORT_DIR

)





# ============================================================

# PERFORMANCE MONITOR

# ============================================================



perf_monitor = PerformanceMonitor()





# ============================================================

# YOLO MODEL

# ============================================================



yolo_model = None



try:

    yolo_model_path = resolve_model_path(

        str(config.YOLO_MODEL_PATH)

    )



    yolo_model = load_yolo_model(

        yolo_model_path

    )



    logger.info(

        "YOLO model loaded successfully"

    )



except Exception as e:

    logger.error(

        f"Failed to load YOLO model: {str(e)}",

        e,

    )





# ============================================================

# OPENVINO MODEL

# ============================================================



openvino_model = None



openvino_model_path = (

    Path(config.YOLO_MODEL_PATH).parent

    / "best_openvino_model"

)



try:



    if openvino_model_path.exists():



        openvino_model = load_openvino_model(

            str(openvino_model_path)

        )



        logger.info(

            "OpenVINO model loaded successfully: "

            f"{openvino_model_path}"

        )



    else:



        logger.warning(

            "OpenVINO model not found: "

            f"{openvino_model_path}"

        )



except Exception as e:



    logger.error(

        f"Failed to load OpenVINO model: {str(e)}",

        e,

    )





# ============================================================

# PRICE MODEL

# ============================================================



price_model = load_price_model(

    str(config.PRICE_MODEL_PATH)

)





# ============================================================

# PAGE CONFIGURATION

# ============================================================



st.set_page_config(

    page_title="Coconut Grading AI",

    page_icon="🥥",

    layout="wide",

    initial_sidebar_state="expanded",

)





# ============================================================

# SESSION STATE

# ============================================================



if "session_token" not in st.session_state:

    st.session_state.session_token = None



if "current_user" not in st.session_state:

    st.session_state.current_user = None



if "page" not in st.session_state:

    st.session_state.page = "login"





# ============================================================


# ============================================================
# PREMIUM COCONUT FARM VISUAL THEME
# ============================================================
COCONUT_FARM_BG = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNjAwIDkwMCI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJzIiB4MT0iMCIgeTE9IjAiIHgyPSIwIiB5Mj0iMSI+PHN0b3Agc3RvcC1jb2xvcj0iIzA3MWIxNiIvPjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzEyM2MyYSIvPjwvbGluZWFyR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJnIiB4MT0iMCIgeTE9IjAiIHgyPSIwIiB5Mj0iMSI+PHN0b3Agc3RvcC1jb2xvcj0iIzE2NGIyZiIvPjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzA2MTMwZiIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxyZWN0IHdpZHRoPSIxNjAwIiBoZWlnaHQ9IjkwMCIgZmlsbD0idXJsKCNzKSIvPjxjaXJjbGUgY3g9IjEyNTAiIGN5PSIxODAiIHI9IjExMCIgZmlsbD0iI2Q4ZjNkYyIgb3BhY2l0eT0iLjEzIi8+PHBhdGggZD0iTTAgNTcwUTI2MCA0MzAgNTIwIDU2MFQxMDUwIDU0MFQxNjAwIDUyMFY5MDBIMFoiIGZpbGw9InVybCgjZykiLz48ZyBmaWxsPSIjMGEyNDE5Ij48cGF0aCBkPSJNMTgwIDY1MEMxOTUgNTIwIDIwNSA0MDAgMjMwIDI4MGgyMGMtMTIgMTQwLTUgMjYwIDE1IDM3MHoiLz48cGF0aCBkPSJNNDMwIDY5MGMxNS0xNDAgMjAtMjYwIDQ1LTM3NWgyMGMtMTMgMTM1LTUgMjU1IDE1IDM3NXoiLz48cGF0aCBkPSJNNzIwIDY3MGMxNS0xNDAgMjAtMjY1IDQ1LTQwNWgyMGMtMTMgMTU1LTUgMjgwIDE1IDQwNXoiLz48cGF0aCBkPSJNMTA0MCA3MDBjMTUtMTUwIDIwLTI5MCA0NS00MzBoMjBjLTEzIDE1MC01IDI5MCAxNSA0MzB6Ii8+PHBhdGggZD0iTTEzNTAgNjgwYzE1LTE1MCAyMC0yNzUgNDUtNDMwaDIwYy0xMyAxNzAtNSAyOTAgMTUgNDMweiIvPjwvZz48ZyBmaWxsPSIjMGMyZjIxIj48cGF0aCBkPSJNMjQwIDMwMFExNTAgMjQ1IDkwIDI4NXE1NS02NSAxMzAtMzUtNzUtODAtMTQ1LTQ1IDk1LTg1IDE3NSAxNSAyNS0xMDAgODAtMTQwLTE1IDEwMC02MCAxNjUgMTAwLTkwIDE2MC03MC03NSA1NS0xNTAgOTUgMTEwLTM1IDE3MCA1LTEwMCAyNS0xOTAgMjB6Ii8+PHBhdGggZD0iTTQ4MCAzMzBRMzkwIDI3MCAzMzAgMzEwcTYwLTgwIDEyNS01MC02NS05MC0xNDAtNTUgMTA1LTkwIDE4NSAzMCAzNS0xMTAgODUtMTQwLTIwIDEwMC02NSAxNzAgMTAwLTg1IDE2MC01NS05MCA1MC0xNTUgOTAgMTE1LTI1IDE3NSAxNS0xMTAgMjUtMjAwIDE1eiIvPjxwYXRoIGQ9Ik03NzAgMjgwUTY4MCAyMjUgNjIwIDI2NXE2MC04NSAxMjUtNTAtNjUtOTUtMTM1LTU1IDEwMC0xMDAgMTgwIDI1IDMwLTEwNSA4MC0xNDAtMjAgMTA1LTYwIDE3NSAxMDAtOTUgMTYwLTY1LTg1IDYwLTE1NSA5NSAxMTUtMjUgMTcwIDE1LTEwMCAzMC0xOTAgMjB6Ii8+PHBhdGggZD0iTTEwOTAgMjkwUTEwMDAgMjMwIDk0MCAyNzVxNjAtOTAgMTI1LTU1LTY1LTk1LTE0MC01NSAxMDUtMTAwIDE4NSAyNSAzMC0xMDUgODAtMTQwLTIwIDEwNS02MCAxNzUgMTAwLTkwIDE2MC02MC05MCA2MC0xNTUgOTUgMTE1LTI1IDE3NSAxNS0xMTAgMzAtMjAwIDIweiIvPjxwYXRoIGQ9Ik0xNDAwIDI3MFExMzEwIDIxNSAxMjUwIDI1NXE2MC04NSAxMjUtNTAtNjUtMTAwLTEzNS01NSAxMDAtMTAwIDE4MCAyNSAzMC0xMDUgODAtMTQwLTIwIDExMC02MCAxODAgMTAwLTk1IDE2MC02MC05MCA1NS0xNTUgOTUgMTE1LTI1IDE3MCAxNS0xMTAgMjUtMjAwIDE1eiIvPjwvZz48L3N2Zz4="

st.markdown(
    f"""
    <style>
      /* ---------- GLOBAL APP ---------- */
      .stApp {{
        background:
          radial-gradient(circle at 82% 8%, rgba(53, 160, 105, .14), transparent 28%),
          radial-gradient(circle at 12% 85%, rgba(27, 110, 74, .12), transparent 30%),
          #07120f !important;
        color: #edf8f1 !important;
      }}

      header[data-testid="stHeader"] {{
        background: rgba(7,18,15,.82) !important;
      }}

      section[data-testid="stMain"] {{
        position: relative;
        z-index: 1;
        background: transparent !important;
      }}

      div[data-testid="stAppViewContainer"] {{
        background: transparent !important;
      }}

      /* ---------- SUBTLE FARM ATMOSPHERE ---------- */
      .coconut-bg {{
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        background-image:
          linear-gradient(rgba(3,13,10,.82), rgba(3,13,10,.90)),
          url("data:image/svg+xml;base64,{COCONUT_FARM_BG}");
        background-size: cover;
        background-position: center;
        opacity: .28;
      }}

      .coconut-bg.home {{
        opacity: .16;
      }}

      /* ---------- GLASSMORPHISM SYSTEM ---------- */
      .glass-card {{
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(210,255,226,.13);
        background:
          linear-gradient(135deg, rgba(255,255,255,.085), rgba(255,255,255,.025));
        box-shadow:
          0 24px 70px rgba(0,0,0,.28),
          inset 0 1px 0 rgba(255,255,255,.10);
        backdrop-filter: blur(22px) saturate(125%);
        -webkit-backdrop-filter: blur(22px) saturate(125%);
      }}

      .glass-card:before {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
          120deg,
          rgba(255,255,255,.08),
          transparent 34%,
          transparent 70%,
          rgba(114,215,155,.045)
        );
        pointer-events: none;
      }}

      .glass-card:after {{
        content: "";
        position: absolute;
        top: -80%;
        left: -35%;
        width: 35%;
        height: 260%;
        transform: rotate(24deg);
        background: linear-gradient(
          90deg,
          transparent,
          rgba(255,255,255,.055),
          transparent
        );
        animation: glassSweep 9s ease-in-out infinite;
        pointer-events: none;
      }}

      @keyframes glassSweep {{
        0%, 58% {{ left: -45%; opacity: 0; }}
        68% {{ opacity: 1; }}
        82%, 100% {{ left: 125%; opacity: 0; }}
      }}

      /* Glass around Streamlit's main content containers */
      div[data-testid="stFileUploader"],
      [data-testid="stMetric"],
      div[data-testid="stExpander"],
      div[data-testid="stAlert"] {{
        background:
          linear-gradient(135deg, rgba(255,255,255,.065), rgba(255,255,255,.018)) !important;
        border: 1px solid rgba(200,250,216,.11) !important;
        box-shadow:
          0 18px 45px rgba(0,0,0,.18),
          inset 0 1px 0 rgba(255,255,255,.07) !important;
        backdrop-filter: blur(18px) saturate(120%);
        -webkit-backdrop-filter: blur(18px) saturate(120%);
        border-radius: 18px !important;
      }}

      /* Glass treatment for common Streamlit tabs */
      button[data-baseweb="tab"] {{
        border-radius: 12px 12px 0 0 !important;
        transition: background .2s ease, color .2s ease, transform .2s ease;
      }}

      button[data-baseweb="tab"]:hover {{
        background: rgba(255,255,255,.045) !important;
        transform: translateY(-1px);
      }}

      /* Inputs */
      div[data-baseweb="input"],
      div[data-baseweb="select"] > div {{
        background: rgba(255,255,255,.045) !important;
        border: 1px solid rgba(210,255,226,.12) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(12px);
      }}

      /* ---------- SIDEBAR ---------- */
      [data-testid="stSidebar"] {{
        background:
          linear-gradient(180deg, rgba(7,25,18,.98), rgba(4,15,11,.98)) !important;
        border-right: 1px solid rgba(168,232,193,.10);
      }}

      [data-testid="stSidebar"] * {{
        color: #e6f5eb !important;
      }}

      [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,.10) !important;
      }}

      /* ---------- LOGIN ---------- */
      .login-shell {{
        position: relative;
        z-index: 2;
        max-width: 920px;
        margin: 7vh auto 3vh;
      }}

      .login-brand {{
        text-align: center;
        color: #aee8bf;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .24em;
        text-transform: uppercase;
        margin-bottom: 12px;
      }}

      .login-title {{
        text-align: center;
        color: #f5fff8;
        font-size: clamp(2.4rem, 5vw, 4.8rem);
        font-weight: 850;
        line-height: .98;
        letter-spacing: -.04em;
        margin: 0;
      }}

      .login-title span {{
        color: #72d79b;
      }}

      .login-copy {{
        max-width: 650px;
        margin: 18px auto 30px;
        text-align: center;
        color: rgba(229,247,236,.68);
        font-size: 1rem;
        line-height: 1.7;
      }}

      .login-panel {{
        position: relative;
        overflow: hidden;
        padding: 30px;
        border: 1px solid rgba(220,255,232,.18);
        border-radius: 28px;
        background:
          linear-gradient(135deg, rgba(255,255,255,.105), rgba(255,255,255,.025));
        box-shadow:
          0 30px 100px rgba(0,0,0,.45),
          inset 0 1px 0 rgba(255,255,255,.12);
        backdrop-filter: blur(26px) saturate(135%);
        -webkit-backdrop-filter: blur(26px) saturate(135%);
      }}

      .login-panel:after {{
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        right: -90px;
        top: -90px;
        border-radius: 50%;
        background: rgba(114,215,155,.12);
        filter: blur(18px);
        pointer-events: none;
      }}

      /* ---------- HOME HERO ---------- */
      .home-hero {{
        position: relative;
        z-index: 2;
        overflow: hidden;
        margin: 12px 0 22px;
        padding: 38px 42px;
        border: 1px solid rgba(210,255,226,.16);
        border-radius: 30px;
        background:
          linear-gradient(110deg, rgba(8,39,27,.78), rgba(17,74,49,.48)),
          url("data:image/svg+xml;base64,{COCONUT_FARM_BG}");
        background-size: cover;
        background-position: center;
        box-shadow:
          0 30px 90px rgba(0,0,0,.34),
          inset 0 1px 0 rgba(255,255,255,.10);
        backdrop-filter: blur(24px) saturate(125%);
        -webkit-backdrop-filter: blur(24px) saturate(125%);
      }}

      .home-hero:after {{
        content: "🥥";
        position: absolute;
        right: 46px;
        top: 20px;
        font-size: 7rem;
        opacity: .10;
        transform: rotate(-13deg);
      }}

      .home-kicker {{
        color: #9ee6b8;
        font-size: .72rem;
        letter-spacing: .22em;
        text-transform: uppercase;
        font-weight: 800;
      }}

      .home-title {{
        color: #f7fff9;
        font-size: clamp(2rem, 4vw, 3.5rem);
        line-height: 1.02;
        font-weight: 850;
        letter-spacing: -.04em;
        margin: 8px 0 10px;
      }}

      .home-copy {{
        color: rgba(235,251,241,.70);
        max-width: 720px;
        margin: 0;
        font-size: 1rem;
        line-height: 1.65;
      }}

      .home-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 20px;
      }}

      .home-badge {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 8px 12px;
        border-radius: 999px;
        color: #dff8e7;
        background: rgba(255,255,255,.07);
        border: 1px solid rgba(255,255,255,.10);
        font-size: .78rem;
        font-weight: 700;
      }}

      /* ---------- WORKFLOW ---------- */
      .workflow-title {{
        position: relative;
        z-index: 2;
        color: #f0fbf4;
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .18em;
        text-transform: uppercase;
        margin: 8px 0 10px;
      }}

      .workflow {{
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 26px;
      }}

      .workflow-card {{
        padding: 16px 18px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,.09);
        background: rgba(255,255,255,.035);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
      }}

      .workflow-number {{
        color: #72d79b;
        font-size: .7rem;
        font-weight: 850;
        letter-spacing: .12em;
      }}

      .workflow-name {{
        color: #f4fff7;
        font-size: 1rem;
        font-weight: 800;
        margin-top: 4px;
      }}

      .workflow-text {{
        color: rgba(232,247,237,.58);
        font-size: .78rem;
        margin-top: 4px;
      }}

      /* ---------- STREAMLIT WIDGETS ---------- */
      div[data-testid="stFileUploader"] {{
        border: 1px dashed rgba(117,220,153,.35);
        border-radius: 18px;
        background: rgba(255,255,255,.035);
        padding: 6px;
      }}

      .stButton > button {{
        border-radius: 12px !important;
        min-height: 44px;
        border: 1px solid rgba(255,255,255,.12) !important;
        transition: transform .18s ease, box-shadow .18s ease !important;
      }}

      .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0,0,0,.24);
      }}

      /* Keep metrics readable on dark theme. */
      [data-testid="stMetric"] {{
        background: rgba(255,255,255,.035);
        border: 1px solid rgba(255,255,255,.08);
        padding: 14px;
        border-radius: 16px;
      }}

      @media (max-width: 800px) {{
        .workflow {{ grid-template-columns: 1fr; }}
        .home-hero {{ padding: 26px 22px; }}
      }}
    </style>
    """, unsafe_allow_html=True
)

# LOGIN PAGE

# ============================================================



def login_page():

    """Display login and registration page."""

    st.markdown('<div class="coconut-bg"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="login-shell">
          <div class="login-brand">AI • AGRICULTURE • COMPUTER VISION</div>
          <h1 class="login-title">Coconut <span>Grading AI</span></h1>
          <p class="login-copy">
            Intelligent coconut maturity detection, bunch-wise grading and
            transparent value estimation — designed for modern farm analytics.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(

        [1, 2, 1]

    )



    with col2:

        st.markdown(
            """
            <div class="login-panel">
              <div style="text-align:center;color:#f5fff8;font-size:1.55rem;font-weight:800;">
                Welcome back 👋
              </div>
              <div style="text-align:center;color:rgba(230,247,236,.58);font-size:.85rem;margin-top:6px;">
                Sign in to your coconut intelligence workspace
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )



        tab1, tab2 = st.tabs(

            ["Login", "Register"]

        )



        # ====================================================

        # LOGIN

        # ====================================================



        with tab1:



            username = st.text_input(

                "Username",

                key="login_username",

            )



            password = st.text_input(

                "Password",

                type="password",

                key="login_password",

            )



            if st.button(

                "Login",

                use_container_width=True,

                type="primary",

            ):



                if not username or not password:



                    st.error(

                        "Please enter username and password"

                    )



                else:



                    success, message, token = (

                        auth_manager.login(

                            username,

                            password,

                        )

                    )



                    if success:



                        st.session_state.session_token = (

                            token

                        )



                        st.session_state.current_user = (

                            auth_manager.get_current_user(

                                token

                            )

                        )



                        st.session_state.page = "app"



                        logger.log_user_action(

                            username,

                            "login",

                            "successful",

                        )



                        st.success(message)



                        st.rerun()



                    else:



                        st.error(message)



                        logger.log_user_action(

                            username,

                            "login",

                            "failed",

                        )



        # ====================================================

        # REGISTER

        # ====================================================



        with tab2:



            st.subheader(

                "Create New Account"

            )



            new_username = st.text_input(

                "New Username",

                key="reg_username",

            )



            new_email = st.text_input(

                "Email",

                key="reg_email",

            )



            new_password = st.text_input(

                "Password",

                type="password",

                key="reg_password",

            )



            new_password_confirm = st.text_input(

                "Confirm Password",

                type="password",

                key="reg_password_confirm",

            )



            role = st.selectbox(

                "Select Role",

                [

                    "farmer",

                    "agent",

                    "dealer",

                ],

                key="reg_role",

            )



            if st.button(

                "Register",

                use_container_width=True,

                type="primary",

            ):



                if (

                    not new_username

                    or not new_email

                    or not new_password

                ):



                    st.error(

                        "Please fill in all fields"

                    )



                elif new_password != new_password_confirm:



                    st.error(

                        "Passwords do not match"

                    )



                else:



                    success, message = (

                        auth_manager.register_user(

                            new_username,

                            new_password,

                            new_email,

                            role,

                        )

                    )



                    if success:



                        st.success(message)



                        logger.log_user_action(

                            new_username,

                            "register",

                            f"role={role}",

                        )



                        st.info(

                            "You can now login with your credentials"

                        )



                    else:



                        st.error(message)





# ============================================================


# ============================================================
# BUNCH MULTI-PASS DETECTION
# ============================================================

def _box_iou(box_a, box_b):
    """IoU for two xyxy boxes."""
    ax1, ay1, ax2, ay2 = [float(v) for v in box_a]
    bx1, by1, bx2, by2 = [float(v) for v in box_b]

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    intersection = iw * ih

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - intersection

    return intersection / union if union > 0 else 0.0


def _classwise_nms(boxes_data, iou_threshold=0.50):
    """
    Merge detections from the full image and overlapping tiles.
    Keeps the highest-confidence detection when two boxes represent
    the same coconut.
    """
    kept = []

    for class_name in ("dry", "green", "tender"):
        class_boxes = [
            item for item in boxes_data
            if str(item.get("class_name", "")).lower().strip() == class_name
        ]
        class_boxes.sort(
            key=lambda item: float(item.get("confidence", 0.0)),
            reverse=True,
        )

        while class_boxes:
            best = class_boxes.pop(0)
            kept.append(best)

            remaining = []
            best_box = best.get("xyxy", [])

            for candidate in class_boxes:
                if _box_iou(best_box, candidate.get("xyxy", [])) < iou_threshold:
                    remaining.append(candidate)

            class_boxes = remaining

    kept.sort(key=lambda item: float(item.get("confidence", 0.0)), reverse=True)
    return kept


def _draw_bunch_boxes(image, boxes_data):
    """Draw the final merged detections on the original image."""
    canvas = image.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)

    colors = {
        "dry": (230, 126, 34),
        "green": (39, 174, 96),
        "tender": (52, 152, 219),
    }

    for idx, item in enumerate(boxes_data, start=1):
        class_name = str(item.get("class_name", "unknown")).lower().strip()
        confidence = float(item.get("confidence", 0.0))
        box = item.get("xyxy", [])

        if len(box) != 4:
            continue

        x1, y1, x2, y2 = [int(round(float(v))) for v in box]
        color = colors.get(class_name, (255, 255, 255))

        draw.rectangle((x1, y1, x2, y2), outline=color, width=4)

        label = f"#{idx} {class_name.title()} {confidence:.0%}"
        try:
            bbox = draw.textbbox((x1, max(0, y1 - 24)), label)
            draw.rectangle(bbox, fill=color)
            draw.text(
                (x1 + 3, max(0, y1 - 22)),
                label,
                fill=(255, 255, 255),
            )
        except Exception:
            draw.text(
                (x1, max(0, y1 - 18)),
                label,
                fill=color,
            )

    # Existing app displays plotted_image as BGR.
    return np.array(canvas)[:, :, ::-1]


def detect_bunch_coconuts(
    detector_fn,
    model,
    image,
    conf_threshold=0.25,
    grid_size=2,
    overlap=0.25,
):
    """
    Multi-pass detection for a coconut bunch.

    Why this is needed:
    A 640x640 image can contain several partially occluded coconuts.
    A single full-image inference may detect only the largest/clearest one.
    This function therefore runs:
      1. the complete image, and
      2. overlapping tiles,
    then maps tile boxes back to the original image and removes duplicates.

    The existing YOLO/OpenVINO detector is still used; this is an
    aggregation layer, so the original detection module remains intact.
    """
    image = image.convert("RGB")
    width, height = image.size

    all_boxes = []
    base_result = None

    # Full image pass at the user's configured threshold.
    full_data = detector_fn(
        model=model,
        image=image,
        conf_threshold=conf_threshold,
    )
    base_result = full_data.get("result")

    for item in full_data.get("boxes_data", []) or []:
        if len(item.get("xyxy", [])) == 4:
            all_boxes.append(
                {
                    **item,
                    "xyxy": [float(v) for v in item["xyxy"]],
                }
            )

    # Lower threshold on tiles so partially visible coconuts are not
    # discarded too early.
    tile_conf = max(0.08, min(conf_threshold, conf_threshold * 0.60))

    # 2x2 overlapping tiles.
    tile_w = int(round(width / (grid_size - (grid_size - 1) * overlap)))
    tile_h = int(round(height / (grid_size - (grid_size - 1) * overlap)))
    step_x = max(1, int(round(tile_w * (1.0 - overlap))))
    step_y = max(1, int(round(tile_h * (1.0 - overlap))))

    x_starts = []
    y_starts = []

    for x in range(0, width, step_x):
        x = min(x, max(0, width - tile_w))
        if x not in x_starts:
            x_starts.append(x)
        if x + tile_w >= width:
            break

    for y in range(0, height, step_y):
        y = min(y, max(0, height - tile_h))
        if y not in y_starts:
            y_starts.append(y)
        if y + tile_h >= height:
            break

    for y0 in y_starts:
        for x0 in x_starts:
            x1 = min(width, x0 + tile_w)
            y1 = min(height, y0 + tile_h)

            tile = image.crop((x0, y0, x1, y1))

            try:
                tile_data = detector_fn(
                    model=model,
                    image=tile,
                    conf_threshold=tile_conf,
                )
            except Exception:
                # Keep the full-image result even if a tile inference fails.
                continue

            for item in tile_data.get("boxes_data", []) or []:
                local_box = item.get("xyxy", [])
                if len(local_box) != 4:
                    continue

                lx1, ly1, lx2, ly2 = [float(v) for v in local_box]

                # Convert tile coordinates to original-image coordinates.
                mapped_box = [
                    max(0.0, min(float(width), lx1 + x0)),
                    max(0.0, min(float(height), ly1 + y0)),
                    max(0.0, min(float(width), lx2 + x0)),
                    max(0.0, min(float(height), ly2 + y0)),
                ]

                if mapped_box[2] <= mapped_box[0] or mapped_box[3] <= mapped_box[1]:
                    continue

                all_boxes.append(
                    {
                        **item,
                        "xyxy": mapped_box,
                        "source": "tile",
                    }
                )

    final_boxes = _classwise_nms(all_boxes, iou_threshold=0.50)

    counts = {"dry": 0, "green": 0, "tender": 0}
    confidences = []

    for item in final_boxes:
        class_name = str(item.get("class_name", "")).lower().strip()
        if class_name in counts:
            counts[class_name] += 1
            confidences.append(float(item.get("confidence", 0.0)))

    total = sum(counts.values())
    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0.0
    )

    return {
        "result": base_result,
        "plotted_image": _draw_bunch_boxes(image, final_boxes),
        "counts": counts,
        "total": total,
        "average_confidence": average_confidence,
        "confidences": confidences,
        "boxes_data": final_boxes,
        "detection_passes": 1 + len(x_starts) * len(y_starts),
        "tile_confidence": tile_conf,
    }


# ============================================================
# BUNCH PRICE BREAKDOWN
# ============================================================

def create_bunch_price_breakdown(detection_data, market_rates):
    """Create one pricing row for every detected coconut in a bunch."""
    rows = []
    boxes_data = detection_data.get("boxes_data", []) or []

    if boxes_data:
        for index, coconut in enumerate(boxes_data, start=1):
            coconut_type = str(coconut.get("class_name", "unknown")).lower()
            if coconut_type not in market_rates:
                continue

            confidence = float(coconut.get("confidence", 0.0))
            price = float(market_rates[coconut_type])

            rows.append({
                "Coconut": index,
                "Type": coconut_type.title(),
                "Confidence": f"{confidence:.2%}",
                "Rate": f"₹{price:.2f}",
                "Value": f"₹{price:.2f}",
            })

        return rows

    counts = detection_data.get("counts", {}) or {}
    index = 1

    for coconut_type in ("dry", "green", "tender"):
        count = int(counts.get(coconut_type, 0))
        price = float(market_rates.get(coconut_type, 0.0))

        for _ in range(count):
            rows.append({
                "Coconut": index,
                "Type": coconut_type.title(),
                "Confidence": "-",
                "Rate": f"₹{price:.2f}",
                "Value": f"₹{price:.2f}",
            })
            index += 1

    return rows



# ============================================================
# BUNCH RESULT SUMMARY UI
# ============================================================

def render_bunch_result_summary(result):
    """Render a clear single-bunch intelligence summary."""
    total = int(result.get("total", 0) or 0)
    total_value = float(result.get("total_value", 0.0) or 0.0)
    avg_conf = float(result.get("average_confidence", 0.0) or 0.0)
    counts = result.get("counts", {}) or {}

    dry = int(counts.get("dry", 0) or 0)
    green = int(counts.get("green", 0) or 0)
    tender = int(counts.get("tender", 0) or 0)

    avg_value = total_value / total if total else 0.0

    st.markdown("### 🥥 Bunch Intelligence")

    c1, c2, c3 = st.columns(3)
    c1.metric("🥥 Detected Coconuts", total)
    c2.metric("💰 Estimated Bunch Value", f"₹{total_value:,.2f}")
    c3.metric("🎯 Avg. Confidence", f"{avg_conf:.1%}")

    c4, c5, c6 = st.columns(3)
    c4.metric("🍂 Dry", dry)
    c5.metric("🌿 Green", green)
    c6.metric("💧 Tender", tender)

    st.info(
        f"💰 Average estimated value per detected coconut: "
        f"**₹{avg_value:,.2f}**"
    )

    if total == 0:
        st.warning(
            "No coconuts were detected. Try lowering the confidence "
            "threshold or using a clearer bunch image."
        )
    else:
        st.success(
            f"🥥 This image contains **{total} detected coconut(s)** "
            f"with an estimated bunch value of **₹{total_value:,.2f}**."
        )


# ============================================================
# NUMBERED COCONUT DETECTION VISUALIZATION
# ============================================================

def draw_numbered_coconut_boxes(image, boxes_data):
    """
    Draw a unique #1, #2, #3... label for every detected coconut.

    boxes_data is expected to contain entries with x1, y1, x2, y2.
    The original detection image is copied so the source image is not
    modified in-place.
    """
    if image is None:
        return image

    try:
        canvas = image.copy()
        draw = ImageDraw.Draw(canvas)

        if not boxes_data:
            return canvas

        # Stable ordering: top-to-bottom, then left-to-right.
        ordered = sorted(
            boxes_data,
            key=lambda b: (
                float(b.get("y1", 0)),
                float(b.get("x1", 0)),
            ),
        )

        for idx, box in enumerate(ordered, start=1):
            x1 = int(float(box.get("x1", 0)))
            y1 = int(float(box.get("y1", 0)))
            x2 = int(float(box.get("x2", 0)))
            y2 = int(float(box.get("y2", 0)))

            # Keep coordinates inside the image.
            x1 = max(0, min(x1, canvas.width - 1))
            y1 = max(0, min(y1, canvas.height - 1))
            x2 = max(0, min(x2, canvas.width - 1))
            y2 = max(0, min(y2, canvas.height - 1))

            draw.rectangle(
                [x1, y1, x2, y2],
                outline="white",
                width=3,
            )

            label = f"#{idx}"

            try:
                bbox = draw.textbbox((0, 0), label)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
            except Exception:
                tw, th = 24, 18

            label_x = x1
            label_y = max(0, y1 - th - 8)

            draw.rounded_rectangle(
                [
                    label_x,
                    label_y,
                    label_x + tw + 12,
                    label_y + th + 8,
                ],
                radius=5,
                fill="black",
            )

            draw.text(
                (label_x + 6, label_y + 4),
                label,
                fill="white",
            )

        return canvas

    except Exception:
        # Never break the analysis pipeline because of visualization.
        return image

# ============================================================
# AI PERFORMANCE LAB
# ============================================================

def run_performance_benchmark(image, yolo_model, openvino_model=None, conf_threshold=0.25):
    """
    Run the same image through YOLO and OpenVINO and return
    measured inference/processing metrics.

    The benchmark intentionally measures the complete model.predict
    call used by the application, rather than displaying fabricated
    performance numbers.
    """
    import time

    result = {
        "yolo": None,
        "openvino": None,
        "speedup": None,
        "detection_match": None,
        "error": None,
    }

    def _run(model):
        start = time.perf_counter()
        predictions = model.predict(
            source=image,
            conf=conf_threshold,
            verbose=False,
        )
        elapsed = time.perf_counter() - start

        count = 0
        confidences = []

        if predictions:
            first = predictions[0]
            if getattr(first, "boxes", None) is not None:
                count = len(first.boxes)
                try:
                    confidences = first.boxes.conf.cpu().numpy().tolist()
                except Exception:
                    try:
                        confidences = [float(x) for x in first.boxes.conf]
                    except Exception:
                        confidences = []

        avg_conf = (
            sum(confidences) / len(confidences)
            if confidences else 0.0
        )

        return {
            "time": elapsed,
            "time_ms": elapsed * 1000.0,
            "fps": (1.0 / elapsed) if elapsed > 0 else 0.0,
            "count": int(count),
            "avg_confidence": avg_conf,
        }

    try:
        if yolo_model is None:
            result["error"] = "YOLO model is not available."
            return result

        result["yolo"] = _run(yolo_model)

        if openvino_model is not None:
            result["openvino"] = _run(openvino_model)

            yolo_time = result["yolo"]["time"]
            ov_time = result["openvino"]["time"]

            if ov_time > 0:
                result["speedup"] = yolo_time / ov_time

            result["detection_match"] = (
                result["yolo"]["count"] == result["openvino"]["count"]
            )
        else:
            result["error"] = (
                "OpenVINO model is not available. "
                "The benchmark can only compare engines when both models are loaded."
            )

    except Exception as exc:
        result["error"] = str(exc)

    return result


# MAIN APPLICATION PAGE

# ============================================================




def performance_lab_page(yolo_model, openvino_model, conf_threshold=0.25):
    """Display the AI engine performance comparison workspace."""

    st.markdown('<div class="coconut-bg home"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="home-hero">
          <div class="home-kicker">Experimental AI Evaluation</div>
          <div class="home-title">⚡ AI Performance Lab</div>
          <p class="home-copy">
            Run the same coconut image through the available inference
            engines and measure actual latency, FPS, confidence and
            detection consistency.
          </p>
          <div class="home-badges">
            <span class="home-badge">⚡ YOLO vs OpenVINO</span>
            <span class="home-badge">⏱️ Real Runtime</span>
            <span class="home-badge">🎯 Detection Consistency</span>
            <span class="home-badge">📈 FPS</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            position:relative;z-index:2;
            color:#8fe2aa;font-size:.72rem;
            letter-spacing:.18em;font-weight:800;
            text-transform:uppercase;margin:12px 0 10px;">
            BENCHMARK WORKSPACE
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "📤 Upload a test coconut-bunch image",
        type=["jpg", "jpeg", "png"],
        key="performance_lab_upload",
        help="Use the same image whenever you want to compare engines consistently.",
    )

    if uploaded is None:
        st.info(
            "Upload one coconut bunch image to start a real YOLO vs OpenVINO benchmark."
        )
        return

    image = Image.open(uploaded).convert("RGB")

    st.image(
        image,
        caption="Benchmark input",
        use_container_width=True,
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        st.caption(
            "Both engines receive the same image and confidence threshold. "
            "Measurements are taken during the actual model prediction call."
        )

    with col2:
        run = st.button(
            "⚡ Run Benchmark",
            type="primary",
            use_container_width=True,
        )

    if not run:
        return

    with st.spinner("Running YOLO and OpenVINO on the same image..."):
        benchmark = run_performance_benchmark(
            image=image,
            yolo_model=yolo_model,
            openvino_model=openvino_model,
            conf_threshold=conf_threshold,
        )

    if benchmark.get("error"):
        st.error(f"Benchmark could not be completed: {benchmark['error']}")
        return

    yolo = benchmark["yolo"]
    ov = benchmark["openvino"]

    st.markdown("### 📊 Live Benchmark Results")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "YOLO Latency",
        f"{yolo['time_ms']:.1f} ms",
    )
    c2.metric(
        "OpenVINO Latency",
        f"{ov['time_ms']:.1f} ms",
    )
    c3.metric(
        "YOLO FPS",
        f"{yolo['fps']:.2f}",
    )
    c4.metric(
        "OpenVINO FPS",
        f"{ov['fps']:.2f}",
    )

    if benchmark["speedup"] is not None:
        st.markdown(
            f"""
            <div class="glass-card" style="
                position:relative;z-index:2;
                margin:18px 0;padding:24px;border-radius:22px;
                text-align:center;">
              <div style="
                color:#8fe2aa;font-size:.72rem;
                letter-spacing:.18em;font-weight:800;">
                MEASURED ACCELERATION
              </div>
              <div style="
                color:#f7fff9;font-size:2.7rem;
                font-weight:850;margin-top:5px;">
                {benchmark["speedup"]:.2f}×
              </div>
              <div style="color:rgba(235,251,241,.60);font-size:.82rem;">
                YOLO runtime ÷ OpenVINO runtime
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 🎯 Detection Consistency")

    d1, d2, d3, d4 = st.columns(4)

    d1.metric("YOLO Objects", yolo["count"])
    d2.metric("OpenVINO Objects", ov["count"])
    d3.metric("YOLO Confidence", f"{yolo['avg_confidence']:.2%}")
    d4.metric("OpenVINO Confidence", f"{ov['avg_confidence']:.2%}")

    if benchmark["detection_match"]:
        st.success(
            f"✅ Both engines detected {yolo['count']} object(s) on this image."
        )
    else:
        st.warning(
            "⚠️ Detection counts differ between the two inference engines. "
            "Review the confidence threshold and model outputs before drawing conclusions."
        )

    st.markdown("### 🧪 Experimental Summary")

    summary_rows = [
        {
            "Metric": "Inference latency",
            "YOLO": f"{yolo['time_ms']:.2f} ms",
            "OpenVINO": f"{ov['time_ms']:.2f} ms",
        },
        {
            "Metric": "FPS",
            "YOLO": f"{yolo['fps']:.2f}",
            "OpenVINO": f"{ov['fps']:.2f}",
        },
        {
            "Metric": "Detected objects",
            "YOLO": yolo["count"],
            "OpenVINO": ov["count"],
        },
        {
            "Metric": "Average confidence",
            "YOLO": f"{yolo['avg_confidence']:.2%}",
            "OpenVINO": f"{ov['avg_confidence']:.2%}",
        },
    ]

    st.dataframe(
        summary_rows,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "⚠️ Benchmark values depend on the machine, model, image size, "
        "OpenVINO device and current system load. Repeat the test over "
        "multiple images for a more reliable experimental result."
    )



def _sync_performance_models():
    """
    Mirror existing model variables into session state without changing
    the application's model-loading implementation.
    """
    if "yolo_model" not in st.session_state:
        try:
            st.session_state["yolo_model"] = globals().get("yolo_model")
        except Exception:
            st.session_state["yolo_model"] = None

    if "openvino_model" not in st.session_state:
        try:
            st.session_state["openvino_model"] = globals().get("openvino_model")
        except Exception:
            st.session_state["openvino_model"] = None



def app_page():

    """Main Coconut Grading AI application."""

    _sync_performance_models()

    # New showcase navigation. Existing analysis controls remain below.
    if "active_workspace" not in st.session_state:
        st.session_state["active_workspace"] = "Coconut Analysis"

    workspace = st.sidebar.radio(
        "🚀 Workspace",
        ["Coconut Analysis", "⚡ AI Performance Lab"],
        index=(
            1
            if st.session_state.get("active_workspace") == "⚡ AI Performance Lab"
            else 0
        ),
        key="workspace_selector",
    )

    st.session_state["active_workspace"] = workspace

    if workspace == "⚡ AI Performance Lab":
        performance_lab_page(
            yolo_model=st.session_state.get("yolo_model"),
            openvino_model=st.session_state.get("openvino_model"),
            conf_threshold=st.session_state.get("confidence_threshold", 0.25),
        )
        return


    st.markdown('<div class="coconut-bg home"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="home-hero">
          <div class="home-kicker">Coconut Intelligence Workspace</div>
          <div class="home-title">Turn every bunch into data.</div>
          <p class="home-copy">
            Detect individual coconuts, understand maturity, and calculate
            transparent bunch-wise value using your selected AI engine.
          </p>
          <div style="display:flex;align-items:center;gap:8px;margin-top:4px;margin-bottom:16px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#72d79b;box-shadow:0 0 16px rgba(114,215,155,.8);"></span>
            <span style="color:rgba(230,250,237,.58);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;">
              AI workspace online
            </span>
          </div>
          <div class="home-badges">
            <span class="home-badge">⚡ OpenVINO Ready</span>
            <span class="home-badge">🎯 Object Detection</span>
            <span class="home-badge">🥥 Bunch Analysis</span>
            <span class="home-badge">💰 Smart Valuation</span>
          </div>
        </div>

        <div class="workflow-title">ANALYSIS PIPELINE</div>
        <div class="workflow">
          <div class="workflow-card">
            <div class="workflow-number">01 / SCAN</div>
            <div class="workflow-name">See the bunch</div>
            <div class="workflow-text">Upload one image or an entire batch.</div>
          </div>
          <div class="workflow-card">
            <div class="workflow-number">02 / UNDERSTAND</div>
            <div class="workflow-name">Detect & classify</div>
            <div class="workflow-text">Count coconuts and identify maturity.</div>
          </div>
          <div class="workflow-card">
            <div class="workflow-number">03 / VALUE</div>
            <div class="workflow-name">Estimate the harvest</div>
            <div class="workflow-text">Get individual and bunch-wise valuation.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )



    # ========================================================

    # SIDEBAR

    # ========================================================



    with st.sidebar:



        # ----------------------------------------------------

        # USER INFORMATION

        # ----------------------------------------------------



        if st.session_state.current_user:



            st.markdown(

                f"**👤 "

                f"{st.session_state.current_user['username']}"

                f"**"

            )



            st.markdown(

                f"*Role: "

                f"{st.session_state.current_user['role']}"

                f"*"

            )



            st.divider()



        # ----------------------------------------------------

        # SETTINGS

        # ----------------------------------------------------



        st.markdown(

            "### ⚙️ Settings"

        )



        # ====================================================

        # AI ENGINE

        # ====================================================



        st.markdown(

            "### 🧠 AI Engine"

        )



        available_engines = [

            "YOLO"

        ]



        if openvino_model is not None:



            available_engines.append(

                "OpenVINO ⚡"

            )



        ai_engine = st.radio(

            "Select Detection Engine",

            available_engines,

            index=(

                1

                if openvino_model is not None

                else 0

            ),

        )



        if ai_engine == "OpenVINO ⚡":



            st.success(

                "⚡ OpenVINO CPU acceleration enabled"

            )



        else:



            st.info(

                "🤖 Standard YOLO inference enabled"

            )



        # ----------------------------------------------------

        # CONFIDENCE

        # ----------------------------------------------------



        conf_threshold = st.slider(

            "Confidence Threshold",

            min_value=config.MIN_CONFIDENCE_THRESHOLD,

            max_value=config.MAX_CONFIDENCE_THRESHOLD,

            value=config.DEFAULT_CONFIDENCE_THRESHOLD,

            step=config.CONFIDENCE_STEP,

        )



        # ----------------------------------------------------

        # MARKET RATES

        # ----------------------------------------------------



        st.divider()



        st.markdown(

            "### 💰 Market Rates (₹)"

        )



        dry_rate = st.number_input(

            "Dry Mature (₹/pc)",

            value=DEFAULT_MARKET_RATES["dry"],

            step=1.0,

        )



        green_rate = st.number_input(

            "Fresh Green (₹/pc)",

            value=DEFAULT_MARKET_RATES["green"],

            step=1.0,

        )



        tender_rate = st.number_input(

            "Tender Water (₹/pc)",

            value=DEFAULT_MARKET_RATES["tender"],

            step=1.0,

        )



        active_rates = {

            "dry": float(dry_rate),

            "green": float(green_rate),

            "tender": float(tender_rate),

        }



        valid, msg = validate_market_rates(

            active_rates

        )



        if not valid:

            st.error(msg)



        # ----------------------------------------------------

        # NAVIGATION

        # ----------------------------------------------------



        st.divider()



        if st.button(

            "📋 View History",

            use_container_width=True,

        ):



            st.session_state.page = "history"

            st.rerun()



        if st.button(

            "📊 Analytics",

            use_container_width=True,

        ):



            st.session_state.page = "analytics"

            st.rerun()



        # ----------------------------------------------------

        # LOGOUT

        # ----------------------------------------------------



        if st.button(

            "🚪 Logout",

            use_container_width=True,

        ):



            logout_username = "unknown"



            if st.session_state.current_user:



                logout_username = (

                    st.session_state.current_user[

                        "username"

                    ]

                )



            auth_manager.logout(

                st.session_state.session_token

            )



            st.session_state.session_token = None

            st.session_state.current_user = None

            st.session_state.page = "login"



            logger.log_user_action(

                logout_username,

                "logout",

            )



            st.rerun()



    # ========================================================

    # MAIN HEADER

    # ========================================================



    st.markdown(
        """
        <div style="position:relative;z-index:2;margin:10px 0 14px;">
          <div style="color:#8fe2aa;font-size:.72rem;letter-spacing:.18em;font-weight:800;text-transform:uppercase;">
            ANALYSIS CONSOLE
          </div>
          <div style="color:#f5fff8;font-size:1.7rem;font-weight:800;margin-top:4px;">
            Start a new coconut analysis
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



    # ========================================================

    # UPLOAD MODE

    # ========================================================



    upload_mode = st.radio(

        "📤 Upload Mode:",

        options=[

            "Single Image",

            "Bulk Upload (Multiple Images)",

        ],

        horizontal=True,

    )



    # ========================================================

    # SINGLE IMAGE

    # ========================================================



    if upload_mode == "Single Image":



        uploaded_file = st.file_uploader(

            "📤 Upload Image",

            type=[

                "jpg",

                "jpeg",

                "png",

                "webp",

            ],

            accept_multiple_files=False,

        )



        if uploaded_file is not None:



            image = Image.open(

                uploaded_file

            ).convert("RGB")



            valid, msg = validate_image(

                image

            )



            if not valid:



                st.error(

                    f"Invalid image: {msg}"

                )



            else:



                col_left, col_right = st.columns(

                    [1, 1],

                    gap="large",

                )



                # ====================================================

                # IMAGE PREVIEW

                # ====================================================



                with col_left:



                    st.subheader(

                        "🖼️ Uploaded Image"

                    )



                    try:



                        image_stats = (

                            ImageProcessor.get_image_statistics(

                                image

                            )

                        )



                        if isinstance(

                            image_stats,

                            dict,

                        ):



                            quality_score = (

                                image_stats.get(

                                    "quality_score",

                                    0,

                                )

                            )



                            quality_level = (

                                image_stats.get(

                                    "quality_level",

                                    "Unknown",

                                )

                            )



                        else:



                            try:



                                (

                                    quality_score,

                                    quality_level,

                                ) = image_stats



                            except Exception:



                                quality_score = 0

                                quality_level = (

                                    "Unknown"

                                )



                    except Exception:



                        quality_score = 0

                        quality_level = (

                            "Unknown"

                        )



                    st.image(

                        image,

                        use_container_width=True,

                    )



                    st.caption(

                        f"Quality: {quality_level}"

                    )



                # ====================================================

                # ANALYSIS

                # ====================================================



                with col_right:



                    st.subheader(

                        "🔍 Analysis"

                    )



                    st.info(

                        f"🧠 Selected Engine: "

                        f"**{ai_engine}**"

                    )



                    if st.button(

                        "🚀 Analyze",

                        type="primary",

                        use_container_width=True,

                    ):



                        # --------------------------------------------

                        # ENGINE VALIDATION

                        # --------------------------------------------



                        if (

                            ai_engine == "OpenVINO ⚡"

                            and openvino_model is None

                        ):



                            st.error(

                                "⚡ OpenVINO model "

                                "is not available."

                            )



                        elif (

                            ai_engine == "YOLO"

                            and yolo_model is None

                        ):



                            st.error(

                                "🤖 YOLO model "

                                "is not available."

                            )



                        else:



                            perf_monitor.start_timer(

                                "single_analysis"

                            )



                            with st.spinner(

                                f"Running {ai_engine} detection..."

                            ):



                                try:



                                    # ====================================

                                    # DETECTION

                                    # ====================================



                                    if (

                                        ai_engine

                                        == "OpenVINO ⚡"

                                    ):



                                        detection_data = detect_bunch_coconuts(
                                            detector_fn=detect_coconuts_openvino,
                                            model=openvino_model,
                                            image=image,
                                            conf_threshold=conf_threshold,
                                        )



                                    else:



                                        detection_data = detect_bunch_coconuts(
                                            detector_fn=detect_coconuts,
                                            model=yolo_model,
                                            image=image,
                                            conf_threshold=conf_threshold,
                                        )



                                    # ====================================

                                    # DETECTION DATA

                                    # ====================================



                                    counts = (

                                        detection_data[

                                            "counts"

                                        ]

                                    )



                                    total = (

                                        detection_data[

                                            "total"

                                        ]

                                    )



                                    avg_conf = (

                                        detection_data[

                                            "average_confidence"

                                        ]

                                    )



                                    # ====================================

                                    # GRADING

                                    # ====================================



                                    grade_info = (

                                        calculate_grade_and_summary(

                                            counts,

                                            avg_conf,

                                        )

                                    )



                                    # ====================================

                                    # VALUATION

                                    # ====================================



                                    (

                                        total_val,

                                        breakdown,

                                    ) = (

                                        calculate_market_valuation(

                                            counts,

                                            active_rates,

                                        )

                                    )



                                    # ====================================

                                    # PROCESSING TIME

                                    # ====================================



                                    processing_time = (

                                        perf_monitor.end_timer(

                                            "single_analysis"

                                        )

                                    )



                                    # ====================================

                                    # DATABASE

                                    # ====================================



                                    if (

                                        st.session_state.current_user

                                    ):



                                        db.save_analysis_result(

                                            user_id=(

                                                st.session_state

                                                .current_user[

                                                    "user_id"

                                                ]

                                            ),

                                            filename=(

                                                uploaded_file.name

                                            ),

                                            counts=counts,

                                            grade=(

                                                grade_info[

                                                    "grade"

                                                ]

                                            ),

                                            confidence=avg_conf,

                                            total_value=total_val,

                                            market_rates=(

                                                active_rates

                                            ),

                                        )



                                        logger.log_analysis(

                                            st.session_state

                                            .current_user[

                                                "username"

                                            ],

                                            uploaded_file.name,

                                            total,

                                            grade_info["grade"],

                                            processing_time,

                                        )



                                    # ====================================

                                    # BUNCH PRICE BREAKDOWN
                                    # ====================================

                                    # One uploaded image is treated as one bunch.
                                    bunch_price_breakdown = create_bunch_price_breakdown(
                                        detection_data,
                                        active_rates,
                                    )

                                    # STORE RESULTS

                                    # ====================================



                                    st.session_state[

                                        "analysis_results"

                                    ] = {



                                        "plotted_image": (

                                            detection_data[

                                                "plotted_image"

                                            ]

                                        ),



                                        "counts": counts,



                                        "total": total,



                                        "avg_conf": avg_conf,



                                        "grade_info": (

                                            grade_info

                                        ),



                                        "total_value": (

                                            total_val

                                        ),



                                        "breakdown": (

                                            breakdown

                                        ),



                                        "processing_time": (

                                            processing_time

                                        ),



                                        "ai_engine": (

                                            ai_engine

                                        ),

                                        "bunch_price_breakdown": (
                                            bunch_price_breakdown
                                        ),

                                        "detection_passes": detection_data.get(
                                            "detection_passes", 1
                                        ),
                                    }



                                    st.success(

                                        "✅ Analysis completed successfully!"

                                    )



                                except Exception as e:



                                    st.error(

                                        f"Analysis failed: {str(e)}"

                                    )



                                    logger.error(

                                        f"Analysis error for "

                                        f"{uploaded_file.name}",

                                        e,

                                    )



    # ========================================================

    # BULK UPLOAD

    # ========================================================



    elif upload_mode == "Bulk Upload (Multiple Images)":



        uploaded_files = st.file_uploader(

            "📤 Upload Multiple Images",

            type=[

                "jpg",

                "jpeg",

                "png",

                "webp",

            ],

            accept_multiple_files=True,

        )



        if uploaded_files:



            st.subheader(

                f"📦 Processing "

                f"{len(uploaded_files)} images..."

            )



            if st.button(

                "🚀 Analyze All",

                type="primary",

                use_container_width=True,

            ):



                # --------------------------------------------

                # ENGINE VALIDATION

                # --------------------------------------------



                if (

                    ai_engine == "OpenVINO ⚡"

                    and openvino_model is None

                ):



                    st.error(

                        "⚡ OpenVINO model "

                        "is not available."

                    )



                elif (

                    ai_engine == "YOLO"

                    and yolo_model is None

                ):



                    st.error(

                        "🤖 YOLO model "

                        "is not available."

                    )



                else:



                    perf_monitor.start_timer(

                        "bulk_analysis"

                    )



                    batch_results = []



                    progress_bar = st.progress(

                        0

                    )



                    status_text = st.empty()



                    # ========================================

                    # PROCESS FILES

                    # ========================================



                    for idx, uploaded_file in enumerate(

                        uploaded_files

                    ):



                        try:



                            status_text.text(

                                f"Processing "

                                f"{idx + 1}/"

                                f"{len(uploaded_files)}: "

                                f"{uploaded_file.name}"

                            )



                            # --------------------------------

                            # LOAD IMAGE

                            # --------------------------------



                            image = Image.open(

                                uploaded_file

                            ).convert("RGB")



                            # --------------------------------

                            # VALIDATE

                            # --------------------------------



                            valid, msg = validate_image(

                                image

                            )



                            if not valid:



                                st.warning(

                                    f"⚠️ "

                                    f"{uploaded_file.name}: "

                                    f"{msg}"

                                )



                                continue



                            # --------------------------------

                            # DETECTION

                            # --------------------------------



                            if (

                                ai_engine

                                == "OpenVINO ⚡"

                            ):



                                detection_data = detect_bunch_coconuts(
                                    detector_fn=detect_coconuts_openvino,
                                    model=openvino_model,
                                    image=image,
                                    conf_threshold=conf_threshold,
                                )



                            else:



                                detection_data = detect_bunch_coconuts(
                                    detector_fn=detect_coconuts,
                                    model=yolo_model,
                                    image=image,
                                    conf_threshold=conf_threshold,
                                )



                            # --------------------------------

                            # DETECTION DATA

                            # --------------------------------



                            counts = detection_data[

                                "counts"

                            ]



                            total = detection_data[

                                "total"

                            ]



                            avg_conf = detection_data[

                                "average_confidence"

                            ]



                            # --------------------------------

                            # GRADING

                            # --------------------------------



                            grade_info = (

                                calculate_grade_and_summary(

                                    counts,

                                    avg_conf,

                                )

                            )



                            # --------------------------------

                            # VALUATION

                            # --------------------------------



                            (

                                total_val,

                                breakdown,

                            ) = (

                                calculate_market_valuation(

                                    counts,

                                    active_rates,

                                )

                            )



                            # --------------------------------

                            # STORE RESULT

                            # --------------------------------



                            batch_results.append(

                                {

                                    "filename": (

                                        uploaded_file.name

                                    ),

                                    "counts": counts,

                                    "total": total,

                                    "avg_conf": avg_conf,

                                    "grade": (

                                        grade_info[

                                            "grade"

                                        ]

                                    ),

                                    "badge_color": (

                                        grade_info[

                                            "badge_color"

                                        ]

                                    ),

                                    "total_value": (

                                        total_val

                                    ),

                                    "breakdown": (

                                        breakdown

                                    ),

                                    "ai_engine": (

                                        ai_engine

                                    ),

                                    "bunch_price_breakdown": (
                                        create_bunch_price_breakdown(
                                            detection_data,
                                            active_rates,
                                        )
                                    ),

                                    "detection_passes": detection_data.get(
                                        "detection_passes", 1
                                    ),
                                }

                            )



                            # --------------------------------

                            # DATABASE

                            # --------------------------------



                            if (

                                st.session_state.current_user

                            ):



                                db.save_analysis_result(

                                    user_id=(

                                        st.session_state

                                        .current_user[

                                            "user_id"

                                        ]

                                    ),

                                    filename=(

                                        uploaded_file.name

                                    ),

                                    counts=counts,

                                    grade=(

                                        grade_info[

                                            "grade"

                                        ]

                                    ),

                                    confidence=avg_conf,

                                    total_value=total_val,

                                    market_rates=(

                                        active_rates

                                    ),

                                )



                            # --------------------------------

                            # PROGRESS

                            # --------------------------------



                            progress_bar.progress(

                                (idx + 1)

                                / len(uploaded_files)

                            )



                        except Exception as e:



                            st.error(

                                f"Error processing "

                                f"{uploaded_file.name}: "

                                f"{str(e)}"

                            )



                            logger.error(

                                f"Bulk analysis error for "

                                f"{uploaded_file.name}",

                                e,

                            )



                    # ========================================

                    # BULK COMPLETE

                    # ========================================



                    if batch_results:



                        processing_time = (

                            perf_monitor.end_timer(

                                "bulk_analysis"

                            )

                        )



                        status_text.success(

                            f"✅ Processed "

                            f"{len(batch_results)}/"

                            f"{len(uploaded_files)} "

                            f"images in "

                            f"{processing_time:.2f}s"

                        )



                        # --------------------------------

                        # TOTAL COCONUTS

                        # --------------------------------



                        total_coconuts = sum(

                            r["total"]

                            for r in batch_results

                        )



                        # --------------------------------

                        # LOGGING

                        # --------------------------------



                        if (

                            st.session_state.current_user

                        ):



                            logger.log_batch_processing(

                                st.session_state

                                .current_user[

                                    "username"

                                ],

                                f"batch_"

                                f"{len(uploaded_files)}",

                                len(batch_results),

                                total_coconuts,

                                processing_time,

                            )



                        # --------------------------------

                        # SAVE RESULTS

                        # --------------------------------



                        st.session_state[

                            "batch_results"

                        ] = batch_results



    # ========================================================

    # DISPLAY BATCH RESULTS

    # ========================================================



    if (

        "batch_results" in st.session_state

        and len(

            st.session_state["batch_results"]

        ) > 0

    ):



        batch_results = st.session_state[

            "batch_results"

        ]



        st.divider()



        st.subheader(

            f"📊 Batch Analysis Results "

            f"({len(batch_results)} images)"

        )



        # --------------------------------------------

        # AGGREGATE STATISTICS

        # --------------------------------------------



        total_coconuts = sum(

            r["total"]

            for r in batch_results

        )



        total_value = sum(

            r["total_value"]

            for r in batch_results

        )



        avg_confidence = (

            sum(

                r["avg_conf"]

                for r in batch_results

            )

            / len(batch_results)

        )



        # --------------------------------------------
        # FARM BATCH INTELLIGENCE SUMMARY
        # --------------------------------------------

        total_dry = sum(
            int(r.get("counts", {}).get("dry", 0) or 0)
            for r in batch_results
        )
        total_green = sum(
            int(r.get("counts", {}).get("green", 0) or 0)
            for r in batch_results
        )
        total_tender = sum(
            int(r.get("counts", {}).get("tender", 0) or 0)
            for r in batch_results
        )

        avg_bunch_value = (
            total_value / len(batch_results)
            if batch_results else 0.0
        )
        avg_coconuts_per_bunch = (
            total_coconuts / len(batch_results)
            if batch_results else 0.0
        )

        st.markdown("### 🌴 Farm Batch Intelligence")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📸 Bunches Analysed", len(batch_results))
        col2.metric("🥥 Total Coconuts", total_coconuts)
        col3.metric("💰 Grand Total Value", f"₹{total_value:,.2f}")
        col4.metric("🎯 Avg Confidence", f"{avg_confidence:.2%}")

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("🍂 Dry", total_dry)
        col6.metric("🌿 Green", total_green)
        col7.metric("💧 Tender", total_tender)
        col8.metric("💰 Avg Value / Bunch", f"₹{avg_bunch_value:,.2f}")

        st.caption(
            f"Average {avg_coconuts_per_bunch:.1f} coconuts detected per "
            f"bunch • Grand estimated value is the sum of all analysed bunches."
        )

        st.divider()


        # --------------------------------------------

        # BUNCH-WISE VALUE CARDS
        # --------------------------------------------

        st.markdown("### 🥥 Bunch-wise Valuation")

        card_cols = st.columns(2)

        for idx, bunch in enumerate(batch_results):
            counts = bunch.get("counts", {}) or {}

            with card_cols[idx % 2]:
                st.markdown(
                    f"""
                    <div style="
                        padding:18px;
                        margin-bottom:14px;
                        border:1px solid rgba(255,255,255,0.12);
                        border-radius:16px;
                        background:rgba(255,255,255,0.035);
                    ">
                        <div style="font-size:18px;font-weight:700;">
                            🥥 Bunch {idx + 1}
                        </div>
                        <div style="font-size:13px;opacity:.72;margin:4px 0 12px;">
                            {bunch.get("filename", "Image")}
                        </div>
                        <div style="font-size:15px;">
                            <b>{bunch.get("total", 0)}</b> coconuts
                            &nbsp; • &nbsp;
                            <b>₹{float(bunch.get("total_value", 0) or 0):,.2f}</b>
                        </div>
                        <div style="font-size:13px;opacity:.82;margin-top:8px;">
                            🍂 {counts.get("dry", 0)} Dry
                            &nbsp; | &nbsp;
                            🌿 {counts.get("green", 0)} Green
                            &nbsp; | &nbsp;
                            💧 {counts.get("tender", 0)} Tender
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.divider()

        # TABS

        # --------------------------------------------



        (

            tab_table,

            tab_detail,

            tab_export,

        ) = st.tabs(

            [

                "📋 Summary Table",

                "🔍 Detailed View",

                "📥 Export",

            ]

        )



        # ============================================

        # SUMMARY TABLE

        # ============================================



        with tab_table:



            table_data = []



            for r in batch_results:



                table_data.append(

                    {

                        "📁 File": r[

                            "filename"

                        ],

                        "🥥 Count": r[

                            "total"

                        ],

                        "🏆 Grade": r[

                            "grade"

                        ],

                        "📊 Confidence": (

                            f"{r['avg_conf']:.2%}"

                        ),

                        "💵 Bunch Total": (

                            f"₹{r['total_value']:.2f}"

                        ),

                        "🧠 Engine": r.get(

                            "ai_engine",

                            "YOLO",

                        ),

                    }

                )



            st.dataframe(

                table_data,

                use_container_width=True,

            )



        # ============================================

        # DETAILED VIEW

        # ============================================



        with tab_detail:



            for idx, result in enumerate(

                batch_results,

                1,

            ):



                with st.expander(

                    (

                        f"📄 "

                        f"{result['filename']} - "

                        f"{result['grade']}"

                    ),

                    expanded=(idx == 1),

                ):



                    col1, col2 = st.columns(

                        [1, 1]

                    )



                    with col1:



                        st.metric(

                            "Total Coconuts",

                            result["total"],

                        )



                        st.metric(

                            "Confidence",

                            f"{result['avg_conf']:.2%}",

                        )



                        st.write(

                            "**Detection Engine:**"

                        )



                        st.write(

                            result.get(

                                "ai_engine",

                                "YOLO",

                            )

                        )



                        breakdown = result[

                            "breakdown"

                        ]



                        st.write(

                            "**Breakdown:**"

                        )



                        for coconut_type in [

                            "dry",

                            "green",

                            "tender",

                        ]:



                            st.write(

                                f"• "

                                f"{coconut_type.title()}: "

                                f"{breakdown[coconut_type]['count']}"

                            )



                    with col2:



                        st.metric(

                            "Total Value",

                            f"₹{result['total_value']:.2f}",

                        )



                        
                        st.write("**🥥 Individual Coconut Pricing:**")

                        individual_rows = result.get("bunch_price_breakdown", [])
                        if individual_rows:
                            st.dataframe(
                                individual_rows,
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.warning("No individual coconut detections are available.")

                        st.write(

                            "**Price Breakdown:**"

                        )



                        for coconut_type in [

                            "dry",

                            "green",

                            "tender",

                        ]:



                            st.write(

                                f"• "

                                f"{coconut_type.title()}: "

                                f"₹{breakdown[coconut_type]['subtotal']:.2f}"

                            )



        # ============================================

        # EXPORT

        # ============================================



        with tab_export:



            if st.button(

                "📄 Export Batch as CSV",

                use_container_width=True,

            ):



                csv_path = (

                    report_gen.generate_csv_report(

                        f"batch_"

                        f"{len(batch_results)}",

                        batch_results,

                    )

                )



                st.success(

                    f"✅ Report saved: "

                    f"{csv_path}"

                )



            if st.button(

                "📄 Export Batch Summary",

                use_container_width=True,

            ):



                summary = {

                    "total_images": (

                        len(batch_results)

                    ),

                    "total_coconuts": (

                        total_coconuts

                    ),

                    "total_value": (

                        total_value

                    ),

                    "avg_confidence": (

                        avg_confidence

                    ),

                    "results": batch_results,

                }



                json_path = (

                    report_gen.generate_json_report(

                        f"batch_"

                        f"{len(batch_results)}"

                        f"_summary",

                        summary,

                    )

                )



                st.success(

                    f"✅ Summary saved: "

                    f"{json_path}"

                )



    # ========================================================

    # DISPLAY SINGLE ANALYSIS RESULTS

    # ========================================================



    if (

        "analysis_results"

        in st.session_state

    ):



        res = st.session_state[

            "analysis_results"

        ]



        st.divider()



        st.subheader(

            "📊 Analysis Results"

        )



        st.caption(

            "🧠 Detection Engine: "

            f"{res.get('ai_engine', 'YOLO')}"

        )



        (

            tab_viz,

            tab_bunch,
            tab_grade,

            tab_pricing,

            tab_export,

        ) = st.tabs(

            [

                "📸 Detection",

                "🥥 Bunch & Price",
                "🏆 Grade",

                "💰 Valuation",

                "📥 Export",

            ]

        )



        # ====================================================

        # DETECTION TAB

        # ====================================================



        with tab_viz:



            st.image(

                res["plotted_image"],

                channels="BGR",

                use_container_width=True,

            )



            m1, m2, m3, m4 = st.columns(

                4

            )



            m1.metric(

                "🥥 Total",

                res["total"],

            )



            m2.metric(

                "🍂 Dry",

                res["counts"]["dry"],

            )



            m3.metric(

                "🌿 Green",

                res["counts"]["green"],

            )



            m4.metric(

                "💧 Tender",

                res["counts"]["tender"],

            )



            st.info(

                f"⏱️ Processing Time: "

                f"{res['processing_time']:.3f} seconds"

            )



            st.info(

                f"📊 Average Confidence: "

                f"{res['avg_conf']:.2%}"

            )



        # ====================================================

        # ====================================================
        # BUNCH & PRICE TAB
        # ====================================================

        with tab_bunch:

            st.subheader("🥥 One Bunch Analysis")
            st.caption(
                "Each uploaded image is treated as one bunch. "
                "The AI counts coconuts, splits them by maturity type, "
                "and calculates an estimated value."
            )

            bunch_total = res["total"]
            bunch_value = res["total_value"]
            bunch_breakdown = res["breakdown"]

            render_bunch_result_summary(res)

            st.divider()
            st.caption(
                "🔢 Detection numbers match the coconut numbers in the pricing table below."
            )

            st.subheader("💰 Individual Coconut Pricing")

            coconut_rows = res.get("bunch_price_breakdown", [])
            if coconut_rows:
                st.dataframe(
                    coconut_rows,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning("No individual coconut detections are available.")

            st.divider()
            st.subheader("🧾 Bunch Price Summary")

            summary_data = [
                {
                    "Coconut Type": "Dry",
                    "Count": bunch_breakdown["dry"]["count"],
                    "Rate": f"₹{bunch_breakdown['dry']['rate']:.2f}",
                    "Subtotal": f"₹{bunch_breakdown['dry']['subtotal']:.2f}",
                },
                {
                    "Coconut Type": "Green",
                    "Count": bunch_breakdown["green"]["count"],
                    "Rate": f"₹{bunch_breakdown['green']['rate']:.2f}",
                    "Subtotal": f"₹{bunch_breakdown['green']['subtotal']:.2f}",
                },
                {
                    "Coconut Type": "Tender",
                    "Count": bunch_breakdown["tender"]["count"],
                    "Rate": f"₹{bunch_breakdown['tender']['rate']:.2f}",
                    "Subtotal": f"₹{bunch_breakdown['tender']['subtotal']:.2f}",
                },
            ]

            st.table(summary_data)
            st.info(
                f"🔎 Multi-pass bunch detection used "
                f"{res.get('detection_passes', 1)} inference passes "
                f"to find partially hidden coconuts."
            )

            st.success(
                f"🥥 This bunch contains {bunch_total} coconuts "
                f"with an estimated total value of ₹{bunch_value:.2f}."
            )

        # GRADE TAB

        # ====================================================



        with tab_grade:



            grade_info = res[

                "grade_info"

            ]



            grade_parts = (

                grade_info["grade"]

                .split()

            )



            if (

                len(grade_parts) > 1

                and grade_parts[0]

                == "Grade"

            ):



                grade_letter = (

                    grade_parts[1][0]

                )



            else:



                grade_letter = "?"



            st.markdown(

                f"""

                <div style="

                    text-align: center;

                    margin: 20px 0;

                ">



                    <div style="

                        display: inline-flex;

                        background-color:

                            {grade_info['badge_color']};

                        color: white;

                        width: 100px;

                        height: 100px;

                        border-radius: 50%;

                        align-items: center;

                        justify-content: center;

                        font-size: 3rem;

                        font-weight: bold;

                    ">

                        {grade_letter}

                    </div>



                </div>



                <h3 style="

                    text-align: center;

                    color:

                        {grade_info['badge_color']};

                ">

                    {grade_info['grade']}

                </h3>

                """,

                unsafe_allow_html=True,

            )



            st.info(

                grade_info["description"]

            )



            # --------------------------------------------

            # DISTRIBUTION

            # --------------------------------------------



            st.subheader(

                "🥥 Coconut Distribution"

            )



            distribution = (

                grade_info[

                    "distribution"

                ]

            )



            for coconut_type in [

                "dry",

                "green",

                "tender",

            ]:



                percentage = distribution.get(

                    coconut_type,

                    0,

                )



                st.write(

                    f"**{coconut_type.title()}** "

                    f"{percentage:.1f}%"

                )



                st.progress(

                    min(

                        max(

                            int(percentage),

                            0,

                        ),

                        100,

                    )

                )



        # ====================================================

        # PRICING TAB

        # ====================================================



        with tab_pricing:



            st.metric(

                "💵 Total Value",

                f"₹{res['total_value']:.2f}",

            )



            breakdown = res[

                "breakdown"

            ]



            pricing_data = [



                {

                    "Type": "Dry Mature",

                    "Count": breakdown[

                        "dry"

                    ]["count"],

                    "Rate": (

                        f"₹"

                        f"{breakdown['dry']['rate']:.2f}"

                    ),

                    "Subtotal": (

                        f"₹"

                        f"{breakdown['dry']['subtotal']:.2f}"

                    ),

                },



                {

                    "Type": "Fresh Green",

                    "Count": breakdown[

                        "green"

                    ]["count"],

                    "Rate": (

                        f"₹"

                        f"{breakdown['green']['rate']:.2f}"

                    ),

                    "Subtotal": (

                        f"₹"

                        f"{breakdown['green']['subtotal']:.2f}"

                    ),

                },



                {

                    "Type": "Tender Water",

                    "Count": breakdown[

                        "tender"

                    ]["count"],

                    "Rate": (

                        f"₹"

                        f"{breakdown['tender']['rate']:.2f}"

                    ),

                    "Subtotal": (

                        f"₹"

                        f"{breakdown['tender']['subtotal']:.2f}"

                    ),

                },

            ]



            st.table(

                pricing_data

            )



            st.caption(

                "💡 Valuation is calculated using "

                "the configured market rates."

            )



        # ====================================================

        # EXPORT TAB

        # ====================================================



        with tab_export:



            if st.button(

                "📄 Export as CSV",

                use_container_width=True,

            ):



                csv_path = (

                    report_gen.generate_csv_report(

                        "analysis",

                        [res],

                    )

                )



                st.success(

                    f"Report saved: "

                    f"{csv_path}"

                )



            if st.button(

                "📄 Export as Text",

                use_container_width=True,

            ):



                txt_path = (

                    report_gen.generate_text_report(

                        "analysis",

                        res,

                    )

                )



                st.success(

                    f"Report saved: "

                    f"{txt_path}"

                )





# ============================================================

# HISTORY PAGE

# ============================================================



def history_page():

    """Display user analysis history."""



    st.title(

        "📋 Analysis History"

    )



    if st.session_state.current_user:



        user_id = (

            st.session_state

            .current_user[

                "user_id"

            ]

        )



        results = db.get_user_results(

            user_id

        )



        if results:



            st.dataframe(

                results,

                use_container_width=True,

            )



        else:



            st.info(

                "No analysis history yet"

            )



    if st.button(

        "← Back to App"

    ):



        st.session_state.page = "app"

        st.rerun()





# ============================================================

# ANALYTICS PAGE

# ============================================================



def analytics_page():

    """Display user analytics and insights."""



    st.title(

        "📊 Analytics & Insights"

    )



    if st.session_state.current_user:



        user_id = (

            st.session_state

            .current_user[

                "user_id"

            ]

        )



        stats = db.get_user_statistics(

            user_id

        )



        col1, col2, col3, col4 = st.columns(

            4

        )



        col1.metric(

            "Total Analyses",

            stats.get(

                "total_analyses",

                0,

            ),

        )



        col2.metric(

            "Total Coconuts",

            stats.get(

                "total_coconuts_analyzed",

                0,

            ),

        )



        col3.metric(

            "Avg Batch Value",

            f"₹"

            f"{stats.get('avg_batch_value', 0):.2f}",

        )



        col4.metric(

            "Total Value",

            f"₹"

            f"{stats.get('total_value', 0):.2f}",

        )



    if st.button(

        "← Back to App"

    ):



        st.session_state.page = "app"

        st.rerun()





# ============================================================

# PAGE ROUTING

# ============================================================



if (

    st.session_state.session_token

    is None

):



    login_page()



elif (

    st.session_state.page

    == "app"

):



    app_page()



elif (

    st.session_state.page

    == "history"

):



    history_page()



elif (

    st.session_state.page

    == "analytics"

):



    analytics_page()
