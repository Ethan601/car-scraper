"""
Canadian Used Car Listing Scraper - Main Flask Application
This application collects used car listings from Kijiji, AutoTrader, and Facebook Marketplace.
Uses HTTP requests and BeautifulSoup for maximum compatibility.
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
        search_url = f"https://www.kijiji.ca/b-cars/{location}/{car_model.replace(' ', '%20')}/k0c174l0"
        
        logger.info(f"Scraping Kijiji: {search_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links containing the car model
        all_links = soup.find_all('a')
        car_links = [
            link for link in all_links 
            if link.get('href') and '/v-cars-trucks/' in link.get('href') and link.get_text().strip()
        ]
        
        logger.info(f"Found {len(car_links)} car links on Kijiji")
        
        for link in car_links[:12]:  # Limit to first 12 results
            try:
                title = link.get_text(strip=True)
                url = link.get('href', '')
                
                if not title or len(title) < 5:
                    continue
                
                # Make URL absolute
                if url and not url.startswith('http'):
                    url = 'https://www.kijiji.ca' + url
                
                # Extract year from title
                year = 'N/A'
                year_match = re.search(r'\b(19|20)\d{2}\b', title)
                if year_match:
                    year = year_match.group(0)
                
                # Extract price from title
                price = 'N/A'
                price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', title)
                if price_match:
                    price = price_match.group(0)
                
                # Extract mileage from title
                mileage = 'N/A'
                km_match = re.search(r'(\d+(?:,\d+)?)\s*(?:km|KM)', title)
                if km_match:
                    mileage = km_match.group(1) + ' km'
                
                # Try to get more details from the listing page
                if not price or price == 'N/A':
                    try:
                        detail_response = requests.get(url, headers=headers, timeout=5)
                        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                        detail_text = detail_soup.get_text()
                        
                        # Try to extract price from detail page
                        price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', detail_text)
                        if price_match:
                            price = price_match.group(0)
                        
                        # Try to extract mileage from detail page
                        if mileage == 'N/A':
                            km_match = re.search(r'(\d+(?:,\d+)?)\s*(?:km|KM)', detail_text)
                            if km_match:
                                mileage = km_match.group(1) + ' km'
                    except:
                        pass  # If detail page fails, just use what we have
                
                # Get description (first 200 chars of title)
                description = title
                if len(description) > 200:
                    description = description[:200] + '...'
                
                listings.append({
                    'title': title,
                    'price': price,
                    'mileage': mileage,
                    'year': year,
                    'description': description,
                    'url': url,
                    'platform': 'Kijiji',
                    'summary': None,
                    'date_posted': 'N/A'
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
        search_url = f"https://www.autotrader.ca/cars/?keyword={car_model.replace(' ', '+')}&prv={location}"
        
        logger.info(f"Scraping AutoTrader: {search_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract data from page text
        page_text = soup.get_text()
        
        # Look for price patterns in the page
        price_matches = re.findall(r'\$[\d,]+(?:\.\d{2})?', page_text)
        year_matches = re.findall(r'\b(20\d{2})\b', page_text)
        km_matches = re.findall(r'(\d+(?:,\d+)?)\s*(?:km|KM)', page_text, re.I)
        
        logger.info(f"Found {len(price_matches)} prices, {len(year_matches)} years, {len(km_matches)} mileage entries")
        
        # If we found some data, create listings from it
        if price_matches and year_matches:
            # Create listings from extracted data
            num_listings = min(len(price_matches), 8)
            for i in range(num_listings):
                try:
                    price = price_matches[i] if i < len(price_matches) else 'N/A'
                    year = year_matches[i] if i < len(year_matches) else 'N/A'
                    mileage = km_matches[i] + ' km' if i < len(km_matches) else 'N/A'
                    
                    listings.append({
                        'title': f"{year} {car_model}",
                        'price': price,
                        'mileage': mileage,
                        'year': year,
                        'description': f"Found on AutoTrader - {car_model}",
                        'url': search_url,
                        'platform': 'AutoTrader',
                        'summary': None,
                        'date_posted': 'N/A'
                    })
                except:
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
    Note: Facebook Marketplace requires authentication and is difficult to scrape.
    This is a simplified version with limited results.
    
    Args:
        car_model (str): The car model to search for
        location (str): Location to search in
    
    Returns:
        list: List of car listings with extracted data
    """
    listings = []
    
    try:
        logger.info(f"Attempting Facebook Marketplace scrape for {car_model}")
        
        # Facebook Marketplace is very difficult to scrape without authentication
        # For now, we'll return empty results
        logger.warning("Facebook Marketplace scraping is limited without authentication")
    
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
            'count': len(all_listings),
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

