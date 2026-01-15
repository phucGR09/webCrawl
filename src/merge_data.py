import json
from pathlib import Path
from typing import Dict


def load_crawler_data(crawler_path: Path) -> Dict:
    data_file = crawler_path / 'data.json'
    if not data_file.exists():
        return {}
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def merge_all_data(crawl_dir: Path, output_file: Path):
    merged_articles = {}
    
    for crawler_path in crawl_dir.iterdir():
        if not crawler_path.is_dir() or not (crawler_path / 'crawler.py').exists():
            continue
        
        crawler_data = load_crawler_data(crawler_path)
        for article_id, article_data in crawler_data.items():
            if article_id not in merged_articles:
                article_data['source'] = crawler_path.name
                merged_articles[article_id] = article_data
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_articles, f, ensure_ascii=False, indent=2)


def main():
    project_root = Path(__file__).parent.parent
    crawl_dir = project_root / 'src' / 'crawl'
    database_dir = project_root / 'database'
    database_dir.mkdir(exist_ok=True)
    
    if not crawl_dir.exists():
        print(f"Error: {crawl_dir} not found")
        return
    
    merge_all_data(crawl_dir, database_dir / 'database.json')


if __name__ == '__main__':
    main()
