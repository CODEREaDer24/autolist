import os
import openai
import base64
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai.api_key = os.getenv("OPENAI_API_KEY")

def encode_image_to_base64(filepath):
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    base64_image = encode_image_to_base64(filepath)

    # ----------- PROMPTS -----------
    single_item_prompt = """
You are a marketplace listing expert. Analyze the item in the image and generate the following:
1. A concise, accurate **title** (under 10 words).
2. A clear, honest **description** using 2–3 short sentences.
3. A realistic **price estimate in USD** based on condition, brand, and recent resale trends.

Assume the seller wants to post this on Facebook Marketplace or Kijiji. Don’t exaggerate or guess wildly — keep it grounded and helpful.
"""

    multi_item_prompt = """
There are multiple items in this image. Describe each one separately with:
1. A short title
2. Description
3. Estimated resale value
Return results as a list.
"""

    # ----------- TOGGLE PROMPT -----------
    prompt_to_use = multi_item_prompt  # change to single_item_prompt for one-object mode

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes product listings."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_to_use},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=800
    )

    output = response['choices'][0]['message']['content']
    return render_template('result.html', image_path=filename, ai_output=output)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
