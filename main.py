from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from openai import OpenAI
import os
import base64
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Use API key from environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clipboard')
def clipboard():
    return render_template('clipboard.html')

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('index'))

    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))

    filename = secure_filename(str(uuid.uuid4()) + '_' + file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'rb') as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')

    prompt = {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            },
            {
                "type": "text",
                "text": "There are multiple items in this image. Describe each one separately with: 1. A short title, 2. Description, 3. Estimated resale value. Return results as a list."
            }
        ]
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[prompt],
            max_tokens=1500
        )
        result_text = response.choices[0].message.content.strip()

    except Exception as e:
        result_text = f"Error analyzing image: {e}"

    return render_template('result.html', result=result_text, image_url=filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
