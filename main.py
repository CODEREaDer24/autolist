import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'static/results'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Ensure upload/result folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded.", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file.", 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)

    # Optionally: resize image for performance
    image = Image.open(filepath)
    image = image.convert("RGB")
    image.save(os.path.join(app.config['RESULT_FOLDER'], unique_name))

    # Simulate result for now (replace with AI logic)
    title = "Nike Comp-Lite Inline Skates"
    description = "Vintage Nike inline skates with aluminum frames and 76mm wheels. Great for collectors or skaters who want solid retro gear."
    price = "$85 CAD"

    return render_template('results.html',
                           image_filename=unique_name,
                           title=title,
                           description=description,
                           price=price)

@app.route('/static/results/<filename>')
def result_image(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
