from transformers import AutoModel

def load_gemma_model():
    model = AutoModel.from_pretrained("devMubashir/gemma-3-text-to-sql")
    return model

if __name__ == "__main__":
    model = load_gemma_model()
    print("Model loaded successfully")