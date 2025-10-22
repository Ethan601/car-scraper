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
import sys
import json

# Get the absolute path to the project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Initialize Flask app with explicit template folder
app = Flask(__name__, template_folder=TEMPLATE_DIR)
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        logger.info(f"Scraping Kijiji: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            logger.warning(f"Kijiji request failed with status {response.status_code}")
            return listings
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Kijiji listing selectors - try multiple approaches
        listing_items = []
        
        # Try different selectors in order of likelihood
        selectors = [
            ('div', {'data-testid': 'listing'}),
            ('a', {'class': re.compile(r'.*listing.*', re.I)}),
            ('div', {'class': re.compile(r'.*search-item.*', re.I)}),
            ('li', {'class': re.compile(r'.*result.*', re.I)}),
            ('div', {'class': re.compile(r'.*item.*', re.I)}),
        ]
        
        for tag, attrs in selectors:
            if tag == 'div' or tag == 'li':
                listing_items = soup.find_all(tag, attrs)
            else:
                listing_items = soup.find_all(tag, attrs)
            
            if listing_items:
                logger.info(f"Found {len(listing_items)} items on Kijiji using selector {tag} {attrs}")
                break
        
        if not listing_items:
            logger.warning("No listings found on Kijiji")
            return listings
        
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
                    title_elem = item.find('h2') or item.find('h3')
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 3:
                    continue
                
                # Make URL absolute
                if url and not url.startswith('http'):
                    url = 'https://www.kijiji.ca' + url
                
                # Extract price
                price = 'N/A'
                price_elem = item.find('span', class_=re.compile('price', re.I))
                if price_elem:
                    price = price_elem.get_text(strip=True)
                else:
                    text = item.get_text()
                    price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', text)
                    if price_match:
                        price = price_match.group(0)
                
                # Extract mileage/km
                mileage = 'N/A'
                text = item.get_text()
                km_match = re.search(r'(\d+(?:,\d+)?)\s*(?:km|KM|kilometers)', text)
                if km_match:
                    mileage = km_match.group(1) + ' km'
                
                # Extract year
                year = 'N/A'
                year_match = re.search(r'\b(19|20)\d{2}\b', title)
                if year_match:
                    year = year_match.group(0)
                
                # Extract description (first 200 chars of text)
                description = item.get_text(strip=True)
                if len(description) > 200:
                    description = description[:200] + '...'
                
                listings.append({
                    'title': title,
                    'price': price,
                    'mileage': mileage,
                    'year': year,
                    'description': description,
                    'url': url,
                    'source': 'Kijiji'
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        logger.info(f"Scraping AutoTrader: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            logger.warning(f"AutoTrader request failed with status {response.status_code}")
            return listings
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all text content to extract data
        page_text = soup.get_text()
        
        # Find all links that look like car listings
        all_links = soup.find_all('a', href=re.compile(r'/cars/\d+'))
        
        logger.info(f"Found {len(all_links)} car links on AutoTrader")
        
        # Extract listing data from links
        seen_titles = set()
        
        for link in all_links[:30]:  # Limit to first 30 results
            try:
                # Get the title
                title = link.get_text(strip=True)
                
                if not title or len(title) < 3 or title in seen_titles:
                    continue
                
                seen_titles.add(title)
                
                # Get URL
                url = link.get('href', '')
                if not url.startswith('http'):
                    url = 'https://www.autotrader.ca' + url
                
                # Find the parent container for this listing
                parent = link.find_parent('div', recursive=True)
                if not parent:
                    parent = link
                
                parent_text = parent.get_text()
                
                # Extract price
                price = 'N/A'
                price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', parent_text)
                if price_match:
                    price = price_match.group(0)
                
                # Extract mileage
                mileage = 'N/A'
                km_match = re.search(r'(\d+(?:,\d+)?)\s*(?:km|KM)', parent_text)
                if km_match:
                    mileage = km_match.group(1) + ' km'
                
                # Extract year from title
                year = 'N/A'
                year_match = re.search(r'\b(19|20)\d{2}\b', title)
                if year_match:
                    year = year_match.group(0)
                
                # Get description from parent text
                description = parent_text.strip()
                if len(description) > 200:
                    description = description[:200] + '...'
                
                listings.append({
                    'title': title,
                    'price': price,
                    'mileage': mileage,
                    'year': year,
                    'description': description,
                    'url': url,
                    'source': 'AutoTrader'
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

def scrape_facebook_marketplace(car_model, location="canada"):
    """
    Scrape used car listings from Facebook Marketplace.
    Note: Facebook Marketplace requires authentication and JavaScript rendering.
    This is a simplified version that may have limited results.
    
    Args:
        car_model (str): The car model to search for
        location (str): Location to search in
    
    Returns:
        list: List of car listings with extracted data
    """
    listings = []
    
    try:
        # Facebook Marketplace search URL
        search_url = f"https://www.facebook.com/marketplace/search/?query={car_model}%20{location}&category_filter_selection=%5B%22VEHICLES%22%5D"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        logger.info(f"Attempting Facebook Marketplace scrape: {search_url}")
        
        # Facebook requires authentication and JavaScript rendering
        # This simplified version may not return results
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.warning(f"Facebook Marketplace request failed with status {response.status_code}")
            return listings
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find listing elements
        listing_items = soup.find_all('div', class_=re.compile('listing|item', re.I))
        
        logger.info(f"Found {len(listing_items)} items on Facebook Marketplace")
        
        for item in listing_items[:20]:
            try:
                # Extract data from item
                title = item.get_text(strip=True)
                
                if not title or len(title) < 3:
                    continue
                
                # Extract price
                price = 'N/A'
                price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', title)
                if price_match:
                    price = price_match.group(0)
                
                listings.append({
                    'title': title[:100],
                    'price': price,
                    'mileage': 'N/A',
                    'year': 'N/A',
                    'description': 'Facebook Marketplace listing',
                    'url': 'https://www.facebook.com/marketplace',
                    'source': 'Facebook Marketplace'
                })
            
            except Exception as e:
                logger.debug(f"Error parsing Facebook Marketplace listing: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(listings)} listings from Facebook Marketplace")
    
    except Exception as e:
        logger.warning(f"Facebook Marketplace scraping error: {e}")
    
    return listings


# ============================================================================
# SUMMARIZE DESCRIPTION WITH LLM
# ============================================================================

def summarize_description(description):
    """
    Summarize a car description using OpenAI LLM.
    
    Args:
        description (str): The description to summarize
    
    Returns:
        str: Summarized description
    """
    if not client or not description or len(description) < 20:
        return description
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes car listings. Keep summaries concise (1-2 sentences) and focus on key features and condition."
                },
                {
                    "role": "user",
                    "content": f"Summarize this car listing description in 1-2 sentences:\n\n{description}"
                }
            ],
            max_tokens=100,
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.warning(f"Error summarizing description: {e}")
        return description


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    template_path = os.path.join(TEMPLATE_DIR, 'index.html')
    template_exists = os.path.exists(template_path)
    
    return jsonify({
        'openai_available': client is not None,
        'status': 'ok',
        'template_dir': TEMPLATE_DIR,
        'template_exists': template_exists,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/search', methods=['POST'])
def search_listings():
    """
    Search for car listings across multiple platforms.
    
    Expected JSON body:
    {
        "car_model": "Honda Civic",
        "location": "canada",
        "summarize": true
    }
    """
    try:
        data = request.get_json()
        car_model = data.get('car_model', '').strip()
        location = data.get('location', 'canada').strip()
        summarize = data.get('summarize', False)
        
        if not car_model:
            return jsonify({'error': 'car_model is required'}), 400
        
        logger.info(f"Search request: car_model={car_model}, location={location}, summarize={summarize}")
        
        # Scrape all platforms
        all_listings = []
        
        # Scrape Kijiji
        logger.info("Starting Kijiji scrape...")
        kijiji_listings = scrape_kijiji(car_model, location)
        all_listings.extend(kijiji_listings)
        logger.info(f"Kijiji returned {len(kijiji_listings)} listings")
        
        # Scrape AutoTrader
        logger.info("Starting AutoTrader scrape...")
        autotrader_listings = scrape_autotrader(car_model, location)
        all_listings.extend(autotrader_listings)
        logger.info(f"AutoTrader returned {len(autotrader_listings)} listings")
        
        # Scrape Facebook Marketplace
        logger.info("Starting Facebook Marketplace scrape...")
        facebook_listings = scrape_facebook_marketplace(car_model, location)
        all_listings.extend(facebook_listings)
        logger.info(f"Facebook Marketplace returned {len(facebook_listings)} listings")
        
        # Summarize descriptions if requested
        if summarize and client:
            logger.info("Summarizing descriptions...")
            for listing in all_listings:
                listing['description'] = summarize_description(listing['description'])
        
        logger.info(f"Total listings found: {len(all_listings)}")
        
        return jsonify({
            'success': True,
            'car_model': car_model,
            'location': location,
            'total_listings': len(all_listings),
            'listings': all_listings,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # For local development
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

