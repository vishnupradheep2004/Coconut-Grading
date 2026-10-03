"""

app_integrated.py



Coconut AI Studio - Full Integration



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
import sqlite3
import json
import uuid
from datetime import datetime

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

    page_title="Coconut AI Studio",

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


def _has_admin_account():
    """Return True when an admin account already exists."""
    try:
        method = getattr(db, "get_users_by_role", None)
        if callable(method):
            return len(method("admin") or []) > 0
    except Exception:
        pass
    for method_name in ("get_all_users", "get_users"):
        method = getattr(db, method_name, None)
        if not callable(method):
            continue
        try:
            for user in (method() or []):
                if isinstance(user, dict):
                    role = user.get("role", user.get("user_role", ""))
                else:
                    role = getattr(user, "role", getattr(user, "user_role", ""))
                if str(role).strip().lower() == "admin":
                    return True
        except Exception:
            continue
    return False


def _register_account_by_role(username, password, email, role):
    """Register a normal account or create the first admin account."""
    if role != "admin":
        return auth_manager.register_user(username, password, email, role)
    create_admin = getattr(auth_manager, "create_admin_user", None)
    if not callable(create_admin):
        return False, "Admin creation is not available. Add create_admin_user() to utils/auth.py first."
    try:
        result = create_admin(username, password, email)
    except TypeError:
        try:
            result = create_admin(username, email, password)
        except Exception as exc:
            return False, f"Unable to create admin account: {exc}"
    except Exception as exc:
        return False, f"Unable to create admin account: {exc}"
    if isinstance(result, tuple):
        return result
    return (True, "Admin account created successfully. You can now log in.") if result else (False, "Admin account could not be created.")





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
    
      /* ---------- ROLE WORKSPACE UI ---------- */
      .role-hero {{
        position: relative;
        z-index: 2;
        margin: 10px 0 22px;
        padding: 34px 38px;
        border-radius: 28px;
        border: 1px solid rgba(210,255,226,.14);
        background:
          linear-gradient(135deg, rgba(32,104,67,.28), rgba(255,255,255,.045));
        box-shadow: 0 28px 80px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.10);
        backdrop-filter: blur(24px) saturate(125%);
        -webkit-backdrop-filter: blur(24px) saturate(125%);
      }}

      .role-kicker {{
        color: #8fe2aa;
        font-size: .70rem;
        font-weight: 900;
        letter-spacing: .20em;
        text-transform: uppercase;
        margin-bottom: 9px;
      }}

      .role-title {{
        color: #f4fff7;
        font-size: clamp(2rem, 4vw, 3.5rem);
        line-height: 1.02;
        font-weight: 900;
        letter-spacing: -.04em;
      }}

      .role-copy {{
        max-width: 760px;
        margin-top: 14px;
        color: rgba(230,250,237,.68);
        font-size: 1rem;
        line-height: 1.7;
      }}

      .role-chip-row {{
        display:flex;
        flex-wrap:wrap;
        gap:8px;
        margin-top:20px;
      }}

      .role-chip {{
        display:inline-flex;
        align-items:center;
        gap:7px;
        padding:8px 12px;
        border-radius:999px;
        color:#dff9e8;
        background:rgba(255,255,255,.055);
        border:1px solid rgba(210,255,226,.12);
        font-size:.72rem;
        font-weight:800;
        letter-spacing:.04em;
      }}

      .role-stat {{
        position:relative;
        z-index:2;
        min-height:150px;
        padding:22px;
        border-radius:22px;
        border:1px solid rgba(210,255,226,.12);
        background:linear-gradient(135deg,rgba(255,255,255,.075),rgba(255,255,255,.025));
        box-shadow:0 20px 55px rgba(0,0,0,.20), inset 0 1px 0 rgba(255,255,255,.08);
        backdrop-filter:blur(18px);
      }}

      .role-stat-label {{
        color:rgba(230,250,237,.50);
        font-size:.68rem;
        font-weight:900;
        letter-spacing:.14em;
        text-transform:uppercase;
      }}

      .role-stat-value {{
        color:#f4fff7;
        font-size:2rem;
        font-weight:900;
        margin-top:12px;
      }}

      .role-stat-note {{
        color:rgba(230,250,237,.55);
        font-size:.76rem;
        margin-top:5px;
      }}

      .role-module {{
        position:relative;
        z-index:2;
        min-height:190px;
        padding:24px;
        border-radius:22px;
        border:1px solid rgba(210,255,226,.11);
        background:linear-gradient(135deg,rgba(255,255,255,.065),rgba(255,255,255,.018));
        box-shadow:0 20px 50px rgba(0,0,0,.18), inset 0 1px 0 rgba(255,255,255,.07);
        transition:transform .22s ease, border-color .22s ease, background .22s ease;
      }}

      .role-module:hover {{
        transform:translateY(-4px);
        border-color:rgba(143,226,170,.28);
        background:linear-gradient(135deg,rgba(70,170,105,.13),rgba(255,255,255,.025));
      }}

      .role-module-icon {{ font-size:1.65rem; }}
      .role-module-title {{
        color:#effff5;
        font-size:1.02rem;
        font-weight:850;
        margin-top:13px;
      }}
      .role-module-text {{
        color:rgba(230,250,237,.58);
        font-size:.78rem;
        line-height:1.55;
        margin-top:8px;
      }}

      .role-section-title {{
        position:relative;
        z-index:2;
        color:#8fe2aa;
        font-size:.72rem;
        font-weight:900;
        letter-spacing:.18em;
        text-transform:uppercase;
        margin:26px 0 12px;
      }}

      .role-callout {{
        position:relative;
        z-index:2;
        margin-top:22px;
        padding:18px 20px;
        border-left:3px solid #72d79b;
        border-radius:0 18px 18px 0;
        background:rgba(114,215,155,.055);
        color:rgba(235,255,242,.72);
      }}

    </style>
    """, unsafe_allow_html=True
)


# ============================================================
# COCONUT AI STUDIO — UI REDESIGN V2
# ============================================================
# This is a presentation-only layer. Existing AI, database,
# authentication, role routing and analysis logic remain intact.
# ============================================================

st.markdown(r"""
<style>
/* ---------- DESIGN TOKENS ---------- */
:root {
  --ca-bg: #07110d;
  --ca-panel: rgba(15, 30, 23, .72);
  --ca-panel-2: rgba(20, 42, 31, .72);
  --ca-border: rgba(184, 255, 211, .13);
  --ca-border-strong: rgba(111, 230, 151, .30);
  --ca-text: #f4fff8;
  --ca-muted: rgba(226, 245, 234, .62);
  --ca-green: #69e49a;
  --ca-green-2: #35b86f;
  --ca-cyan: #63d8c1;
  --ca-shadow: 0 24px 70px rgba(0,0,0,.28);
}

/* ---------- APP CANVAS ---------- */
.stApp {
  background:
    radial-gradient(circle at 8% 0%, rgba(61,190,117,.13), transparent 28%),
    radial-gradient(circle at 92% 12%, rgba(56,207,173,.10), transparent 25%),
    radial-gradient(circle at 55% 100%, rgba(31,113,73,.10), transparent 34%),
    #07110d !important;
}

.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(to bottom, black, transparent 92%);
}

[data-testid="stAppViewContainer"], section[data-testid="stMain"] {
  background: transparent !important;
}

[data-testid="stMainBlockContainer"] {
  max-width: 1500px !important;
  padding-top: 2rem !important;
  padding-bottom: 4rem !important;
}

/* ---------- TYPOGRAPHY ---------- */
html, body, [class*="css"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

h1, h2, h3 {
  color: var(--ca-text) !important;
  letter-spacing: -.025em !important;
}

p, label, .stMarkdown, .stCaption {
  color: var(--ca-muted);
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
  width: 300px !important;
  background:
    linear-gradient(180deg, rgba(8,23,16,.985), rgba(5,14,10,.99)) !important;
  border-right: 1px solid var(--ca-border) !important;
  box-shadow: 18px 0 60px rgba(0,0,0,.20);
}

section[data-testid="stSidebar"] > div {
  padding: 1.1rem .85rem 1.4rem !important;
}

section[data-testid="stSidebar"] hr {
  margin: 14px 4px !important;
  border-color: rgba(255,255,255,.07) !important;
}

/* ---------- SIDEBAR RADIO NAV ---------- */
section[data-testid="stSidebar"] [role="radiogroup"] {
  gap: 7px !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] label {
  min-height: 46px !important;
  padding: 10px 12px !important;
  border: 1px solid transparent !important;
  border-radius: 14px !important;
  background: transparent !important;
  transition: all .18s ease !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(105,228,154,.075) !important;
  border-color: rgba(105,228,154,.13) !important;
  transform: translateX(2px);
}

section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(90deg, rgba(71,198,117,.17), rgba(71,198,117,.055)) !important;
  border-color: var(--ca-border-strong) !important;
  box-shadow: inset 3px 0 0 var(--ca-green), 0 8px 22px rgba(24,120,70,.12) !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] label p {
  color: #eaf9ef !important;
  font-weight: 700 !important;
  font-size: .82rem !important;
}

/* ---------- BUTTONS ---------- */
.stButton > button,
.stDownloadButton > button,
button[kind="secondary"],
button[kind="primary"] {
  min-height: 42px !important;
  border-radius: 13px !important;
  border: 1px solid rgba(156,239,185,.16) !important;
  background: linear-gradient(135deg, rgba(61,170,104,.18), rgba(255,255,255,.045)) !important;
  color: #edfff3 !important;
  font-weight: 750 !important;
  box-shadow: 0 9px 26px rgba(0,0,0,.16), inset 0 1px 0 rgba(255,255,255,.07) !important;
  transition: transform .18s ease, border-color .18s ease, background .18s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
  transform: translateY(-2px) !important;
  border-color: rgba(105,228,154,.42) !important;
  background: linear-gradient(135deg, rgba(61,190,117,.28), rgba(255,255,255,.07)) !important;
}

.stButton > button:focus, .stDownloadButton > button:focus {
  box-shadow: 0 0 0 2px rgba(105,228,154,.16), 0 10px 28px rgba(0,0,0,.18) !important;
}

/* ---------- INPUTS ---------- */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
  background: rgba(255,255,255,.045) !important;
  border: 1px solid rgba(193,245,211,.12) !important;
  border-radius: 12px !important;
  color: #f2fff6 !important;
}

input, textarea {
  color: #f2fff6 !important;
}

input:focus, textarea:focus {
  border-color: rgba(105,228,154,.55) !important;
  box-shadow: 0 0 0 1px rgba(105,228,154,.18) !important;
}

/* ---------- SELECT / FILE UPLOADER ---------- */
div[data-testid="stFileUploader"],
div[data-testid="stExpander"],
div[data-testid="stAlert"],
div[data-testid="stMetric"] {
  border: 1px solid var(--ca-border) !important;
  border-radius: 18px !important;
  background: linear-gradient(145deg, rgba(255,255,255,.065), rgba(255,255,255,.018)) !important;
  box-shadow: var(--ca-shadow), inset 0 1px 0 rgba(255,255,255,.055) !important;
  backdrop-filter: blur(18px) !important;
}

div[data-testid="stFileUploader"] {
  padding: 7px !important;
}

/* ---------- METRICS ---------- */
div[data-testid="stMetric"] {
  padding: 18px 18px 15px !important;
  position: relative;
  overflow: hidden;
}

div[data-testid="stMetric"]::after {
  content: "";
  position: absolute;
  width: 100px;
  height: 100px;
  right: -45px;
  top: -45px;
  border-radius: 50%;
  background: rgba(105,228,154,.08);
}

div[data-testid="stMetricLabel"] p {
  color: rgba(224,246,232,.55) !important;
  font-size: .72rem !important;
  font-weight: 800 !important;
  text-transform: uppercase;
  letter-spacing: .08em;
}

div[data-testid="stMetricValue"] {
  color: #f4fff8 !important;
  font-weight: 900 !important;
}

/* ---------- TABS ---------- */
div[data-baseweb="tab-list"] {
  gap: 6px !important;
  padding: 5px !important;
  border: 1px solid rgba(255,255,255,.07) !important;
  border-radius: 15px !important;
  background: rgba(255,255,255,.025) !important;
}

button[data-baseweb="tab"] {
  border-radius: 11px !important;
  color: rgba(225,246,232,.58) !important;
  font-weight: 750 !important;
  border-bottom: 0 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
  color: #effff4 !important;
  background: rgba(105,228,154,.13) !important;
}

/* ---------- DATAFRAMES ---------- */
div[data-testid="stDataFrame"] {
  border: 1px solid rgba(190,245,209,.10) !important;
  border-radius: 16px !important;
  overflow: hidden !important;
  box-shadow: 0 18px 45px rgba(0,0,0,.17) !important;
}

/* ---------- EXPANDERS ---------- */
div[data-testid="stExpander"] summary {
  font-weight: 750 !important;
}

/* ---------- STATUS / ALERTS ---------- */
div[data-testid="stAlert"] {
  color: #eafff0 !important;
}

/* ---------- DIVIDERS ---------- */
hr {
  border-color: rgba(255,255,255,.075) !important;
}

/* ---------- IMAGES ---------- */
div[data-testid="stImage"] img {
  border-radius: 18px !important;
  border: 1px solid rgba(184,255,211,.12) !important;
  box-shadow: 0 22px 55px rgba(0,0,0,.25) !important;
}

/* ---------- ROLE / HOME CARDS ---------- */
.role-hero, .home-hero {
  border: 1px solid rgba(184,255,211,.15) !important;
  background:
    radial-gradient(circle at 85% 20%, rgba(92,221,145,.13), transparent 25%),
    linear-gradient(135deg, rgba(22,53,38,.84), rgba(8,23,16,.72)) !important;
  border-radius: 28px !important;
  box-shadow: 0 30px 90px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.08) !important;
  backdrop-filter: blur(22px) !important;
}

.role-module, .workflow-card, .role-stat {
  border-color: rgba(184,255,211,.12) !important;
  background: linear-gradient(145deg, rgba(255,255,255,.065), rgba(255,255,255,.018)) !important;
  box-shadow: 0 20px 55px rgba(0,0,0,.18), inset 0 1px 0 rgba(255,255,255,.055) !important;
}

.role-module:hover, .workflow-card:hover {
  border-color: rgba(105,228,154,.34) !important;
  box-shadow: 0 25px 65px rgba(25,130,75,.13), inset 0 1px 0 rgba(255,255,255,.07) !important;
}

.role-title, .home-title {
  text-shadow: 0 10px 35px rgba(0,0,0,.35);
}

/* ---------- TABLE / JSON / CODE ---------- */
pre, code {
  border-radius: 12px !important;
}

/* ---------- MOBILE ---------- */
@media (max-width: 900px) {
  section[data-testid="stSidebar"] { width: 260px !important; }
  [data-testid="stMainBlockContainer"] { padding: 1rem !important; }
  .home-title, .role-title { font-size: 2rem !important; }
}
</style>
""", unsafe_allow_html=True)

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



            # The first Admin can be created from public registration.
            # Once an Admin exists, the Admin option is automatically hidden.
            admin_exists = _has_admin_account()
            registration_roles = ["farmer", "agent", "dealer"]
            if not admin_exists:
                registration_roles.append("admin")

            role_labels = {
                "farmer": "🌱 Farmer",
                "agent": "🤝 Agent",
                "dealer": "🏪 Dealer",
                "admin": "👑 Admin (Initial Setup)",
            }

            role = st.selectbox(
                "Select Role",
                registration_roles,
                format_func=lambda value: role_labels[value],
                key="reg_role",
            )

            if not admin_exists:
                st.info(
                    "🔐 No Admin account exists yet. Create the first Admin now. "
                    "After it is created, Admin will disappear from public registration."
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



                    success, message = _register_account_by_role(
                        new_username,
                        new_password,
                        new_email,
                        role,
                    )



                    if success:



                        st.success(message)



                        logger.log_user_action(

                            new_username,

                            "register",

                            f"role={role}",

                        )



                        if role == "admin":
                            st.success("👑 Initial Admin account created. You can now log in to access the Admin Control Center.")
                        else:
                            st.info("You can now login with your credentials")



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




if "admin_market_rates" not in st.session_state:
    st.session_state["admin_market_rates"] = {k: float(v) for k, v in DEFAULT_MARKET_RATES.items()}

def get_logged_in_role():
    """Return the authenticated user's role safely."""
    current_user = st.session_state.get("current_user") or {}
    role = str(current_user.get("role", "farmer")).strip().lower()
    return role if role in {"farmer", "agent", "dealer", "admin"} else "farmer"


def _role_dashboard_config(role):
    configs = {
        "farmer": {
            "icon": "🌱",
            "name": "Farmer",
            "title": "Your harvest. Your intelligence.",
            "copy": "Analyze your coconut harvest, understand maturity, and track transparent value from every image.",
            "chips": ["🥥 Harvest Analysis", "📦 My Batches", "💰 Valuation", "📈 My Insights"],
            "modules": [
                ("🥥", "Coconut Analysis", "Detect individual coconuts, classify maturity and estimate the value of your uploaded harvest."),
                ("📦", "My Batches", "Keep your analyzed harvest activity organized and easy to review."),
                ("💰", "My Valuation", "See transparent coconut-wise and bunch-wise estimates using configured benchmark rates."),
                ("📊", "My Analytics", "Understand your analysis count, coconut count and estimated value over time."),
            ],
            "callout": "Built for field use: scan a bunch, understand what was detected, then move directly to valuation."
        },
        "agent": {
            "icon": "🤝",
            "name": "Agent",
            "title": "Manage the harvest flow.",
            "copy": "A field-ready workspace for handling farmer collections, batch analysis and operational intelligence.",
            "chips": ["👨‍🌾 Farmers", "📦 Collections", "📊 Batch Intelligence", "⚡ AI Analysis"],
            "modules": [
                ("👨‍🌾", "Farmer Network", "Organize the farmers you work with and keep collection activity structured."),
                ("📦", "Collection Batches", "Track incoming coconut batches and connect field collections with AI analysis."),
                ("📊", "Batch Analytics", "Review detected composition, maturity distribution and estimated batch value."),
                ("🥥", "Field AI", "Run the same coconut detection and valuation engine used by the core application."),
            ],
            "callout": "Agent mode keeps the same AI engine but changes the workspace around multi-farmer collection operations."
        },
        "dealer": {
            "icon": "🏪",
            "name": "Dealer",
            "title": "Turn coconut data into trade intelligence.",
            "copy": "Analyze incoming stock, understand maturity mix and organize valuation for trading decisions.",
            "chips": ["📦 Inventory", "💰 Transactions", "📊 Business Analytics", "🥥 Stock Analysis"],
            "modules": [
                ("📦", "Inventory", "Organize incoming coconut stock and keep maturity information connected to each batch."),
                ("💰", "Transactions", "Structure purchase and trading records around transparent coconut-wise valuation."),
                ("📊", "Business Analytics", "Review analysis volume, detected coconuts and estimated value from your workspace."),
                ("🥥", "Stock AI", "Use AI detection to understand the maturity composition of incoming coconut batches."),
            ],
            "callout": "Dealer mode focuses the same detection engine on stock, valuation and trading workflows."
        },
        "admin": {
            "icon": "👑",
            "name": "Admin",
            "title": "Control the coconut intelligence platform.",
            "copy": "Manage users, review system activity and maintain the benchmark settings used across the application.",
            "chips": ["👥 Users", "💰 Market Rates", "📊 System Analytics", "⚙️ Controls"],
            "modules": [
                ("👥", "User Management", "Review registered farmers, agents and dealers from one control workspace."),
                ("💰", "Market Rates", "Review the benchmark rates used by the valuation engine."),
                ("📊", "System Analytics", "Review analysis activity and system-level statistics."),
                ("⚙️", "AI Operations", "Monitor the available AI engines and application configuration."),
            ],
            "callout": "Admin controls are separated from operational farmer, agent and dealer workspaces."
        },
    }
    return configs.get(role, configs["farmer"])


def _open_workspace(workspace):
    """Queue workspace navigation safely for the next Streamlit rerun.

    The sidebar radio widget owns ``role_workspace_selector`` once it is
    instantiated, so button callbacks must not write to that widget key
    during the same script run.
    """
    st.session_state["pending_workspace"] = workspace
    st.session_state["active_workspace"] = workspace
    st.rerun()


def render_role_dashboard(role):
    """Render the creative role-specific dashboard with live role actions."""
    current_user = st.session_state.get("current_user") or {}
    username = current_user.get("username", "User")
    config_role = _role_dashboard_config(role)

    stats = {}
    user_id = current_user.get("user_id")
    if user_id is not None:
        try:
            stats = db.get_user_statistics(user_id) or {}
        except Exception:
            stats = {}

    st.markdown(
        f"""
        <div class="role-hero">
          <div class="role-kicker">{config_role["icon"]} {config_role["name"].upper()} INTELLIGENCE WORKSPACE</div>
          <div class="role-title">{config_role["title"]}</div>
          <div class="role-copy">
            Welcome back, <strong>{username}</strong>. {config_role["copy"]}
          </div>
          <div class="role-chip-row">
            {''.join(f'<span class="role-chip">{chip}</span>' for chip in config_role["chips"])}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="role-section-title">LIVE WORKSPACE SNAPSHOT</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    stat_items = [
        ("ANALYSES", stats.get("total_analyses", 0), "Recorded AI analyses"),
        ("COCONUTS", stats.get("total_coconuts_analyzed", 0), "Detected in your analyses"),
        ("AVG VALUE", f'₹{stats.get("avg_batch_value", 0):,.0f}', "Average estimated batch"),
        ("TOTAL VALUE", f'₹{stats.get("total_value", 0):,.0f}', "Recorded estimated value"),
    ]
    for col, (label, value, note) in zip((c1, c2, c3, c4), stat_items):
        with col:
            st.markdown(
                f"""
                <div class="role-stat">
                  <div class="role-stat-label">{label}</div>
                  <div class="role-stat-value">{value}</div>
                  <div class="role-stat-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Farmer dashboard gets real navigation actions instead of decorative cards.
    if role == "farmer":
        st.markdown('<div class="role-section-title">QUICK ACTIONS</div>', unsafe_allow_html=True)

        q1, q2, q3, q4 = st.columns(4)

        with q1:
            if st.button("🥥 Analyze Harvest", use_container_width=True, type="primary"):
                _open_workspace("🥥 Coconut Analysis")

        with q2:
            if st.button("📦 My Batches", use_container_width=True):
                _open_workspace("📦 My Batches")

        with q3:
            if st.button("💰 My Valuation", use_container_width=True):
                _open_workspace("💰 My Valuation")

        with q4:
            if st.button("📊 My Analytics", use_container_width=True):
                _open_workspace("📊 My Analytics")

        st.markdown('<div class="role-section-title">RECENT HARVEST ACTIVITY</div>', unsafe_allow_html=True)

        recent = []
        if user_id is not None:
            try:
                recent = db.get_user_results(user_id) or []
            except Exception:
                recent = []

        if recent:
            # Show only a compact recent view on the dashboard.
            st.dataframe(recent[:5], use_container_width=True, hide_index=True)
        else:
            st.info("🌱 No harvest analysis recorded yet. Start by analyzing your first coconut batch.")

        st.markdown(
            f'<div class="role-callout">💡 <strong>Farmer mode:</strong> '
            f'{config_role["callout"]}</div>',
            unsafe_allow_html=True,
        )
        return

    # Agent dashboard is driven by permanent Farmer batches, not the
    # agent's own analysis history.
    if role == "agent":
        summary = _phase6_agent_batch_summary(_phase6_resolve_user_id(current_user))
        batch_rows = summary["rows"]

        st.markdown('<div class="role-section-title">LIVE COLLECTION SNAPSHOT</div>', unsafe_allow_html=True)
        a1, a2, a3, a4 = st.columns(4)
        agent_stats = [
            ("BATCHES", len(batch_rows), "Permanent farmer batches"),
            ("AVAILABLE", len(summary["available"]), "Ready for collection"),
            ("COCONUTS", f'{summary["available_coconuts"]:,}', "Available to agent"),
            ("VALUE", f'₹{summary["available_value"]:,.0f}', "Estimated available value"),
        ]
        for col, (label, value, note) in zip((a1, a2, a3, a4), agent_stats):
            with col:
                st.markdown(
                    f"""
                    <div class="role-stat">
                      <div class="role-stat-label">{label}</div>
                      <div class="role-stat-value">{value}</div>
                      <div class="role-stat-note">{note}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="role-section-title">QUICK ACTIONS</div>', unsafe_allow_html=True)
        q1,q2,q3,q4=st.columns(4)
        with q1:
            if st.button("👨‍🌾 Farmer Network",use_container_width=True,type="primary",key="agent_quick_farmers"):
                _open_workspace("👨‍🌾 Farmers")
        with q2:
            if st.button("📦 Collection Center",use_container_width=True,key="agent_quick_collections"):
                _open_workspace("📦 Collection Batches")
        with q3:
            if st.button("🥥 Field AI",use_container_width=True,key="agent_quick_ai"):
                _open_workspace("🥥 Coconut Analysis")
        with q4:
            if st.button("📊 Batch Analytics",use_container_width=True,key="agent_quick_analytics"):
                _open_workspace("📊 Batch Analytics")

        if batch_rows:
            st.markdown('<div class="role-section-title">LATEST FARMER BATCHES</div>', unsafe_allow_html=True)
            latest = []
            for row in batch_rows[:6]:
                latest.append({
                    "Batch": row.get("batch_code") or "—",
                    "Farmer": row.get("farmer_name") or "Farmer",
                    "Coconuts": int(row.get("total_coconuts", 0) or 0),
                    "Grade": row.get("grade") or "—",
                    "Value": f'₹{float(row.get("estimated_value", 0) or 0):,.2f}',
                    "Status": row.get("status") or "Available",
                    "Created": row.get("created_at") or "—",
                })
            st.dataframe(latest, use_container_width=True, hide_index=True)
        else:
            st.info("🌱 No permanent farmer batches yet. Create one from a Farmer account to see it here.")

        st.markdown(f'<div class="role-callout">💡 <strong>Agent mode:</strong> {config_role["callout"]} New permanent farmer batches appear here automatically.</div>',unsafe_allow_html=True)
        return

    # Dealer dashboard keeps its operational UI. Admin gets real control shortcuts.
    if role == "admin":
        st.markdown('<div class="role-section-title">ADMIN QUICK ACTIONS</div>', unsafe_allow_html=True)
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            if st.button("👥 Manage Users", use_container_width=True, type="primary", key="admin_quick_users"):
                _open_workspace("👥 Users")
        with q2:
            if st.button("💰 Market Rates", use_container_width=True, key="admin_quick_rates"):
                _open_workspace("💰 Market Rates")
        with q3:
            if st.button("📊 System Analytics", use_container_width=True, key="admin_quick_analytics"):
                _open_workspace("📊 System Analytics")
        with q4:
            if st.button("⚙️ AI Operations", use_container_width=True, key="admin_quick_ai"):
                _open_workspace("⚙️ AI Operations")

        st.markdown('<div class="role-section-title">PLATFORM SNAPSHOT</div>', unsafe_allow_html=True)
        try:
            platform_rows = []
            total_users = total_analyses = total_coconuts = 0
            total_value = 0.0
            for role_name in ("farmer", "agent", "dealer", "admin"):
                users = _get_users_by_role_compat(role_name)
                total_users += len(users)
                role_analysis = 0
                for user in users:
                    uid = _safe_result_value(user, "user_id", "id", default=None)
                    if uid is None:
                        continue
                    try: results = db.get_user_results(uid) or []
                    except Exception: results = []
                    role_analysis += len(results); total_analyses += len(results)
                    for row in results:
                        total_coconuts += int(_safe_result_value(row, "total_coconuts", "total_coconuts_analyzed", default=0) or 0)
                        total_value += float(_safe_result_value(row, "total_value", "batch_value", "estimated_value", default=0) or 0)
                platform_rows.append({"Role": role_name.title(), "Users": len(users), "Analyses": role_analysis})
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Platform Users", total_users); p2.metric("AI Analyses", total_analyses)
            p3.metric("Detected Coconuts", total_coconuts); p4.metric("Estimated Value", f"₹{total_value:,.0f}")
            if platform_rows:
                import pandas as pd
                st.dataframe(pd.DataFrame(platform_rows), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.info(f"Platform statistics will appear when analysis records are available. ({exc})")
        st.markdown(f'<div class="role-callout">💡 <strong>Admin mode:</strong> {config_role["callout"]}</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="role-section-title">YOUR OPERATIONAL MODULES</div>', unsafe_allow_html=True)
    module_cols = st.columns(2)
    for index, (icon, title, description) in enumerate(config_role["modules"]):
        with module_cols[index % 2]:
            st.markdown(f"""<div class="role-module"><div class="role-module-icon">{icon}</div><div class="role-module-title">{title}</div><div class="role-module-text">{description}</div></div>""", unsafe_allow_html=True)
        if index % 2 == 1 and index != len(config_role["modules"]) - 1:
            st.write("")
    st.markdown(f'<div class="role-callout">💡 <strong>{config_role["name"]} mode:</strong> {config_role["callout"]}</div>', unsafe_allow_html=True)



def _get_users_by_role_compat(role_name=None):
    for method_name in ("get_users_by_role", "get_all_users", "get_users"):
        method = getattr(db, method_name, None)
        if not callable(method): continue
        try:
            users = method(role_name) if method_name == "get_users_by_role" else method()
            users = users or []
            if role_name and method_name != "get_users_by_role":
                users = [u for u in users if str(_safe_result_value(u, "role", "user_role", default="")).lower() == role_name]
            return users
        except Exception:
            continue
    return []

def admin_users_page():
    st.markdown("""<div class="role-hero"><div class="role-kicker">👑 ADMIN CONTROL CENTER</div><div class="role-title">User management</div><div class="role-copy">Review platform accounts and create farmer, agent or dealer accounts.</div></div>""", unsafe_allow_html=True)
    users=[]
    for role_name in ("farmer","agent","dealer","admin"): users.extend(_get_users_by_role_compat(role_name))
    rows=[]
    for u in users:
        rows.append({"User ID":_safe_result_value(u,"user_id","id",default="—"),"Username":_safe_result_value(u,"username","name","full_name",default="—"),"Email":_safe_result_value(u,"email",default="—"),"Role":str(_safe_result_value(u,"role","user_role",default="—")).title(),"Status":_safe_result_value(u,"status","is_active",default="Active")})
    if rows: st.dataframe(rows,use_container_width=True,hide_index=True)
    else: st.info("No users are available from the current database API.")
    st.markdown('<div class="role-section-title">CREATE OPERATIONAL ACCOUNT</div>',unsafe_allow_html=True)
    with st.form("admin_create_user_form",clear_on_submit=False):
        c1,c2=st.columns(2)
        with c1: new_username=st.text_input("Username",key="admin_new_username"); new_email=st.text_input("Email",key="admin_new_email")
        with c2: new_role=st.selectbox("Role",["farmer","agent","dealer"],key="admin_new_role"); new_password=st.text_input("Temporary Password",type="password",key="admin_new_password")
        create=st.form_submit_button("➕ Create Account",use_container_width=True,type="primary")
    if create:
        if not new_username.strip() or not new_email.strip() or not new_password: st.error("Please fill username, email and password.")
        else:
            try:
                success,message=auth_manager.register_user(new_username.strip(),new_password,new_email.strip(),new_role)
                if success: st.success(message); st.rerun()
                else: st.error(message)
            except Exception as exc: st.error(f"Unable to create account: {exc}")

def _get_admin_market_rates():
    stored=st.session_state.get("admin_market_rates")
    if isinstance(stored,dict):
        try: return {k:float(stored.get(k,DEFAULT_MARKET_RATES[k])) for k in ("dry","green","tender")}
        except Exception: pass
    return {k:float(v) for k,v in DEFAULT_MARKET_RATES.items()}

def market_price_view_page(role):
    """Read-only market price visibility for farmer, agent and dealer users.
    Rates are controlled only by the admin workspace.
    """
    if role not in {"farmer", "agent", "dealer"}:
        st.error("Market price visibility is restricted to farmer, agent and dealer accounts.")
        return

    rates = _get_admin_market_rates()
    values = [float(rates.get(k, 0.0)) for k in ("dry", "green", "tender")]
    low = min(values) if values else 0.0
    high = max(values) if values else 0.0

    st.markdown(
        f"""<div class=\"role-hero\">
        <div class=\"role-kicker\">💰 MARKET PRICE VIEW</div>
        <div class=\"role-title\">Current coconut price range</div>
        <div class=\"role-copy\">Read-only indicative benchmark rates for {role.title()} users. Only an administrator can change these values.</div>
        </div>""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Lowest rate", f"₹{low:,.0f} / coconut")
    c2.metric("Highest rate", f"₹{high:,.0f} / coconut")
    c3.metric("Overall range", f"₹{low:,.0f} – ₹{high:,.0f}")

    rows = [
        {"Coconut Type": "Dry Mature", "Indicative Rate": f"₹{rates['dry']:,.2f} / coconut"},
        {"Coconut Type": "Fresh Green", "Indicative Rate": f"₹{rates['green']:,.2f} / coconut"},
        {"Coconut Type": "Tender Water", "Indicative Rate": f"₹{rates['tender']:,.2f} / coconut"},
    ]
    st.markdown('<div class="role-section-title">INDICATIVE PRICE BY TYPE</div>', unsafe_allow_html=True)
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.info("ℹ️ These are configurable benchmark estimates used by the valuation engine, not live verified market quotations.")
    st.caption("Price control: Admin only • Visibility: Farmer / Agent / Dealer")


def admin_market_rates_page():
    st.markdown("""<div class="role-hero"><div class="role-kicker">💰 ADMIN CONTROL CENTER</div><div class="role-title">Market rate control</div><div class="role-copy">Set benchmark values used for transparent coconut valuation. These are configurable estimates, not verified live market prices.</div></div>""",unsafe_allow_html=True)
    rates=_get_admin_market_rates(); c1,c2,c3=st.columns(3)
    with c1: dry=st.number_input("Dry Mature (₹/pc)",min_value=0.0,value=rates["dry"],step=1.0,key="admin_rate_dry")
    with c2: green=st.number_input("Fresh Green (₹/pc)",min_value=0.0,value=rates["green"],step=1.0,key="admin_rate_green")
    with c3: tender=st.number_input("Tender Water (₹/pc)",min_value=0.0,value=rates["tender"],step=1.0,key="admin_rate_tender")
    proposed={"dry":float(dry),"green":float(green),"tender":float(tender)}; valid,msg=validate_market_rates(proposed)
    if not valid: st.error(msg)
    else: st.success("✓ Rate set is valid")
    if st.button("💾 Save Benchmark Rates",use_container_width=True,type="primary",key="admin_save_rates"):
        if valid: st.session_state["admin_market_rates"]=proposed; st.success("Market rates saved for this session.")
        else: st.error(msg)
    st.caption("🔐 Admin only: these benchmark rates control valuation across the current Streamlit session. Farmer, Agent and Dealer accounts can view the current range but cannot edit it.")

def _phase9_supply_chain_snapshot():
    """Return real supply-chain metrics from permanent SQLite records."""
    snapshot = {
        "farmers": 0, "agents": 0, "dealers": 0, "admins": 0,
        "batches": 0, "available_batches": 0, "collected_batches": 0,
        "dealer_inventory_batches": 0, "depleted_batches": 0,
        "total_coconuts": 0, "available_coconuts": 0, "collected_coconuts": 0,
        "dealer_stock_coconuts": 0, "estimated_value": 0.0,
        "dealer_stock_value": 0.0, "purchases": 0.0, "sales": 0.0,
        "transactions": 0,
    }
    for role_name, key in (("farmer", "farmers"), ("agent", "agents"), ("dealer", "dealers"), ("admin", "admins")):
        snapshot[key] = len(_get_users_by_role_compat(role_name))

    try:
        _phase6_init_batch_table()
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, farmer_id, agent_id, dealer_id, total_coconuts,
                       available_quantity, sold_quantity, estimated_value, status,
                       dry_count, green_count, tender_count, grade, created_at,
                       collected_at, received_at
                FROM coconut_batches
                ORDER BY id DESC
            """).fetchall()
            for r in rows:
                d = dict(r)
                status = str(d.get("status") or "").strip().lower()
                total = int(d.get("total_coconuts") or 0)
                available = d.get("available_quantity")
                available = int(available) if available is not None else (total if status in {"available", "collected"} else 0)
                estimated = float(d.get("estimated_value") or 0)
                snapshot["batches"] += 1
                snapshot["total_coconuts"] += total
                snapshot["estimated_value"] += estimated
                if status == "available":
                    snapshot["available_batches"] += 1
                    snapshot["available_coconuts"] += available
                elif status == "collected":
                    snapshot["collected_batches"] += 1
                    snapshot["collected_coconuts"] += total
                elif status in {"in dealer inventory", "depleted", "sold"}:
                    snapshot["dealer_inventory_batches"] += 1
                    snapshot["dealer_stock_coconuts"] += max(0, available)
                    if status in {"depleted", "sold"}:
                        snapshot["depleted_batches"] += 1
                    if total > 0:
                        snapshot["dealer_stock_value"] += estimated * (max(0, available) / total)

            tx_rows = conn.execute("""
                SELECT transaction_type, amount
                FROM transactions
            """).fetchall()
            snapshot["transactions"] = len(tx_rows)
            for t in tx_rows:
                amount = float(t[1] or 0)
                tx_type = str(t[0] or "").strip().lower()
                if tx_type == "purchase":
                    snapshot["purchases"] += amount
                elif tx_type == "sale":
                    snapshot["sales"] += amount
    except Exception as exc:
        logger.error(f"Phase 9 supply-chain snapshot failed: {exc}")
    return snapshot


def admin_system_analytics_page():
    """Admin control center with real end-to-end supply-chain analytics."""
    st.markdown("""
        <div class="role-hero">
          <div class="role-kicker">📊 PHASE 9 · ADMIN CONTROL CENTER</div>
          <div class="role-title">Supply-chain intelligence</div>
          <div class="role-copy">A live view of permanent Farmer batches, Agent collections, Dealer inventory and recorded transactions.</div>
        </div>
    """, unsafe_allow_html=True)

    snapshot = _phase9_supply_chain_snapshot()
    st.markdown('<div class="role-section-title">LIVE SUPPLY CHAIN</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("👥 Farmers", snapshot["farmers"])
    c2.metric("🤝 Agents", snapshot["agents"])
    c3.metric("🏪 Dealers", snapshot["dealers"])
    c4.metric("📦 Permanent Batches", snapshot["batches"])

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🟢 Available", snapshot["available_batches"])
    c2.metric("🤝 Collected", snapshot["collected_batches"])
    c3.metric("🏪 Dealer Lots", snapshot["dealer_inventory_batches"])
    c4.metric("🥥 Total Coconuts", f'{snapshot["total_coconuts"]:,}')

    st.markdown('<div class="role-section-title">FLOW STATUS</div>', unsafe_allow_html=True)
    flow = [
        {"Stage":"🌱 Farmer Batches", "Batches":snapshot["batches"], "Coconuts":snapshot["total_coconuts"], "Value":f'₹{snapshot["estimated_value"]:,.2f}'},
        {"Stage":"🟢 Available for Collection", "Batches":snapshot["available_batches"], "Coconuts":snapshot["available_coconuts"], "Value":"—"},
        {"Stage":"🤝 Agent Collected", "Batches":snapshot["collected_batches"], "Coconuts":snapshot["collected_coconuts"], "Value":"—"},
        {"Stage":"🏪 Dealer Inventory", "Batches":snapshot["dealer_inventory_batches"], "Coconuts":snapshot["dealer_stock_coconuts"], "Value":f'₹{snapshot["dealer_stock_value"]:,.2f}'},
    ]
    st.dataframe(flow, use_container_width=True, hide_index=True)

    st.markdown('<div class="role-section-title">TRADE ACTIVITY</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🛒 Purchases", f'₹{snapshot["purchases"]:,.2f}')
    c2.metric("💵 Sales", f'₹{snapshot["sales"]:,.2f}')
    c3.metric("📈 Sales − Purchases", f'₹{snapshot["sales"]-snapshot["purchases"]:,.2f}')
    c4.metric("🧾 Transactions", snapshot["transactions"])

    st.markdown('<div class="role-section-title">MATURITY COMPOSITION</div>', unsafe_allow_html=True)
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            row = conn.execute("""
                SELECT COALESCE(SUM(dry_count),0), COALESCE(SUM(green_count),0), COALESCE(SUM(tender_count),0)
                FROM coconut_batches
            """).fetchone()
        composition = [
            {"Type":"Dry", "Coconuts":int(row[0] or 0)},
            {"Type":"Green", "Coconuts":int(row[1] or 0)},
            {"Type":"Tender", "Coconuts":int(row[2] or 0)},
        ]
        st.dataframe(composition, use_container_width=True, hide_index=True)
    except Exception as exc:
        st.info(f"Maturity composition will appear when batch records are available. ({exc})")

    st.markdown('<div class="role-section-title">SYSTEM NOTE</div>', unsafe_allow_html=True)
    st.info("ℹ️ These figures come from permanent SQLite batch and transaction records. Estimated values use the configured benchmark pricing; they are not verified live market prices.")

def _phase10_table_health(table_name, required_columns):
    """Check table existence and required columns without changing the database."""
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            ).fetchone() is not None
            if not exists:
                return {"table": table_name, "status": "MISSING", "missing": required_columns}
            cols = {row[1] for row in conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()}
            missing = [c for c in required_columns if c not in cols]
            return {"table": table_name, "status": "OK" if not missing else "MISSING COLUMNS", "missing": missing}
    except Exception as exc:
        return {"table": table_name, "status": f"ERROR: {exc}", "missing": required_columns}


def admin_system_health_page():
    """Phase 10 read-only final QA and data-integrity dashboard."""
    st.markdown("""
        <div class="role-hero">
          <div class="role-kicker">🛡️ PHASE 10 · FINAL QA</div>
          <div class="role-title">System health & data integrity</div>
          <div class="role-copy">Read-only checks for the database schema, supply-chain consistency and AI runtime before final demonstration.</div>
        </div>
    """, unsafe_allow_html=True)

    checks = [
        _phase10_table_health("users", ["id", "username", "role"]),
        _phase10_table_health("coconut_batches", ["id", "batch_code", "batch_name", "farmer_id", "agent_id", "dealer_id", "total_coconuts", "status"]),
        _phase10_table_health("transactions", ["id", "transaction_type", "amount"]),
    ]
    healthy = sum(1 for c in checks if c["status"] == "OK")
    c1, c2, c3 = st.columns(3)
    c1.metric("🗄️ Tables Healthy", f"{healthy}/{len(checks)}")
    c2.metric("🤖 YOLO", "READY" if globals().get("yolo_model") is not None else "NOT LOADED")
    c3.metric("⚡ OpenVINO", "READY" if globals().get("openvino_model") is not None else "NOT LOADED")

    st.markdown('<div class="role-section-title">DATABASE SCHEMA</div>', unsafe_allow_html=True)
    schema_rows = []
    for item in checks:
        schema_rows.append({
            "Table": item["table"],
            "Status": item["status"],
            "Missing Columns": ", ".join(item["missing"]) if item["missing"] else "—",
        })
    st.dataframe(schema_rows, use_container_width=True, hide_index=True)

    st.markdown('<div class="role-section-title">SUPPLY-CHAIN CONSISTENCY</div>', unsafe_allow_html=True)
    issues = []
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT id, farmer_id, agent_id, dealer_id, total_coconuts,
                       available_quantity, sold_quantity, status
                FROM coconut_batches
            """).fetchall()
            for row in rows:
                r = dict(row)
                total = int(r.get("total_coconuts") or 0)
                available = r.get("available_quantity")
                sold = r.get("sold_quantity")
                if available is not None and int(available) < 0:
                    issues.append(f"Batch {r.get('id')}: negative available quantity")
                if sold is not None and int(sold) < 0:
                    issues.append(f"Batch {r.get('id')}: negative sold quantity")
                if available is not None and sold is not None and int(available) + int(sold) > total:
                    issues.append(f"Batch {r.get('id')}: available + sold exceeds total")
                status = str(r.get("status") or "").strip().lower()
                if status == "collected" and not r.get("agent_id"):
                    issues.append(f"Batch {r.get('id')}: collected without agent_id")
                if status in {"in dealer inventory", "depleted", "sold"} and not r.get("dealer_id"):
                    issues.append(f"Batch {r.get('id')}: dealer-stage status without dealer_id")
    except Exception as exc:
        issues.append(f"Integrity check error: {exc}")

    if issues:
        st.error(f"⚠️ {len(issues)} integrity issue(s) detected.")
        st.dataframe([{"Issue": x} for x in issues[:100]], use_container_width=True, hide_index=True)
    else:
        st.success("✅ No supply-chain quantity or ownership inconsistencies detected in the current database.")

    st.markdown('<div class="role-section-title">DEMO CHECKLIST</div>', unsafe_allow_html=True)
    checklist = [
        {"Step": "Farmer creates permanent batch", "Expected": "Batch status = Available"},
        {"Step": "Agent accepts batch", "Expected": "Agent assigned; status = Collected"},
        {"Step": "Dealer receives batch", "Expected": "Dealer assigned; inventory quantity initialized"},
        {"Step": "Dealer records sale", "Expected": "Available quantity decreases"},
        {"Step": "Admin opens System Analytics", "Expected": "Counts reflect permanent records"},
    ]
    st.dataframe(checklist, use_container_width=True, hide_index=True)
    st.caption("This page is read-only. It does not modify or repair your database automatically.")


def admin_ai_operations_page():
    st.markdown("""<div class="role-hero"><div class="role-kicker">⚙️ ADMIN CONTROL CENTER</div><div class="role-title">AI operations</div><div class="role-copy">Inspect the runtime availability of the detection engines and model assets. These are actual runtime checks.</div></div>""",unsafe_allow_html=True)
    yolo=globals().get("yolo_model"); ovino=globals().get("openvino_model")
    try: yolo_path=resolve_model_path()
    except Exception: yolo_path=None
    rows=[{"Engine":"YOLO","Runtime Status":"Loaded" if yolo is not None else "Not loaded","Model Path":str(yolo_path or "—")},{"Engine":"OpenVINO","Runtime Status":"Loaded" if ovino is not None else "Not loaded","Model Path":str(globals().get("OPENVINO_MODEL_PATH","—"))}]
    st.dataframe(rows,use_container_width=True,hide_index=True)
    c1,c2=st.columns(2); c1.metric("YOLO Available","YES" if yolo is not None else "NO"); c2.metric("OpenVINO Available","YES" if ovino is not None else "NO")
    st.markdown('<div class="role-section-title">CONFIGURATION</div>',unsafe_allow_html=True)
    st.write({"Default Confidence":getattr(config,"DEFAULT_CONFIDENCE_THRESHOLD","—"),"Database":str(getattr(config,"DB_PATH","—")),"Benchmark Rates":_get_admin_market_rates()})

def render_role_module(role, module):
    """Creative placeholder/summary screens for role-specific modules not yet backed by dedicated CRUD pages."""
    labels = {
        "👨‍🌾 Farmers": ("👨‍🌾 Farmer Network", "Connect field collections with the farmers you work with."),
        "📦 Collection Batches": ("📦 Collection Batches", "Organize collected batches before analysis and valuation."),
        "📊 Batch Analytics": ("📊 Batch Intelligence", "Review batch-level AI composition and valuation information."),
        "📦 Inventory": ("📦 Dealer Inventory", "Organize incoming coconut stock around detected maturity."),
        "💵 Sales": ("💵 Dealer Sales", "Sell available stock and update batch quantities permanently."),
        "💰 Transactions": ("💰 Trading & Transactions", "Structure trading records around transparent coconut valuation."),
        "📊 Business Analytics": ("📊 Business Intelligence", "Review your analysis and valuation activity."),
        "👥 Users": ("👥 User Management", "Review registered platform users by role."),
        "💰 Market Rates": ("💰 Market Rate Control", "Admin-only control for benchmark rates used by the valuation engine."),
        "📊 System Analytics": ("📊 System Analytics", "Review platform activity and your available system statistics."),
        "⚙️ AI Operations": ("⚙️ AI Operations", "Inspect the runtime status of YOLO, OpenVINO and application configuration."),
        "🛡️ System Health": ("🛡️ System Health", "Run read-only schema, quantity and supply-chain consistency checks."),
    }
    title, copy = labels.get(module, (module, "Workspace module"))
    st.markdown(
        f"""
        <div class="role-hero">
          <div class="role-kicker">{_role_dashboard_config(role)["icon"]} ROLE MODULE</div>
          <div class="role-title">{title}</div>
          <div class="role-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if module == "👥 Users" and role == "admin":
        admin_users_page(); return
    if module == "💰 Market Rates" and role == "admin":
        admin_market_rates_page(); return
    if module == "📊 System Analytics" and role == "admin":
        admin_system_analytics_page(); return
    if module == "⚙️ AI Operations" and role == "admin":
        admin_ai_operations_page(); return
    if module == "🛡️ System Health" and role == "admin":
        admin_system_health_page(); return
    if module == "📊 Batch Analytics" and role == "agent":
        agent_batch_analytics_page(); return
    if module == "📊 Business Analytics":
        analytics_page(); return

    st.markdown(
        """
        <div class="role-module" style="margin-top:18px;">
          <div class="role-module-icon">🚧</div>
          <div class="role-module-title">Operational module</div>
          <div class="role-module-text">
            The creative workspace is ready here. The next implementation phase can connect
            this screen to the dedicated farmer, batch, inventory or transaction database tables
            without changing the existing AI detection pipeline.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def app_page():
    """Main Coconut Grading AI application with creative role-based workspaces."""

    _sync_performance_models()

    current_user = st.session_state.get("current_user") or {}
    role = get_logged_in_role()
    role_cfg = _role_dashboard_config(role)

    workspace_options = {
        "farmer": [
            "🏠 Dashboard",
            "🥥 Coconut Analysis",
            "📦 My Batches",
            "💰 My Valuation",
            "💰 Market Prices",
            "📋 My History",
            "📊 My Analytics",
            "⚡ AI Performance Lab",
        ],
        "agent": [
            "🏠 Dashboard",
            "🥥 Coconut Analysis",
            "👨‍🌾 Farmers",
            "📦 Collection Batches",
            "📊 Batch Analytics",
            "💰 Market Prices",
            "⚡ AI Performance Lab",
        ],
        "dealer": [
            "🏠 Dashboard",
            "🥥 Coconut Analysis",
            "📦 Inventory",
            "💵 Sales",
            "💰 Transactions",
            "💰 Market Prices",
            "📊 Business Analytics",
            "⚡ AI Performance Lab",
        ],
        "admin": [
            "🏠 Dashboard",
            "🥥 Coconut Analysis",
            "👥 Users",
            "💰 Market Rates",
            "📊 System Analytics",
            "⚙️ AI Operations",
            "🛡️ System Health",
            "⚡ AI Performance Lab",
        ],
    }

    # Apply navigation requested by a dashboard button BEFORE the sidebar
    # radio widget is instantiated. This avoids Streamlit's widget-state
    # mutation exception.
    pending_workspace = st.session_state.pop("pending_workspace", None)
    if pending_workspace in workspace_options.get(role, []):
        st.session_state["role_workspace_selector"] = pending_workspace

    with st.sidebar:
        st.markdown(
            """
            <div style="padding:10px 8px 18px;">
              <div style="font-size:.62rem;letter-spacing:.18em;color:#69e49a;font-weight:900;text-transform:uppercase;">🥥 COCONUT AI</div>
              <div style="font-size:1.42rem;font-weight:900;letter-spacing:-.04em;color:#f4fff8;margin-top:3px;">Studio</div>
              <div style="font-size:.70rem;color:rgba(226,245,234,.48);margin-top:4px;">AI harvest intelligence platform</div>
            </div>
            <div style="height:1px;background:linear-gradient(90deg,rgba(105,228,154,.28),transparent);margin:0 5px 15px;"></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                padding:14px 14px 12px;
                border:1px solid rgba(210,255,226,.10);
                border-radius:16px;
                background:rgba(255,255,255,.035);
                margin-bottom:14px;">
              <div style="font-size:.62rem;letter-spacing:.16em;color:#8fe2aa;font-weight:900;text-transform:uppercase;">
                CURRENT SESSION
              </div>
              <div style="font-size:1rem;font-weight:850;color:#f4fff7;margin-top:5px;">
                {role_cfg["icon"]} {current_user.get("username", "User")}
              </div>
              <div style="font-size:.72rem;color:rgba(230,250,237,.52);margin-top:4px;">
                {role_cfg["name"]} workspace
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        workspace = st.radio(
            "🚀 Workspace",
            workspace_options[role],
            key="role_workspace_selector",
        )
        st.session_state["active_workspace"] = workspace

        if st.button("🚪 Logout", use_container_width=True):
            logout_username = current_user.get("username", "unknown")
            auth_manager.logout(st.session_state.session_token)
            st.session_state.session_token = None
            st.session_state.current_user = None
            st.session_state.page = "login"
            st.session_state["active_workspace"] = "🏠 Dashboard"
            st.session_state.pop("pending_workspace", None)
            st.session_state.pop("role_workspace_selector", None)
            logger.log_user_action(logout_username, "logout")
            st.rerun()

    if workspace == "🏠 Dashboard":
        render_role_dashboard(role)
        return

    if workspace == "👨‍🌾 Farmers" and role == "agent":
        agent_farmers_page()
        return

    if workspace == "📦 Collection Batches" and role == "agent":
        agent_batches_page()
        return

    if workspace == "📦 Inventory" and role == "dealer":
        dealer_inventory_page()
        return

    if workspace == "💵 Sales" and role == "dealer":
        dealer_sales_page()
        return

    if workspace == "💰 Transactions" and role == "dealer":
        dealer_transactions_page()
        return

    if workspace == "💰 Market Prices" and role in {"farmer", "agent", "dealer"}:
        market_price_view_page(role)
        return

    if workspace == "📊 Business Analytics" and role == "dealer":
        dealer_business_analytics_page()
        return

    if workspace in {
        "📊 Batch Analytics", "👥 Users", "💰 Market Rates", "📊 System Analytics", "⚙️ AI Operations", "🛡️ System Health",
    }:
        render_role_module(role, workspace)
        return

    if workspace == "📦 My Batches":
        farmer_batches_page()
        return

    if workspace == "💰 My Valuation":
        farmer_valuation_page()
        return

    if workspace == "📋 My History":
        history_page()
        return

    if workspace == "📊 My Analytics":
        analytics_page()
        return

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
          <div class="home-kicker">Coconut AI Studio</div>
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
        # ANALYSIS SETTINGS
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
            index=0,
            key="analysis_ai_engine",
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

        # MARKET PRICES — READ ONLY

        # ----------------------------------------------------

        st.divider()
        st.markdown("### 💰 Market Price Range")

        active_rates = _get_admin_market_rates()
        rate_values = [float(active_rates.get(k, 0.0)) for k in ("dry", "green", "tender")]
        min_rate = min(rate_values) if rate_values else 0.0
        max_rate = max(rate_values) if rate_values else 0.0

        st.markdown(
            f"<div style=\"padding:12px 14px;border:1px solid rgba(105,228,154,.18);border-radius:14px;background:rgba(105,228,154,.06);margin-bottom:10px;\">"
            f"<div style=\"font-size:.62rem;letter-spacing:.12em;color:#8fe2aa;font-weight:900;text-transform:uppercase;\">CURRENT RANGE</div>"
            f"<div style=\"font-size:1.35rem;font-weight:900;color:#f4fff8;margin-top:4px;\">₹{min_rate:,.0f} – ₹{max_rate:,.0f}</div>"
            f"<div style=\"font-size:.68rem;color:rgba(230,250,237,.55);margin-top:3px;\">per coconut • admin controlled</div></div>",
            unsafe_allow_html=True,
        )
        st.caption(f"Dry ₹{active_rates['dry']:,.0f} • Green ₹{active_rates['green']:,.0f} • Tender ₹{active_rates['tender']:,.0f}")
        st.caption("Read-only price information. Changes are available only in Admin → Market Rates.")

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

        # ----------------------------------------------------
        # NOTE: Logout is handled by the role workspace sidebar.
        # This analysis sidebar intentionally has no second Logout
        # button, preventing duplicate Streamlit widget IDs.
        # ----------------------------------------------------


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

                                        "filename": uploaded_file.name,
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

        # ============================================================
        # PHASE 6 — BULK ANALYSIS -> PERMANENT FARMER BATCHES
        # ============================================================
        # Bulk analysis previously saved only analysis_results. That meant
        # Agent/Dealer could not see those images in the supply-chain flow.
        # Each analyzed image is now optionally promoted to its own
        # permanent coconut_batches record.
        if get_logged_in_role() == "farmer":
            st.markdown("### 📦 Convert Bulk Harvest Into Permanent Batches")
            st.caption(
                "Each uploaded image represents one harvest/bunch batch. "
                "Save them here to make every batch visible to Agent collection "
                "and later Dealer inventory."
            )

            bulk_saved = st.session_state.get("phase6_bulk_saved_codes", {})
            pending_count = 0
            for idx, item in enumerate(batch_results):
                key_name = str(item.get("filename", f"image_{idx + 1}"))
                if key_name not in bulk_saved:
                    pending_count += 1

            action_col1, action_col2 = st.columns([2, 1])
            with action_col1:
                if st.button(
                    f"📦 Create {pending_count} Permanent Batch{'es' if pending_count != 1 else ''}",
                    type="primary",
                    use_container_width=True,
                    disabled=(pending_count == 0),
                    key="phase6_bulk_create_permanent_batches",
                ):
                    current_user = st.session_state.get("current_user") or {}
                    resolved_user_id = _phase6_resolve_user_id(current_user)
                    created = []
                    already_saved = []
                    failed = []

                    for idx, item in enumerate(batch_results):
                        filename = str(item.get("filename", f"bulk_image_{idx + 1}"))
                        item_key = filename

                        # Skip a batch already created in this browser session.
                        if item_key in bulk_saved:
                            already_saved.append(bulk_saved[item_key])
                            continue

                        bulk_result = dict(item)
                        bulk_result["grade_info"] = {
                            "grade": str(item.get("grade", "—")),
                            "badge_color": str(item.get("badge_color", "#16a34a")),
                        }

                        success, batch_code, message = _phase6_create_batch(
                            resolved_user_id,
                            bulk_result,
                            filename,
                            active_rates,
                        )

                        if success:
                            created.append(batch_code)
                            bulk_saved[item_key] = batch_code
                        elif batch_code:
                            # Fingerprint protection means the database already
                            # contains this permanent batch. Treat it as saved.
                            already_saved.append(batch_code)
                            bulk_saved[item_key] = batch_code
                        else:
                            failed.append(f"{filename}: {message}")

                    st.session_state["phase6_bulk_saved_codes"] = bulk_saved

                    if created:
                        st.success(
                            f"✅ Created {len(created)} permanent batch{'es' if len(created) != 1 else ''}. "
                            "Agent and Dealer workspaces can now see them."
                        )
                    if already_saved:
                        st.info(
                            f"ℹ️ {len(already_saved)} batch{'es were' if len(already_saved) != 1 else ' was'} "
                            "already saved and were not duplicated."
                        )
                    if failed:
                        for error_text in failed:
                            st.error(error_text)

            with action_col2:
                st.metric("🟢 Pending", pending_count)

            if bulk_saved:
                st.caption(
                    "Saved in this session: "
                    + ", ".join(list(bulk_saved.values())[-5:])
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

        # ====================================================
        # PHASE 6 — SAVE ANALYSIS AS PERMANENT FARMER BATCH
        # ====================================================
        if get_logged_in_role() == "farmer":
            st.markdown("### 📦 Harvest Batch")
            st.caption(
                "Turn this completed AI analysis into a permanent batch. "
                "The batch remains owned by you and is ready for the future Agent collection workflow."
            )
            batch_col1, batch_col2 = st.columns([2, 1])
            with batch_col1:
                st.info(
                    f"🥥 {int(res.get('total', 0) or 0)} coconuts  •  "
                    f"{res.get('grade_info', {}).get('grade', '—')}  •  "
                    f"Estimated value ₹{float(res.get('total_value', 0) or 0):,.2f}"
                )
            with batch_col2:
                if st.button(
                    "📦 Create Permanent Batch",
                    type="primary",
                    use_container_width=True,
                    key="phase6_create_permanent_batch",
                ):
                    current_user = st.session_state.get("current_user") or {}
                    resolved_user_id = _phase6_resolve_user_id(current_user)
                    success, batch_code, message = _phase6_create_batch(
                        resolved_user_id,
                        res,
                        res.get("filename", "uploaded_harvest"),
                        active_rates,
                    )
                    if success:
                        st.session_state["phase6_last_batch_code"] = batch_code
                        st.success(f"✅ {message} Batch ID: **{batch_code}**")
                    elif batch_code:
                        st.info(f"ℹ️ {message} Batch ID: **{batch_code}**")
                    else:
                        st.error(message)



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




# ============================================================
# AGENT WORKSPACE PAGES
# ============================================================


def _safe_result_value(row, *keys, default=""):
    """Read a value from a database result regardless of minor schema naming differences."""
    if isinstance(row, dict):
        for key in keys:
            if key in row and row[key] is not None:
                return row[key]
    return default


def _get_farmers_for_agent():
    """Compatibility helper: load farmer users across database API versions."""
    for method_name in ("get_users_by_role", "get_all_users", "get_users"):
        method = getattr(db, method_name, None)
        if not callable(method):
            continue
        try:
            users = method("farmer") if method_name == "get_users_by_role" else method()
            users = users or []
            if method_name != "get_users_by_role":
                users = [u for u in users if str(_safe_result_value(u, "role", "user_role", default="")).lower() == "farmer"]
            return users
        except TypeError:
            continue
        except Exception:
            continue
    return []



def _phase6_get_agent_batch_records(agent_id=None):
    """Return permanent farmer batches for the agent workspace.

    Phase 6 batches are the source of truth for agent-side collection
    visibility. This intentionally reads coconut_batches rather than the
    agent's own analysis history.
    """
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            if agent_id is not None:
                rows = conn.execute(
                    """
                    SELECT
                        cb.id,
                        cb.batch_code,
                        cb.batch_name,
                        cb.farmer_id,
                        cb.created_by,
                        cb.source_filename,
                        cb.dry_count,
                        cb.green_count,
                        cb.tender_count,
                        cb.total_coconuts,
                        cb.grade,
                        cb.average_confidence,
                        cb.estimated_value,
                        cb.ai_engine,
                        cb.status,
                        cb.created_at,
                        cb.agent_id,
                        cb.collected_at,
                        cb.collected_by,
                        COALESCE(u.username, 'Farmer') AS farmer_name,
                        COALESCE(u.email, '—') AS farmer_email,
                        COALESCE(a.username, '—') AS agent_name
                    FROM coconut_batches cb
                    LEFT JOIN users u ON u.id = cb.farmer_id
                    LEFT JOIN users a ON a.id = cb.agent_id
                    ORDER BY cb.id DESC
                    """
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT
                        cb.id,
                        cb.batch_code,
                        cb.batch_name,
                        cb.farmer_id,
                        cb.created_by,
                        cb.source_filename,
                        cb.dry_count,
                        cb.green_count,
                        cb.tender_count,
                        cb.total_coconuts,
                        cb.grade,
                        cb.average_confidence,
                        cb.estimated_value,
                        cb.ai_engine,
                        cb.status,
                        cb.created_at,
                        cb.agent_id,
                        cb.collected_at,
                        cb.collected_by,
                        COALESCE(u.username, 'Farmer') AS farmer_name,
                        COALESCE(u.email, '—') AS farmer_email,
                        COALESCE(a.username, '—') AS agent_name
                    FROM coconut_batches cb
                    LEFT JOIN users u ON u.id = cb.farmer_id
                    LEFT JOIN users a ON a.id = cb.agent_id
                    ORDER BY cb.id DESC
                    """
                ).fetchall()
            return [dict(row) for row in rows]
    except Exception as exc:
        logger.error(f"Unable to read permanent farmer batches for agent: {exc}")
        return []


def _phase6_agent_batch_summary(agent_id=None):
    """Calculate live agent metrics from permanent coconut batches."""
    rows = _phase6_get_agent_batch_records(agent_id)
    available = [r for r in rows if str(r.get("status", "")).lower() == "available"]
    collected = [
        r for r in rows
        if str(r.get("status", "")).lower() in {"collected", "accepted", "assigned"}
    ]

    # If collection fields are not present in this Phase 6 schema yet, all
    # farmer-owned batches are still visible as available to an agent.
    available_coconuts = sum(int(r.get("total_coconuts", 0) or 0) for r in available)
    available_value = sum(float(r.get("estimated_value", 0) or 0) for r in available)
    collected_coconuts = sum(int(r.get("total_coconuts", 0) or 0) for r in collected)
    collected_value = sum(float(r.get("estimated_value", 0) or 0) for r in collected)

    my_collected = [
        r for r in collected
        if agent_id is not None and str(r.get("agent_id", "")) == str(agent_id)
    ]
    my_collected_coconuts = sum(int(r.get("total_coconuts", 0) or 0) for r in my_collected)
    my_collected_value = sum(float(r.get("estimated_value", 0) or 0) for r in my_collected)
    return {
        "rows": rows,
        "available": available,
        "collected": collected,
        "my_collected": my_collected,
        "available_coconuts": available_coconuts,
        "available_value": available_value,
        "collected_coconuts": collected_coconuts,
        "collected_value": collected_value,
        "my_collected_coconuts": my_collected_coconuts,
        "my_collected_value": my_collected_value,
    }


def agent_batch_analytics_page():
    """Live batch analytics sourced from permanent farmer batches."""
    current_user = st.session_state.get("current_user") or {}
    agent_id = _phase6_resolve_user_id(current_user)

    summary = _phase6_agent_batch_summary(agent_id)
    rows = summary["rows"]

    st.markdown("""
        <div class="role-hero">
          <div class="role-kicker">📊 AGENT · LIVE BATCH INTELLIGENCE</div>
          <div class="role-title">Analyze the harvest batches created by your farmers.</div>
          <div class="role-copy">
            This screen reads the permanent <strong>coconut_batches</strong> records created
            from Farmer → Coconut Analysis → Create Permanent Batch.
          </div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total Batches", len(rows))
    c2.metric("🟢 Available", len(summary["available"]))
    c3.metric("🥥 Available Coconuts", f'{summary["available_coconuts"]:,}')
    c4.metric("💰 Available Value", f'₹{summary["available_value"]:,.2f}')

    if not rows:
        st.info(
            "🌱 No permanent farmer batches yet. "
            "Login as a Farmer, analyze a harvest and click 'Create Permanent Batch'."
        )
        return

    st.markdown("### 📋 Live Farmer Batch Feed")
    display = []
    for row in rows:
        display.append({
            "Batch ID": row.get("batch_code") or "—",
            "Farmer": row.get("farmer_name") or "Farmer",
            "Coconuts": int(row.get("total_coconuts", 0) or 0),
            "Dry": int(row.get("dry_count", 0) or 0),
            "Green": int(row.get("green_count", 0) or 0),
            "Tender": int(row.get("tender_count", 0) or 0),
            "Grade": row.get("grade") or "—",
            "Value": f'₹{float(row.get("estimated_value", 0) or 0):,.2f}',
            "Status": row.get("status") or "Available",
            "AI": row.get("ai_engine") or "—",
            "Created": row.get("created_at") or "—",
        })

    st.dataframe(display, use_container_width=True, hide_index=True)

    # Composition across all farmer batches.
    dry_total = sum(int(r.get("dry_count", 0) or 0) for r in rows)
    green_total = sum(int(r.get("green_count", 0) or 0) for r in rows)
    tender_total = sum(int(r.get("tender_count", 0) or 0) for r in rows)
    total_value = sum(float(r.get("estimated_value", 0) or 0) for r in rows)

    st.markdown("### 🥥 Network Composition")
    a, b, c, d = st.columns(4)
    a.metric("🟤 Dry", dry_total)
    b.metric("🟢 Green", green_total)
    c.metric("💧 Tender", tender_total)
    d.metric("💰 Total Estimated", f"₹{total_value:,.2f}")


def agent_farmers_page():
    """Show farmer network using permanent Phase 6 batch records."""
    current_user = st.session_state.get("current_user") or {}
    agent_name = current_user.get("username", "Agent")
    summary = _phase6_agent_batch_summary(_phase6_resolve_user_id(current_user))
    rows = summary["rows"]

    st.markdown(f"""
        <div class="role-hero">
          <div class="role-kicker">🤝 AGENT FARMER NETWORK</div>
          <div class="role-title">Your field network, in one view.</div>
          <div class="role-copy">
            Welcome <strong>{agent_name}</strong>. Farmer activity below is now based on
            permanent batches created from the Farmer workspace.
          </div>
        </div>
        """, unsafe_allow_html=True)

    if not rows:
        st.info("👨‍🌾 No permanent farmer batches are available yet.")
        return

    grouped = {}
    for row in rows:
        key = row.get("farmer_id")
        grouped.setdefault(key, {
            "Farmer": row.get("farmer_name") or "Farmer",
            "Email": row.get("farmer_email") or "—",
            "Batches": 0,
            "Coconuts": 0,
            "Estimated Value": 0.0,
            "Last Batch": "—",
        })
        item = grouped[key]
        item["Batches"] += 1
        item["Coconuts"] += int(row.get("total_coconuts", 0) or 0)
        item["Estimated Value"] += float(row.get("estimated_value", 0) or 0)
        if item["Last Batch"] == "—":
            item["Last Batch"] = row.get("created_at") or "—"

    display = []
    for item in grouped.values():
        display.append({
            **item,
            "Estimated Value": f'₹{item["Estimated Value"]:,.2f}',
        })

    c1,c2,c3=st.columns(3)
    c1.metric("👨‍🌾 Farmers", len(display))
    c2.metric("📦 Permanent Batches", len(rows))
    c3.metric("🥥 Coconuts", f'{sum(int(r.get("total_coconuts",0) or 0) for r in rows):,}')

    st.markdown("### 👨‍🌾 Farmer Activity")
    st.dataframe(display, use_container_width=True, hide_index=True)


def _phase6_accept_collection(batch_id, agent_id):
    """Atomically assign an available farmer batch to the logged-in agent."""
    try:
        agent_id = int(agent_id)
        batch_id = int(batch_id)
    except (TypeError, ValueError):
        return False, "Invalid batch or agent ID."
    if agent_id <= 0 or batch_id <= 0:
        return False, "Invalid batch or agent ID."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            # Only an available, unassigned batch can be claimed.
            cur = conn.execute(
                """
                UPDATE coconut_batches
                SET agent_id = ?, collected_by = ?, collected_at = ?, status = 'Collected'
                WHERE id = ?
                  AND LOWER(COALESCE(status, 'Available')) = 'available'
                  AND (agent_id IS NULL OR agent_id = 0)
                """,
                (agent_id, agent_id, now, batch_id),
            )
            if cur.rowcount != 1:
                row = conn.execute(
                    "SELECT status, agent_id FROM coconut_batches WHERE id = ?",
                    (batch_id,),
                ).fetchone()
                if not row:
                    return False, "Batch not found."
                if str(row[0]).lower() != "available":
                    return False, f"This batch is already {row[0]}."
                return False, "This batch has already been assigned to another agent."
            conn.commit()
            return True, "Collection accepted successfully."
    except Exception as exc:
        logger.error(f"Phase 6 collection acceptance failed: {exc}")
        return False, f"Unable to accept collection: {exc}"


def agent_batches_page():
    """Agent collection center sourced from permanent farmer batches."""
    current_user = st.session_state.get("current_user") or {}
    agent_id = _phase6_resolve_user_id(current_user)
    summary = _phase6_agent_batch_summary(agent_id)
    rows = summary["rows"]

    st.markdown("""
        <div class="role-hero">
          <div class="role-kicker">📦 AGENT COLLECTION CENTER</div>
          <div class="role-title">Collect permanent harvest batches from farmers.</div>
          <div class="role-copy">
            Available farmer batches can be claimed by the logged-in agent. Once accepted,
            the batch is permanently assigned to you and its status changes to Collected.
          </div>
        </div>
        """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📦 Batches", len(rows))
    c2.metric("🟢 Available", len(summary["available"]))
    c3.metric("🤝 My Collected", len(summary.get("my_collected", [])))
    c4.metric("🥥 Available Coconuts", f'{summary["available_coconuts"]:,}')

    if not rows:
        st.info("📭 No permanent farmer batches yet. Create a batch from a Farmer account and return here.")
        return

    available = [r for r in rows if str(r.get("status", "")).lower() == "available"]
    collected = [
        r for r in rows
        if str(r.get("status", "")).lower() == "collected"
        and str(r.get("agent_id", "")) == str(agent_id)
    ]

    if available:
        st.markdown("### 📋 Available Farmer Batches")
        for row in available:
            batch_id = row.get("id")
            left, mid, right = st.columns([4, 2, 1.5])
            with left:
                st.markdown(f"**📦 {row.get('batch_code') or 'Batch'}**")
                st.caption(
                    f"👨‍🌾 {row.get('farmer_name') or 'Farmer'}  •  "
                    f"🥥 {int(row.get('total_coconuts', 0) or 0)} coconuts  •  "
                    f"🏆 {row.get('grade') or '—'}"
                )
            with mid:
                st.metric("💰 Estimated", f"₹{float(row.get('estimated_value', 0) or 0):,.2f}")
            with right:
                if st.button(
                    "🤝 Accept Collection",
                    type="primary",
                    use_container_width=True,
                    key=f"accept_collection_{batch_id}",
                ):
                    ok, message = _phase6_accept_collection(batch_id, agent_id)
                    if ok:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            st.divider()
    else:
        st.success("✅ There are no unassigned farmer batches waiting for collection.")

    if collected:
        st.markdown("### 🤝 My Collected Batches")
        display = []
        for row in collected:
            display.append({
                "Batch ID": row.get("batch_code") or "—",
                "Farmer": row.get("farmer_name") or "Farmer",
                "Coconuts": int(row.get("total_coconuts", 0) or 0),
                "Grade": row.get("grade") or "—",
                "Estimated Value": f'₹{float(row.get("estimated_value", 0) or 0):,.2f}',
                "Collected At": row.get("collected_at") or "—",
                "Status": "Collected",
            })
        st.dataframe(display, use_container_width=True, hide_index=True)

    st.markdown("### 📊 Batch Overview")
    display_all = []
    for row in rows:
        display_all.append({
            "Batch ID": row.get("batch_code") or "—",
            "Farmer": row.get("farmer_name") or "Farmer",
            "Coconuts": int(row.get("total_coconuts", 0) or 0),
            "Grade": row.get("grade") or "—",
            "Estimated Value": f'₹{float(row.get("estimated_value", 0) or 0):,.2f}',
            "Status": row.get("status") or "Available",
            "Agent": row.get("agent_name") or "—",
        })
    st.dataframe(display_all, use_container_width=True, hide_index=True)


def _dealer_records():
    """Build dealer inventory records from the dealer's existing analysis history."""
    current_user = st.session_state.get("current_user") or {}
    user_id = current_user.get("user_id")
    try:
        results = db.get_user_results(user_id) or [] if user_id is not None else []
    except Exception:
        results = []
    records = []
    for i, row in enumerate(results, 1):
        total = int(_safe_result_value(row, "total_coconuts", "total_coconuts_analyzed", default=0) or 0)
        value = float(_safe_result_value(row, "total_value", "batch_value", "estimated_value", default=0) or 0)
        records.append({
            "Batch": f"STOCK-{i:03d}",
            "File": _safe_result_value(row, "filename", "file_name", default="—"),
            "Coconuts": total,
            "Grade": _safe_result_value(row, "grade", default="—"),
            "Estimated Value": value,
            "Date": _safe_result_value(row, "created_at", "analysis_date", "date", "timestamp", default="—"),
        })
    return list(reversed(records))


def dealer_inventory_page():
    """Dealer inventory connected to permanently collected Agent batches."""
    current_user = st.session_state.get("current_user") or {}
    dealer_id = _phase6_resolve_user_id(current_user)
    rows = _phase7_get_dealer_batches(dealer_id) if dealer_id else []
    waiting = [r for r in rows if str(r.get("status", "")).lower() == "collected" and not r.get("dealer_id")]
    mine = [r for r in rows if str(r.get("status", "")).lower() == "in dealer inventory" and int(r.get("dealer_id") or 0) == int(dealer_id or -1)]
    st.markdown("""
        <div class="role-hero"><div class="role-kicker">🏪 PHASE 7 · DEALER INVENTORY</div>
        <div class="role-title">Receive collected batches into your stock.</div>
        <div class="role-copy">Collected Farmer batches now flow from Agent collection into permanent Dealer inventory.</div></div>
    """, unsafe_allow_html=True)
    stock_coconuts = sum(int(r.get("total_coconuts",0) or 0) for r in mine)
    stock_value = sum(float(r.get("estimated_value",0) or 0) for r in mine)
    pending_value = sum(float(r.get("estimated_value",0) or 0) for r in waiting)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📦 My Stock Lots", len(mine)); c2.metric("🥥 Stock Coconuts", f"{stock_coconuts:,}")
    c3.metric("💰 Stock Value", f"₹{stock_value:,.2f}"); c4.metric("🤝 Pending Receipt", f"₹{pending_value:,.2f}")
    if waiting:
        st.markdown("### 🤝 Collected Batches Waiting for Dealer")
        for row in waiting:
            a,b,c = st.columns([4,2,1.5])
            with a:
                st.markdown(f"**📦 {row.get('batch_code') or 'Batch'}**")
                st.caption(f"👨‍🌾 {row.get('farmer_name') or 'Farmer'} • 🥥 {int(row.get('total_coconuts',0) or 0)} coconuts • 🏆 {row.get('grade') or '—'}")
            with b: st.metric("Estimated", f"₹{float(row.get('estimated_value',0) or 0):,.2f}")
            with c:
                if st.button("📥 Receive", type="primary", use_container_width=True, key=f"dealer_receive_{row.get('id')}"):
                    ok,msg = _phase7_receive_batch(row.get('id'), dealer_id)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)
            st.divider()
    else: st.success("✅ No collected batches are waiting for dealer receipt.")
    st.markdown("### 📦 My Dealer Inventory")
    if not mine:
        st.info("Your dealer inventory is empty. An Agent must collect a Farmer batch before it can be received here.")
        return
    display=[{
        "Batch ID":r.get("batch_code") or "—","Farmer":r.get("farmer_name") or "Farmer",
        "Coconuts":int(r.get("total_coconuts",0) or 0),"Dry":int(r.get("dry_count",0) or 0),
        "Green":int(r.get("green_count",0) or 0),"Tender":int(r.get("tender_count",0) or 0),
        "Grade":r.get("grade") or "—","Value":f"₹{float(r.get('estimated_value',0) or 0):,.2f}",
        "Received":r.get("received_at") or "—","Status":"In Dealer Inventory"
    } for r in mine]
    st.dataframe(display, use_container_width=True, hide_index=True)


def dealer_transactions_page():
    """Persistent dealer purchase/sale ledger tied to batches."""
    current_user = st.session_state.get("current_user") or {}
    dealer_id = _phase6_resolve_user_id(current_user)
    inventory = _phase7_get_dealer_batches(dealer_id) if dealer_id else []
    mine = [r for r in inventory if str(r.get("status","")).lower()=="in dealer inventory" and int(r.get("dealer_id") or 0)==int(dealer_id or -1)]
    txs = _phase7_get_transactions(dealer_id) if dealer_id else []
    st.markdown("""
        <div class="role-hero"><div class="role-kicker">💰 PHASE 7 · DEALER TRANSACTIONS</div>
        <div class="role-title">Record purchases and sales against real inventory.</div>
        <div class="role-copy">Transactions are stored permanently in SQLite.</div></div>
    """, unsafe_allow_html=True)
    with st.form("phase7_dealer_transaction_form", clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        tx_type=c1.selectbox("Transaction",["Purchase","Sale"],key="phase7_tx_type")
        batch_options={f"{r.get('batch_code')} · {int(r.get('available_quantity', r.get('total_coconuts',0)) or 0)} available":r.get('id') for r in mine}
        selected_label=c2.selectbox("Inventory Batch",["— No batch —"]+list(batch_options.keys()),key="phase7_tx_batch")
        party=c3.text_input("Farmer / Buyer",placeholder="Party name",key="phase7_tx_party")
        c4,c5=st.columns(2); quantity=c4.number_input("Quantity",min_value=0,step=1,key="phase7_tx_qty"); amount=c5.number_input("Amount (₹)",min_value=0.0,step=100.0,key="phase7_tx_amount")
        notes=st.text_input("Notes",placeholder="Optional transaction note",key="phase7_tx_notes")
        submitted=st.form_submit_button("➕ Save Transaction",type="primary",use_container_width=True)
        if submitted:
            if amount<=0: st.error("Enter an amount greater than ₹0.")
            elif selected_label=="— No batch —" and quantity>0: st.error("Select an inventory batch when entering a quantity.")
            else:
                ok,msg=_phase7_add_transaction(dealer_id,batch_options.get(selected_label),tx_type,party,quantity,amount,notes)
                if ok: st.success(msg); st.rerun()
                else: st.error(msg)
    purchases=sum(float(t.get("amount",0) or 0) for t in txs if t.get("transaction_type")=="Purchase")
    sales=sum(float(t.get("amount",0) or 0) for t in txs if t.get("transaction_type")=="Sale")
    c1,c2,c3=st.columns(3); c1.metric("🛒 Purchases",f"₹{purchases:,.2f}"); c2.metric("💵 Sales",f"₹{sales:,.2f}"); c3.metric("📈 Difference",f"₹{sales-purchases:,.2f}")
    st.markdown("### 🧾 Permanent Transaction Ledger")
    if txs:
        st.dataframe([{"Type":t.get("transaction_type"),"Batch":t.get("batch_code") or "—","Party":t.get("party_name") or "—","Quantity":t.get("quantity",0),"Amount":f"₹{float(t.get('amount',0) or 0):,.2f}","Notes":t.get("notes") or "—","Date":t.get("created_at") or "—"} for t in txs],use_container_width=True,hide_index=True)
    else: st.info("No dealer transactions have been recorded yet.")


def dealer_business_analytics_page():
    """Dealer analytics based on permanent inventory and transactions."""
    current_user=st.session_state.get("current_user") or {}; dealer_id=_phase6_resolve_user_id(current_user)
    rows=_phase7_get_dealer_batches(dealer_id) if dealer_id else []
    mine=[r for r in rows if str(r.get("status","")).lower()=="in dealer inventory" and int(r.get("dealer_id") or 0)==int(dealer_id or -1)]
    txs=_phase7_get_transactions(dealer_id) if dealer_id else []
    stock_value=sum(float(r.get("estimated_value",0) or 0) for r in mine); stock_count=sum(int(r.get("total_coconuts",0) or 0) for r in mine)
    purchases=sum(float(t.get("amount",0) or 0) for t in txs if t.get("transaction_type")=="Purchase"); sales=sum(float(t.get("amount",0) or 0) for t in txs if t.get("transaction_type")=="Sale")
    st.markdown("""
        <div class="role-hero"><div class="role-kicker">📊 PHASE 7 · DEALER BUSINESS INTELLIGENCE</div>
        <div class="role-title">Connect inventory with real trade activity.</div>
        <div class="role-copy">Every metric below comes from permanent Dealer inventory and transaction tables.</div></div>
    """,unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4); c1.metric("📦 Inventory Lots",len(mine)); c2.metric("🥥 Stock Coconuts",f"{stock_count:,}"); c3.metric("💰 Stock Value",f"₹{stock_value:,.2f}"); c4.metric("📈 Trade Difference",f"₹{sales-purchases:,.2f}")
    st.markdown("### 💳 Transaction Summary")
    st.dataframe([{"Metric":"Purchases","Value":f"₹{purchases:,.2f}"},{"Metric":"Sales","Value":f"₹{sales:,.2f}"},{"Metric":"Recorded Transactions","Value":len(txs)}],use_container_width=True,hide_index=True)

# ============================================================
# PHASE 8 — DEALER SALES + INVENTORY QUANTITY TRACKING
# ============================================================

def _phase8_ensure_inventory_columns():
    """Migrate existing dealer inventory rows to quantity-aware stock tracking."""
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(coconut_batches)").fetchall()}
            additions = {
                "available_quantity": "INTEGER NOT NULL DEFAULT 0",
                "sold_quantity": "INTEGER NOT NULL DEFAULT 0",
                "depleted_at": "TEXT",
            }
            for name, definition in additions.items():
                if name not in cols:
                    conn.execute(f"ALTER TABLE coconut_batches ADD COLUMN {name} {definition}")
            conn.execute("""
                UPDATE coconut_batches
                SET available_quantity = CASE
                    WHEN COALESCE(available_quantity, 0) = 0
                         AND LOWER(COALESCE(status, '')) IN ('in dealer inventory', 'collected')
                    THEN COALESCE(total_coconuts, 0)
                    ELSE COALESCE(available_quantity, 0)
                END
                WHERE LOWER(COALESCE(status, '')) IN ('in dealer inventory', 'collected')
            """)
            conn.execute("""
                UPDATE coconut_batches
                SET sold_quantity = CASE
                    WHEN COALESCE(sold_quantity, 0) < 0 THEN 0
                    ELSE COALESCE(sold_quantity, 0)
                END
            """)
            conn.commit()
            return True
    except Exception as exc:
        logger.error(f"Phase 8 inventory migration failed: {exc}")
        return False


def _phase8_get_inventory_batches(dealer_id):
    _phase8_ensure_inventory_columns()
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT cb.id, cb.batch_code, cb.batch_name, cb.farmer_id, cb.agent_id,
                       cb.dealer_id, cb.total_coconuts, cb.available_quantity, cb.sold_quantity,
                       cb.dry_count, cb.green_count, cb.tender_count, cb.grade,
                       cb.average_confidence, cb.estimated_value, cb.status,
                       cb.created_at, cb.collected_at, cb.received_at, cb.depleted_at,
                       COALESCE(u.username, 'Farmer') AS farmer_name
                FROM coconut_batches cb
                LEFT JOIN users u ON u.id = cb.farmer_id
                WHERE cb.dealer_id = ?
                  AND LOWER(COALESCE(cb.status, '')) IN ('in dealer inventory', 'depleted', 'sold')
                ORDER BY cb.id DESC
            """, (int(dealer_id),)).fetchall()
            return [dict(r) for r in rows]
    except Exception as exc:
        logger.error(f"Phase 8 inventory retrieval failed: {exc}")
        return []


def _phase8_record_sale(dealer_id, batch_id, buyer_name, quantity, amount, notes):
    try:
        dealer_id, batch_id, quantity = int(dealer_id), int(batch_id), int(quantity)
        amount = float(amount)
    except (TypeError, ValueError):
        return False, "Invalid sale details."
    if dealer_id <= 0 or batch_id <= 0:
        return False, "Invalid dealer or batch."
    if quantity <= 0:
        return False, "Sale quantity must be greater than 0."
    if amount <= 0:
        return False, "Sale amount must be greater than ₹0."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT id, dealer_id, available_quantity, total_coconuts, status
                FROM coconut_batches WHERE id = ?
            """, (batch_id,)).fetchone()
            if not row:
                return False, "Inventory batch not found."
            if int(row["dealer_id"] or 0) != dealer_id:
                return False, "This batch does not belong to the logged-in dealer."
            current_available = int(row["available_quantity"] or 0)
            if current_available <= 0:
                return False, "This batch has no remaining stock."
            if quantity > current_available:
                return False, f"Only {current_available} coconuts are available in this batch."

            remaining = current_available - quantity
            sold_total = int(row["total_coconuts"] or 0) - remaining
            if sold_total < 0:
                sold_total = 0

            if remaining == 0:
                cur = conn.execute("""
                    UPDATE coconut_batches
                    SET available_quantity = 0, sold_quantity = ?,
                        status = 'Depleted', depleted_at = ?
                    WHERE id = ? AND dealer_id = ? AND available_quantity = ?
                """, (sold_total, now, batch_id, dealer_id, current_available))
            else:
                cur = conn.execute("""
                    UPDATE coconut_batches
                    SET available_quantity = ?, sold_quantity = ?
                    WHERE id = ? AND dealer_id = ? AND available_quantity = ?
                """, (remaining, sold_total, batch_id, dealer_id, current_available))

            if cur.rowcount != 1:
                conn.rollback()
                return False, "Inventory changed before the sale was completed. Please try again."

            conn.execute("""
                INSERT INTO transactions
                (batch_id, dealer_id, transaction_type, party_name, quantity, amount, notes, created_at)
                VALUES (?, ?, 'Sale', ?, ?, ?, ?, ?)
            """, (batch_id, dealer_id, buyer_name or "Buyer", quantity, amount, notes or "", now))
            conn.commit()
            status_text = "Batch fully sold and marked Depleted." if remaining == 0 else f"{remaining} coconuts remain in this batch."
            return True, f"Sale recorded successfully. {status_text}"
    except Exception as exc:
        logger.error(f"Phase 8 sale failed: {exc}")
        return False, f"Unable to record sale: {exc}"


def dealer_sales_page():
    """Dealer sales page with permanent quantity-aware inventory updates."""
    current_user = st.session_state.get("current_user") or {}
    dealer_id = _phase6_resolve_user_id(current_user)
    inventory = _phase8_get_inventory_batches(dealer_id) if dealer_id else []
    active = [r for r in inventory if str(r.get("status", "")).lower() == "in dealer inventory" and int(r.get("available_quantity", 0) or 0) > 0]
    sold = [r for r in inventory if str(r.get("status", "")).lower() == "depleted"]

    st.markdown("""
        <div class="role-hero"><div class="role-kicker">💰 PHASE 8 · DEALER SALES</div>
        <div class="role-title">Sell stock and update inventory in real time.</div>
        <div class="role-copy">Every sale permanently reduces the selected batch's available coconut quantity.</div></div>
    """, unsafe_allow_html=True)

    total_available = sum(int(r.get("available_quantity", 0) or 0) for r in active)
    stock_value = sum(
        float(r.get("estimated_value", 0) or 0) *
        (int(r.get("available_quantity", 0) or 0) / max(int(r.get("total_coconuts", 0) or 0), 1))
        for r in active
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Active Lots", len(active))
    c2.metric("🥥 Available Coconuts", total_available)
    c3.metric("💰 Remaining Stock Value", f"₹{stock_value:,.2f}")

    if not active:
        st.info("No available stock for sale. Receive a collected batch into Dealer Inventory first.")
        return

    st.markdown("### 🧾 Create Sale")
    batch_options = {
        f"{r.get('batch_code') or 'Batch'} · {int(r.get('available_quantity', 0) or 0)} available · {r.get('grade') or '—'}": r.get("id")
        for r in active
    }
    with st.form("phase8_dealer_sale_form", clear_on_submit=True):
        selected = st.selectbox("Inventory Batch", list(batch_options.keys()), key="phase8_sale_batch")
        c1, c2, c3 = st.columns(3)
        buyer = c1.text_input("Buyer / Customer", placeholder="Customer name", key="phase8_sale_buyer")
        qty = c2.number_input("Quantity", min_value=1, step=1, key="phase8_sale_qty")
        amount = c3.number_input("Sale Amount (₹)", min_value=1.0, step=100.0, key="phase8_sale_amount")
        notes = st.text_input("Notes", placeholder="Optional sale note", key="phase8_sale_notes")
        submit = st.form_submit_button("💵 Complete Sale", type="primary", use_container_width=True)
        if submit:
            ok, msg = _phase8_record_sale(dealer_id, batch_options[selected], buyer, qty, amount, notes)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("### 📦 Current Inventory")
    st.dataframe([
        {"Batch ID": r.get("batch_code") or "—", "Farmer": r.get("farmer_name") or "Farmer",
         "Original": int(r.get("total_coconuts", 0) or 0), "Available": int(r.get("available_quantity", 0) or 0),
         "Sold": int(r.get("sold_quantity", 0) or 0), "Grade": r.get("grade") or "—", "Status": r.get("status") or "—"}
        for r in inventory
    ], use_container_width=True, hide_index=True)

    if sold:
        st.markdown("### ✅ Depleted Batches")
        st.dataframe([
            {"Batch ID": r.get("batch_code") or "—", "Original": int(r.get("total_coconuts", 0) or 0),
             "Sold": int(r.get("sold_quantity", 0) or 0), "Depleted": r.get("depleted_at") or "—"}
            for r in sold
        ], use_container_width=True, hide_index=True)


# ============================================================
# PHASE 7 — DEALER INVENTORY + PERSISTENT TRANSACTIONS
# ============================================================

def _phase7_get_dealer_batches(dealer_id):
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT cb.id, cb.batch_code, cb.batch_name, cb.farmer_id, cb.agent_id,
                       cb.dealer_id, cb.total_coconuts, cb.dry_count, cb.green_count,
                       cb.tender_count, cb.grade, cb.average_confidence, cb.estimated_value,
                       cb.status, cb.created_at, cb.collected_at, cb.received_at,
                       COALESCE(u.username, 'Farmer') AS farmer_name
                FROM coconut_batches cb
                LEFT JOIN users u ON u.id = cb.farmer_id
                WHERE LOWER(COALESCE(cb.status, '')) IN ('collected', 'in dealer inventory')
                   OR cb.dealer_id = ?
                ORDER BY cb.id DESC
                """,
                (int(dealer_id),),
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as exc:
        logger.error(f"Phase 7 dealer batch retrieval failed: {exc}")
        return []


def _phase7_receive_batch(batch_id, dealer_id):
    try:
        batch_id, dealer_id = int(batch_id), int(dealer_id)
    except (TypeError, ValueError):
        return False, "Invalid batch or dealer ID."
    if batch_id <= 0 or dealer_id <= 0:
        return False, "Invalid batch or dealer ID."
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            cur = conn.execute(
                """
                UPDATE coconut_batches
                SET dealer_id = ?, received_at = ?, status = 'In Dealer Inventory'
                WHERE id = ?
                  AND LOWER(COALESCE(status, '')) = 'collected'
                  AND (dealer_id IS NULL OR dealer_id = 0)
                """,
                (dealer_id, now, batch_id),
            )
            if cur.rowcount != 1:
                row = conn.execute("SELECT status, dealer_id FROM coconut_batches WHERE id = ?", (batch_id,)).fetchone()
                if not row:
                    return False, "Batch not found."
                if row[1] not in (None, 0, dealer_id):
                    return False, "This batch is already assigned to another dealer."
                return False, f"This batch is already {row[0]}."
            conn.commit()
            return True, "Batch received into dealer inventory."
    except Exception as exc:
        logger.error(f"Phase 7 dealer receipt failed: {exc}")
        return False, f"Unable to receive batch: {exc}"


def _phase7_add_transaction(dealer_id, batch_id, tx_type, party_name, quantity, amount, notes):
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO transactions
                (batch_id, dealer_id, transaction_type, party_name, quantity, amount, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (batch_id, int(dealer_id), tx_type, party_name or "—", int(quantity or 0),
                 float(amount or 0), notes or "", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            conn.commit()
            return True, "Transaction saved permanently."
    except Exception as exc:
        logger.error(f"Phase 7 transaction insert failed: {exc}")
        return False, f"Unable to save transaction: {exc}"


def _phase7_get_transactions(dealer_id):
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT t.id, t.batch_id, t.transaction_type, t.party_name, t.quantity,
                       t.amount, t.notes, t.created_at, cb.batch_code
                FROM transactions t
                LEFT JOIN coconut_batches cb ON cb.id = t.batch_id
                WHERE t.dealer_id = ?
                ORDER BY t.id DESC
                """,
                (int(dealer_id),),
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as exc:
        logger.error(f"Phase 7 transaction retrieval failed: {exc}")
        return []

# ============================================================
# PHASE 6 — PERMANENT FARMER BATCH STORAGE
# ============================================================

def _phase6_init_batch_table():
    """Create or migrate the permanent farmer batch table safely.

    Older Phase 6 versions may already have created ``coconut_batches`` with a
    different schema. ``CREATE TABLE IF NOT EXISTS`` does not migrate an
    existing SQLite table, so this function adds any missing columns instead.
    """
    required_columns = {
        "batch_code": "TEXT",
        "batch_name": "TEXT",
        "farmer_id": "INTEGER",
        "created_by": "INTEGER",
        "source_filename": "TEXT",
        "dry_count": "INTEGER NOT NULL DEFAULT 0",
        "green_count": "INTEGER NOT NULL DEFAULT 0",
        "tender_count": "INTEGER NOT NULL DEFAULT 0",
        "total_coconuts": "INTEGER NOT NULL DEFAULT 0",
        "grade": "TEXT",
        "average_confidence": "REAL NOT NULL DEFAULT 0",
        "estimated_value": "REAL NOT NULL DEFAULT 0",
        "market_rates": "TEXT",
        "ai_engine": "TEXT",
        "status": "TEXT NOT NULL DEFAULT 'Available'",
        "created_at": "TEXT",
        "fingerprint": "TEXT",
        "agent_id": "INTEGER",
        "collected_at": "TEXT",
        "collected_by": "INTEGER",
        "dealer_id": "INTEGER",
        "received_at": "TEXT",
    }

    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS coconut_batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_code TEXT,
                    batch_name TEXT,
                    farmer_id INTEGER,
                    created_by INTEGER,
                    source_filename TEXT,
                    dry_count INTEGER NOT NULL DEFAULT 0,
                    green_count INTEGER NOT NULL DEFAULT 0,
                    tender_count INTEGER NOT NULL DEFAULT 0,
                    total_coconuts INTEGER NOT NULL DEFAULT 0,
                    grade TEXT,
                    average_confidence REAL NOT NULL DEFAULT 0,
                    estimated_value REAL NOT NULL DEFAULT 0,
                    market_rates TEXT,
                    ai_engine TEXT,
                    status TEXT NOT NULL DEFAULT 'Available',
                    created_at TEXT,
                    fingerprint TEXT,
                    agent_id INTEGER,
                    collected_at TEXT,
                    collected_by INTEGER,
                    dealer_id INTEGER,
                    received_at TEXT
                )
                """
            )

            existing_columns = {
                row[1] for row in conn.execute("PRAGMA table_info(coconut_batches)").fetchall()
            }

            # Migrate tables created by earlier versions.
            for column, definition in required_columns.items():
                if column not in existing_columns:
                    conn.execute(
                        f"ALTER TABLE coconut_batches ADD COLUMN {column} {definition}"
                    )

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Populate missing legacy values so the new workflow can use them.
            rows = conn.execute(
                "SELECT id, batch_code, batch_name, created_at, status FROM coconut_batches"
            ).fetchall()
            used_codes = {
                str(row[1]) for row in rows
                if row[1] is not None and str(row[1]).strip()
            }

            # Keep legacy creator information populated. For farmer-owned batches,
            # the farmer_id is the original creator when no separate value exists.
            if "created_by" in existing_columns or "created_by" in required_columns:
                conn.execute(
                    "UPDATE coconut_batches SET created_by = farmer_id "
                    "WHERE created_by IS NULL AND farmer_id IS NOT NULL"
                )

            for row in rows:
                row_id = row[0]
                code = str(row[1]).strip() if row[1] is not None else ""
                if not code or code in used_codes and sum(
                    1 for r in rows if r[1] == code
                ) > 1:
                    # Generate a guaranteed-new code for legacy/duplicate rows.
                    while True:
                        candidate = (
                            f"CB-LEGACY-{datetime.now().strftime('%Y%m%d%H%M%S')}-"
                            f"{str(uuid.uuid4())[:6].upper()}"
                        )
                        if candidate not in used_codes:
                            break
                    used_codes.add(candidate)
                    conn.execute(
                        "UPDATE coconut_batches SET batch_code = ? WHERE id = ?",
                        (candidate, row_id),
                    )

                batch_name = str(row[2]).strip() if len(row) > 2 and row[2] is not None else ""
                if not batch_name:
                    code_for_name = str(row[1]).strip() if row[1] is not None else f"CB-{row_id}"
                    conn.execute(
                        "UPDATE coconut_batches SET batch_name = ? WHERE id = ?",
                        (f"Harvest Batch {code_for_name}", row_id),
                    )

                created_at_value = row[3] if len(row) > 3 else None
                if created_at_value is None or not str(created_at_value).strip():
                    conn.execute(
                        "UPDATE coconut_batches SET created_at = ? WHERE id = ?",
                        (now, row_id),
                    )

            # Useful indexes; batch_code uniqueness is enforced for new rows
            # by the application-level duplicate check as well.
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_coconut_batches_farmer "
                "ON coconut_batches(farmer_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_coconut_batches_status "
                "ON coconut_batches(status)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_coconut_batches_code "
                "ON coconut_batches(batch_code)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_coconut_batches_dealer "
                "ON coconut_batches(dealer_id)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id INTEGER,
                    dealer_id INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    party_name TEXT,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    amount REAL NOT NULL DEFAULT 0,
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            # Migrate an older transaction table if one already exists.
            tx_defs = {
                "batch_id": "INTEGER",
                "dealer_id": "INTEGER",
                "transaction_type": "TEXT",
                "party_name": "TEXT",
                "quantity": "INTEGER NOT NULL DEFAULT 0",
                "amount": "REAL NOT NULL DEFAULT 0",
                "notes": "TEXT",
                "created_at": "TEXT",
            }
            tx_existing = {row[1] for row in conn.execute("PRAGMA table_info(transactions)").fetchall()}
            for col, definition in tx_defs.items():
                if col not in tx_existing:
                    conn.execute(f"ALTER TABLE transactions ADD COLUMN {col} {definition}")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_dealer ON transactions(dealer_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_batch ON transactions(batch_id)"
            )
            conn.commit()

    except Exception as exc:
        logger.error(f"Phase 6 batch table initialization/migration failed: {exc}")


def _phase6_resolve_user_id(current_user):
    """Resolve the authenticated user's numeric database id across auth versions."""
    if not isinstance(current_user, dict):
        return None

    # Different versions of auth.py used different keys.
    for key in ("user_id", "id", "uid"):
        value = current_user.get(key)
        if value not in (None, "", 0, "0"):
            try:
                return int(value)
            except (TypeError, ValueError):
                pass

    username = current_user.get("username") or current_user.get("user_name")
    if username:
        try:
            with sqlite3.connect(config.DB_PATH) as conn:
                row = conn.execute(
                    "SELECT id FROM users WHERE username = ? LIMIT 1",
                    (str(username),),
                ).fetchone()
                if row and row[0] is not None:
                    return int(row[0])
        except Exception as exc:
            logger.error(f"Unable to resolve user id for batch creation: {exc}")

    return None


def _phase6_create_batch(user_id, result, filename, market_rates):
    """Persist one completed AI analysis as a farmer-owned coconut batch."""
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False, None, (
            "Unable to create batch: the logged-in user's database ID could not be resolved. "
            "Please logout, login again, and retry."
        )

    if user_id <= 0:
        return False, None, "Unable to create batch: invalid logged-in user ID."

    counts = result.get("counts") or {}
    grade_info = result.get("grade_info") or {}
    dry = int(counts.get("dry", 0) or 0)
    green = int(counts.get("green", 0) or 0)
    tender = int(counts.get("tender", 0) or 0)
    total = int(result.get("total", dry + green + tender) or 0)
    grade = str(grade_info.get("grade", "—"))
    confidence = float(result.get("avg_conf", 0) or 0)
    estimated_value = float(result.get("total_value", 0) or 0)
    ai_engine = str(result.get("ai_engine", "YOLO"))

    fingerprint = "|".join([
        str(user_id), str(filename), str(dry), str(green), str(tender),
        str(total), grade, f"{estimated_value:.4f}", ai_engine
    ])

    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            existing = conn.execute(
                "SELECT batch_code FROM coconut_batches WHERE fingerprint = ?",
                (fingerprint,),
            ).fetchone()
            if existing:
                return False, existing[0], "This analysis is already saved as a permanent batch."

            batch_code = f"CB-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:6].upper()}"
            conn.execute(
                """
                INSERT INTO coconut_batches
                (batch_code, batch_name, farmer_id, created_by, source_filename, dry_count, green_count,
                 tender_count, total_coconuts, grade, average_confidence,
                 estimated_value, market_rates, ai_engine, status, created_at, fingerprint)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Available', ?, ?)
                """,
                (
                    batch_code, f"Harvest Batch {batch_code}", int(user_id), int(user_id), filename, dry, green, tender,
                    total, grade, confidence, estimated_value,
                    json.dumps(market_rates or {}), ai_engine,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fingerprint,
                ),
            )
            conn.commit()
            return True, batch_code, "Permanent farmer batch created successfully."
    except Exception as exc:
        logger.error(f"Phase 6 batch creation failed: {exc}", exc)
        return False, None, f"Unable to create batch: {exc}"


def _phase6_get_farmer_batches(user_id):
    """Read permanent batches for one farmer."""
    try:
        with sqlite3.connect(config.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT batch_code, source_filename, dry_count, green_count,
                       tender_count, total_coconuts, grade, average_confidence,
                       estimated_value, ai_engine, status, created_at, agent_id, collected_at,
                       dealer_id, received_at
                FROM coconut_batches
                WHERE farmer_id = ?
                ORDER BY id DESC
                """,
                (int(user_id),),
            ).fetchall()
            return [dict(row) for row in rows]
    except Exception as exc:
        logger.error(f"Phase 6 batch retrieval failed: {exc}", exc)
        return []


_phase6_init_batch_table()


def farmer_batches_page():
    """Permanent farmer-owned batch vault for Phase 6."""
    current_user = st.session_state.get("current_user") or {}
    user_id = current_user.get("user_id")

    st.markdown(
        """
        <div class="role-hero">
          <div class="role-kicker">📦 PHASE 6 · FARMER BATCH VAULT</div>
          <div class="role-title">Your harvest is now a permanent batch.</div>
          <div class="role-copy">
            Every completed AI analysis can be converted into a traceable farmer batch
            that will later flow into the Agent collection and Dealer inventory modules.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    batches = _phase6_get_farmer_batches(user_id) if user_id is not None else []

    total_coconuts = sum(int(row.get("total_coconuts", 0) or 0) for row in batches)
    total_value = sum(float(row.get("estimated_value", 0) or 0) for row in batches)
    available = sum(1 for row in batches if row.get("status") == "Available")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Saved Batches", len(batches))
    c2.metric("🥥 Total Coconuts", total_coconuts)
    c3.metric("💰 Estimated Value", f"₹{total_value:,.2f}")
    c4.metric("🟢 Available", available)

    st.markdown("### 📋 Permanent Batch Records")

    if not batches:
        st.info("No permanent batches yet. Complete a Coconut Analysis and choose 'Create Permanent Batch'.")
        if st.button("🥥 Analyze My First Batch", type="primary", use_container_width=True, key="phase6_first_batch"):
            _open_workspace("🥥 Coconut Analysis")
        return

    display_rows = []
    for row in batches:
        display_rows.append({
            "Batch ID": row["batch_code"],
            "File": row.get("source_filename") or "—",
            "Coconuts": row.get("total_coconuts", 0),
            "Dry": row.get("dry_count", 0),
            "Green": row.get("green_count", 0),
            "Tender": row.get("tender_count", 0),
            "Grade": row.get("grade") or "—",
            "Confidence": f"{float(row.get('average_confidence', 0) or 0) * 100:.1f}%",
            "Value": f"₹{float(row.get('estimated_value', 0) or 0):,.2f}",
            "Status": row.get("status") or "Available",
            "Agent ID": row.get("agent_id") or "—",
            "Collected At": row.get("collected_at") or "—",
            "Created": row.get("created_at") or "—",
        })

    st.dataframe(display_rows, use_container_width=True, hide_index=True)

    if st.button("🥥 Analyze Another Harvest", type="primary", use_container_width=True, key="phase6_another_batch"):
        _open_workspace("🥥 Coconut Analysis")


def farmer_valuation_page():
    """Display a farmer-focused valuation summary from existing recorded statistics."""
    current_user = st.session_state.get("current_user") or {}
    user_id = current_user.get("user_id")

    stats = {}
    if user_id is not None:
        try:
            stats = db.get_user_statistics(user_id) or {}
        except Exception:
            stats = {}

    st.markdown(
        """
        <div class="role-hero">
          <div class="role-kicker">💰 FARMER VALUATION</div>
          <div class="role-title">Know the estimated value of your harvest.</div>
          <div class="role-copy">
            This view uses the values already recorded by the application. Estimates are based on the configured benchmark rates.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("🥥 Coconuts Analyzed", stats.get("total_coconuts_analyzed", 0))
    c2.metric("📦 Average Batch Value", f"₹{stats.get('avg_batch_value', 0):,.2f}")
    c3.metric("💰 Recorded Total Value", f"₹{stats.get('total_value', 0):,.2f}")

    st.markdown("### 🧾 Valuation workflow")
    st.info(
        "Upload a batch → detect individual coconuts → classify maturity → "
        "calculate coconut-wise and bunch-wise valuation."
    )

    if st.button("🥥 Open Coconut Analysis", type="primary", use_container_width=True):
        _open_workspace("🥥 Coconut Analysis")



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
