File: main.py

from flask import Flask, request, render_template, redirect, url_for from werkzeug.utils import secure_filename import os from PIL import Image import base64 import io

app = Flask(name) UPLOAD_FOLDER = 'static/uploads' os.makedirs(UPLOAD_FOLDER, exist_ok=True) app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Replace with your actual OpenAI API call later

def fake_ai_analysis(image_path): return { "title": "Vintage Kitchen Scale", "description": "A charming retro-style orange kitchen scale in working condition.", "price": "$25" }

@app.route('/') def index(): return render_template('index.html')

@app.route('/upload', methods=['POST']) def upload(): if 'image' not in request.files: return "No file part", 400 file = request.files['image'] if file.filename == '': return "No selected file", 400

filename = secure_filename(file.filename)
filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
file.save(filepath)

result = fake_ai_analysis(filepath)
image_url = url_for('static', filename=f"uploads/{filename}")

return render_template('result.html', image_url=image_url, **result)

@app.route('/clipboard') def clipboard(): return render_template('clipboard.html')

if name == 'main': app.run(debug=True)

