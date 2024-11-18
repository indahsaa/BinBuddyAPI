import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import io
import tensorflow as tf
import keras
import numpy as np
from PIL import Image

from flask import Flask, request, jsonify

model = keras.models.load_model("./model/efficientnetv2_b2_t1.keras")

def transform_image(pillow_image):
    data = np.asarray(pillow_image)
    data = np.float32((data / 127.5) - 1)
    data = np.expand_dims(data, axis=0)

    data = keras.layers.Resizing(256, 256, pad_to_aspect_ratio=True)(data)
    data = keras.layers.CenterCrop(224, 224)(data)
    return data

def predict(data):
    class_names = ['battery', 'biological', 'brown-glass', 
                   'cardboard', 'clothes', 'green-glass', 
                   'metal', 'paper', 'plastic', 
                   'shoes', 'trash', 'white-glass']
    predictions = model.predict(data)
    prediction_sort = np.argsort(predictions[0])[::-1]
    prediction_confidence = predictions[0][prediction_sort]

    result_list = []
    for i in range(len(class_names)):
        result_dict = {
            "class_name": class_names[prediction_sort[i]],
            "probability": round(float(prediction_confidence[i]), 4)
        }
        result_list.append(result_dict)
        
    return result_list

app = Flask(__name__)

@app.route("/show", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get('file')
        if file is None or file.filename == "":
            return jsonify({"error": "no file"})

        try:
            image_bytes = file.read()
            pillow_img = Image.open(io.BytesIO(image_bytes))
            tensor = transform_image(pillow_img)
            prediction = predict(tensor)
            return jsonify(prediction)
        except Exception as e:
            return jsonify({"error": str(e)})

    return "OK"

@app.route("/<class_name>", methods=["POST"])
def get_class_probability(class_name):
    file = request.files.get('file')
    if file is None or file.filename == "":
        return jsonify({"error": "no file"})

    try:
        # Transform image
        image_bytes = file.read()
        pillow_img = Image.open(io.BytesIO(image_bytes))
        tensor = transform_image(pillow_img)

        # Predict
        prediction = predict(tensor)

        # Find the requested class
        for result in prediction:
            if result["class_name"] == class_name:
                return jsonify(result)

        # If class not found
        return jsonify({"error": f"Class '{class_name}' not found in predictions"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
