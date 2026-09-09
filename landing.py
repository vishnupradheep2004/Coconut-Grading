"""
app_integrated.py
Coconut Grading AI - Full Integration with All Features
Includes authentication, database, analytics, caching, and exports
"""

import streamlit as st
from PIL import Image
from pathlib import Path
import time

# Import all utilities
from utils import (
    # Original
    load_yolo_model, detect_coconuts, resolve_model_path,
    calculate_grade_and_summary,
    load_price_model, predict_market_price, calculate_market_valuation, DEFAULT_MARKET_RATES,
    # New
    get_config, ensure_directories,
    validate_image, validate_confidence_threshold, validate_market_rates,
    Database, AuthManager, ImageProcessor, ReportGenerator, Analytics,
    LoggingManager, PerformanceMonitor, Cache, ModelCache
)

# ============================================================
# INITIALIZATION
# ============================================================

# Initialize config and directories
config = get_config()
ensure_directories()

# Initialize database
db = Database(config.DB_PATH)

# Initialize authentication
auth_manager = AuthManager(db)

# Initialize logging
logger = LoggingManager(config.LOG_DIR, level=config.LOG_LEVEL)

# Initialize caching
model_cache = ModelCache(ttl_seconds=config.CACHE_TTL)
general_cache = Cache(ttl_seconds=config.CACHE_TTL)

# Initialize report generator
report_gen = ReportGenerator(config.EXPORT_DIR)

# Initialize performance monitor
perf_monitor = PerformanceMonitor()

# Initialize YOLO model
yolo_model = None
try:
    yolo_model_path = resolve_model_path(str(config.YOLO_MODEL_PATH))
    yolo_model = load_yolo_model(yolo_model_path)
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {str(e)}", e)

# Initialize price model
price_model = load_price_model(str(config.PRICE_MODEL_PATH))

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Coconut Grading AI",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "session_token" not in st.session_state:
    st.session_state.session_token = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ============================================================

# ============================================================
# HIGGSFIELD-INSPIRED PREMIUM UI
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

.stApp {
    background:
      radial-gradient(circle at 90% 5%, rgba(92,190,105,.16), transparent 28%),
      radial-gradient(circle at 5% 40%, rgba(126,231,135,.06), transparent 24%),
      #06100b;
    color:#f4f8f5;
}
.block-container{max-width:1450px!important;padding-top:1rem!important;}
#MainMenu,footer,header{visibility:hidden;}
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#08140e,#06100b);
    border-right:1px solid rgba(255,255,255,.08);
}
.topbar{
    display:flex;justify-content:space-between;align-items:center;
    padding:12px 2px 22px;border-bottom:1px solid rgba(255,255,255,.08);
}
.brand{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:700;}
.brand-icon{
    width:42px;height:42px;border-radius:13px;display:flex;
    align-items:center;justify-content:center;
    background:linear-gradient(135deg,#8de96d,#258c52);
    box-shadow:0 12px 30px rgba(126,231,135,.16);font-size:23px;
}
.nav-pill{
    padding:9px 15px;border-radius:999px;
    border:1px solid rgba(126,231,135,.25);
    background:rgba(126,231,135,.06);color:#7ee787;
    font-size:12px;font-weight:700;
}
.hero{
    position:relative;overflow:hidden;min-height:590px;
    margin-top:20px;padding:65px 6%;
    border:1px solid rgba(255,255,255,.09);border-radius:30px;
    display:flex;align-items:center;
    background:
      radial-gradient(circle at 78% 45%,rgba(126,231,135,.14),transparent 27%),
      linear-gradient(135deg,rgba(255,255,255,.055),rgba(255,255,255,.015));
    box-shadow:0 35px 100px rgba(0,0,0,.3);
}
.hero-copy{width:55%;position:relative;z-index:2;}
.eyebrow{
    display:inline-flex;align-items:center;gap:8px;padding:8px 13px;
    border-radius:999px;border:1px solid rgba(126,231,135,.23);
    background:rgba(126,231,135,.06);color:#7ee787;
    font-size:12px;font-weight:700;letter-spacing:.5px;
}
.dot{width:7px;height:7px;border-radius:50%;background:#7ee787;box-shadow:0 0 13px #7ee787;}
.hero h1{
    font-family:'Playfair Display',serif;font-size:clamp(48px,6vw,82px);
    line-height:.98;letter-spacing:-3px;margin:25px 0 0;
}
.hero h1 span{
    background:linear-gradient(90deg,#7ee787,#c8f36b);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.hero p{max-width:650px;color:#93a39a;font-size:17px;line-height:1.75;margin-top:25px;}
.hero-art{
    position:absolute;right:3%;top:50%;transform:translateY(-50%);
    width:43%;height:480px;border-radius:28px;
    background:radial-gradient(circle at 50% 42%,rgba(126,231,135,.13),transparent 35%),rgba(255,255,255,.025);
    border:1px solid rgba(255,255,255,.09);
}
.coconut-orb{
    position:absolute;left:50%;top:49%;width:245px;height:245px;
    transform:translate(-50%,-50%);border-radius:50%;
    background:radial-gradient(circle at 35% 28%,#bd9360,#6b442b 45%,#21160f 82%);
    box-shadow:inset -30px -30px 50px rgba(0,0,0,.5),0 35px 75px rgba(0,0,0,.5);
    display:flex;align-items:center;justify-content:center;font-size:145px;
}
.scan{
    position:absolute;left:50%;top:49%;width:285px;height:285px;
    transform:translate(-50%,-50%);border:2px solid #7ee787;border-radius:22px;
    box-shadow:0 0 30px rgba(126,231,135,.13);
}
.ai-chip{
    position:absolute;padding:9px 12px;border-radius:10px;background:#08130d;
    border:1px solid rgba(126,231,135,.3);color:#7ee787;font-size:11px;font-weight:700;
}
.chip1{left:7%;top:25%}.chip2{right:6%;bottom:28%}
.result-mini{
    position:absolute;left:22px;bottom:22px;width:190px;padding:15px;border-radius:15px;
    background:rgba(6,16,11,.9);border:1px solid rgba(255,255,255,.09);
}
.result-mini small{color:#84958a;font-size:10px}.result-mini strong{display:block;color:#7ee787;font-size:22px;margin:3px 0;}
.glass{
    background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.025));
    border:1px solid rgba(255,255,255,.09);border-radius:22px;padding:24px;
}
.section-tag{color:#7ee787;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;}
.section-title{font-family:'Playfair Display',serif;font-size:44px;letter-spacing:-1.5px;margin:5px 0 0;}
.muted{color:#93a39a;line-height:1.7;}
.stButton>button,.stDownloadButton>button{border-radius:11px!important;min-height:44px!important;font-weight:700!important;}
.stButton>button[kind="primary"]{
    background:linear-gradient(135deg,#7ee787,#c8f36b)!important;
    color:#06100b!important;border:0!important;
}
.stButton>button:hover{transform:translateY(-2px);transition:.2s;}
[data-testid="stFileUploader"]{
    background:rgba(126,231,135,.035);border:1px dashed rgba(126,231,135,.3);
    border-radius:18px;padding:8px;
}
[data-testid="stMetric"]{
    background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.08);
    border-radius:16px;padding:14px;
}
[data-testid="stMetricLabel"]{color:#91a197!important;}
[data-testid="stMetricValue"]{color:#f4f8f5!important;}
button[data-baseweb="tab"]{color:#9daaa2!important;}
button[data-baseweb="tab"][aria-selected="true"]{color:#7ee787!important;}
.grade-panel{
    text-align:center;padding:35px;border-radius:22px;
    background:linear-gradient(145deg,rgba(126,231,135,.08),rgba(255,255,255,.025));
    border:1px solid rgba(255,255,255,.09);
}
.grade-circle{
    width:105px;height:105px;border-radius:50%;margin:0 auto 15px;
    display:flex;align-items:center;justify-content:center;color:white;
    font-size:48px;font-weight:800;
}
.footer{
    margin-top:55px;padding-top:25px;border-top:1px solid rgba(255,255,255,.08);
    color:#718078;font-size:11px;display:flex;justify-content:space-between;
}
@media(max-width:900px){
    .hero{display:block;padding:55px 7%;min-height:auto;}
    .hero-copy{width:100%}.hero-art{position:relative;right:auto;top:auto;transform:none;width:100%;margin-top:55px;}
}
@media(max-width:600px){
    .hero h1{font-size:48px}.hero-art{height:400px}.coconut-orb{width:190px;height:190px;font-size:115px;}
    .scan{width:220px;height:220px}.footer{display:block;line-height:2;}
}
</style>
""", unsafe_allow_html=True)


def topbar():
    st.markdown("""
    <div class="topbar">
        <div class="brand"><div class="brand-icon">🥥</div>Coconut Grading AI</div>
        <div class="nav-pill">AI • OPENVINO</div>
    </div>
    """, unsafe_allow_html=True)


def landing_hero():
    st.markdown("""
    <div class="hero">
        <div class="hero-copy">
            <div class="eyebrow"><span class="dot"></span>INTELLIGENT AGRICULTURE</div>
            <h1>See the quality.<br><span>Know the value.</span></h1>
            <p>
                AI-powered coconut maturity detection, quality grading and
                market valuation in one streamlined workflow, with
                OpenVINO-optimized inference for efficient processing.
            </p>
        </div>
        <div class="hero-art">
            <div class="ai-chip chip1">🥥 TENDER · 96.4%</div>
            <div class="ai-chip chip2">✓ AI DETECTED</div>
            <div class="coconut-orb">🥥</div>
            <div class="scan"></div>
            <div class="result-mini">
                <small>ESTIMATED BATCH VALUE</small>
                <strong>₹1,240</strong>
                <small>Quality analysis complete</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def login_page():
    topbar()
    landing_hero()
    st.markdown("<br>", unsafe_allow_html=True)

    left, center, right = st.columns([1.2, 2, 1.2])
    with center:
        st.markdown("""
        <div class="glass">
            <div class="section-tag">SECURE ACCESS</div>
            <div class="section-title" style="font-size:34px;">Welcome back</div>
            <p class="muted">Sign in to analyze coconut batches and manage reports.</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign in", "Create account"])

        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Continue to AI Workspace →", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("Please enter username and password")
                else:
                    success, message, token = auth_manager.login(username, password)
                    if success:
                        st.session_state.session_token = token
                        st.session_state.current_user = auth_manager.get_current_user(token)
                        st.session_state.page = "app"
                        logger.log_user_action(username, "login", "successful")
                        st.rerun()
                    else:
                        st.error(message)
                        logger.log_user_action(username, "login", "failed")

        with tab2:
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm = st.text_input("Confirm password", type="password", key="reg_password_confirm")
            role = st.selectbox("Role", ["farmer", "agent", "dealer"], key="reg_role")

            if st.button("Create account →", use_container_width=True, type="primary"):
                if not new_username or not new_email or not new_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm:
                    st.error("Passwords do not match")
                else:
                    success, message = auth_manager.register_user(
                        new_username, new_password, new_email, role
                    )
                    if success:
                        st.success(message)
                        st.info("You can now sign in with your credentials.")
                    else:
                        st.error(message)

    st.markdown("""
    <div class="footer">
        <span>© 2026 Coconut Grading & Value Prediction AI</span>
        <span>Computer Vision · OpenVINO · AI</span>
    </div>
    """, unsafe_allow_html=True)


def sidebar_controls():
    with st.sidebar:
        st.markdown("## 🥥 AI Workspace")
        if st.session_state.current_user:
            u = st.session_state.current_user
            st.caption(f"Signed in as **{u['username']}**")
            st.caption(f"Role · {u['role'].title()}")

        st.divider()
        st.markdown("### Inference")
        conf_threshold = st.slider(
            "Confidence threshold",
            min_value=config.MIN_CONFIDENCE_THRESHOLD,
            max_value=config.MAX_CONFIDENCE_THRESHOLD,
            value=config.DEFAULT_CONFIDENCE_THRESHOLD,
            step=config.CONFIDENCE_STEP
        )

        st.divider()
        st.markdown("### Market benchmark")
        dry = st.number_input("Dry Mature · ₹/pc", value=DEFAULT_MARKET_RATES["dry"], step=1.0)
        green = st.number_input("Fresh Green · ₹/pc", value=DEFAULT_MARKET_RATES["green"], step=1.0)
        tender = st.number_input("Tender Water · ₹/pc", value=DEFAULT_MARKET_RATES["tender"], step=1.0)
        active_rates = {"dry": float(dry), "green": float(green), "tender": float(tender)}

        valid, msg = validate_market_rates(active_rates)
        if not valid:
            st.error(msg)

        st.divider()
        if st.button("📋 Analysis history", use_container_width=True):
            st.session_state.page = "history"; st.rerun()
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.page = "analytics"; st.rerun()
        if st.button("🚪 Sign out", use_container_width=True):
            username = st.session_state.current_user["username"] if st.session_state.current_user else "unknown"
            auth_manager.logout(st.session_state.session_token)
            st.session_state.session_token = None
            st.session_state.current_user = None
            st.session_state.page = "login"
            logger.log_user_action(username, "logout")
            st.rerun()

    return conf_threshold, active_rates


def app_page():
    topbar()
    conf_threshold, active_rates = sidebar_controls()

    st.markdown("""
    <div style="padding:18px 0 12px;">
        <div class="section-tag">AI ANALYSIS WORKSPACE</div>
        <div class="section-title">Turn coconut images into decisions.</div>
        <p class="muted">
            Upload one image for detailed inspection or process a complete batch
            for aggregate grading and valuation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio(
        "Processing mode",
        ["Single Image", "Bulk Upload (Multiple Images)"],
        horizontal=True
    )

    if mode == "Single Image":
        uploaded_file = st.file_uploader(
            "Drop a coconut image here",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=False
        )

        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            valid, msg = validate_image(image)

            if not valid:
                st.error(f"Invalid image: {msg}")
            else:
                quality_score, quality_level = ImageProcessor.get_image_statistics(image)
                left, right = st.columns([1.15, .85], gap="large")

                with left:
                    st.markdown("### Image preview")
                    st.image(image, use_container_width=True)
                    st.caption(f"Image quality · {quality_level} · score {quality_score:.0f}")

                with right:
                    st.markdown("### Analysis pipeline")
                    st.markdown("""
                    <div class="glass">
                        <div class="section-tag">PIPELINE</div>
                        <p class="muted">
                            Detection → maturity classification → quality grade →
                            transparent market valuation.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🚀 Analyze coconut batch", use_container_width=True, type="primary"):
                        if not yolo_model:
                            st.error("YOLO model not loaded")
                        else:
                            perf_monitor.start_timer("single_analysis")
                            with st.spinner("Running AI inference..."):
                                try:
                                    d = detect_coconuts(yolo_model, image, conf_threshold)
                                    counts, total, avg_conf = d["counts"], d["total"], d["average_confidence"]
                                    grade = calculate_grade_and_summary(counts, avg_conf)
                                    total_val, breakdown = calculate_market_valuation(counts, active_rates)
                                    processing_time = perf_monitor.end_timer("single_analysis")

                                    st.session_state["analysis_results"] = {
                                        "plotted_image": d["plotted_image"],
                                        "counts": counts, "total": total, "avg_conf": avg_conf,
                                        "grade_info": grade, "total_value": total_val,
                                        "breakdown": breakdown, "processing_time": processing_time
                                    }

                                    if st.session_state.current_user:
                                        db.save_analysis_result(
                                            user_id=st.session_state.current_user["user_id"],
                                            filename=uploaded_file.name,
                                            counts=counts, grade=grade["grade"],
                                            confidence=avg_conf, total_value=total_val,
                                            market_rates=active_rates
                                        )
                                    st.success(f"Analysis completed in {processing_time:.2f}s")
                                except Exception as e:
                                    st.error(f"Analysis failed: {str(e)}")
                                    logger.error(f"Analysis error for {uploaded_file.name}", e)

    else:
        uploaded_files = st.file_uploader(
            "Drop multiple coconut images here",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.info(f"{len(uploaded_files)} image(s) selected")
            if st.button("🚀 Analyze complete batch", use_container_width=True, type="primary"):
                if not yolo_model:
                    st.error("YOLO model not loaded")
                else:
                    perf_monitor.start_timer("bulk_analysis")
                    batch_results = []
                    progress = st.progress(0)
                    status = st.empty()

                    for idx, uploaded_file in enumerate(uploaded_files):
                        try:
                            status.text(f"Analyzing {idx + 1}/{len(uploaded_files)} · {uploaded_file.name}")
                            image = Image.open(uploaded_file).convert("RGB")
                            valid, msg = validate_image(image)
                            if not valid:
                                st.warning(f"{uploaded_file.name}: {msg}")
                                continue

                            d = detect_coconuts(yolo_model, image, conf_threshold)
                            counts, total, avg_conf = d["counts"], d["total"], d["average_confidence"]
                            grade = calculate_grade_and_summary(counts, avg_conf)
                            total_val, breakdown = calculate_market_valuation(counts, active_rates)

                            batch_results.append({
                                "filename": uploaded_file.name, "counts": counts, "total": total,
                                "avg_conf": avg_conf, "grade": grade["grade"],
                                "badge_color": grade["badge_color"], "total_value": total_val,
                                "breakdown": breakdown
                            })

                            if st.session_state.current_user:
                                db.save_analysis_result(
                                    user_id=st.session_state.current_user["user_id"],
                                    filename=uploaded_file.name, counts=counts,
                                    grade=grade["grade"], confidence=avg_conf,
                                    total_value=total_val, market_rates=active_rates
                                )

                            progress.progress((idx + 1) / len(uploaded_files))
                        except Exception as e:
                            st.warning(f"Error processing {uploaded_file.name}: {str(e)}")
                            logger.error(f"Bulk analysis error for {uploaded_file.name}", e)

                    if batch_results:
                        elapsed = perf_monitor.end_timer("bulk_analysis")
                        status.success(f"Processed {len(batch_results)}/{len(uploaded_files)} images in {elapsed:.2f}s")
                        st.session_state["batch_results"] = batch_results

    if st.session_state.get("batch_results"):
        results = st.session_state["batch_results"]
        st.markdown("## Batch intelligence")
        total_coconuts = sum(r["total"] for r in results)
        total_value = sum(r["total_value"] for r in results)
        avg_conf = sum(r["avg_conf"] for r in results) / len(results)

        a,b,c,d = st.columns(4)
        a.metric("Images", len(results)); b.metric("Coconuts", total_coconuts)
        c.metric("Estimated value", f"₹{total_value:.2f}")
        d.metric("Confidence", f"{avg_conf:.2%}")

        t1,t2,t3 = st.tabs(["Summary","Detailed view","Export"])
        with t1:
            st.dataframe([{
                "File":r["filename"],"Coconuts":r["total"],
                "Grade":r["grade"],"Confidence":f"{r['avg_conf']:.2%}",
                "Value":f"₹{r['total_value']:.2f}"
            } for r in results], use_container_width=True, hide_index=True)
        with t2:
            for i,r in enumerate(results,1):
                with st.expander(f"{i:02d} · {r['filename']}", expanded=(i==1)):
                    x,y=st.columns(2)
                    x.metric("Total coconuts",r["total"])
                    x.metric("Confidence",f"{r['avg_conf']:.2%}")
                    y.metric("Estimated value",f"₹{r['total_value']:.2f}")
                    y.write(f"**Grade:** {r['grade']}")
        with t3:
            if st.button("📄 Export batch as CSV", use_container_width=True):
                path=report_gen.generate_csv_report(f"batch_{len(results)}",results)
                st.success(f"Saved: {path}")
            if st.button("📄 Export batch summary as JSON", use_container_width=True):
                summary={"total_images":len(results),"total_coconuts":total_coconuts,
                         "total_value":total_value,"avg_confidence":avg_conf,"results":results}
                path=report_gen.generate_json_report(f"batch_{len(results)}_summary",summary)
                st.success(f"Saved: {path}")

    if st.session_state.get("analysis_results"):
        res=st.session_state["analysis_results"]
        st.markdown("## Analysis result")
        v,g,p,e=st.tabs(["Detection","Quality grade","Valuation","Export"])

        with v:
            st.image(res["plotted_image"],channels="BGR",use_container_width=True)
            a,b,c,d=st.columns(4)
            a.metric("Total",res["total"]);b.metric("Dry",res["counts"]["dry"])
            c.metric("Green",res["counts"]["green"]);d.metric("Tender",res["counts"]["tender"])

        with g:
            info=res["grade_info"]
            letter=info["grade"].split()[1] if "Grade" in info["grade"] else "?"
            st.markdown(f"""
            <div class="grade-panel">
                <div class="grade-circle" style="background:{info['badge_color']}">{letter}</div>
                <h2>{info['grade']}</h2>
                <p class="muted">{info['description']}</p>
                <p>Detection confidence · <strong>{res['avg_conf']:.2%}</strong></p>
            </div>
            """,unsafe_allow_html=True)

        with p:
            st.metric("Estimated total value",f"₹{res['total_value']:.2f}")
            b=res["breakdown"]
            st.table([
                {"Type":"Dry Mature","Count":b["dry"]["count"],"Rate":f"₹{b['dry']['rate']:.2f}","Subtotal":f"₹{b['dry']['subtotal']:.2f}"},
                {"Type":"Fresh Green","Count":b["green"]["count"],"Rate":f"₹{b['green']['rate']:.2f}","Subtotal":f"₹{b['green']['subtotal']:.2f}"},
                {"Type":"Tender Water","Count":b["tender"]["count"],"Rate":f"₹{b['tender']['rate']:.2f}","Subtotal":f"₹{b['tender']['subtotal']:.2f}"}
            ])

        with e:
            if st.button("📄 Export CSV",use_container_width=True):
                st.success(f"Saved: {report_gen.generate_csv_report('analysis',[res])}")
            if st.button("📄 Export text report",use_container_width=True):
                st.success(f"Saved: {report_gen.generate_text_report('analysis',res)}")


def history_page():
    topbar()
    st.markdown('<div class="section-tag">HISTORY</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your analysis history</div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    if st.session_state.current_user:
        rows=db.get_user_results(st.session_state.current_user["user_id"])
        if rows: st.dataframe(rows,use_container_width=True,hide_index=True)
        else: st.info("No analysis history yet.")
    if st.button("← Back to workspace"):
        st.session_state.page="app";st.rerun()


def analytics_page():
    topbar()
    st.markdown('<div class="section-tag">INSIGHTS</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your AI analytics</div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    if st.session_state.current_user:
        s=db.get_user_statistics(st.session_state.current_user["user_id"])
        a,b,c,d=st.columns(4)
        a.metric("Total analyses",s.get("total_analyses",0))
        b.metric("Coconuts analyzed",s.get("total_coconuts_analyzed",0))
        c.metric("Average batch value",f"₹{s.get('avg_batch_value',0):.2f}")
        d.metric("Total value",f"₹{s.get('total_value',0):.2f}")
    if st.button("← Back to workspace"):
        st.session_state.page="app";st.rerun()


# ============================================================
# PAGE ROUTING
# ============================================================

if st.session_state.session_token is None:
    login_page()
elif st.session_state.page == "app":
    app_page()
elif st.session_state.page == "history":
    history_page()
elif st.session_state.page == "analytics":
    analytics_page()
