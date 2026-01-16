# Web Crawler Project

## Project Structure
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
        "image_id": "16hex",
        "caption": "...",
        "author": "..."
      }
    ],
    "content": "..."
  }
}
```

article_
