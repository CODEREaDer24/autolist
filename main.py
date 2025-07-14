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

            # OpenAI Vision API
            with open(filepath, "rb") as image_file:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Identify and describe the item(s) in this image as if for a sales listing. Be specific and include a fair price estimate."
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
            lines = content.strip().split('\n')
            title = lines[0] if len(lines) > 0 else ""
            description = lines[1] if len(lines) > 1 else ""
            price = lines[2] if len(lines) > 2 else ""

            return render_template("listing.html",
                                   listing_title=title.strip(),
                                   listing_description=description.strip(),
                                   listing_price=price.strip(),
                                   image_url=url_for('static', filename=f'uploads/{filename}'))

    return render_template('upload.html')

@app.route('/clipboard')
def clipboard():
    return render_template('clipboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=10000)
