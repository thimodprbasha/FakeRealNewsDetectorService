import os
from transformers import TFAutoModelForSequenceClassification, AutoTokenizer
import numpy as np
import json
from tqdm import tqdm


model_path = "model"
CLASS_NAMES = ["Fake", "Real"]
mode_file = ["config.json", "tf_model.h5"]
bert_name = "bert-base-uncased"


def load_test_data():
    with open("data/test_data.json", "r") as f:
        return json.load(f)


def detect_real_or_fake_news(data):
    if os.path.exists(model_path):
        for file in mode_file:
            if not os.path.isfile(os.path.join(model_path, file)):
                raise FileNotFoundError(f"No such model file : '{file}'")
    else:
        raise FileNotFoundError(f"No such model directory : '{model_path}'")

    return_objs = {
        "result": [],
    }

    tokenizer = AutoTokenizer.from_pretrained(
        bert_name,
        padding="max_length",
        do_lower_case=True,
        add_special_tokens=True,
    )

    model = TFAutoModelForSequenceClassification.from_pretrained("model")

    for _, data in tqdm(enumerate(data)):
        tokens = tokenizer(
            data["text"], return_tensors="tf", padding="max_length", truncation=True
        ).input_ids

        pred = np.abs(np.round(model.predict(tokens, verbose=0).logits))

        result_data = {
            "id": data["id"],
            "text": data["text"],
            "predicted_class": CLASS_NAMES[int(pred)],
        }

        return_objs["result"].append(result_data)
    return return_objs


if __name__ == "__main__":
    data = load_test_data()
    detect_real_or_fake_news(data)
