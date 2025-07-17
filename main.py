from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from openai import OpenAI
import os
import uuid
import time
from PIL import Image
import base64
from io import BytesIO

# === App Setup ===
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'changeme')
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === OpenAI Setup ===
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No image uploaded", 400

    image = request.files['image']
    if image.filename == '':
        return "No file selected", 400

    filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)

    session['image_path'] = filepath
    return redirect(url_for('loading'))

@app.route('/loading')
def loading():
    time.sleep(2)
    return redirect(url_for('result'))

@app.route('/result')
def result():
    image_path = session.get('image_path')
    if not image_path:
        return redirect(url_for('index'))

    raw_output = ""
    title = "Unknown Item"
    description = ""
    price = ""

    try:
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a resale listing assistant. Return only:\n1. Title\n2. Description\n3. Price in USD."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the item in this image and suggest a resale price."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]
                }
            ],
            max_tokens=300
        )

        raw_output = response.choices[0].message.content.strip()
        lines = raw_output.split("\n")

        title = next((line.split(":", 1)[1].strip() for line in lines if "title" in line.lower()), title)
        description = next((line.split(":", 1)[1].strip() for line in lines if "description" in line.lower()), description)
        price = next((line.split(":", 1)[1].strip() for line in lines if "price" in line.lower()), price)

    except Exception as e:
        raw_output = f"[OpenAI Error] {str(e)}"
        description = "Could not analyze image. Please try again or check the format."

    return render_template(
        'result.html',
        image_url=image_path,
        title=title,
        description=description,
        price=price,
        raw_output=raw_output
    )

# === Launch App ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
