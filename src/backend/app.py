from flask import Flask, jsonify, request
from flask_cors import CORS
from config import MOCK_MODE
from pipeline.preprocess import validate_image
from pipeline.disagreement import get_disagreement

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])
MODELS = [{"id": "resnet50", "name": "ResNet-50"}, {"id": "densenet121", "name": "DenseNet-121"}]

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model_loaded": False, "mock_mode": MOCK_MODE})

@app.get("/api/models")
def models():
    return jsonify(MODELS)

@app.get("/api/demo-images")
def demo_images():
    return jsonify([])  # TODO: include licensed, locally bundled RIGA samples

@app.post("/api/analyze")
def analyze():
    file = request.files.get("file")
    model = request.form.get("model", "resnet50")
    if not file:
        return jsonify({"error": "Please choose an image."}), 400
    if model not in {m["id"] for m in MODELS}:
        return jsonify({"error": "Please choose a supported model."}), 400
    try:
        validate_image(file)  # in memory; no uploads stored
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if not MOCK_MODE:
        return jsonify({"error": "Live analysis is not connected yet."}), 501
    # Clearly marked illustrative values, NOT model or Quantus output.
    return jsonify({
        "demo_mode": True,
        "prediction": {"label": "glaucoma", "confidence": 0.93, "model": model},
        "explanations": [
            {"method": key, "label": label, "image": None, "error": "Demo placeholder: no heatmap generated."}
            for key, label in [("grad_cam", "Grad-CAM"), ("integrated_gradients", "Integrated Gradients"), ("lime", "LIME")]
        ],
        "quantus": {"faithfulness": 0.81, "robustness": 0.74, "localization": 0.67, "source": "mock"},
        "expert_disagreement": get_disagreement(),
        "timing_ms": {"classify": 0, "explain": 0, "evaluate": 0}
    })

@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Image must be smaller than 10 MB."}), 413

if __name__ == "__main__":
    app.run(debug=True, port=5000)
