from typing import *
import numpy as np
from onnxruntime import InferenceSession

def encode_with_bge_m3(texts: List[str], model_path: str, tokenizer_path: str) -> np.ndarray:
    print(f'Генерируем эмбедденги текстов.')
    tokenizer: InferenceSession = InferenceSession(tokenizer_path)
    model: InferenceSession = InferenceSession(model_path)

    embeddings: List[np.ndarray] = []
    for text in texts:
        inputs: Sequence[np.ndarray] = tokenizer.run(None, { "text": [text] })
        input_ids, attention_mask = inputs[0], inputs[1]
        outputs: Sequence[np.ndarray] = model.run(None, { "input_ids": input_ids, "attention_mask": attention_mask })
        embedding: np.ndarray = outputs[0][0]

        norm: np.floating[Any] = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        embeddings.append(embedding)

    result: np.ndarray = np.array(embeddings, dtype=np.float32)
    return result
