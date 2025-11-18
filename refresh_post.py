import requests
import time
import random
import logging
from datetime import datetime
import re
from bs4 import BeautifulSoup
import os
import sys
import json

# ========================================
# GITHUB ACTIONS CONFIGURATION
# ========================================
# Check if running on GitHub Actions
IS_GITHUB_ACTIONS = 'GITHUB_ACTIONS' in os.environ

def load_cookies():
    """Load cookies from GitHub Secrets or local file"""
    cookies = {}
    
    # Try GitHub Secrets first
    if IS_GITHUB_ACTIONS:
        print("🚀 Running on GitHub Actions")
        COOKIES_JSON = os.getenv('QATAR_COOKIES')
        if COOKIES_JSON:
            try:
                cookies = json.loads(COOKIES_JSON)
                print(f"✅ Loaded {len(cookies)} cookies from GitHub Secrets")
                return cookies
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing cookies from GitHub Secrets: {e}")
        else:
            print("❌ No cookies found in GitHub Secrets")
    
    # Try local cookies file
    local_cookie_file = "qatar_cookies.json"
    if os.path.exists(local_cookie_file):
        try:
            with open(local_cookie_file, 'r') as f:
                cookies = json.load(f)
            print(f"✅ Loaded {len(cookies)} cookies from {local_cookie_file}")
            return cookies
        except Exception as e:
            print(f"❌ Error loading cookies from {local_cookie_file}: {e}")
    
    # No cookies found
    print("💥 No cookies found in GitHub Secrets or local file")
    print(f"📁 Create {local_cookie_file} with your cookies JSON")
    return None

def load_bump_url():
    """Load bump URL from file or environment variable"""
    # Try from environment variable first
    bump_url = os.getenv('BUMP_URL')
    if bump_url:
        print(f"✅ Loaded bump URL from environment: {bump_url}")
        return bump_url
    
    # Try from local file
    bump_file = "bump_url.txt"
    if os.path.exists(bump_file):
        try:
            with open(bump_file, 'r') as f:
                bump_url = f.read().strip()
            if bump_url:
                print(f"✅ Loaded bump URL from {bump_file}: {bump_url}")
                return bump_url
        except Exception as e:
            print(f"❌ Error loading bump URL from {bump_file}: {e}")
    
    # Try from JSON config file
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            if config.get('bump_url'):
                print(f"✅ Loaded bump URL from {config_file}: {config['bump_url']}")
                return config['bump_url']
        except Exception as e:
            print(f"❌ Error loading config from {config_file}: {e}")
    
    print("💥 No bump URL found")
    print("📁 Create bump_url.txt with your bump URL or set BUMP_URL environment variable")
    return None

COOKIES = load_cookies()
BUMP_URL = load_bump_url()

# ========================================
# APPLICATION CONFIGURATION
# ========================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36",
]

MAX_RETRIES = 3
MAX_WAIT = 15

# ========================================
# LOGGING SETUP
# ========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # GitHub Actions captures stdout
    ]
)

session = requests.Session()

# ========================================
# COOKIE FINDER SCRIPT
# ========================================
COOKIE_FINDER_SCRIPT = """// === QATAR LIVING COOKIE FINDER ===
// 1. Go to https://www.qatarliving.com
// 2. Make sure you're logged in
// 3. Press F12 → Console
// 4. Paste this code and press Enter
// 5. Copy the JSON output to qatar_cookies.json

var cookies = document.cookie.split(';');
var cookieObj = {};
cookies.forEach((cookie) => {
    var [name, value] = cookie.trim().split('=');
    cookieObj[name] = value || '';
});
console.log('Copy this JSON to qatar_cookies.json:');
console.log(JSON.stringify(cookieObj));
copy(JSON.stringify(cookieObj));
console.log('✅ JSON copied to clipboard!');
"""

# ========================================
# URL PARSING FUNCTIONS
# ========================================
def parse_bump_url(bump_url):
    """Extract node ID and destination from bump URL"""
    try:
        # Parse the URL to extract components
        if '?' in bump_url:
            base_url, query_string = bump_url.split('?', 1)
        else:
            base_url = bump_url
            query_string = ""
        
        # Extract node ID
        node_match = re.search(r'/bump/node/(\d+)', base_url)
        if not node_match:
            print("❌ Invalid bump URL - no node ID found")
            return None
        
        node_id = node_match.group(1)
        
        # Extract destination from query parameters
        destination = None
        if query_string:
            params = query_string.split('&')
            for param in params:
                if param.startswith('destination='):
                    destination = param.split('=', 1)[1]
                    break
        
        if not destination:
            print("❌ No destination found in URL")
            return None
        
        print(f"🔗 Parsed URL - Node ID: {node_id}, Destination: {destination}")
        
        return {
            'node_id': node_id,
            'destination': destination,
            'bump_url': base_url,
            'full_url': bump_url
        }
    
    except Exception as e:
        print(f"❌ Error parsing bump URL: {e}")
        return None

# ========================================
# STEP 1: Test Authentication
# ========================================
def test_cookies():
    """Test if cookies provide valid authentication"""
    try:
        # Simple test by accessing the homepage
        homepage_url = "https://www.qatarliving.com"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml",
        }
        response = session.get(homepage_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Check for logout link or user-specific content
            if 'logout' in response.text.lower() or 'my account' in response.text.lower():
                print("✅ Authentication: PASSED - User is logged in")
                return True
            else:
                print("❌ Authentication: FAILED - Not logged in")
                return False
        else:
            print(f"❌ Authentication: FAILED - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

# ========================================
# STEP 2: Get CSRF Token from Job Page
# ========================================
def get_csrf_token(destination):
    try:
        job_page_url = f"https://www.qatarliving.com{destination}"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html",
            "Referer": "https://www.qatarliving.com/classifieds"
        }
        response = session.get(job_page_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Failed to load job page: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for form_token in hidden input
        token_input = soup.find("input", {"name": "form_token"})
        if token_input and token_input.get("value"):
            token = token_input["value"]
            print(f"🔑 CSRF Token found: {token[:20]}...")
            return token

        # Alternative: look for form_build_id
        build_id = soup.find("input", {"name": "form_build_id"})
        if build_id and build_id.get("value"):
            print(f"🔑 Form Build ID found: {build_id['value'][:20]}...")
            return build_id["value"]

        print("❌ No CSRF token or form_build_id found")
        return None

    except Exception as e:
        print(f"❌ Error fetching CSRF: {e}")
        return None

# ========================================
# STEP 3: Perform Bump (POST with CSRF)
# ========================================
def refresh_post(url_info):
    csrf_token = get_csrf_token(url_info['destination'])
    if not csrf_token:
        print("💥 Cannot proceed without CSRF token")
        return False

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.qatarliving.com{url_info['destination']}",
                "Origin": "https://www.qatarliving.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # Try POST first
            data = {
                "form_id": "classified_bump_form",
                "form_token": csrf_token,
                "form_build_id": csrf_token,  # sometimes reused
                "bump": "Bump to top",
                "destination": url_info['destination']
            }

            print(f"🔄 Attempt {attempt}/{MAX_RETRIES} (POST bump)...")
            response = session.post(
                url_info['bump_url'],
                headers=headers,
                data=data,
                timeout=30,
                allow_redirects=True
            )

            print(f"📊 Status: {response.status_code}")
            print(f"📍 Final URL: {response.url}")

            if response.status_code in [200, 302]:
                if any(word in response.text.lower() for word in ["bumped", "success", "refreshed"]):
                    print("✅ SUCCESS: Post bumped via POST!")
                    logging.info("Post bumped successfully via POST")
                    return True
                if url_info['destination'] in response.url:
                    print("✅ SUCCESS: Redirected to job page after bump")
                    logging.info("Redirected to job page - bump likely succeeded")
                    return True

            # Fallback: Try GET if POST fails
            if attempt == 1:
                print("⚠️ POST failed, trying GET fallback...")
                get_url = f"{url_info['bump_url']}?destination={url_info['destination']}"
                get_response = session.get(get_url, headers=headers, timeout=30)
                if any(word in get_response.text.lower() for word in ["bumped", "success", "refreshed"]) or url_info['destination'] in get_response.url:
                    print("✅ SUCCESS: Post bumped via GET fallback!")
                    return True

        except Exception as e:
            print(f"❌ Error on attempt {attempt}: {e}")
            logging.error(f"Attempt {attempt} failed: {e}")

        if attempt < MAX_RETRIES:
            wait = random.uniform(5, MAX_WAIT)
            print(f"⏳ Waiting {wait:.1f}s before retry...")
            time.sleep(wait)

    print("🚫 All attempts failed")
    return False

# ========================================
# MAIN
# ========================================
if __name__ == "__main__":
    print("🔁 Qatar Living Auto-Refresh Job Started")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    if not COOKIES:
        print("💥 No cookies available")
        if not IS_GITHUB_ACTIONS:
            print("-" * 50)
            print("🔄 Need fresh cookies? Run this in browser console:")
            print(COOKIE_FINDER_SCRIPT)
        sys.exit(1)

    if not BUMP_URL:
        print("💥 No bump URL available")
        print("📝 Create bump_url.txt with your URL like:")
        print("https://www.qatarliving.com/bump/node/46590548?destination=/jobseeker/username/job-name")
        sys.exit(1)

    # Set cookies globally
    for name, value in COOKIES.items():
        session.cookies.set(name, value, domain=".qatarliving.com")

    # Parse the bump URL
    url_info = parse_bump_url(BUMP_URL)
    if not url_info:
        sys.exit(1)

    # Test authentication
    if not test_cookies():
        print("💥 Authentication failed - cookies may be expired")
        sys.exit(1)

    print(f"🎯 Target URL: {BUMP_URL}")
    print("-" * 50)

    # Perform the bump
    if refresh_post(url_info):
        print("🎉 Refresh completed successfully!")
        sys.exit(0)
    else:
        print("💥 Refresh failed")
        sys.exit(1)

    print("-" * 50)
    print(f"🕒 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")