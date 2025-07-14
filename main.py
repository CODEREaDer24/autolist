# ─────────────────────────────
# SECTION 1: Setup & Imports
# ─────────────────────────────
import os
from flask import Flask, render_template, url_for

app = Flask(__name__)

# ─────────────────────────────
# SECTION 2: Routes
# ─────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/listings")
def listings():
    return render_template("listings.html")

# ─────────────────────────────
# SECTION 3: App Entry Point
# ─────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Required for Render
    app.run(host="0.0.0.0", port=port)
