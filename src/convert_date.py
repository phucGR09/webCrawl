import json
import argparse
import re
from pathlib import Path
from datetime import datetime


def convert_date_format(date_str):
    if 'T' in date_str and date_str.endswith('Z'):
        return date_str
    
    if date_str.startswith('Thứ') or date_str.startswith('Chủ'):
        match = re.search(r'ngày (\d{2}/\d{2}/\d{4}) - (\d{2}:\d{2})', date_str)
        if match:
            dt = datetime.strptime(f"{match.group(1)} {match.group(2)}", '%d/%m/%Y %H:%M')
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='Path to specific data.json file')
    args = parser.parse_args()
    
    if args.path:
        data_files = [Path(args.path)]
    else:
        script_dir = Path(__file__).parent
        crawl_dir = script_dir / 'crawl'
        data_files = list(crawl_dir.glob('*/data.json'))
    
    for data_file in data_files:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for article_data in data.values():
            if 'date' in article_data:
                article_data['date'] = convert_date_format(article_data['date'])
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
