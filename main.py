from flask import Flask, request, render_template, redirect, url_for, session
import base64
import openai
import os
from io import BytesIO
from PIL import Image
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

    # Encode for OpenAI
    content_type = image.content_type
    encoded = base64.b64encode(image.read()).decode("utf-8")
    data_url = f"data:{content_type};base64,{encoded}"

    # Prompt for better AI description
    prompt = (
        "You're a witty secondhand item copywriter. Describe everything you can see in this image "
        "as if you’re writing a Facebook Marketplace listing. Be detailed, specific, and add a little character. "
        "Include a title, a clear description, and a suggested price."
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

    content = response.choices[0].message.content

    # Parse result
    title = content.split("\n")[0].replace("Title:", "").strip()
    description = ""
    price = ""

    for line in content.split("\n")[1:]:
        if line.lower().startswith("description:"):
            description = line.replace("Description:", "").strip()
        elif line.lower().startswith("price:") or line.lower().startswith("suggested price:"):
            price = line.replace("Price:", "").replace("Suggested Price:", "").strip()
        else:
            description += " " + line.strip()

    # Add to session clipboard
    history = session.get("history", [])
    history.insert(0, {"title": title, "description": description, "price": price})
    session["history"] = history[:10]

    # Render HTML first (so image still loads), then delete file
    rendered_page = render_template("result.html", image_url=image_url, title=title, description=description, price=price)

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
