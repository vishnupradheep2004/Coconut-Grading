# Coconut Grading & Quality Detection AI

A computer vision application that detects coconut maturity classes (`Dry`, `Green`, `Tender`), assigns a quality grade, and estimates market valuation.

## Directory Layout
```
finalp/
├── app.py                             # Main Streamlit web application
├── requirements.txt                   # Python dependencies
├── README.md                          # Documentation & guide
├── utils/                             # Modular backend package
│   ├── __init__.py
│   ├── detector.py                    # YOLO inference & box extraction
│   ├── grading.py                     # Grading calculation
│   └── pricing.py                     # Price model inference
├── models/                            # Model weights directory
│   ├── coconut_yolo_v3/
│   │   └── weights/                   # Location for best.pt
│   └── price_prediction_model.pkl     # Trained Random Forest Regressor
└── Coconut_Grading_AI (1).ipynb       # Original exploration notebook
```

## Model Weights Placement
To run the application locally, place your trained model files in:
1. **YOLO V3 Weights:** `models/coconut_yolo_v3/weights/best.pt` (or `models/best.pt`)
2. **Price Model:** `models/price_prediction_model.pkl`

## Setup & Execution
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
