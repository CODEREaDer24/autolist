from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import uuid
import time

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'defaultsecret')
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    # Placeholder: Real AI not enabled in this version
    title = "Vintage Coffee Maker"
    description = "Classic kitchen appliance with retro design and reliable function."
    price = "$25.00"

    return render_template('result.html', image_url=image_path, title=title, description=description, price=price)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
