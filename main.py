# ─────────────────────────────
# SECTION 1: Setup & Imports
# ─────────────────────────────
import os
import base64
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
    return redirect(url_for('upload'))

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

        # Convert image to base64
        with open(path, "rb") as img:
            base64_image = base64.b64encode(img.read()).decode("utf-8")

        # Send to OpenAI Vision
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Describe this item like a Kijiji listing. Return ONLY the following:\n\nTitle:\nDescription:\nPrice:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=300
        )

        content = response.choices[0].message.content
        title = extract_between(content, "Title:", "Description:")
        description = extract_between(content, "Description:", "Price:")
        price = content.split("Price:")[-1].strip()

        return render_template("result.html",
                               listing_title=title.strip(),
                               listing_description=description.strip(),
                               listing_price=price.strip(),
                               image_url=url_for('static', filename=f'uploads/{filename}'))

    return render_template("upload.html")

# Helper function
def extract_between(text, start, end):
    try:
        return text.split(start)[1].split(end)[0]
    except:
        return ""

# ─────────────────────────────
# SECTION 3: App Entry Point
# ─────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
