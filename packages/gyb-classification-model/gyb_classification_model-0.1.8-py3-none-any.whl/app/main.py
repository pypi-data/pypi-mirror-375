from gyb_classification_model import predictor

def predict_category(text):
    category = predictor.predict_text(text)
    return category