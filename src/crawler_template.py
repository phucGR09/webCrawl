import json
import hashlib
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from pathlib import Path
import time

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class CrawlerConfig:
    def __init__(self, 
                 base_urls: List[str],
                 framework: str = "requests",
                 max_depth: int = 2,
                 delay: float = 1.0,
                 output_dir: str = ".",
                 user_agent: str = None,
                 headless: bool = True,
                 timeout: int = 30):
        self.base_urls = base_urls
        self.framework = framework
        self.max_depth = max_depth
        self.delay = delay
        self.output_dir = Path(output_dir)
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.headless = headless
        self.timeout = timeout
        self.image_dir = self.output_dir / "image"
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
        if framework == "requests" and not BS4_AVAILABLE:
            raise ImportError("BeautifulSoup4 required")
        if framework == "selenium" and not SELENIUM_AVAILABLE:
            raise ImportError("Selenium required")


class CrawlerTemplate(ABC):
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.visited_urls: Set[str] = set()
        self.articles: Dict[str, Dict] = {}
        self.session = None
        self.driver = None
        self._init_framework()
        
    def _init_framework(self):
        if self.config.framework == "requests":
            self.session = requests.Session()
            self.session.headers.update({'User-Agent': self.config.user_agent})
        elif self.config.framework == "selenium":
            if not SELENIUM_AVAILABLE:
                raise ImportError("Selenium required")
            options = Options()
            if self.config.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={self.config.user_agent}')
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.config.timeout)
    
    def _generate_hash_id(self, content: str) -> str:
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def _get_page_content(self, url: str) -> Optional[str]:
        try:
            if self.config.framework == "requests":
                response = self.session.get(url, timeout=self.config.timeout)
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                return response.text
            else:
                self.driver.get(url)
                time.sleep(2)
                return self.driver.page_source
        except:
            return None
    
    def _parse_html(self, html: str):
        if not BS4_AVAILABLE:
            return None
        return BeautifulSoup(html, 'html.parser')
    
    def _download_image(self, image_url: str, image_id: str) -> bool:
        try:
            if not image_url.startswith('http'):
                return False
            response = requests.get(image_url, timeout=self.config.timeout, stream=True)
            response.raise_for_status()
            image_path = self.config.image_dir / f"{image_id}.jpg"
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except:
            return False
    
    def _extract_links(self, soup, base_url: str) -> List[str]:
        links = []
        if soup:
            for link in soup.find_all('a', href=True):
                full_url = urljoin(base_url, link['href'])
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    links.append(full_url)
        return links
    
    @abstractmethod
    def should_crawl_url(self, url: str) -> bool:
        pass
    
    @abstractmethod
    def extract_article_data(self, url: str, html: str, soup) -> Optional[Dict]:
        # Return: {"url": str, "date": str, "title": str, "images": [{"url": str, "caption": str, "author": str}], "content": str}
        pass
    
    def _process_images(self, images_info: List[Dict]) -> List[Dict]:
        processed_images = []
        for img_info in images_info:
            img_url = img_info.get('url', '')
            if not img_url:
                continue
            image_id = self._generate_hash_id(img_url)
            if self._download_image(img_url, image_id):
                processed_images.append({
                    'id_image': image_id,
                    'caption': img_info.get('caption', ''),
                    'author': img_info.get('author', '')
                })
        return processed_images
    
    def _crawl_recursive(self, url: str, depth: int = 0):
        if depth > self.config.max_depth or url in self.visited_urls or not self.should_crawl_url(url):
            return
        
        self.visited_urls.add(url)
        html = self._get_page_content(url)
        if not html:
            return
        
        soup = self._parse_html(html)
        article_data = self.extract_article_data(url, html, soup)
        
        if article_data:
            article_id = self._generate_hash_id(url + article_data.get('title', ''))
            processed_images = self._process_images(article_data.get('images', []))
            self.articles[article_id] = {
                'url': article_data['url'],
                'date': article_data.get('date', ''),
                'title': article_data.get('title', ''),
                'images': processed_images,
                'content': article_data.get('content', '')
            }
        
        time.sleep(self.config.delay)
        
        if depth < self.config.max_depth:
            for link in self._extract_links(soup, url):
                self._crawl_recursive(link, depth + 1)
    
    def crawl(self):
        for base_url in self.config.base_urls:
            self._crawl_recursive(base_url, depth=0)
    
    def save_metadata(self, filename: str = "data.json"):
        with open(self.config.output_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
    
    def cleanup(self):
        if self.session:
            self.session.close()
        if self.driver:
            self.driver.quit()

