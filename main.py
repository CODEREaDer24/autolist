from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from openai import OpenAI
import os
import uuid
import time
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'defaultsecret')
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No image part", 400

    image = request.files['image']
    if image.filename == '':
        return "No selected file", 400

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

    try:
        # Convert image to base64
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()

        # Call OpenAI GPT-4o Vision
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resale assistant. Return only:\n1. Title\n2. Description\n3. Estimated resale price in USD."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What item is in this image? Describe it and suggest a resale price."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]
                }
            ],
            max_tokens=300
        )

        ai_text = response.choices[0].message.content.strip()

        # Very basic extraction
        lines = ai_text.split("\n")
        title = next((line.split(":", 1)[1].strip() for line in lines if "title" in line.lower()), "Unknown Item")
        description = next((line.split(":", 1)[1].strip() for line in lines if "description" in line.lower()), "")
        price = next((line.split(":", 1)[1].strip() for line in lines if "price" in line.lower()), "")

    except Exception as e:
        title = "Error generating title"
        description = f"AI failed: {str(e)}"
        price = "N/A"

    return render_template('result.html', image_url=image_path, title=title, description=description, price=price)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
