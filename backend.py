from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import re

app = Flask(__name__)
CORS(app)

genai.configure(api_key="key_here")

model = genai.GenerativeModel("gemini-2.5-flash")

def extract_fields(text):
    # Extract classification
    classification_match = re.search(r"[Cc]lassification[:\- ]+(.*)", text)
    classification = classification_match.group(1).strip() if classification_match else "Unknown"

    # Extract confidence
    conf_match = re.search(r"[Cc]onfidence[:\- ]+(\d+)", text)
    confidence = conf_match.group(1).strip() if conf_match else "N/A"

    # Extract explanation
    exp_match = re.search(r"[Ee]xplanation[:\- ]+(.*)", text)
    explanation = exp_match.group(1).strip() if exp_match else "No explanation."

    # Extract fact-checking
    fc_match = re.search(r"[Ff]act.*[:\- ]+(.*)", text)
    factcheck = fc_match.group(1).strip() if fc_match else "No sources provided."

    return classification, confidence, explanation, factcheck


@app.route("/analyze", methods=["POST"])
def analyze():
    user_text = request.json.get("text", "")

    prompt = f"""
    Analyze whether the following statement is fake or real:

    "{user_text}"

    Respond strictly in this format:
    Classification: <Fake/Real/Uncertain>
    Confidence: <0-100>
    Explanation: <short explanation>
    Fact-check: <sources or known info>
    """

    result = model.generate_content(prompt)
    raw = result.text

    # Extract structured data
    classification, confidence, explanation, factcheck = extract_fields(raw)

    return jsonify({
        "classification": classification,
        "confidence": confidence,
        "explanation": explanation,
        "factCheck": factcheck,
        "raw_model_output": raw  # for debugging
    })


if __name__ == "__main__":
    app.run(port=5000)

