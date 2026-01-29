import json
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('files', nargs='+', help='JSON files to merge')
parser.add_argument('--output', default='merged_data.json', help='Output file')
args = parser.parse_args()

merged = {}

for file_path in args.files:
    with open(file_path, encoding='utf-8') as f:
        merged.update(json.load(f))

with open(args.output, 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"Merged {len(merged)} articles to {args.output}")
