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
    """Load bump URL from GitHub Secrets or local file"""
    # Try from GitHub Secrets first (for GitHub Actions)
    if IS_GITHUB_ACTIONS:
        print("🔍 Checking for bump URL in GitHub Secrets...")
        bump_url = os.getenv('BUMP_URL')
        if bump_url:
            print(f"✅ Loaded bump URL from GitHub Secrets: {bump_url}")
            return bump_url
        else:
            print("ℹ️ BUMP_URL not found in GitHub Secrets, checking local files...")
    
    # Try from environment variable (for local development)
    bump_url = os.getenv('BUMP_URL')
    if bump_url:
        print(f"✅ Loaded bump URL from environment variable: {bump_url}")
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
    print("📁 For GitHub Actions: Set BUMP_URL as GitHub Secret")
    print("📁 For local development: Create bump_url.txt or set BUMP_URL environment variable")
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


def check_cookie_status():
    """Check what cookies we have and their status"""
    print("🔍 Checking cookie status...")
    
    # Count cookies
    print(f"📊 Total cookies loaded: {len(COOKIES)}")
    
    # List important cookies
    important_cookies = ['qatarliving-sso-token', 'qat', '_ga', '_gid']
    for cookie in important_cookies:
        if cookie in COOKIES:
            value = COOKIES[cookie]
            preview = value[:50] + "..." if len(value) > 50 else value
            print(f"   ✅ {cookie}: {preview}")
        else:
            print(f"   ❌ {cookie}: MISSING")
    
    # Check if cookies look valid
    if 'qatarliving-sso-token' in COOKIES and 'qat' in COOKIES:
        print("✅ Essential cookies present")
        return True
    else:
        print("❌ Missing essential cookies")
        return False

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
        # Try to access a page that requires login
        test_url = "https://www.qatarliving.com/user"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html",
        }
        
        print("🔐 Testing authentication...")
        response = session.get(test_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Failed to access user page: {response.status_code}")
            return False
        
        # Check if we're logged in by looking for common elements
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for logout link (indicates we're logged in)
        logout_links = soup.find_all('a', href=lambda href: href and 'logout' in href.lower())
        
        # Look for user profile elements
        user_elements = soup.find_all(['a', 'div'], class_=lambda c: c and any(x in str(c).lower() for x in ['user', 'profile', 'account']))
        
        # Check page title or content for login indicators
        page_text = response.text.lower()
        
        # Check for "My Account" or similar
        if ('my account' in page_text or 
            'logout' in page_text or 
            logout_links or 
            user_elements):
            print("✅ Authentication: SUCCESS - User is logged in")
            return True
        else:
            print("❌ Authentication: FAILED - Not logged in")
            print("💡 Quick check of page content:")
            print(f"   Page contains 'logout': {'logout' in page_text}")
            print(f"   Page contains 'my account': {'my account' in page_text}")
            print(f"   Found {len(logout_links)} logout links")
            print(f"   Found {len(user_elements)} user profile elements")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        # If we can't test properly, assume it might work and let the bump attempt fail
        print("⚠️ Could not verify authentication, proceeding with caution...")
        return True  
    
def extract_username():
    """Extract and display logged-in username"""
    try:
        # Decode JWT token from qat cookie to get username
        if 'qat' in COOKIES:
            try:
                # The qat cookie is a JWT token, we can decode the middle part (payload)
                qat_token = COOKIES['qat']
                # Split JWT token (header.payload.signature)
                parts = qat_token.split('.')
                if len(parts) == 3:
                    # Decode the payload (middle part)
                    import base64
                    import json as json_module
                    
                    # JWT uses base64url encoding, need to add padding if necessary
                    payload = parts[1]
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding
                    
                    payload_decoded = base64.b64decode(payload)
                    payload_json = json_module.loads(payload_decoded)
                    
                    # Extract username from JWT payload
                    if 'user' in payload_json:
                        user_data = payload_json['user']
                        if 'alias' in user_data:
                            return user_data['alias']
                        elif 'name' in user_data:
                            return user_data['name']
                        elif 'email' in user_data:
                            return user_data['email'].split('@')[0]
                            
            except Exception as e:
                print(f"⚠️ Could not decode JWT token: {e}")
        
        # Try to access user profile page
        profile_url = "https://www.qatarliving.com/user"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html",
        }
        
        response = session.get(profile_url, headers=headers, timeout=15)
        if response.status_code != 200:
            # Try alternative profile endpoints
            endpoints = [
                "https://www.qatarliving.com/my-account",
                "https://www.qatarliving.com/account",
                "https://www.qatarliving.com/profile"
            ]
            
            for endpoint in endpoints:
                response = session.get(endpoint, headers=headers, timeout=10)
                if response.status_code == 200:
                    break
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 1: Look for user profile link in navigation
        profile_links = soup.find_all('a', href=lambda href: href and '/user/' in href)
        for link in profile_links:
            if link.text and link.text.strip() and link.text.strip() != "My Account":
                username = link.text.strip()
                if username and len(username) > 1:
                    return username
        
        # Method 2: Look for username in meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name') in ['author', 'twitter:creator'] and meta.get('content'):
                username = meta.get('content')
                if username and '@' in username:
                    username = username.replace('@', '')
                return username
        
        # Method 3: Look for username in page content
        # Try to find text that looks like a username (not email, no spaces, etc.)
        import re
        page_text = response.text
        
        # Look for patterns like "Hello, username" or "Welcome, username"
        username_patterns = [
            r'(?:Hello|Welcome|Hi)[,\s]+([a-zA-Z0-9_\-]+)',
            r'(?:Logged in as|You are logged in as|Signed in as)[:\s]+([a-zA-Z0-9_\-]+)',
            r'user/([a-zA-Z0-9_\-]+)',
        ]
        
        for pattern in username_patterns:
            matches = re.search(pattern, page_text, re.IGNORECASE)
            if matches:
                username = matches.group(1)
                if username and len(username) > 2 and username.lower() not in ['sign', 'login', 'logout']:
                    return username
        
        # Method 4: Try to extract from destination URL (from bump URL)
        if 'url_info' in globals() and url_info:
            dest_parts = url_info['destination'].split('/')
            if len(dest_parts) >= 3:
                # Usually format is /jobseeker/username/job-title
                if dest_parts[1] == 'jobseeker':
                    username = dest_parts[2]
                    if username and username != 'jobseeker':
                        return username
        
        # Method 5: Look for user avatar or profile image with alt text
        img_tags = soup.find_all('img', alt=True)
        for img in img_tags:
            alt_text = img.get('alt', '')
            if alt_text and 'profile' in alt_text.lower() or 'avatar' in alt_text.lower():
                username = alt_text.replace('Profile picture of', '').replace('Avatar of', '').strip()
                if username and len(username) > 1:
                    return username
        
        return None
        
    except Exception as e:
        print(f"⚠️ Could not extract username: {e}")
        return None
    
# Continue anyway and let bump fail if cookies are bad
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

    # Check cookie status first
    if not check_cookie_status():
        print("⚠️ Cookie validation failed - some essential cookies missing")

    # Set cookies globally
    for name, value in COOKIES.items():
        session.cookies.set(name, value, domain=".qatarliving.com")

    # Parse the bump URL
    url_info = parse_bump_url(BUMP_URL)
    if not url_info:
        sys.exit(1)

    # Test authentication
        # Test authentication
        # Test authentication
    if not test_cookies():
        print("💥 Authentication failed - cookies may be expired or invalid")
        print("🔧 Try getting fresh cookies:")
        print("   1. Login to Qatar Living in browser")
        print("   2. Open Developer Tools (F12)")
        print("   3. Go to Console tab")
        print("   4. Paste the cookie extractor script from above")
        sys.exit(1)
    else:
        # Extract and display username
        username = extract_username()
        if username:
            print(f"👤 Logged in as: {username}")
            # Also try to get more user info from the qat cookie
            if 'qat' in COOKIES:
                try:
                    qat_token = COOKIES['qat']
                    parts = qat_token.split('.')
                    if len(parts) == 3:
                        import base64
                        import json as json_module
                        
                        payload = parts[1]
                        padding = 4 - len(payload) % 4
                        if padding != 4:
                            payload += '=' * padding
                        
                        payload_decoded = base64.b64decode(payload)
                        payload_json = json_module.loads(payload_decoded)
                        
                        if 'user' in payload_json:
                            user_data = payload_json['user']
                            if 'email' in user_data:
                                print(f"   📧 Email: {user_data['email']}")
                            if 'phone' in user_data:
                                print(f"   📞 Phone: {user_data['phone']}")
                except:
                    pass
        else:
            print("👤 User is logged in (could not extract username)")

    print(f"🎯 Target URL: {BUMP_URL}")
    print("-" * 50)

    # Rest of your code...

    # Perform the bump
    if refresh_post(url_info):
        print("🎉 Refresh completed successfully!")
        sys.exit(0)
    else:
        print("💥 Refresh failed")
        sys.exit(1)

    print("-" * 50)
    print(f"🕒 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")