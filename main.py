from flask import Flask, request, render_template
import base64
import openai

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/upload", methods=["POST"])
def upload():
    image = request.files.get("image")
    if not image:
        return "No image uploaded", 400

    content_type = image.content_type  # 'image/jpeg', etc.
    encoded = base64.b64encode(image.read()).decode("utf-8")
    data_url = f"data:{content_type};base64,{encoded}"

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image."},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    )

    return response.choices[0].message.content
