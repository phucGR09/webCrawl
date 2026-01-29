import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
import requests
from bs4 import BeautifulSoup
import json
import time
from utils import hash_id, save_image, format_datetime

class NhanDanCrawler:
  def __init__(self, zone_id=1251):
    self.zone_id = zone_id
    self.base_domain = "https://nhandan.vn"
    self.api_base_url = "https://api.nhandan.vn/api"
    self.articles_data = {}
    self.image_dir = Path(__file__).parent / "image"
    self.image_dir.mkdir(parents=True, exist_ok=True)
    self.debug_dir = Path(__file__).parent / "debug_html"
    self.debug_dir.mkdir(parents=True, exist_ok=True)
    
    self.api_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'origin': 'https://nhandan.vn',
        'referer': 'https://nhandan.vn/vanhoa/',
        'accept': '*/*'
    }    
  def crawl_articles_from_api(self, max_pages=3, page_size=30):
    all_articles = []
    
    for page in range(1, max_pages + 1):
      api_url = f"{self.api_base_url}/morenews-zone-{self.zone_id}-{page}.html"
      params = {'phrase': '', 'page_size': page_size, 'sz': self.zone_id, 'st': 'zone'}
      
      response = requests.get(api_url, params=params, headers=self.api_headers)
      data = response.json()
      
      if data['error_code'] != 0:
        print(f"API Error: {data['error_message']}")
        break
      
      contents = data['data']['contents']
      for item in contents:
        article = {
          'content_id': item['content_id'],
          'title': item['title'],
          'url': item['url'],
          'date': format_datetime(item['date']),
          'description': item.get('description', ''),
          'avatar_url': item.get('avatar_url', ''),
          'zone_name': item['zone']['name']
        }
        all_articles.append(article)
      
      #print(f"Page {page}: {len(contents)} articles")
      
      if not data['data'].get('load_more', False):
        break
      
      time.sleep(0.5)
    
    return all_articles
  
  def crawl_article_detail(self, article_url):
    try:
      response = requests.get(article_url, headers=self.api_headers, timeout=10)
      response.raise_for_status()
      
      soup = BeautifulSoup(response.content, 'html.parser')
      
      # Nhandan structure: <div class="article">
      article = soup.find('div', class_='article')
      if not article:
        return None
      
      # Title
      title_tag = article.find('h1', class_='article__title')
      title = title_tag.get_text(strip=True) if title_tag else "No Title"
      
      # Date from article__meta time tag
      article_meta = article.find('div', class_='article__meta')
      time_tag = article_meta.find('time') if article_meta else None
      raw_time = time_tag.get_text(strip=True) if time_tag else ""
      formatted_date = format_datetime(raw_time)
      
      # Content
      content_parts = []
      article_body = article.find('div', class_='article__body')
      
      images = []
      
      if article_body:
        # Extract images from <figure> tags
        figures = article_body.find_all('figure')
        for fig in figures:
          img_tag = fig.find('img')
          if img_tag:
            # Check data-src first (lazy-load), fallback to src
            img_src = img_tag.get('data-src') or img_tag.get('src', '')
            # Skip placeholder images (data:image/...)
            if img_src and not img_src.startswith('data:'):
              img_url = img_src if img_src.startswith('http') else f"https:{img_src}"
              img_id = hash_id(img_url + article_url)
              
              figcaption = fig.find('figcaption')
              caption = figcaption.get_text(strip=True) if figcaption else ''
              
              saved_path = save_image(img_url, str(self.image_dir), img_id)
              
              images.append({
                'id_image': img_id,
                'caption': caption,
                'author': ''
              })
        
        # Extract images from <table class="picture"> structure
        picture_tables = article_body.find_all('table', class_='picture')
        for table in picture_tables:
          pic_td = table.find('td', class_='pic')
          if pic_td:
            img_tag = pic_td.find('img')
            if img_tag:
              # Check data-src first (lazy-load), fallback to src
              img_src = img_tag.get('data-src') or img_tag.get('src', '')
              # Skip placeholder images (data:image/...)
              if img_src and not img_src.startswith('data:'):
                img_url = img_src if img_src.startswith('http') else f"https:{img_src}"
                img_id = hash_id(img_url + article_url)
                
                # Caption from alt attribute or <td class="caption">
                caption = img_tag.get('alt', '')
                if not caption:
                  caption_td = table.find('td', class_='caption')
                  if caption_td:
                    caption = caption_td.get_text(strip=True)
                
                saved_path = save_image(img_url, str(self.image_dir), img_id)
                
                images.append({
                  'id_image': img_id,
                  'caption': caption,
                  'author': ''
                })
        
        # Extract text from <p> tags
        paragraphs = article_body.find_all('p')
        for para in paragraphs:
          text = para.get_text(strip=True)
          if text:
            content_parts.append(text)
      
      full_content = '\n\n'.join(content_parts)
      article_id = hash_id(article_url)
      
      return {
        article_id: {
          'url': article_url,
          'date': formatted_date,
          'title': title,
          'images': images,
          'content': full_content
        }
      }
    
    except Exception as e:
      print(f"  Error: {article_url} - {e}")
      return None

  
def main():
  crawler = NhanDanCrawler(zone_id=1251)
  
  # Step 1: Get article list from API
  articles = crawler.crawl_articles_from_api(max_pages=1000)
  
  # Step 2: Crawl detail for each article
  articles_detail = {}
  total = len(articles)
  for idx, article in enumerate(articles, 1):
    detail = crawler.crawl_article_detail(article['url'])
    if detail:
      articles_detail.update(detail)
    time.sleep(0.5)
  
  # Save
  output_file = Path(__file__).parent / "articles_detail.json"
  with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(articles_detail, f, ensure_ascii=False, indent=2)
  print(f"\nSaved: {output_file}")
  print(f"Articles: {len(articles_detail)}")
  print(f"Images: {sum(len(a['images']) for a in articles_detail.values())}")

if __name__ == "__main__":
  main()