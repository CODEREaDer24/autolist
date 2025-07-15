File: main.py

from flask import Flask, request, render_template, redirect, url_for from werkzeug.utils import secure_filename import os from PIL import Image import base64 import io import uuid

app = Flask(name) UPLOAD_FOLDER = 'static/uploads' os.makedirs(UPLOAD_FOLDER, exist_ok=True) app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Fake AI segmentation for multiple items (for demo purposes)

def mock_segment_and_analyze(image_path): return [ { "title": "Vintage Kitchen Scale", "description": "A charming retro-style orange kitchen scale in working condition.", "price": "$25" }, { "title": "Transparent Glass Mugs (Set of 4)", "description": "Clear stackable mugs, perfect for tea or coffee.", "price": "$10" } ]

@app.route('/') def index(): return render_template('index.html')

@app.route('/upload', methods=['POST']) def upload(): if 'image' not in request.files: return "No file part", 400 file = request.files['image'] if file.filename == '': return "No selected file", 400

filename = secure_filename(file.filename)
unique_name = str(uuid.uuid4()) + os.path.splitext(filename)[1]
filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
file.save(filepath)

segmented_results = mock_segment_and_analyze(filepath)
image_url = url_for('static', filename=f"uploads/{unique_name}")

return render_template('result.html', image_url=image_url, items=segmented_results)

@app.route('/clipboard') def clipboard(): return render_template('clipboard.html')

if name == 'main': app.run(debug=True)

