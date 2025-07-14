from flask import Flask, request, render_template, redirect, url_for, session
import base64
import openai
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devsecret")

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    image = request.files.get("image")
    if not image:
        return "No image uploaded", 400

    # Save uploaded image temporarily
    ext = image.filename.split('.')[-1]
    image_id = str(uuid.uuid4()) + "." + ext
    path = os.path.join(UPLOAD_FOLDER, image_id)
    image.save(path)
    image_url = f"/{path}"

    # Rewind file before encoding
    image.seek(0)
    content_type = image.content_type
    encoded = base64.b64encode(image.read()).decode("utf-8")
    data_url = f"data:{content_type};base64,{encoded}"

    # Multi-item prompt for segmentation-style result
    prompt = (
        "You're an expert at writing resale listings. Look at the image and identify each distinct item. "
        "For each one, write:\n\n"
        "- A title\n"
        "- A short but vivid description\n"
        "- A suggested price\n\n"
        "Label them as Item 1, Item 2, etc. Make sure they are listed clearly and separately. "
        "This image may contain many different objects — treat each as a separate listing."
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]}
        ],
    )

    content = response.choices[0].message.content.strip()

    # Save response to clipboard
    history = session.get("history", [])
    history.insert(0, {"title": "Multi-item analysis", "description": content, "price": "N/A"})
    session["history"] = history[:10]

    # Render and delete image
    rendered_page = render_template("result.html", image_url=image_url, title="Multiple Items", description=content, price="See listings above")
    try:
        os.remove(path)
    except Exception as e:
        print(f"Failed to delete image: {e}")

    return rendered_page

@app.route("/clipboard")
def clipboard():
    history = session.get("history", [])
    return render_template("clipboard.html", history=history)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
