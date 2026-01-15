# Web Crawler Project

## Cấu trúc
```
webCrawl/
├── src/
│   ├── crawler_template.py       # Template cơ sở cho crawler
│   ├── merge_data.py             # Script gộp dữ liệu (tùy chọn)
│   └── crawl/
│       ├── baomoi/
│       │   ├── crawler.py        # Crawler cho BaoMoi
│       │   ├── data.json         # Metadata đã crawl
│       │   └── image/            # Thư mục chứa ảnh
│       └── baovanhoa/
│           ├── crawler.py        # Crawler cho BaoVanHoa
│           ├── data.json
│           └── image/
├── eventa_temp.json              # Template format dữ liệu
├── requirements.txt              # Dependencies
├── .env.example                  # Mẫu file cấu hình
├── run.bat                       # Script chạy cho Windows
├── run.sh                        # Script chạy cho Linux/Mac
└── README.md
```

## Format Data

```json
{
  "article_id_16hex": {
    "url": "...",
    "date": "...",
    "title": "...",
    "images": [
      {
        "id_image": "16hex",
        "caption": "...",
        "author": "..."
      }
    ],
    "content": "..."
  }
}
```

## Tạo Crawler Mới

```python
# src/crawl/mysite/crawler.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.crawler_template import CrawlerTemplate, CrawlerConfig

class MySiteCrawler(CrawlerTemplate):
    def should_crawl_url(self, url: str) -> bool:
        return '/article/' in url
    
    def extract_article_data(self, url: str, html: str, soup):
        if not soup:
            return None
        
        title = soup.find('h1')
        if not title:
            return None
        
        images = []
        for img in soup.find_all('img'):
            images.append({
                'url': img.get('src', ''),
                'caption': img.get('alt', ''),
                'author': ''
            })
        
        return {
            'url': url,
            'date': '',
            'title': title.get_text(strip=True),
            'images': images,
            'content': soup.find('div', class_='content').get_text(strip=True)
        }

if __name__ == '__main__':
    config = CrawlerConfig(
        base_urls=['https://mysite.com'],
        framework='requests',
        max_depth=1,
        output_dir=str(Path(__file__).parent)
    )
    crawler = MySiteCrawler(config)
    crawler.crawl()
    crawler.save_metadata()
    crawler.cleanup()
```


## Setup

```bash
# Tạo venv và cài dependencies
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Chạy Crawler

```bash
# Windows
run.bat crawl          # Chạy tất cả
run.bat crawl baomoi   # Chạy crawler cụ thể
run.bat merge          # Merge data

# Linux/Mac
./run.sh crawl
./run.sh crawl baomoi
./run.sh merge
```
