import numpy as np
from PIL import Image
import io
import random

try:
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
    from tensorflow.keras.preprocessing import image
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("WARNING: TensorFlow not found. Running in MOCK mode.")

class InferenceService:
    _model = None

    @classmethod
    def load_model(cls):
        global TF_AVAILABLE
        if TF_AVAILABLE and cls._model is None:
            # Load pre-trained MobileNetV2
            try:
                cls._model = MobileNetV2(weights='imagenet')
            except Exception as e:
                print(f"Error loading model: {e}")
                # Fallback to mock if model load fails despite TF being present
                TF_AVAILABLE = False

    @classmethod
    def predict(cls, image_bytes: bytes) -> str:
        if TF_AVAILABLE:
            if cls._model is None:
                cls.load_model()
            
            try:
                # Preprocess the image
                img = Image.open(io.BytesIO(image_bytes)).resize((224, 224))
                x = image.img_to_array(img)
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)

                # Predict
                preds = cls._model.predict(x)
                # Decode Key: top 1 result
                decoded = decode_predictions(preds, top=1)[0]
                label = decoded[0][1] # (class_name, label, score)
                return label
            except Exception as e:
                print(f"Inference error: {e}. Falling back to mock.")
                return cls.mock_predict()
        else:
            return cls.mock_predict()

    @classmethod
    def mock_predict(cls) -> str:
        # Simulate AI detection for demo/fallback purposes
        options = ['cheeseburger', 'pizza', 'green_salad', 'banana', 'granny_smith']
        return random.choice(options)
