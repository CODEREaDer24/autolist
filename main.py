# ─────────────────────────────
# SECTION 1: Setup & Imports
# ─────────────────────────────
import os
import openai
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# ─────────────────────────────
# SECTION 2: Routes
# ─────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/listings")
def listings():
    return render_template("listings.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if 'image' not in request.files:
            return "No file part"
        file = request.files['image']
        if file.filename == '':
            return "No selected file"
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        # Send image to OpenAI
        with open(path, "rb") as img:
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe this item like a Kijiji listing, including a title, description, and suggested price."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img.read().encode('base64').decode()}" }}
                    ]}
                ],
                max_tokens=300
            )

        listing = response.choices[0].message.content
        return render_template("result.html", listing=listing, image_url=url_for('static', filename=f'uploads/{filename}'))

    return render_template("upload.html")

# ─────────────────────────────
# SECTION 3: App Entry Point
# ─────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
