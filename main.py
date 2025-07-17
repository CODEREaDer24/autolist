from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from openai import OpenAI
import os
import base64
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'defaultsecret')

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

    filename = secure_filename(image.filename)
    filepath = os.path.join('static/uploads', filename)
    image.save(filepath)

    # Placeholder for AI logic
    title = "Generated Title"
    description = "Generated Description"
    price = "$9.99"

    return render_template('results.html', image_url=filepath, title=title, description=description, price=price)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
