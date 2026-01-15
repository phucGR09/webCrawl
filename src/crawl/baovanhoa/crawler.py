import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from crawler_template import CrawlerTemplate, CrawlerConfig
from typing import Optional, Dict
import re


class BaoVanHoaCrawler(CrawlerTemplate):
    def should_crawl_url(self, url: str) -> bool:
        patterns = ['/tin-tuc/', '/su-kien/', '/bai-viet/']
        return any(p in url for p in patterns)
    
    def extract_article_data(self, url: str, html: str, soup) -> Optional[Dict]:
        if not soup:
            return None
        
        article = soup.find('article') or soup.find('div', class_=re.compile('article|detail'))
        if not article:
            return None
        
        title_elem = soup.find('h1')
        if not title_elem:
            return None
        
        content_elem = article.find('div', class_=re.compile('content|body'))
        content = content_elem.get_text(strip=True) if content_elem else ''
        
        images = []
        for img in article.find_all('img'):
            img_url = img.get('src') or img.get('data-src')
            if img_url and not img_url.startswith('data:'):
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://baovanhoa.vn' + img_url
                
                images.append({
                    'url': img_url,
                    'caption': img.get('alt', ''),
                    'author': ''
                })
        
        return {
            'url': url,
            'date': '',
            'title': title_elem.get_text(strip=True),
            'images': images,
            'content': content
        }


if __name__ == '__main__':
    current_dir = Path(__file__).parent
    
    config = CrawlerConfig(
        base_urls=['https://baovanhoa.vn'],
        framework='selenium',
        max_depth=1,
        delay=2.0,
        output_dir=str(current_dir)
    )
    
    crawler = BaoVanHoaCrawler(config)
    crawler.crawl()
    crawler.save_metadata()
    crawler.cleanup()
