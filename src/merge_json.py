import json
from pathlib import Path

crawl_dir = Path(__file__).parent / 'crawl' / 'baovanhoa'
merged = {}

for json_file in sorted(crawl_dir.glob('data*.json')):
    with open(json_file, encoding='utf-8') as f:
        merged.update(json.load(f))

with open(crawl_dir / 'merged_data.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"Merged {len(merged)} articles")
