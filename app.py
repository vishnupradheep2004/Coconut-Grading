"""
Coconut-Grading-AI - Streamlit Web Application
Production-ready, modular, and portable entrypoint for coconut maturity detection and grading.
"""

import os
import streamlit as st
from PIL import Image
from pathlib import Path

from utils.detector import load_yolo_model, detect_coconuts, resolve_model_path
from utils.grading import calculate_grade_and_summary
from utils.pricing import load_price_model, predict_market_price, calculate_market_valuation, DEFAULT_MARKET_RATES


# ============================================================
# PAGE CONFIGURATION & STYLING
# ============================================================
st.set_page_config(
    page_title="Coconut Grading & Quality Detection AI",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern polished styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a29;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4a5568;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .grade-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# PATHS & MODEL LOADING (Relative & Portable)
# ============================================================
BASE_DIR = Path(__file__).resolve().parent

YOLO_MODEL_PATH = resolve_model_path(
    str(BASE_DIR / "models" / "coconut_yolo_v3" / "weights" / "best.pt"),
    fallback_paths=[
        str(BASE_DIR / "models" / "best.pt"),
        str(BASE_DIR / "models" / "coconut_yolo.pt"),
        "/content/drive/MyDrive/Coconut-Grading-AI/models/coconut_yolo_v3/weights/best.pt",
        "/content/Coconut-Grading-AI/models/coconut_yolo_v3/weights/best.pt"
    ]
)

PRICE_MODEL_PATH = resolve_model_path(
    str(BASE_DIR / "models" / "price_prediction_model.pkl"),
    fallback_paths=[
        "/content/drive/MyDrive/Coconut-Grading-AI/models/price_prediction_model.pkl",
        "/content/Coconut-Grading-AI/models/price_prediction_model.pkl"
    ]
)


# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/coconut.png", width=64)
    st.title("Settings & Rates")
    
    st.markdown("### ⚙️ Inference Settings")
    conf_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.25,
        step=0.05,
        help="Minimum confidence for coconut bounding box detections."
    )
    
    st.divider()
    st.markdown("### 💰 Market Benchmark Rates (₹)")
    dry_rate = st.number_input(
        "Dry Mature (₹/pc)",
        value=DEFAULT_MARKET_RATES["dry"],
        step=1.0
    )
    green_rate = st.number_input(
        "Fresh Green (₹/pc)",
        value=DEFAULT_MARKET_RATES["green"],
        step=1.0
    )
    tender_rate = st.number_input(
        "Tender Water (₹/pc)",
        value=DEFAULT_MARKET_RATES["tender"],
        step=1.0
    )
    
    active_rates = {
        "dry": float(dry_rate),
        "green": float(green_rate),
        "tender": float(tender_rate)
    }
    
    st.divider()
    st.caption("Coconut-Grading-AI v3.0 | Standalone Edition")


# ============================================================
# LOAD MODELS SAFELY
# ============================================================
model = None
model_loaded = False

if os.path.exists(YOLO_MODEL_PATH):
    try:
        model = load_yolo_model(YOLO_MODEL_PATH)
        model_loaded = True
    except Exception as e:
        st.sidebar.error(f"Error loading YOLO weights: {e}")

price_model = load_price_model(PRICE_MODEL_PATH)


# ============================================================
# MAIN UI
# ============================================================
st.markdown('<div class="main-header">🥥 Coconut Grading & Quality Detection AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Automated maturity classification (Dry, Green, Tender), '
    'quality grade assessment, and batch valuation engine.</div>',
    unsafe_allow_html=True
)

if not model_loaded:
    st.warning(
        "⚠️ **YOLO Model Weights Not Detected**\n\n"
        f"Place your trained `best.pt` file into:\n"
        f"- `{BASE_DIR / 'models' / 'coconut_yolo_v3' / 'weights' / 'best.pt'}` or\n"
        f"- `{BASE_DIR / 'models' / 'best.pt'}`\n\n"
        "Once placed, reload the page to run inference."
    )

# ============================================================
# UPLOAD MODE SELECTION
# ============================================================
st.markdown("### 📤 Upload Mode")
upload_mode = st.radio(
    "Choose upload mode:",
    options=["Single Image", "Bulk Upload (Multiple Images)"],
    horizontal=True,
    help="Process one image at a time or upload and analyze multiple images in batch."
)

# ============================================================
# SINGLE IMAGE MODE
# ============================================================
if upload_mode == "Single Image":
    uploaded_file = st.file_uploader(
        "📤 Upload Coconut Batch Image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload an image of single or clustered coconuts for maturity analysis.",
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            st.subheader("🖼️ Uploaded Image")
            st.image(image, use_container_width=True)
            
        with col_right:
            st.subheader("🔍 Analysis Action")
            analyze_btn = st.button("🚀 Analyze Coconut Batch", type="primary", use_container_width=True)
            
            if analyze_btn:
                if not model_loaded:
                    st.error("Cannot perform analysis: YOLO model is not loaded.")
                else:
                    with st.spinner("Processing image through YOLO v3 model..."):
                        detection_data = detect_coconuts(
                            model=model,
                            image=image,
                            conf_threshold=conf_threshold
                        )
                        
                    plotted_image = detection_data["plotted_image"]
                    counts = detection_data["counts"]
                    total = detection_data["total"]
                    avg_conf = detection_data["average_confidence"]
                    
                    st.session_state["analysis_results"] = {
                        "plotted_image": plotted_image,
                        "counts": counts,
                        "total": total,
                        "avg_conf": avg_conf,
                        "boxes_data": detection_data["boxes_data"]
                    }

# ============================================================
# BULK UPLOAD MODE
# ============================================================
else:  # Bulk Upload Mode
    st.markdown("#### 📂 Upload Multiple Images for Batch Processing")
    uploaded_files = st.file_uploader(
        "📤 Upload Multiple Coconut Images",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        help="Upload multiple images to process them all at once and get batch statistics."
    )
    
    if uploaded_files:
        st.info(f"📊 {len(uploaded_files)} image(s) selected for processing")
        
        analyze_bulk_btn = st.button(
            "🚀 Analyze All Images (Bulk Processing)",
            type="primary",
            use_container_width=True
        )
        
        if analyze_bulk_btn:
            if not model_loaded:
                st.error("Cannot perform analysis: YOLO model is not loaded.")
            else:
                # Process all images
                all_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    try:
                        # Update progress
                        progress = (idx + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing image {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Process image
                        image = Image.open(uploaded_file).convert("RGB")
                        detection_data = detect_coconuts(
                            model=model,
                            image=image,
                            conf_threshold=conf_threshold
                        )
                        
                        all_results.append({
                            "filename": uploaded_file.name,
                            "image": image,
                            "plotted_image": detection_data["plotted_image"],
                            "counts": detection_data["counts"],
                            "total": detection_data["total"],
                            "avg_conf": detection_data["average_confidence"],
                            "boxes_data": detection_data["boxes_data"]
                        })
                    except Exception as e:
                        st.warning(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                
                status_text.text("✅ Processing complete!")
                progress_bar.empty()
                
                # Store results
                st.session_state["bulk_results"] = all_results
                st.session_state["bulk_mode"] = True
                st.success(f"✅ Successfully processed {len(all_results)}/{len(uploaded_files)} images")

    # Render analysis results if available
    if "analysis_results" in st.session_state:
        res = st.session_state["analysis_results"]
        counts = res["counts"]
        total = res["total"]
        avg_conf = res["avg_conf"]
        
        st.divider()
        st.subheader("📊 Inspection & Detection Results")
        
        # Tabs for organized view
        tab_viz, tab_grade, tab_pricing = st.tabs(["📸 Detection Overlay", "🏆 Grading & Batch Breakdown", "💰 Market Valuation"])
        
        with tab_viz:
            st.image(res["plotted_image"], channels="BGR", use_container_width=True)
            
            # Metric row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🥥 Total Detected", total)
            m2.metric("🍂 Dry (Mature)", counts["dry"])
            m3.metric("🌿 Green (Fresh)", counts["green"])
            m4.metric("💧 Tender (Water)", counts["tender"])
            
            st.caption(f"Average Detection Confidence: **{avg_conf * 100:.2f}%**")
            
        with tab_grade:
            grade_info = calculate_grade_and_summary(counts, avg_conf)
            
            # Extract grade letter (A, B, or C)
            grade_letter = grade_info['grade'].split()[1] if 'Grade' in grade_info['grade'] else '?'
            
            # Large prominent grade display
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 20px;">
                    <div style="background-color: {grade_info['badge_color']}; color: white; width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 4rem; font-weight: bold; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                        {grade_letter}
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: {grade_info['badge_color']};">
                            {grade_info['grade']}
                        </div>
                        <div style="font-size: 0.9rem; color: #666; margin-top: 8px;">
                            {grade_info['description']}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if total > 0:
                st.write("**Batch Composition Breakdown:**")
                dist = grade_info["distribution"]
                
                col_g1, col_g2, col_g3 = st.columns(3)
                with col_g1:
                    st.write(f"🍂 Dry Mature: **{dist['dry']:.1f}%** ({counts['dry']} pcs)")
                    st.progress(dist["dry"] / 100.0)
                with col_g2:
                    st.write(f"🌿 Fresh Green: **{dist['green']:.1f}%** ({counts['green']} pcs)")
                    st.progress(dist["green"] / 100.0)
                with col_g3:
                    st.write(f"💧 Tender Water: **{dist['tender']:.1f}%** ({counts['tender']} pcs)")
                    st.progress(dist["tender"] / 100.0)
                    
        with tab_pricing:
            total_val, breakdown = calculate_market_valuation(counts, active_rates)
            
            pv1, pv2 = st.columns(2)
            pv1.metric("💵 Total Estimated Batch Value", f"₹{total_val:.2f}")
            avg_unit_val = (total_val / total) if total > 0 else 0.0
            pv2.metric("🏷️ Average Unit Value", f"₹{avg_unit_val:.2f} / pc")
            
            st.write("**Itemized Price Breakdown:**")
            breakdown_data = [
                {
                    "Maturity Class": "Dry Mature",
                    "Detected Count": breakdown["dry"]["count"],
                    "Benchmark Rate (₹/pc)": f"₹{breakdown['dry']['rate']:.2f}",
                    "Subtotal (₹)": f"₹{breakdown['dry']['subtotal']:.2f}"
                },
                {
                    "Maturity Class": "Fresh Green",
                    "Detected Count": breakdown["green"]["count"],
                    "Benchmark Rate (₹/pc)": f"₹{breakdown['green']['rate']:.2f}",
                    "Subtotal (₹)": f"₹{breakdown['green']['subtotal']:.2f}"
                },
                {
                    "Maturity Class": "Tender Water",
                    "Detected Count": breakdown["tender"]["count"],
                    "Benchmark Rate (₹/pc)": f"₹{breakdown['tender']['rate']:.2f}",
                    "Subtotal (₹)": f"₹{breakdown['tender']['subtotal']:.2f}"
                }
            ]
            st.table(breakdown_data)
            
            if price_model is not None:
                rf_predicted = predict_market_price(price_model, counts, total, avg_conf)
                st.caption(f"🤖 Random Forest Prototype Model Estimate: ₹{rf_predicted:.2f}/kg")

# ============================================================
# BULK MODE RESULTS DISPLAY
# ============================================================
if "bulk_results" in st.session_state and st.session_state.get("bulk_mode"):
    bulk_results = st.session_state["bulk_results"]
    
    st.divider()
    st.subheader("📊 Bulk Processing Results")
    
    # Aggregate statistics
    total_coconuts = sum(r["total"] for r in bulk_results)
    total_dry = sum(r["counts"]["dry"] for r in bulk_results)
    total_green = sum(r["counts"]["green"] for r in bulk_results)
    total_tender = sum(r["counts"]["tender"] for r in bulk_results)
    avg_conf_all = sum(r["avg_conf"] for r in bulk_results) / len(bulk_results) if bulk_results else 0
    
    # Aggregate counts
    aggregate_counts = {
        "dry": total_dry,
        "green": total_green,
        "tender": total_tender
    }
    
    # Summary metrics
    st.markdown("#### 📈 Aggregate Summary")
    sum_m1, sum_m2, sum_m3, sum_m4, sum_m5 = st.columns(5)
    sum_m1.metric("📁 Total Images", len(bulk_results))
    sum_m2.metric("🥥 Total Coconuts", total_coconuts)
    sum_m3.metric("🍂 Total Dry", total_dry)
    sum_m4.metric("🌿 Total Green", total_green)
    sum_m5.metric("💧 Total Tender", total_tender)
    
    st.caption(f"Average Detection Confidence: **{avg_conf_all * 100:.2f}%**")
    
    # Tabs for bulk results
    tab_imgs, tab_agg_grade, tab_agg_pricing, tab_details = st.tabs(
        ["🖼️ Image Gallery", "🏆 Aggregate Grading", "💰 Aggregate Valuation", "📋 Detailed Breakdown"]
    )
    
    with tab_imgs:
        st.write("#### Processed Images with Detection Overlay")
        for idx, result in enumerate(bulk_results, 1):
            with st.expander(f"🖼️ Image {idx}: {result['filename']} ({result['total']} coconuts detected)", expanded=(idx == 1)):
                col_img_1, col_img_2 = st.columns(2)
                with col_img_1:
                    st.write("**Original Image:**")
                    st.image(result["image"], use_container_width=True)
                with col_img_2:
                    st.write("**Detection Overlay:**")
                    st.image(result["plotted_image"], channels="BGR", use_container_width=True)
                    
                # Mini metrics
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total", result["total"])
                c2.metric("Dry", result["counts"]["dry"])
                c3.metric("Green", result["counts"]["green"])
                c4.metric("Tender", result["counts"]["tender"])
    
    with tab_agg_grade:
        grade_info = calculate_grade_and_summary(aggregate_counts, avg_conf_all)
        
        # Extract grade letter (A, B, or C)
        grade_letter = grade_info['grade'].split()[1] if 'Grade' in grade_info['grade'] else '?'
        
        # Large prominent grade display
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 20px;">
                <div style="background-color: {grade_info['badge_color']}; color: white; width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 4rem; font-weight: bold; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                    {grade_letter}
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: {grade_info['badge_color']};">
                        {grade_info['grade']}
                    </div>
                    <div style="font-size: 0.9rem; color: #666; margin-top: 8px;">
                        {grade_info['description']}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if total_coconuts > 0:
            st.write("**Aggregate Batch Composition:**")
            dist = grade_info["distribution"]
            
            col_agg1, col_agg2, col_agg3 = st.columns(3)
            with col_agg1:
                st.write(f"🍂 Dry Mature: **{dist['dry']:.1f}%** ({total_dry} pcs)")
                st.progress(dist["dry"] / 100.0)
            with col_agg2:
                st.write(f"🌿 Fresh Green: **{dist['green']:.1f}%** ({total_green} pcs)")
                st.progress(dist["green"] / 100.0)
            with col_agg3:
                st.write(f"💧 Tender Water: **{dist['tender']:.1f}%** ({total_tender} pcs)")
                st.progress(dist["tender"] / 100.0)
    
    with tab_agg_pricing:
        total_val, breakdown = calculate_market_valuation(aggregate_counts, active_rates)
        
        pv1, pv2, pv3 = st.columns(3)
        pv1.metric("💵 Total Batch Value", f"₹{total_val:.2f}")
        avg_unit_val = (total_val / total_coconuts) if total_coconuts > 0 else 0.0
        pv2.metric("🏷️ Average Unit Value", f"₹{avg_unit_val:.2f} / pc")
        avg_value_per_image = (total_val / len(bulk_results)) if bulk_results else 0.0
        pv3.metric("📊 Avg Value/Image", f"₹{avg_value_per_image:.2f}")
        
        st.write("**Itemized Price Breakdown (Aggregate):**")
        breakdown_data = [
            {
                "Maturity Class": "Dry Mature",
                "Detected Count": breakdown["dry"]["count"],
                "Benchmark Rate (₹/pc)": f"₹{breakdown['dry']['rate']:.2f}",
                "Subtotal (₹)": f"₹{breakdown['dry']['subtotal']:.2f}"
            },
            {
                "Maturity Class": "Fresh Green",
                "Detected Count": breakdown["green"]["count"],
                "Benchmark Rate (₹/pc)": f"₹{breakdown['green']['rate']:.2f}",
                "Subtotal (₹)": f"₹{breakdown['green']['subtotal']:.2f}"
            },
            {
                "Maturity Class": "Tender Water",
                "Detected Count": breakdown["tender"]["count"],
                "Benchmark Rate (₹/pc)": f"₹{breakdown['tender']['rate']:.2f}",
                "Subtotal (₹)": f"₹{breakdown['tender']['subtotal']:.2f}"
            }
        ]
        st.table(breakdown_data)
        
        if price_model is not None:
            rf_predicted = predict_market_price(price_model, aggregate_counts, total_coconuts, avg_conf_all)
            st.caption(f"🤖 Random Forest Prototype Model Estimate (Aggregate): ₹{rf_predicted:.2f}/kg")
    
    with tab_details:
        st.write("#### Per-Image Analysis Details")
        
        # Create detailed table
        details_data = []
        for idx, result in enumerate(bulk_results, 1):
            grade_info = calculate_grade_and_summary(result["counts"], result["avg_conf"])
            total_val, _ = calculate_market_valuation(result["counts"], active_rates)
            
            details_data.append({
                "Image #": idx,
                "Filename": result["filename"],
                "Total Detected": result["total"],
                "Dry": result["counts"]["dry"],
                "Green": result["counts"]["green"],
                "Tender": result["counts"]["tender"],
                "Grade": grade_info["grade"],
                "Confidence": f"{result['avg_conf'] * 100:.1f}%",
                "Est. Value (₹)": f"{total_val:.2f}"
            })
        
        st.dataframe(details_data, use_container_width=True)

