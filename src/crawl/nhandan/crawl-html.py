import bs4
import requests
from bs4 import BeautifulSoup
import json
import time

#config
url = "https://nhandan.vn/le-hoi-anh-sang-tai-festival-hue-2024-post808953.html"
html_path = "nhandan.html"

response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

content = soup.prettify()
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

