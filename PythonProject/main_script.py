import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, \
    PreTrainedTokenizer
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
import matplotlib.pyplot as plt
import torch
from transformers import TrainerCallback
from onnxruntime import InferenceSession

from DataSetSource import *

class LRFinderCallback(TrainerCallback):
    def __init__(self, start_lr=1e-7, end_lr=1e-2, num_iter=100):
        self.start_lr = start_lr
        self.end_lr = end_lr
        self.num_iter = num_iter
        self.step_count = 0
        self.lrs = []
        self.losses = []

    def on_step_end(self, args, state, control, **kwargs):
        if self.step_count < self.num_iter:
            # Вычисляем LR
            lr = self.start_lr * (self.end_lr / self.start_lr) ** (self.step_count / self.num_iter)
            # Устанавливаем LR для оптимизатора
            if hasattr(kwargs.get('model'), 'optimizer'):
                for param_group in kwargs['model'].optimizer.param_groups:
                    param_group['lr'] = lr
            else:
                # Альтернатива: получаем модель и оптимизатор через trainer
                # Это может не сработать напрямую — смотри ниже
                pass

            # Сохраняем LR и loss (loss нужно получать через on_log)
            self.lrs.append(lr)
            # loss пока неизвестен, см. on_log

            self.step_count += 1

            if self.step_count >= self.num_iter:
                self.plot()

    def on_log(self, args, state, control, logs=None, **kwargs):
        if len(self.losses) < len(self.lrs):  # синхронизация с LR
            self.losses.append(logs.get('loss', float('inf')))

    def plot(self):
        if len(self.lrs) == len(self.losses):
            plt.figure(figsize=(10, 6))
            plt.plot(self.lrs, self.losses)
            plt.xscale('log')
            plt.xlabel('Learning Rate (log scale)')
            plt.ylabel('Loss')
            plt.title('Learning Rate Finder')
            plt.grid()
            plt.show()
        else:
            print("Warning: lrs and losses have different lengths.")

class EngineTypeDataset(Dataset):
    def __init__(self, encodings, label_ids):  # ← ожидаем уже числа
        self.encodings = encodings
        self.label_ids = label_ids

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.label_ids[idx], dtype=torch.long)  # ← числа
        return item

    def __len__(self):
        return len(self.label_ids)

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    accuracy = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average='weighted')
    return {
        'accuracy': accuracy,
        'f1': f1,
    }

def main():
    max_length = 256

    print(f'cuda is available {torch.cuda.is_available()}')

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # данные
    dataset: list[tuple[str, str]] = create_engine_type_dataset()
    model_name = "ai-forever/ruBert-base"
    onnx_output = "engine_classifier.onnx"

    labels = sorted(list(set(label for _, label in dataset)))
    label_to_id = {label: i for i, label in enumerate(labels)}
    id_to_label = {i: label for label, i in label_to_id.items()}
    print(f'Метки: {labels}')
    print(f'Количество примеров: {len(dataset)}')

    texts, text_labels = zip(*dataset)
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, text_labels, test_size=0.2, random_state=42, stratify=text_labels
    )
    print(f'Размер тренировочной выборки: {len(train_texts)}')
    print(f'Размер валидационной выборки: {len(val_texts)}')

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_encodings = tokenizer(list(train_texts), truncation=True, padding=True, max_length=max_length)
    val_encodings = tokenizer(list(val_texts), truncation=True, padding=True, max_length=max_length)

    train_label_ids = [label_to_id[label] for label in train_labels]
    val_label_ids = [label_to_id[label] for label in val_labels]

    train_dataset = EngineTypeDataset(train_encodings, train_label_ids)
    val_dataset = EngineTypeDataset(val_encodings, val_label_ids)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(labels),
        id2label=id_to_label,
        label2id=label_to_id,
    )

    model.to(device)

    batch_size = 16
    gradient_accumulation_steps = 2
    num_train_epochs = 3

    steps_per_epoch = len(train_dataset) // batch_size
    total_steps = steps_per_epoch * num_train_epochs
    warmup_steps = min(5000, int(0.05 * total_steps))  # 10% от общего
    print(f'Приблизительное количество шагов за эпоху: {steps_per_epoch}')
    print(f'Приблизительное общее количество шагов: {total_steps}')
    print(f'Warmup_steps: {warmup_steps}')

    # если с колбеком, тогда надо ставить эпоху в 1.
    # lr_finder_callback = LRFinderCallback(start_lr=1e-7, end_lr=1e-2, num_iter=100)

    # для теста разных лернинг рейтов
    # lrs_to_test = [5e-6, 1e-5, 2e-5, 3e-5]
    # for lr in lrs_to_test:
    #     print(f"\n--- Testing LR: {lr} ---")
    #     training_args = TrainingArguments(
    #         output_dir=f'./results_{lr}',
    #         num_train_epochs=2,
    #         learning_rate=lr,
    #         per_device_train_batch_size=16,
    #         gradient_accumulation_steps=2,
    #         warmup_steps=5000,
    #         weight_decay=0.01,
    #         logging_steps=50,
    #         eval_strategy="epoch",
    #         save_strategy="epoch",
    #         load_best_model_at_end=True,
    #         metric_for_best_model="eval_f1",
    #         greater_is_better=True,
    #         fp16=True,
    #         dataloader_num_workers=4,
    #         report_to=None,
    #     )
    #     trainer = Trainer(
    #         model=model,
    #         args=training_args,
    #         train_dataset=train_dataset,
    #         eval_dataset=val_dataset,
    #         compute_metrics=compute_metrics
    #     )
    #     trainer.train()


    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=num_train_epochs,
        learning_rate=7e-6, # попробовать 7e-06 или 8e-06 | старый был 1e-5
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=64,
        warmup_steps=warmup_steps,
        gradient_accumulation_steps=gradient_accumulation_steps,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=100,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_f1",
        greater_is_better=True,
        fp16=True,
        dataloader_num_workers=4,
        report_to=None,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )

    trainer.train()
    export_to_onnx(model, tokenizer, onnx_output, max_length)

    test_text = "Двигатель дизельный, мощность 200 л.с."
    predicted_label, logits = predict_onnx(
        text=test_text,
        tokenizer=tokenizer,
        onnx_path=onnx_output,
        id_to_label=id_to_label,
        threshold=0.65,
        max_length=max_length,
    )
    print(f"\nТест: '{test_text}' → Предсказание: {predicted_label}")
    print(f"Логиты: {logits}")

def export_to_onnx(model, tokenizer: PreTrainedTokenizer, output_path: str, max_length):
    model = model.cpu()
    model.eval()
    dummy_input = tokenizer(
        "Пример текста для двигателя",
        return_tensors="pt",
        padding="max_length",
        max_length=max_length,
        truncation=True
    )

    torch.onnx.export(
        model,
        (dummy_input["input_ids"], dummy_input["attention_mask"]),
        output_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence"},
            "attention_mask": {0: "batch_size", 1: "sequence"},
            "logits": {0: "batch_size"}
        },
        opset_version=18,  # Увеличена версия opset
        do_constant_folding=True,
        export_params=True
        # op_level_debug убран
    )
    print(f"Модель экспортирована в {output_path}")


def predict_onnx(text: str, tokenizer, onnx_path: str, id_to_label: dict, threshold=0.65, max_length: int=256):
    inputs = tokenizer(
        text,
        return_tensors="np",
        padding="max_length",
        max_length=max_length,
        truncation=True
    )
    ort_session = InferenceSession(onnx_path)
    ort_inputs = {
        "input_ids": inputs["input_ids"].astype(np.int64),
        "attention_mask": inputs["attention_mask"].astype(np.int64)
    }
    logits = ort_session.run(None, ort_inputs)[0][0]

    # Softmax
    exp_logits = np.exp(logits - np.max(logits))  # стабильность
    probs = exp_logits / np.sum(exp_logits)
    max_prob = np.max(probs)
    pred_id = int(np.argmax(logits))

    if max_prob < threshold:
        return "неизвестно", logits
    return id_to_label[pred_id], logits

if __name__ == '__main__':
    main()
