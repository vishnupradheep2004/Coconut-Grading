from pathlib import Path
from ultralytics import YOLO


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "coconut_yolo_v3"
    / "weights"
    / "best.pt"
)


# ============================================================
# EXPORT MODEL
# ============================================================

def export_model():

    print("\n" + "=" * 60)
    print("🥥 COCONUT AI - OPENVINO MODEL EXPORT")
    print("=" * 60)

    if not MODEL_PATH.exists():
        print("\n❌ YOLO model not found:")
        print(MODEL_PATH)
        return

    print("\n📦 Loading YOLO model...")
    print(f"Model: {MODEL_PATH}")

    model = YOLO(str(MODEL_PATH))

    print("\n⚡ Exporting YOLO → OpenVINO...")
    print("Please wait...")

    exported_path = model.export(
        format="openvino",
        imgsz=640
    )

    print("\n" + "=" * 60)
    print("✅ OPENVINO EXPORT COMPLETED")
    print("=" * 60)

    print(f"\n📁 Exported model:")
    print(exported_path)

    print("\nYou can now use this model for inference.")


if __name__ == "__main__":
    export_model()