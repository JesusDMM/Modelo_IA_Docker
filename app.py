from flask import Flask, request, jsonify
from PIL import Image
from flask_cors import CORS
from io import BytesIO
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

app = Flask(__name__)
CORS(app)

modelo = tf.keras.models.load_model('modelo/Modelo_EfficientNetV2B0_cana.keras')

def preprocess_image(image, target_size):
    img_array = np.array(image)
    
    img_array = tf.image.resize(img_array, target_size)
    
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

@app.route('/api/modelo_cana/v1.0/diagnostico', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Error general"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No seleccionaste un archivo"}), 400
    
    if file:
        img = Image.open(file.stream)
        img = img.convert("RGB")
        
        imagen_preprocesada = preprocess_image(img, target_size=(493, 493))
        predicciones = modelo.predict(imagen_preprocesada)
        clase_predicha = np.argmax(predicciones, axis=1)
        clases = ['Healthy', 'Mosaic', 'RedRot', 'Rust', 'Yellow']
        enfermedad = clases[clase_predicha[0]]
        porcentaje = round(float(np.max(predicciones)) * 100, 2)
        
        return jsonify({"message": enfermedad,
                        "porcentaje": porcentaje}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)