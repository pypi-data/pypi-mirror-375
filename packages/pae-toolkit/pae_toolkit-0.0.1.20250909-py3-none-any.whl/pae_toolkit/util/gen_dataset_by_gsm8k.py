import json
from pathlib import Path

from tqdm import tqdm
from transformers import AutoTokenizer


def gen_dataset_by_gsm8k(
    batch_size: int,
    input_len: int,
    dataset_path: str,
    model_path: str,
    output_dir="./output",
):
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = [str(json.loads(line)["question"]) for line in f]
    output_dir = Path(output_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # repeat input_len
    def ex(sentence: str):
        words = tokenizer.tokenize(sentence)
        if len(words) == 0:
            return None
        len_num = len(words) // input_len
        if len_num == 0:
            multiplier = (input_len // len(words)) + 1
            repeated_len = words * multiplier
            words = repeated_len[:input_len]
        else:
            words = words[:input_len]
        return tokenizer.convert_tokens_to_string(words)

    if len(dataset) < batch_size:
        dataset = dataset * ((batch_size // len(dataset)) + 1)
    dataset = dataset[:batch_size]

    save_path = output_dir / f"gsm8k-in{input_len}-bs{batch_size}.jsonl"
    open(save_path, "w", encoding="utf-8").close()
    with tqdm(dataset, desc=f"Gen dataset to {save_path}") as data_list:
        for sentence in data_list:
            decoded_text = ex(sentence)
            if decoded_text is not None:
                with open(save_path, "a+", encoding="utf-8") as f:
                    f.write(json.dumps({"question": decoded_text, "answer": ""}, ensure_ascii=False) + "\n")


def process_txt2gsm8k(dataset_path: str):
    import json

    with open("output/测试小说.txt", "r", encoding="utf-8") as f:
        contents = f.readlines()

    contents = [text.strip() for text in contents]
    content = "\n".join(contents)[:131072]

    with open(dataset_path, "w") as f:
        for _ in range(10):
            f.write(json.dumps({"question": content, "answer": ""}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    process_txt2gsm8k("./sm.jsonl")
    gen_dataset_by_gsm8k(20, 20480, "./sm.jsonl", "/mnt/d/weights/Qwen3-8B")
