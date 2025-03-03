import os
from flask import Flask, render_template, request, send_from_directory
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io

app = Flask(__name__, template_folder='templates')

# Load the model
model = load_model('autoencoder_final.keras')

# The folder where uploaded images will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to enhance the image using the model
def enhance_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((1200, 800))  # Resize the image if it's different
    img_array = np.array(img) / 255.0  # Convert the image to an array and normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add an extra dimension to make it (1, 256, 256, 3)
    
    # Get the enhanced image using the model
    enhanced_img_array = model.predict(img_array)

    # Convert the enhanced image back to a PIL image
    enhanced_img = (enhanced_img_array[0] * 255).astype(np.uint8)
    enhanced_img = Image.fromarray(enhanced_img)

    # Save the enhanced image
    enhanced_img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'enhanced_image.jpg')
    enhanced_img.save(enhanced_img_path)

    return enhanced_img_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        # Save the uploaded image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)

        # Enhance the image
        enhanced_image_path = enhance_image(image_path)

        # Return the enhanced image to the user
        return send_from_directory(app.config['UPLOAD_FOLDER'], 'enhanced_image.jpg')

if __name__ == '__main__':
    app.run(debug=True)
