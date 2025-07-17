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
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'changeme')
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

    items = []
    raw_output = ""

    try:
        with open(image_path, "rb") as img_file:
            image_b64 = base64.b64encode(img_file.read()).decode()

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You're a resale listing expert. Analyze the image and identify multiple items. "
                        "For each item, return:\n"
                        "- Title\n"
                        "- Description\n"
                        "- Estimated resale price in USD\n\n"
                        "Format like:\n"
                        "Item 1:\\nTitle: ...\\nDescription: ...\\nPrice: ...\\n\\n"
                        "Item 2:\\n..."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "There are multiple items in this image. Describe each."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                    ]
                }
            ],
            max_tokens=1000
        )

        raw_output = response.choices[0].message.content.strip()
        blocks = raw_output.split("Item ")
        for block in blocks[1:]:
            lines = block.strip().split("\n")
            title = description = price = ""
            for line in lines:
                if "Title:" in line:
                    title = line.split("Title:", 1)[1].strip()
                elif "Description:" in line:
                    description = line.split("Description:", 1)[1].strip()
                elif "Price:" in line:
                    price = line.split("Price:", 1)[1].strip()
            if title:
                items.append({"title": title, "description": description, "price": price})

    except Exception as e:
        raw_output = f"[OpenAI Error] {str(e)}"
        items = []

    return render_template("result.html", image_url=image_path, items=items, raw_output=raw_output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
