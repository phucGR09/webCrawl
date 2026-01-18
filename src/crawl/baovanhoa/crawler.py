"""
Crawler for baovanhoa.vn
Crawl articles from culture section with pagination
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import requests
import bs4
from bs4 import BeautifulSoup
import json
import time
import argparse
from utils import hash_id, save_image, format_datetime, normalize_url


class BaoVanHoaCrawler:
    def __init__(self, base_url="https://baovanhoa.vn/van-hoa", page_start=1, max_pages=5):
        self.base_url = base_url
        self.page_start = page_start
        self.max_pages = max_pages
        self.base_domain = "https://baovanhoa.vn"
        self.articles_data = {}
        self.image_dir = Path(__file__).parent / "image"
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.debug_dir = Path(__file__).parent / "debug_html"
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def get_article_links_from_page(self, page_num: int) -> list:
        try:
            # Construct page URL
            if page_num == 1:
                url = self.base_url + "/"
            else:
                url = f"{self.base_url}/?page={page_num}"
            
            # Get page HTML
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Save HTML for debugging
            debug_file = self.debug_dir / f"page_{page_num}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find zone--timeline section
            zone_timeline = soup.find('section', class_='zone--timeline')
            if not zone_timeline:
                return []
            
            # Find all articles
            articles = zone_timeline.find_all('article', class_='story')
            
            article_links = []
            for article in articles:
                # Find the <a> tag in <h3 class="story__title">
                title_tag = article.find('h3', class_='story__title')
                if title_tag:
                    link_tag = title_tag.find('a')
                    if link_tag and link_tag.get('href'):
                        article_url = normalize_url(link_tag['href'], self.base_domain)
                        article_links.append(article_url)
            
            return article_links
        
        except Exception as e:
            print(f"Error crawling page {page_num}: {str(e)}")
            return []
    
    def crawl_article_detail(self, article_url: str) -> dict:
        try:
            # Get article HTML
            response = requests.get(article_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Save HTML for debugging
            article_id_temp = hash_id(article_url)
            debug_file = self.debug_dir / f"article_{article_id_temp}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find main article tag with specific class
            article = soup.find('article', class_='article-detail')
            if not article:
                return None
            
            # Extract title from <h1 class="detail__title">
            title_tag = article.find('h1', class_='detail__title')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            
            # Extract author from <span class="detail__author">
            author_tag = article.find('span', class_='detail__author')
            author = author_tag.get_text(strip=True) if author_tag else ""
            
            # Extract time from <time>
            time_tag = article.find('time')
            raw_time = time_tag.get_text(strip=True) if time_tag else ""
            formatted_date = format_datetime(raw_time)
            
            # Extract summary from <h2 class="detail__summary">
            summary_tag = article.find('h2', class_='detail__summary')
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            
            # Extract content from detail__content
            content_parts = []
            detail_content = article.find('div', class_='detail__content')
            
            images = []
            
            if detail_content:
                # Add summary to content
                if summary:
                    content_parts.append(summary)
                
                # Extract images from content-image figures
                gallery_items = detail_content.find_all('figure', class_='content-image')
                for gallery in gallery_items:
                    img_tag = gallery.find('img')
                    if img_tag:
                        # Use data-original if exists, otherwise src
                        img_src = img_tag.get('data-original') or img_tag.get('src', '')
                        img_alt = img_tag.get('alt', '')
                        img_caption_tag = gallery.find('figcaption', class_='fig')
                        img_caption = img_caption_tag.get_text(strip=True) if img_caption_tag else ''
                        
                        if img_src:
                            # Normalize image URL
                            img_url = normalize_url(img_src, self.base_domain)
                            
                            # Generate unique image ID
                            img_id = hash_id(img_url + article_url)
                            
                            # Save image
                            saved_path = save_image(img_url, str(self.image_dir), img_id)
                            
                            images.append({
                                'id_image': img_id,
                                'caption': img_caption or img_alt,
                                'author': author
                            })
                
                # Extract text from all <p> tags
                paragraphs = detail_content.find_all('p')
                for para in paragraphs:
                    text_content = para.get_text(strip=True)
                    if text_content:
                        content_parts.append(text_content)
            
            # Combine all content
            full_content = '\n\n'.join(content_parts)
            
            # Generate article ID
            article_id = hash_id(article_url)
            
            article_data = {
                'url': article_url,
                'date': formatted_date,
                'title': title,
                'images': images,
                'content': full_content
            }
            
            return {article_id: article_data}
        
        except Exception as e:
            print(f"    Error crawling article {article_url}: {str(e)}")
            return None
    
    def crawl_all_pages(self):
        print(f"\n{'='*60}")
        print(f"Starting crawler for baovanhoa.vn")
        print(f"Page range: {self.page_start} to {self.page_start + self.max_pages - 1}")
        print(f"Total pages to crawl: {self.max_pages}")
        print(f"{'='*60}\n")
        
        all_article_links = []
        
        # Step 1: Collect all article links from all pages
        page_end = self.page_start + self.max_pages
        for page_num in range(self.page_start, page_end):
            links = self.get_article_links_from_page(page_num)
            all_article_links.extend(links)
            time.sleep(1)  # Be polite to the server
        print(f"Total article links found: {len(all_article_links)}\n")
        # Step 2: Crawl each article detail
        for article_url in all_article_links:
            article_data = self.crawl_article_detail(article_url)
            
            if article_data:
                self.articles_data.update(article_data)
            
            time.sleep(1)  # Be polite to the server
        
        print(f"\n{'='*60}")
        print(f"Crawling completed!")
        print(f"Total articles crawled: {len(self.articles_data)}")
        print(f"Total images saved: {sum(len(art['images']) for art in self.articles_data.values())}")
        print(f"{'='*60}\n")
    
    def save_to_json(self, filename='data.json'):

        output_path = Path(__file__).parent / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.articles_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Data saved to: {output_path}\n")
        
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Crawl articles from baovanhoa.vn',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crawl pages 1-5, save to data_phase1.json
  python crawler.py --page-begin 1 --amount 5 --output data_phase1.json
  
  # Crawl pages 6-10, save to data_phase2.json (second phase)
  python crawler.py --page-begin 6 --amount 5 --output data_phase2.json
  
  # Crawl pages 11-15, save to data_phase3.json (third phase)
  python crawler.py --page-begin 11 --amount 5 --output data_phase3.json
  
  # Crawl default (pages 1-2, save to data.json)
  python crawler.py
        """
    )
    
    parser.add_argument(
        '--page-begin',
        type=int,
        default=1,
        help='Starting page number (default: 1)'
    )
    
    parser.add_argument(
        '--amount',
        type=int,
        default=2,
        help='Number of pages to crawl (default: 2)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data.json',
        help='Output JSON file path (default: data.json)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.page_begin < 1:
        print("Error: --page-begin must be >= 1")
        return
    
    if args.amount < 1:
        print("Error: --amount must be >= 1")
        return
    
    # Create crawler instance with provided arguments
    crawler = BaoVanHoaCrawler(
        base_url="https://baovanhoa.vn/van-hoa",
        page_start=args.page_begin,
        max_pages=args.amount
    )
    
    # Crawl all pages
    crawler.crawl_all_pages()
    
    # Save to specified output file
    crawler.save_to_json(args.output)


if __name__ == '__main__':
    main()