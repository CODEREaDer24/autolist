from flask import Flask, request, render_template
import base64
import openai
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    image = request.files.get("image")
    if not image:
        return "No image uploaded", 400

    content_type = image.content_type  # e.g. 'image/jpeg'
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

# 🔥 Required by Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
