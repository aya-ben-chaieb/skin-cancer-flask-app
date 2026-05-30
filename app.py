from flask import Flask, render_template, request, redirect, session, flash, url_for
import os
import numpy as np
import zipfile
import traceback

from tensorflow.keras.applications import VGG16
from tensorflow.keras import layers, Model
from tensorflow.keras.preprocessing import image

import mysql.connector
from werkzeug.utils import secure_filename
from functools import wraps


# =========================
# APP CONFIG
# =========================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_change_me")

UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# LOGIN REQUIRED DECORATOR
# =========================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# =========================
# DATABASE CONNECTION
# =========================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="skin_cancer_db"
    )


# =========================
# MODEL BUILD + LOAD
# =========================
def build_model():
    base = VGG16(weights=None, include_top=False, input_shape=(224, 224, 3))
    base.trainable = False

    x = layers.Flatten()(base.output)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    output = layers.Dense(1, activation='sigmoid')(x)

    return Model(inputs=base.input, outputs=output)


model = build_model()

MODEL_PATH = "model/vgg16_skin_cancer.keras"
EXTRACT_PATH = "model/keras_extracted"

with zipfile.ZipFile(MODEL_PATH, 'r') as z:
    z.extractall(EXTRACT_PATH)

weights_path = os.path.join(EXTRACT_PATH, "model.weights.h5")
model.load_weights(weights_path)

print("✅ Model loaded successfully!")


# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()
        db.close()

        if user:
            session["user"] = username
            flash("Login successful ✔", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials ❌", "danger")

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# =========================
# PREDICT
# =========================
@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():

    if request.method == "POST":

        try:
            name = request.form["name"]
            age = request.form["age"]
            file = request.files["image"]

            if not file or file.filename == "":
                flash("Please select an image", "warning")
                return redirect(url_for("predict"))

            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            # IMAGE PREPROCESS
            img = image.load_img(path, target_size=(224, 224))
            img = image.img_to_array(img) / 255.0
            img = np.expand_dims(img, axis=0)

            # PREDICTION
            pred = float(model.predict(img)[0][0])
            result = "Malignant" if pred > 0.5 else "Benign"

            img_url = url_for('static', filename=f'uploads/{filename}')

            # DB INSERT
            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO patients (name, age, result, probability, image_path)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, age, result, pred, img_url))

            db.commit()
            db.close()

            flash("Analysis completed ✔", "success")

            return render_template(
                "results.html",
                result=result,
                prob=round(pred * 100, 2),
                img=img_url
            )

        except Exception:
            print(traceback.format_exc())
            flash("System error ❌", "danger")
            return redirect(url_for("predict"))

    return render_template("predict.html")


# =========================
# PATIENTS
# =========================
@app.route("/patients")
@login_required
def patients():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
    data = cursor.fetchall()

    db.close()

    return render_template("patients.html", patients=data)


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("login"))


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
