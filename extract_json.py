import os
import re
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
embedding_manager = EmbeddingManager(backend="minilm")  # or "gemini"
def clean_text(text: str) -> str:
    # Remove emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport
        "\U0001F1E0-\U0001F1FF"  # Flags
        "\U00002700-\U000027BF"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub('', text)

    # Remove markdown
    markdown_pattern = re.compile(r'[*_`#>~\-]{1,}', flags=re.UNICODE)
    text = markdown_pattern.sub('', text)

    return text.strip()

def load_chat_log(filename="chats.json", log_dir="./extract", limit=None):
    file_path = Path(log_dir) / filename
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            cleaned = []
            for entry in data:
                mapping = entry.get("mapping", {})
                for node in mapping.values():
                    msg = node.get("message")
                    if not msg:
                        continue

                    role = msg.get("author", {}).get("role", "")
                    ts = msg.get("create_time")
                    parts = msg.get("content", {}).get("parts", [])

                    for part in parts:
                        if isinstance(part, str):
                            text = clean_text(part)
                            if text:
                                cleaned.append({
                                    "role": "Moti" if role == "user" else "Ray" if role == "assistant" else role,
                                    "text": text,
                                    "timestamp": datetime.utcfromtimestamp(ts).isoformat() if ts else None
                                })

                                if limit and len(cleaned) >= limit:
                                    return cleaned
            return cleaned
        else:
            print(f"⚠️ Unexpected structure in file: {file_path}")
            return []

    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return []

def export_clean_chat_log(logs, out_basename="cleaned_chat_log"):
    with open(f"{out_basename}.jsonl", "w", encoding="utf-8") as f:
        for entry in logs:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    with open(f"{out_basename}.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["role", "text", "timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in logs:
            writer.writerow(row)

    print(f"✅ Exported {len(logs)} entries to {out_basename}.jsonl and .csv")

# 🚀 MAIN
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and clean chat logs.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of chat entries to extract")
    parser.add_argument("--filename", type=str, default="chats.json", help="Input file name")
    parser.add_argument("--log_dir", type=str, default="./extract", help="Directory containing the chat log")
    parser.add_argument("--output", type=str, default="cleaned_chat_log", help="Base name for output files")

    args = parser.parse_args()

    log_data = load_chat_log(filename=args.filename, log_dir=args.log_dir, limit=args.limit)
    export_clean_chat_log(log_data, out_basename=args.output)
