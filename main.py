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
    time.sleep(1.5)
    return redirect(url_for('result'))

@app.route('/result')
def result():
    image_path = session.get('image_path')
    if not image_path:
        return redirect(url_for('index'))

    # Convert image to base64 for OpenAI vision input
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()

    # Send image and prompt to OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You're an expert resale listing assistant. Describe items clearly and suggest prices based on typical used values."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this item with:\n1. A short title\n2. A concise description\n3. An estimated resale price"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]
                }
            ],
            max_tokens=300
        )

        # Extract structured text
        ai_text = response.choices[0].message.content.strip()
        lines = ai_text.split("\n")
        title = lines[0].split(":", 1)[1].strip() if "Title" in lines[0] else "Unknown Item"
        description = lines[1].split(":", 1)[1].strip() if "Description" in lines[1] else ""
        price = lines[2].split(":", 1)[1].strip() if "Price" in lines[2] else ""

    except Exception as e:
        title = "Error generating title"
        description = f"AI failed: {e}"
        price = "N/A"

    return render_template('result.html', image_url=image_path, title=title, description=description, price=price)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
