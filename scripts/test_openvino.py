from pathlib import Path
from ultralytics import YOLO
import time


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "coconut_yolo_v3"
    / "weights"
    / "best_openvino_model"
)


# ============================================================
# TEST
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("🥥 COCONUT AI - OPENVINO DETECTION TEST")
    print("=" * 60)

    if not MODEL_PATH.exists():
        print("\n❌ OpenVINO model not found:")
        print(MODEL_PATH)
        return

    print("\n📦 Loading OpenVINO model...")
    print(MODEL_PATH)

    model = YOLO(str(MODEL_PATH))

    print("\n✅ OpenVINO model loaded successfully!")

    print("\nModel classes:")

    for class_id, class_name in model.names.items():
        print(f"  {class_id}: {class_name}")

    print("\n" + "=" * 60)
    print("MODEL READY")
    print("=" * 60)

    print("\nNow we need an image to test detection.")

    image_path = input(
        "\nEnter the path of a coconut image: "
    ).strip().strip('"')

    if not Path(image_path).exists():
        print("\n❌ Image not found:")
        print(image_path)
        return

    print("\n🔍 Running OpenVINO inference...")

    start_time = time.perf_counter()

    results = model.predict(
        source=image_path,
        imgsz=640,
        conf=0.25,
        device="intel:cpu",
        verbose=False,
        save=True
    )

    elapsed = time.perf_counter() - start_time

    result = results[0]

    print("\n" + "=" * 60)
    print("✅ DETECTION COMPLETE")
    print("=" * 60)

    print(f"\n⏱️ Inference time: {elapsed:.3f} seconds")

    if result.boxes is None or len(result.boxes) == 0:

        print("\n⚠️ No coconuts detected.")

    else:

        print(
            f"\n🥥 Coconuts detected: "
            f"{len(result.boxes)}"
        )

        print("\nDetection details:")

        for i, box in enumerate(result.boxes):

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = result.names[class_id]

            print(
                f"  {i + 1}. "
                f"{class_name} "
                f"→ {confidence:.2%}"
            )

    print("\n📁 Annotated result was saved by Ultralytics.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()