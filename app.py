
from flask import Flask, render_template, request, redirect, session, flash
import os
import numpy as np
import zipfile
from tensorflow.keras.applications import VGG16
from tensorflow.keras import layers, Model
from tensorflow.keras.preprocessing import image
import mysql.connector
import tensorflow as tf
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "secret"

# Upload folder
UPLOAD_FOLDER = "static/uploads/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ──────────────────────────────────────────
# Rebuild model + load weights
# ──────────────────────────────────────────
def build_model():
    base = VGG16(weights=None, include_top=False, input_shape=(224, 224, 3))
    base.trainable = False
    x = layers.Flatten()(base.output)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    output = layers.Dense(1, activation='sigmoid')(x)
    return Model(inputs=base.input, outputs=output)

model = build_model()

# Extract weights from the .keras zip and load them
with zipfile.ZipFile("model/vgg16_skin_cancer.keras", 'r') as z:
    z.extractall("model/keras_extracted")
    print("📦 Files inside .keras:", z.namelist())

model.load_weights("model/keras_extracted/model.weights.h5")
print("✅ Model loaded successfully!")
# ──────────────────────────────────────────

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="skin_cancer_db"
)
cursor = db.cursor(dictionary=True)


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (user, pwd)
        )
        result = cursor.fetchone()

        if result:
            session["user"] = user
            flash("Login réussi ✔", "success")
            return redirect("/dashboard")
        else:
            flash("Erreur login ❌", "danger")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")


# ---------------- PREDICT ----------------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        try:
            name = request.form["name"]
            age = request.form["age"]
            file = request.files["image"]

            if file.filename == "":
                flash("Veuillez choisir une image", "warning")
                return redirect("/predict")

            # Secure the filename and ensure upload folder exists
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            # Save file
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            # Preprocess image
            img = image.load_img(path, target_size=(224, 224))
            img = image.img_to_array(img) / 255.0
            img = np.expand_dims(img, axis=0)

            # Prediction
            pred = model.predict(img)[0][0]
            result = "Malignant" if pred > 0.5 else "Benign"

            # URL path for browser (not filesystem path)
            img_url = "/" + path.replace("\\", "/")  # handles Windows too

            # Insert into DB — store the URL path, not filesystem path
            cursor.execute("""
                INSERT INTO patients (name, age, result, probability, image_path)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, age, result, float(pred), img_url))
            db.commit()

            flash("Analyse réussie ✔", "success")

            return render_template(
                "results.html",
                result=result,
                prob=round(pred * 100, 2),
                img_path=img_url   # ← now a proper URL
            )

        except Exception as e:
            import traceback
            traceback.print_exc()   # ← prints the FULL error to console
            flash(f"Erreur système ❌: {str(e)}", "danger")
            return redirect("/predict")

    return render_template("predict.html")
# ---------------- PATIENTS ----------------
@app.route("/patients")
def patients():
    if "user" not in session:
        return redirect("/")
    cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
    data = cursor.fetchall()
    return render_template("patients.html", patients=data)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté", "info")
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True) 