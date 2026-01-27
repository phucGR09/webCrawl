import bs4
import requests
from bs4 import BeautifulSoup
import json
import time

#config
url = "https://nhandan.vn/bao-vat-quoc-gia-nhung-bieu-tuong-song-dong-cho-su-truong-ton-cua-dan-toc-post938314.html"
html_path = "nhandan.html"

response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

content = soup.prettify()
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

