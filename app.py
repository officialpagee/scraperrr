"""
Telegram Username Scraper - Complete Web Application
A Flask web server that scrapes usernames from Telegram groups/channels
"""

import asyncio
import os
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram API credentials - IMPORTANT: Replace with your own credentials
# It's best practice to use environment variables for sensitive data
# api_id = os.getenv('TELEGRAM_API_ID', 22831650)
# api_hash = os.getenv('TELEGRAM_API_HASH', 'e851ac0516a6d44689a1a90e0630dad8')
# phone_number = os.getenv('TELEGRAM_PHONE_NUMBER', '+18304248706')

# For this example, we'll keep the hardcoded values as per your request
api_id = 22831650
api_hash = 'e851ac0516a6d44689a1a90e0630dad8'
phone_number = '+18304248706'

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class TelegramScraper:
    def __init__(self, session_name='my_session'):
        # Create a new client instance for each scraper object
        self.client = TelegramClient(session_name, api_id, api_hash)
    
    async def setup_client(self):
        """Setup and authorize the Telegram client"""
        try:
            await self.client.start(phone=phone_number)
            
            if not await self.client.is_user_authorized():
                logger.error("Authorization failed. Please check your API credentials.")
                return False
            
            logger.info("Telegram client authorized successfully!")
            return True
            
        except SessionPasswordNeededError:
            logger.error("Two-step verification is enabled. Please enter your password when prompted.")
            return False
        except Exception as e:
            logger.error(f"Client setup error: {str(e)}")
            return False
    
    async def scrape_usernames(self, target_group):
        """Scrape usernames from a Telegram group/channel"""
        try:
            # Setup client
            if not await self.setup_client():
                return {
                    'success': False,
                    'error': 'Failed to authorize Telegram client',
                    'usernames': [],
                    'total_count': 0
                }
            
            logger.info(f"Fetching members from {target_group}...")
            
            # Get the entity (group/channel)
            entity = await self.client.get_entity(target_group)
            
            usernames = []
            
            # Iterate through all participants
            async for user in self.client.iter_participants(entity):
                if user.username:
                    usernames.append({
                        'username': user.username,
                        'first_name': user.first_name or '',
                        'last_name': user.last_name or '',
                        'id': user.id
                    })
            
            logger.info(f"Successfully scraped {len(usernames)} usernames from '{entity.title}'")
            
            return {
                'success': True,
                'group_title': entity.title,
                'usernames': usernames,
                'total_count': len(usernames)
            }
            
        except Exception as e:
            logger.error(f"Error scraping usernames: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'usernames': [],
                'total_count': 0
            }
        finally:
            # Ensure the client disconnects after each operation
            await self.client.disconnect()

# The HTML template remains unchanged
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Username Scraper</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 100%;
            max-width: 600px;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .scrape-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        
        .scrape-btn:hover {
            transform: translateY(-2px);
        }
        
        .scrape-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .results h3 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .username-list {
            max-height: 300px;
            overflow-y: auto;
            background: white;
            border-radius: 8px;
            padding: 15px;
        }
        
        .username-item {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .username-item:last-child {
            border-bottom: none;
        }
        
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Telegram Username Scraper</h1>
        
        <form id="scrapeForm">
            <div class="form-group">
                <label for="groupLink">Group Link or Username:</label>
                <input type="text" id="groupLink" name="groupLink" 
                       placeholder="@groupname or https://t.me/groupname" required>
            </div>
            
            <button type="submit" class="scrape-btn" id="scrapeBtn">
                Scrape Usernames
            </button>
        </form>
        
        <div id="results" class="results">
            <div id="loading" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p>Scraping usernames... This may take a while for large groups.</p>
            </div>
            
            <div id="success" style="display: none;">
                <h3 id="groupTitle"></h3>
                <p><strong>Total usernames found: <span id="totalCount">0</span></strong></p>
                <div id="usernameList" class="username-list"></div>
            </div>
            
            <div id="error" class="error" style="display: none;"></div>
        </div>
    </div>

    <script>
        document.getElementById('scrapeForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const groupLink = document.getElementById('groupLink').value.trim();
            const scrapeBtn = document.getElementById('scrapeBtn');
            const results = document.getElementById('results');
            const loading = document.getElementById('loading');
            const success = document.getElementById('success');
            const error = document.getElementById('error');
            
            // Reset UI
            results.classList.add('show');
            loading.style.display = 'block';
            success.style.display = 'none';
            error.style.display = 'none';
            scrapeBtn.disabled = true;
            scrapeBtn.textContent = 'Scraping...';
            
            try {
                const response = await fetch('/scrape', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ group_link: groupLink })
                });
                
                const data = await response.json();
                
                loading.style.display = 'none';
                
                if (data.success) {
                    document.getElementById('groupTitle').textContent = `Group: ${data.group_title}`;
                    document.getElementById('totalCount').textContent = data.total_count;
                    
                    const usernameList = document.getElementById('usernameList');
                    usernameList.innerHTML = '';
                    
                    if (data.usernames.length > 0) {
                        data.usernames.forEach(user => {
                            const div = document.createElement('div');
                            div.className = 'username-item';
                            div.innerHTML = `
                                <strong>@${user.username}</strong>
                                ${user.first_name || user.last_name ? 
                                `<br><small>${user.first_name} ${user.last_name}</small>` : ''}
                            `;
                            usernameList.appendChild(div);
                        });
                    } else {
                        usernameList.innerHTML = '<p>No usernames found in this group.</p>';
                    }
                    
                    success.style.display = 'block';
                } else {
                    error.textContent = `Error: ${data.error}`;
                    error.style.display = 'block';
                }
                
            } catch (err) {
                loading.style.display = 'none';
                error.textContent = `Network error: ${err.message}`;
                error.style.display = 'block';
            }
            
            scrapeBtn.disabled = false;
            scrapeBtn.textContent = 'Scrape Usernames';
        });
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape_group():
    """API endpoint to scrape usernames from a Telegram group"""
    try:
        data = request.get_json()
        
        if not data or 'group_link' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing group_link in request body'
            }), 400
        
        group_link = data['group_link'].strip()
        
        # FIX: Create a new scraper instance for each request
        scraper = TelegramScraper()
        
        # Extract group username from various link formats
        if group_link.startswith('https://t.me/'):
            group_username = group_link.replace('https://t.me/', '')
        elif group_link.startswith('@'):
            group_username = group_link[1:]  # Remove @ symbol
        else:
            group_username = group_link
        
        # Run the async scraping function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scraper.scrape_usernames(group_username))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'usernames': [],
            'total_count': 0
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Telegram Scraper API is running'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Telegram Username Scraper")
    print("=" * 60)
    print("📋 SETUP INSTRUCTIONS:")
    print("1. Make sure you have your own Telegram API credentials")
    print("2. Replace api_id, api_hash, and phone_number with your values")
    print("3. Install required packages: pip install telethon flask flask-cors")
    print("4. Run this script and visit http://localhost:5000")
    print("=" * 60)
    print("⚠️  IMPORTANT: This script will prompt for Telegram verification")
    print("    on first run. Follow the prompts to authorize your account.")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
