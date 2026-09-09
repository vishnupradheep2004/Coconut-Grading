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
# AUTHENTICATION PAGES
# ============================================================

def login_page():
    """Login page"""
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; color: white; font-size: 2.5rem;">🥥 Coconut Grading AI</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## Login")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("Please enter username and password")
                else:
                    success, message, token = auth_manager.login(username, password)
                    
                    if success:
                        st.session_state.session_token = token
                        st.session_state.current_user = auth_manager.get_current_user(token)
                        st.session_state.page = "app"
                        logger.log_user_action(username, "login", "successful")
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                        logger.log_user_action(username, "login", "failed")
        
        with tab2:
            st.subheader("Create New Account")
            
            new_username = st.text_input("New Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            new_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
            
            role = st.selectbox("Select Role", ["farmer", "agent", "dealer"], key="reg_role")
            
            if st.button("Register", use_container_width=True, type="primary"):
                if not new_username or not new_email or not new_password:
                    st.error("Please fill in all fields")
                elif new_password != new_password_confirm:
                    st.error("Passwords do not match")
                else:
                    success, message = auth_manager.register_user(new_username, new_password, new_email, role)
                    
                    if success:
                        st.success(message)
                        logger.log_user_action(new_username, "register", f"role={role}")
                        st.info("You can now login with your credentials")
                    else:
                        st.error(message)


def app_page():
    """Main application page"""
    
    # Sidebar with user info
    with st.sidebar:
        if st.session_state.current_user:
            st.markdown(f"**👤 {st.session_state.current_user['username']}**")
            st.markdown(f"*Role: {st.session_state.current_user['role']}*")
            st.divider()
        
        st.markdown("### ⚙️ Settings")
        
        conf_threshold = st.slider(
            "Confidence Threshold",
            min_value=config.MIN_CONFIDENCE_THRESHOLD,
            max_value=config.MAX_CONFIDENCE_THRESHOLD,
            value=config.DEFAULT_CONFIDENCE_THRESHOLD,
            step=config.CONFIDENCE_STEP
        )
        
        st.divider()
        st.markdown("### 💰 Market Rates (₹)")
        
        dry_rate = st.number_input("Dry Mature (₹/pc)", value=DEFAULT_MARKET_RATES["dry"], step=1.0)
        green_rate = st.number_input("Fresh Green (₹/pc)", value=DEFAULT_MARKET_RATES["green"], step=1.0)
        tender_rate = st.number_input("Tender Water (₹/pc)", value=DEFAULT_MARKET_RATES["tender"], step=1.0)
        
        active_rates = {"dry": float(dry_rate), "green": float(green_rate), "tender": float(tender_rate)}
        
        # Validate rates
        valid, msg = validate_market_rates(active_rates)
        if not valid:
            st.error(msg)
        
        st.divider()
        
        if st.button("📋 View History", use_container_width=True):
            st.session_state.page = "history"
        
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.page = "analytics"
        
        if st.button("🚪 Logout", use_container_width=True):
            auth_manager.logout(st.session_state.session_token)
            st.session_state.session_token = None
            st.session_state.current_user = None
            st.session_state.page = "login"
            logger.log_user_action(st.session_state.current_user["username"] if st.session_state.current_user else "unknown", "logout")
            st.rerun()
    
    # Main content
    st.markdown("# 🥥 Coconut Grading & Quality Detection AI")
    st.markdown("*Single and Bulk Image Processing with AI-Powered Analysis*")
    
    # Upload mode selection
    upload_mode = st.radio(
        "📤 Upload Mode:",
        options=["Single Image", "Bulk Upload (Multiple Images)"],
        horizontal=True
    )
    
    # Single image mode
    if upload_mode == "Single Image":
        uploaded_file = st.file_uploader(
            "📤 Upload Image",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=False
        )
        
        if uploaded_file is not None:
            # Validate image
            image = Image.open(uploaded_file).convert("RGB")
            valid, msg = validate_image(image)
            
            if not valid:
                st.error(f"Invalid image: {msg}")
            else:
                col_left, col_right = st.columns([1, 1], gap="large")
                
                with col_left:
                    st.subheader("🖼️ Uploaded Image")
                    # Get image quality
                    quality_score, quality_level = ImageProcessor.get_image_statistics(image)
                    st.image(image, use_container_width=True)
                    st.caption(f"Quality: {quality_level}")
                
                with col_right:
                    st.subheader("🔍 Analysis")
                    
                    if st.button("🚀 Analyze", type="primary", use_container_width=True):
                        if not yolo_model:
                            st.error("YOLO model not loaded")
                        else:
                            perf_monitor.start_timer("single_analysis")
                            
                            with st.spinner("Processing..."):
                                try:
                                    detection_data = detect_coconuts(
                                        model=yolo_model,
                                        image=image,
                                        conf_threshold=conf_threshold
                                    )
                                    
                                    counts = detection_data["counts"]
                                    total = detection_data["total"]
                                    avg_conf = detection_data["average_confidence"]
                                    
                                    # Get grading
                                    grade_info = calculate_grade_and_summary(counts, avg_conf)
                                    
                                    # Calculate valuation
                                    total_val, breakdown = calculate_market_valuation(counts, active_rates)
                                    
                                    processing_time = perf_monitor.end_timer("single_analysis")
                                    
                                    # Save to database
                                    if st.session_state.current_user:
                                        db.save_analysis_result(
                                            user_id=st.session_state.current_user["user_id"],
                                            filename=uploaded_file.name,
                                            counts=counts,
                                            grade=grade_info["grade"],
                                            confidence=avg_conf,
                                            total_value=total_val,
                                            market_rates=active_rates
                                        )
                                        logger.log_analysis(
                                            st.session_state.current_user["username"],
                                            uploaded_file.name,
                                            total,
                                            grade_info["grade"],
                                            processing_time
                                        )
                                    
                                    st.session_state["analysis_results"] = {
                                        "plotted_image": detection_data["plotted_image"],
                                        "counts": counts,
                                        "total": total,
                                        "avg_conf": avg_conf,
                                        "grade_info": grade_info,
                                        "total_value": total_val,
                                        "breakdown": breakdown,
                                        "processing_time": processing_time
                                    }
                                    
                                except Exception as e:
                                    st.error(f"Analysis failed: {str(e)}")
                                    logger.error(f"Analysis error for {uploaded_file.name}", e)
    
    # Bulk upload mode
    elif upload_mode == "Bulk Upload (Multiple Images)":
        uploaded_files = st.file_uploader(
            "📤 Upload Multiple Images",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.subheader(f"📦 Processing {len(uploaded_files)} images...")
            
            if st.button("🚀 Analyze All", type="primary", use_container_width=True):
                if not yolo_model:
                    st.error("YOLO model not loaded")
                else:
                    perf_monitor.start_timer("bulk_analysis")
                    
                    batch_results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        try:
                            status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                            
                            # Load and validate image
                            image = Image.open(uploaded_file).convert("RGB")
                            valid, msg = validate_image(image)
                            
                            if not valid:
                                st.warning(f"⚠️ {uploaded_file.name}: {msg}")
                                continue
                            
                            # Detect coconuts
                            detection_data = detect_coconuts(
                                model=yolo_model,
                                image=image,
                                conf_threshold=conf_threshold
                            )
                            
                            counts = detection_data["counts"]
                            total = detection_data["total"]
                            avg_conf = detection_data["average_confidence"]
                            
                            # Get grading
                            grade_info = calculate_grade_and_summary(counts, avg_conf)
                            
                            # Calculate valuation
                            total_val, breakdown = calculate_market_valuation(counts, active_rates)
                            
                            # Add to batch results
                            batch_results.append({
                                "filename": uploaded_file.name,
                                "counts": counts,
                                "total": total,
                                "avg_conf": avg_conf,
                                "grade": grade_info["grade"],
                                "badge_color": grade_info["badge_color"],
                                "total_value": total_val,
                                "breakdown": breakdown
                            })
                            
                            # Save to database
                            if st.session_state.current_user:
                                db.save_analysis_result(
                                    user_id=st.session_state.current_user["user_id"],
                                    filename=uploaded_file.name,
                                    counts=counts,
                                    grade=grade_info["grade"],
                                    confidence=avg_conf,
                                    total_value=total_val,
                                    market_rates=active_rates
                                )
                            
                            progress_bar.progress((idx + 1) / len(uploaded_files))
                            
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                            logger.error(f"Bulk analysis error for {uploaded_file.name}", e)
                    
                    if batch_results:
                        processing_time = perf_monitor.end_timer("bulk_analysis")
                        status_text.success(f"✅ Processed {len(batch_results)}/{len(uploaded_files)} images in {processing_time:.2f}s")
                        
                        # Calculate aggregate stats for logging
                        total_coconuts = sum(r["total"] for r in batch_results)
                        
                        # Log batch processing
                        if st.session_state.current_user:
                            logger.log_batch_processing(
                                st.session_state.current_user["username"],
                                f"batch_{len(uploaded_files)}",
                                len(batch_results),
                                total_coconuts,
                                processing_time
                            )
                        
                        # Store batch results
                        st.session_state["batch_results"] = batch_results
    
    # Display batch results
    if "batch_results" in st.session_state and len(st.session_state["batch_results"]) > 0:
        batch_results = st.session_state["batch_results"]
        
        st.divider()
        st.subheader(f"📊 Batch Analysis Results ({len(batch_results)} images)")
        
        # Aggregate statistics
        total_coconuts = sum(r["total"] for r in batch_results)
        total_value = sum(r["total_value"] for r in batch_results)
        avg_confidence = sum(r["avg_conf"] for r in batch_results) / len(batch_results)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📸 Images Processed", len(batch_results))
        col2.metric("🥥 Total Coconuts", total_coconuts)
        col3.metric("💵 Total Value", f"₹{total_value:.2f}")
        col4.metric("📊 Avg Confidence", f"{avg_confidence:.2%}")
        
        st.divider()
        
        # Results table
        tab_table, tab_detail, tab_export = st.tabs(["📋 Summary Table", "🔍 Detailed View", "📥 Export"])
        
        with tab_table:
            table_data = []
            for r in batch_results:
                table_data.append({
                    "📁 File": r["filename"],
                    "🥥 Count": r["total"],
                    "🏆 Grade": r["grade"],
                    "📊 Confidence": f"{r['avg_conf']:.2%}",
                    "💵 Value": f"₹{r['total_value']:.2f}"
                })
            st.dataframe(table_data, use_container_width=True)
        
        with tab_detail:
            for idx, result in enumerate(batch_results, 1):
                with st.expander(f"📄 {result['filename']} - Grade {result['grade'].split()[-1]}", expanded=(idx == 1)):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.metric("Total Coconuts", result["total"])
                        st.metric("Confidence", f"{result['avg_conf']:.2%}")
                        breakdown = result["breakdown"]
                        st.write("**Breakdown:**")
                        for coconut_type in ["dry", "green", "tender"]:
                            st.write(f"• {coconut_type.title()}: {breakdown[coconut_type]['count']}")
                    
                    with col2:
                        st.metric("Total Value", f"₹{result['total_value']:.2f}")
                        st.write("**Price Breakdown:**")
                        for coconut_type in ["dry", "green", "tender"]:
                            st.write(f"• {coconut_type.title()}: ₹{breakdown[coconut_type]['subtotal']:.2f}")
        
        with tab_export:
            if st.button("📄 Export Batch as CSV", use_container_width=True):
                csv_path = report_gen.generate_csv_report(f"batch_{len(batch_results)}", batch_results)
                st.success(f"✅ Report saved: {csv_path}")
            
            if st.button("📄 Export Batch Summary", use_container_width=True):
                summary = {
                    "total_images": len(batch_results),
                    "total_coconuts": total_coconuts,
                    "total_value": total_value,
                    "avg_confidence": avg_confidence,
                    "results": batch_results
                }
                json_path = report_gen.generate_json_report(f"batch_{len(batch_results)}_summary", summary)
                st.success(f"✅ Summary saved: {json_path}")
    
    # Display results
    if "analysis_results" in st.session_state:
        res = st.session_state["analysis_results"]
        
        st.divider()
        st.subheader("📊 Analysis Results")
        
        tab_viz, tab_grade, tab_pricing, tab_export = st.tabs(
            ["📸 Detection", "🏆 Grade", "💰 Valuation", "📥 Export"]
        )
        
        with tab_viz:
            st.image(res["plotted_image"], channels="BGR", use_container_width=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🥥 Total", res["total"])
            m2.metric("🍂 Dry", res["counts"]["dry"])
            m3.metric("🌿 Green", res["counts"]["green"])
            m4.metric("💧 Tender", res["counts"]["tender"])
        
        with tab_grade:
            grade_info = res["grade_info"]
            grade_letter = grade_info['grade'].split()[1] if 'Grade' in grade_info['grade'] else '?'
            
            st.markdown(
                f"""
                <div style="text-align: center; margin: 20px 0;">
                    <div style="display: inline-block; background-color: {grade_info['badge_color']}; color: white; width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 3rem; font-weight: bold;">
                        {grade_letter}
                    </div>
                </div>
                <h3 style="text-align: center; color: {grade_info['badge_color']};">{grade_info['grade']}</h3>
                """,
                unsafe_allow_html=True
            )
            st.info(grade_info["description"])
        
        with tab_pricing:
            st.metric("💵 Total Value", f"₹{res['total_value']:.2f}")
            breakdown = res["breakdown"]
            pricing_data = [
                {"Type": "Dry Mature", "Count": breakdown["dry"]["count"], "Rate": f"₹{breakdown['dry']['rate']:.2f}", "Subtotal": f"₹{breakdown['dry']['subtotal']:.2f}"},
                {"Type": "Fresh Green", "Count": breakdown["green"]["count"], "Rate": f"₹{breakdown['green']['rate']:.2f}", "Subtotal": f"₹{breakdown['green']['subtotal']:.2f}"},
                {"Type": "Tender Water", "Count": breakdown["tender"]["count"], "Rate": f"₹{breakdown['tender']['rate']:.2f}", "Subtotal": f"₹{breakdown['tender']['subtotal']:.2f}"}
            ]
            st.table(pricing_data)
        
        with tab_export:
            if st.button("📄 Export as CSV", use_container_width=True):
                csv_path = report_gen.generate_csv_report("analysis", [res])
                st.success(f"Report saved: {csv_path}")
            
            if st.button("📄 Export as Text", use_container_width=True):
                txt_path = report_gen.generate_text_report("analysis", res)
                st.success(f"Report saved: {txt_path}")


# ============================================================
# HISTORY PAGE
# ============================================================

def history_page():
    """User analysis history"""
    st.title("📋 Analysis History")
    
    if st.session_state.current_user:
        user_id = st.session_state.current_user["user_id"]
        results = db.get_user_results(user_id)
        
        if results:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No analysis history yet")
    
    if st.button("← Back to App"):
        st.session_state.page = "app"
        st.rerun()


# ============================================================
# ANALYTICS PAGE
# ============================================================

def analytics_page():
    """User analytics and insights"""
    st.title("📊 Analytics & Insights")
    
    if st.session_state.current_user:
        user_id = st.session_state.current_user["user_id"]
        stats = db.get_user_statistics(user_id)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Analyses", stats.get("total_analyses", 0))
        col2.metric("Total Coconuts", stats.get("total_coconuts_analyzed", 0))
        col3.metric("Avg Batch Value", f"₹{stats.get('avg_batch_value', 0):.2f}")
        col4.metric("Total Value", f"₹{stats.get('total_value', 0):.2f}")
    
    if st.button("← Back to App"):
        st.session_state.page = "app"
        st.rerun()


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
