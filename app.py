"""
Canadian Used Car Listing Scraper - Main Flask Application
This application collects used car listings from Kijiji, AutoTrader, and Facebook Marketplace.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
import time
from openai import OpenAI
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client for description summarization
try:
    client = OpenAI()
except Exception as e:
    logger.warning(f"OpenAI client initialization warning: {e}")
    client = None

# ============================================================================
# KIJIJI SCRAPER
# ============================================================================

def scrape_kijiji(car_model, location="canada"):
    """
    Scrape used car listings from Kijiji.
    
    Args:
        car_model (str): The car model to search for (e.g., "Honda Civic")
        location (str): Location to search in (default: "canada")
    
    Returns:
        list: List of car listings with extracted data
    """
    listings = []
    
    try:
        # Kijiji search URL for cars category
        search_url = f"https://www.kijiji.ca/b-cars/{location}/{car_model}/k0c174l0"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        logger.info(f"Scraping Kijiji: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            logger.warning(f"Kijiji request failed with status {response.status_code}")
            return listings
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Kijiji uses various selectors - try multiple approaches
        # Look for listing containers
        listing_items = []
        
        # Try different selectors
        listing_items = soup.find_all('div', {'data-testid': 'listing'})
        if not listing_items:
            listing_items = soup.find_all('a', class_=re.compile('listing'))
        if not listing_items:
            listing_items = soup.find_all('div', class_=re.compile('search-item|result'))
        
        logger.info(f"Found {len(listing_items)} items on Kijiji")
        
        for item in listing_items[:20]:  # Limit to first 20 results
            try:
                # Try to extract title and URL
                title_elem = None
                url = None
                
                # If item is an 'a' tag, use it directly
                if item.name == 'a':
                    title_elem = item
                    url = item.get('href', '')
                else:
                    # Look for 'a' tag within the item
                    title_elem = item.find('a')
                    if title_elem:
                        url = title_elem.get('href', '')
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 3:
                    continue
                
                if not url.startswith('http'):
                    url = 'https://www.kijiji.ca' + url if url else ''
                
                # Extract price - look for various patterns
                price = 'N/A'
                price_elem = item.find('span', class_=re.compile('price'))
                if price_elem:
                    price = price_elem.get_text(strip=True)
                else:
                    # Try to find price in text
                    text = item.get_text()
                    price_match = re.search(r'\$[\d,]+', text)
                    if price_match:
                        price = price_match.group(0)
                
                # Extract location
                location_elem = item.find('span', class_=re.compile('location'))
                location_text = location_elem.get_text(strip=True) if location_elem else 'N/A'
                
                # Extract date posted
                date_elem = item.find('span', class_=re.compile('date'))
                date_posted = date_elem.get_text(strip=True) if date_elem else 'N/A'
                
                # Extract description
                desc_elem = item.find('div', class_=re.compile('description'))
                if not desc_elem:
                    desc_elem = item.find('p')
                description = desc_elem.get_text(strip=True) if desc_elem else title
                
                # Try to extract year and mileage from description
                year = extract_year(description)
                mileage = extract_mileage(description)
                
                listings.append({
                    'platform': 'Kijiji',
                    'title': title,
                    'price': price,
                    'location': location_text,
                    'year': year,
                    'mileage': mileage,
                    'description': description,
                    'url': url,
                    'date_posted': date_posted
                })
            
            except Exception as e:
                logger.debug(f"Error parsing Kijiji listing: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(listings)} listings from Kijiji")
    
    except Exception as e:
        logger.error(f"Kijiji scraping error: {e}")
    
    return listings


# ============================================================================
# AUTOTRADER SCRAPER
# ============================================================================

def scrape_autotrader(car_model, location="canada"):
    """
    Scrape used car listings from AutoTrader.
    
    Args:
        car_model (str): The car model to search for
        location (str): Location to search in
    
    Returns:
        list: List of car listings with extracted data
    """
    listings = []
    
    try:
        # AutoTrader search URL
        search_url = f"https://www.autotrader.ca/cars/?keyword={car_model}&prv={location}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        logger.info(f"Scraping AutoTrader: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            logger.warning(f"AutoTrader request failed with status {response.status_code}")
            return listings
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all listing items - try multiple selectors
        listing_items = soup.find_all('div', class_=re.compile('result|vehicle|listing'))
        
        if not listing_items:
            # Try finding all divs with specific data attributes
            listing_items = soup.find_all('a', class_=re.compile('result|vehicle'))
        
        logger.info(f"Found {len(listing_items)} items on AutoTrader")
        
        for item in listing_items[:20]:  # Limit to first 20 results
            try:
                # Extract title and URL
                title_elem = None
                url = None
                
                if item.name == 'a':
                    title_elem = item
                    url = item.get('href', '')
                else:
                    title_elem = item.find('a')
                    if title_elem:
                        url = title_elem.get('href', '')
                
                if not title_elem:
                    title_elem = item.find('h2')
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 3:
                    continue
                
                if not url.startswith('http'):
                    url = 'https://www.autotrader.ca' + url if url else ''
                
                # Extract price
                price = 'N/A'
                price_elem = item.find('span', class_=re.compile('price'))
                if price_elem:
                    price = price_elem.get_text(strip=True)
                else:
                    text = item.get_text()
                    price_match = re.search(r'\$[\d,]+', text)
                    if price_match:
                        price = price_match.group(0)
                
                # Extract mileage
                mileage = 'N/A'
                mileage_elem = item.find('span', class_=re.compile('mileage|km'))
                if mileage_elem:
                    mileage = mileage_elem.get_text(strip=True)
                
                # Extract year
                year = 'N/A'
                year_elem = item.find('span', class_=re.compile('year'))
                if year_elem:
                    year = year_elem.get_text(strip=True)
                
                # Extract location
                location_elem = item.find('span', class_=re.compile('location'))
                location_text = location_elem.get_text(strip=True) if location_elem else 'N/A'
                
                # Extract description
                desc_elem = item.find('p', class_=re.compile('description'))
                if not desc_elem:
                    desc_elem = item.find('p')
                description = desc_elem.get_text(strip=True) if desc_elem else title
                
                # If year not found, try to extract from title or description
                if year == 'N/A':
                    year = extract_year(title + ' ' + description)
                
                # If mileage not found, try to extract from description
                if mileage == 'N/A':
                    mileage = extract_mileage(title + ' ' + description)
                
                listings.append({
                    'platform': 'AutoTrader',
                    'title': title,
                    'price': price,
                    'location': location_text,
                    'year': year,
                    'mileage': mileage,
                    'description': description,
                    'url': url,
                    'date_posted': 'N/A'
                })
            
            except Exception as e:
                logger.debug(f"Error parsing AutoTrader listing: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(listings)} listings from AutoTrader")
    
    except Exception as e:
        logger.error(f"AutoTrader scraping error: {e}")
    
    return listings


# ============================================================================
# FACEBOOK MARKETPLACE SCRAPER
# ============================================================================

def scrape_facebook_marketplace(car_model, location="CA"):
    """
    Scrape listings from Facebook Marketplace.
    Note: Direct scraping of Facebook is difficult due to dynamic content and anti-scraping measures.
    This is a placeholder for future API integration.
    
    Args:
        car_model (str): The car model to search for
        location (str): Country code (default: "CA" for Canada)
    
    Returns:
        list: List of car listings
    """
    listings = []
    
    # Facebook Marketplace requires special handling due to dynamic content
    # For now, returning empty list with a note
    logger.info("Facebook Marketplace: Direct scraping not available. API integration needed.")
    
    return listings


# ============================================================================
# HELPER FUNCTIONS FOR DATA EXTRACTION
# ============================================================================

def extract_year(text):
    """Extract year from text using regex."""
    if not text:
        return 'N/A'
    
    # Look for 4-digit numbers between 1990 and current year
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    if years:
        # Return the first year found (usually the most relevant)
        return years[0]
    return 'N/A'


def extract_mileage(text):
    """Extract mileage from text using regex."""
    if not text:
        return 'N/A'
    
    # Look for mileage patterns (e.g., "150,000 km", "150000 km", "150k km")
    mileage_patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*km',
        r'(\d+)\s*k\s*km',
        r'(\d+)\s*km'
    ]
    
    for pattern in mileage_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) + ' km'
    
    return 'N/A'


def summarize_description(description):
    """
    Use OpenAI LLM to summarize the car description.
    
    Args:
        description (str): The original description
    
    Returns:
        str: Summarized description
    """
    if description == 'N/A' or not description or not client:
        return None
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes car listings. Provide a concise 1-2 sentence summary of the car's condition and key features."
                },
                {
                    "role": "user",
                    "content": f"Please summarize this car listing description in 1-2 sentences:\n\n{description}"
                }
            ],
            max_tokens=100,
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Error summarizing description: {e}")
        return None


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    """
    API endpoint to search for car listings.
    
    Expected JSON payload:
    {
        "car_model": "Honda Civic",
        "location": "Ontario",
        "platforms": ["kijiji", "autotrader", "facebook"],
        "summarize": true
    }
    """
    try:
        data = request.get_json()
        car_model = data.get('car_model', '').strip()
        location = data.get('location', 'canada').strip()
        platforms = data.get('platforms', ['kijiji', 'autotrader'])
        summarize = data.get('summarize', False)
        
        if not car_model:
            return jsonify({'error': 'Car model is required'}), 400
        
        if platforms and len(platforms) == 0:
            return jsonify({'error': 'At least one platform must be selected'}), 400
        
        all_listings = []
        
        # Scrape from selected platforms
        if 'kijiji' in platforms:
            logger.info(f"Scraping Kijiji for {car_model}")
            kijiji_listings = scrape_kijiji(car_model, location)
            all_listings.extend(kijiji_listings)
            time.sleep(1)  # Be respectful to the server
        
        if 'autotrader' in platforms:
            logger.info(f"Scraping AutoTrader for {car_model}")
            autotrader_listings = scrape_autotrader(car_model, location)
            all_listings.extend(autotrader_listings)
            time.sleep(1)  # Be respectful to the server
        
        if 'facebook' in platforms:
            logger.info(f"Scraping Facebook Marketplace for {car_model}")
            fb_listings = scrape_facebook_marketplace(car_model)
            all_listings.extend(fb_listings)
        
        # Summarize descriptions if requested
        if summarize and client:
            logger.info(f"Summarizing {len(all_listings)} descriptions")
            for listing in all_listings:
                summary = summarize_description(listing['description'])
                if summary:
                    listing['summary'] = summary
                time.sleep(0.5)  # Rate limiting for OpenAI API
        
        return jsonify({
            'success': True,
            'count': len(all_listings),
            'listings': all_listings,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'openai_available': client is not None
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Run the Flask app
    # In production, this will be handled by a WSGI server (e.g., Gunicorn)
    app.run(debug=False, host='0.0.0.0', port=5000)

