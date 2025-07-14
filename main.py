from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from openai import OpenAI

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenAI setup
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # OpenAI Vision Prompt
            with open(filepath, "rb") as image_file:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Identify the main item in this image for resale. Give a one-line title, a two-sentence description, and a fair estimated price in USD."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"attachment://{filename}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=300,
                    temperature=0.7
                )

            content = response.choices[0].message.content or ""
            lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
            title = lines[0] if len(lines) > 0 else "Untitled"
            description = lines[1] if len(lines) > 1 else "No description available."
            price = lines[2] if len(lines) > 2 else "N/A"

            return render_template("listing.html",
                                   listing_title=title,
                                   listing_description=description,
                                   listing_price=price,
                                   image_url=url_for('static', filename=f'uploads/{filename}'))

    return render_template('upload.html')

@app.route('/clipboard')
def clipboard():
    return render_template('clipboard.html')

# Use correct port binding for Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
