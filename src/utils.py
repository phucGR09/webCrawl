"""
Utility functions for web crawling project
"""
import hashlib
import os
import requests
from datetime import datetime
from typing import Optional
from pathlib import Path


def hash_id(text: str) -> str:
    """
    Generate a 16-character hexadecimal hash ID from text
    
    Args:
        text: Input string to hash (usually URL or unique identifier)
    
    Returns:
        16-character hex string
    """
    hash_object = hashlib.md5(text.encode('utf-8'))
    return hash_object.hexdigest()[:16]


def save_image(image_url: str, save_dir: str, image_id: str) -> Optional[str]:
    """
    Download and save image from URL
    
    Args:
        image_url: URL of the image to download
        save_dir: Directory path to save the image
        image_id: Unique ID for the image filename
    
    Returns:
        Saved file path if successful, None otherwise
    """
    try:
        # Create directory if not exists
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        # Get image extension from URL
        ext = os.path.splitext(image_url.split('?')[0])[1]
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'  # Default extension
        
        # Download image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Save to file
        filename = f"{image_id}{ext}"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    
    except Exception as e:
        print(f"Error saving image {image_url}: {str(e)}")
        return None


def format_datetime(time_element_text) -> str:
    try:
        # Handle Unix timestamp (int)
        if isinstance(time_element_text, int):
            dt = datetime.fromtimestamp(time_element_text)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Remove extra whitespace for string
        time_str = time_element_text.strip()
        
        # Try common Vietnamese datetime formats
        formats = [
            '%d/%m/%Y %H:%M',           # 17/01/2026 14:30
            '%d/%m/%Y - %H:%M',         # 17/01/2026 - 14:30
            '%d-%m-%Y %H:%M',           # 17-01-2026 14:30
            '%d.%m.%Y %H:%M',           # 17.01.2026 14:30
            '%Y-%m-%d %H:%M:%S',        # 2026-01-17 14:30:00
            '%Y-%m-%d %H:%M',           # 2026-01-17 14:30
            '%d/%m/%Y',                 # 17/01/2026
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                continue
        
        # If no format matches, return original
        return time_str
    
    except Exception as e:
        print(f"Error formatting datetime '{time_element_text}': {str(e)}")
        return time_element_text


def normalize_url(url: str, base_url: str = '') -> str:
    if url.startswith('http://') or url.startswith('https://'):
        return url
    elif url.startswith('//'):
        return 'https:' + url
    elif url.startswith('/'):
        return base_url.rstrip('/') + url
    else:
        return base_url.rstrip('/') + '/' + url
