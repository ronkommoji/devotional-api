"""
Web scraper for Our Daily Bread Ministries devotionals.
"""
import json
import re
from datetime import datetime
from typing import Optional, Dict, List
import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


BASE_URL = "https://www.odbm.org"
DEVOTIONALS_URL = f"{BASE_URL}/en/devotionals/"


async def fetch_page(url: str) -> BeautifulSoup:
    """Fetch and parse a webpage."""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")


def extract_text(element) -> str:
    """Safely extract text from a BeautifulSoup element."""
    if element is None:
        return ""
    return element.get_text(strip=True)


def parse_date(date_str: str) -> Optional[str]:
    """Parse date string to YYYY-MM-DD format."""
    try:
        dt = date_parser.parse(date_str)
        return dt.strftime("%Y-%m-%d")
    except:
        return None


async def scrape_devotional_page(url: str) -> Dict:
    """
    Scrape a full devotional page.
    
    Args:
        url: Full URL or path to devotional page
        
    Returns:
        Dictionary with devotional data
    """
    # Ensure full URL
    if not url.startswith("http"):
        url = BASE_URL + url if url.startswith("/") else f"{BASE_URL}/{url}"
    
    # Fetch raw HTML to check for embedded data
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        html_text = response.text
    
    # Try to extract JSON data from window._model
    page_data = None
    # Find the start of window._model
    model_start = html_text.find('window._model = {')
    if model_start != -1:
        # Find the matching closing brace
        brace_count = 0
        start_pos = model_start + len('window._model = ')
        json_start = start_pos
        for i in range(start_pos, min(start_pos + 500000, len(html_text))):  # Limit search
            if html_text[i] == '{':
                brace_count += 1
            elif html_text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_str = html_text[json_start:i+1]
                    try:
                        page_data = json.loads(json_str)
                        break
                    except json.JSONDecodeError:
                        pass
    
    soup = BeautifulSoup(html_text, "lxml")
    
    # Extract data from JSON if available
    if page_data and "pageModel" in page_data:
        pm = page_data["pageModel"]
        
        # Extract title
        title = pm.get("pageTitle", "") or pm.get("heroTitle", "")
        
        # Extract date
        date_str = ""
        if "devotionalDate" in pm:
            date_str = parse_date(pm["devotionalDate"]) or ""
        
        # Extract author - check nested structure
        author = ""
        if "heroContent" in pm:
            hero = pm["heroContent"]
            # Check if heroContent has a model field
            if isinstance(hero, dict):
                if "model" in hero and isinstance(hero["model"], dict):
                    hero = hero["model"]
                if "author" in hero:
                    author_obj = hero["author"]
                    if isinstance(author_obj, dict):
                        author = author_obj.get("name", "")
        
        # Extract featured verse
        featured_verse = ""
        if "heroContent" in pm:
            hero = pm["heroContent"]
            # Check if heroContent has a model field
            if isinstance(hero, dict):
                if "model" in hero and isinstance(hero["model"], dict):
                    hero = hero["model"]
                if "summary" in hero:
                    featured_verse = hero["summary"].strip()
        
        # Extract scripture
        scripture = pm.get("bibleVerseText", "")
        
        # Extract content
        content = []
        if "devotionBody" in pm:
            # Parse HTML content
            body_soup = BeautifulSoup(pm["devotionBody"], "lxml")
            paragraphs = body_soup.find_all("p")
            content = [extract_text(p) for p in paragraphs if extract_text(p)]
        
        # Extract Reflect & Pray
        reflect_pray = {"question": "", "prayer": ""}
        if "reflectBody" in pm:
            reflect_soup = BeautifulSoup(pm["reflectBody"], "lxml")
            strong_tags = reflect_soup.find_all("strong")
            if strong_tags:
                reflect_pray["question"] = extract_text(strong_tags[-1])
        
        if "prayerBody" in pm:
            prayer_soup = BeautifulSoup(pm["prayerBody"], "lxml")
            em_tags = prayer_soup.find_all("em")
            if em_tags:
                reflect_pray["prayer"] = extract_text(em_tags[0])
        
        # Extract insights
        insights = ""
        if "insightsBody" in pm:
            insights_soup = BeautifulSoup(pm["insightsBody"], "lxml")
            # Get first paragraph, skip images/links
            paragraphs = insights_soup.find_all("p")
            insight_texts = [extract_text(p) for p in paragraphs if extract_text(p) and len(extract_text(p)) > 20]
            insights = " ".join(insight_texts)
        
        # Extract Bible in a Year
        bible_in_year = {"old_testament": "", "new_testament": ""}
        if "bibleInAYearEntries" in pm and pm["bibleInAYearEntries"]:
            entry = pm["bibleInAYearEntries"][0]
            verse_text = entry.get("bibleVerseText", "")
            if verse_text:
                # Split by semicolon if present
                parts = verse_text.split(";")
                if len(parts) >= 2:
                    bible_in_year["old_testament"] = parts[0].strip()
                    bible_in_year["new_testament"] = parts[1].strip()
                else:
                    # Try to determine which testament
                    if any(book in verse_text for book in ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "Samuel", "Kings", "Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi"]):
                        bible_in_year["old_testament"] = verse_text
                    else:
                        bible_in_year["new_testament"] = verse_text
        
        # Extract image URL
        image_url = ""
        if "heroContent" in pm:
            hero = pm["heroContent"]
            # Check if heroContent has a model field
            if isinstance(hero, dict):
                if "model" in hero and isinstance(hero["model"], dict):
                    hero = hero["model"]
                if "backgroundImage" in hero:
                    bg_img = hero["backgroundImage"]
                    if isinstance(bg_img, dict):
                        img_path = bg_img.get("url", "")
                        if img_path:
                            image_url = BASE_URL + img_path if img_path.startswith("/") else img_path
        
    else:
        # Fallback to HTML parsing if JSON not found
        title = ""
        title_elem = soup.find("h1")
        if title_elem:
            title = extract_text(title_elem)
        
        date_str = ""
        date_pattern = re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b")
        date_match = date_pattern.search(html_text)
        if date_match:
            date_str = parse_date(date_match.group()) or ""
        
        author = ""
        author_links = soup.find_all("a", href=re.compile(r"/authors/"))
        for link in author_links:
            link_text = extract_text(link)
            if link_text and len(link_text) < 50 and not any(ext in link_text.lower() for ext in [".jpg", ".png", ".gif", ".svg"]):
                author = link_text
                break
        
        featured_verse = ""
        verse_pattern = re.compile(r'["\']([^"\']+)["\']\s+[A-Z][a-z]+\s+\d+:\d+')
        verse_match = verse_pattern.search(html_text)
        if verse_match:
            featured_verse = verse_match.group(0)
        
        scripture = ""
        scripture_btn = soup.find("button", string=re.compile(r"\d+:\d+"))
        if scripture_btn:
            scripture = extract_text(scripture_btn)
        
        content = []
        main_content = soup.find("main")
        if main_content:
            all_paragraphs = main_content.find_all("p")
            content = [extract_text(p) for p in all_paragraphs 
                      if len(extract_text(p)) > 50 and 
                      not any(skip in extract_text(p).lower() for skip in ["subscribe", "privacy", "terms", "cookie", "menu", "skip"])]
        
        reflect_pray = {"question": "", "prayer": ""}
        insights = ""
        bible_in_year = {"old_testament": "", "new_testament": ""}
        image_url = ""
    
    
    return {
        "title": title,
        "date": date_str,
        "author": author,
        "scripture": scripture,
        "featured_verse": featured_verse,
        "content": content,
        "reflect_pray": reflect_pray,
        "insights": insights,
        "bible_in_year": bible_in_year,
        "url": url,
        "image_url": image_url
    }


async def scrape_today() -> Dict:
    """
    Scrape today's devotional from the main devotionals page.
    
    Returns:
        Dictionary with today's devotional data
    """
    # Fetch the page HTML
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = await client.get(DEVOTIONALS_URL, headers=headers)
        response.raise_for_status()
        html_text = response.text
    
    # Search for devotional URLs in the raw HTML (they may be in script tags or data attributes)
    url_pattern = re.compile(r'/devotionals/devotional-category/[^"\')\s<>]+')
    urls = url_pattern.findall(html_text)
    
    if urls:
        # The first URL is typically today's devotional
        devotional_path = urls[0]
        devotional_url = BASE_URL + devotional_path
        return await scrape_devotional_page(devotional_url)
    
    # Fallback: try parsing with BeautifulSoup
    soup = BeautifulSoup(html_text, "lxml")
    main_content = soup.find("main")
    if main_content:
        devotional_link = main_content.find("a", href=re.compile(r"/devotionals/devotional-category/"))
        if devotional_link:
            devotional_url = devotional_link.get("href", "")
            return await scrape_devotional_page(devotional_url)
    
    raise ValueError("Could not find today's devotional")


async def scrape_devotional_list(limit: int = 10, offset: int = 0) -> List[Dict]:
    """
    Scrape list of devotionals from the main page.
    
    Args:
        limit: Number of devotionals to return
        offset: Number of devotionals to skip
        
    Returns:
        List of devotional preview dictionaries
    """
    soup = await fetch_page(DEVOTIONALS_URL)
    
    devotionals = []
    
    # Find all devotional links in the list
    devotional_links = soup.find_all("a", href=re.compile(r"/devotionals/devotional-category/"))
    
    # Remove duplicates
    seen_urls = set()
    unique_links = []
    for link in devotional_links:
        url = link.get("href", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_links.append(link)
    
    # Apply offset and limit
    paginated_links = unique_links[offset:offset + limit]
    
    for link in paginated_links:
        url = link.get("href", "")
        if not url:
            continue
        
        # Extract preview data from the link's parent container
        parent = link.find_parent()
        if parent:
            # Find title
            title_elem = link.find("h2") or link.find("h3")
            title = extract_text(title_elem) if title_elem else extract_text(link)
            
            # Find date
            date_str = ""
            date_elem = parent.find(string=re.compile(r"\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}", re.I))
            if date_elem:
                date_str = parse_date(date_elem) or ""
            
            # Find author
            author = ""
            author_elem = parent.find(string=re.compile(r"^[A-Z][a-z]+\s+[A-Z]"))
            if author_elem:
                author = extract_text(author_elem.find_parent()) if author_elem.find_parent() else ""
            
            # Find preview text
            preview = ""
            preview_elem = parent.find("p") or parent.find("div", class_=re.compile(r"preview|excerpt|summary", re.I))
            if preview_elem:
                preview = extract_text(preview_elem)
            
            # Find image
            image_url = ""
            img_elem = parent.find("img")
            if img_elem:
                img_src = img_elem.get("src", "")
                if img_src:
                    image_url = BASE_URL + img_src if img_src.startswith("/") else img_src
            
            full_url = BASE_URL + url if url.startswith("/") else url
            
            devotionals.append({
                "title": title,
                "date": date_str,
                "author": author,
                "preview": preview,
                "url": full_url,
                "image_url": image_url
            })
    
    return devotionals


async def scrape_by_date(date: str) -> Dict:
    """
    Scrape devotional for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        Dictionary with devotional data
    """
    # Parse the date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date}. Use YYYY-MM-DD")
    
    # Get list of devotionals and find the one matching the date
    soup = await fetch_page(DEVOTIONALS_URL)
    
    # Find all devotional items with dates
    devotional_items = soup.find_all("a", href=re.compile(r"/devotionals/devotional-category/"))
    
    for item in devotional_items:
        # Check parent for date
        parent = item.find_parent()
        if parent:
            date_text = parent.get_text()
            # Try to find date in format like "18 Jan 2026" or "January 18, 2026"
            date_match = re.search(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})", date_text, re.I)
            if date_match:
                day, month, year = date_match.groups()
                month_map = {
                    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
                }
                month_num = month_map.get(month.lower()[:3], 0)
                if month_num:
                    item_date = datetime(int(year), month_num, int(day))
                    if item_date.date() == target_date.date():
                        url = item.get("href", "")
                        if url:
                            full_url = BASE_URL + url if url.startswith("/") else url
                            return await scrape_devotional_page(full_url)
    
    raise ValueError(f"Devotional not found for date: {date}")


async def scrape_by_slug(slug: str) -> Dict:
    """
    Scrape devotional by slug/URL path.
    
    Args:
        slug: Devotional slug (e.g., "faith-and-false-accusation")
        
    Returns:
        Dictionary with devotional data
    """
    url = f"{BASE_URL}/en/devotionals/devotional-category/{slug}"
    return await scrape_devotional_page(url)
