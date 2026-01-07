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
# THEME CONFIGURATION
# ========================================
# ========================================
# THEME CONFIGURATION
# ========================================
class SpiderManTheme:
    # Color codes
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @staticmethod
    def print_header(text):
        print(f"\n{SpiderManTheme.RED}{SpiderManTheme.BOLD}🕷️ {text}{SpiderManTheme.END}")
        print(f"{SpiderManTheme.BLUE}{'═' * 60}{SpiderManTheme.END}")
    
    @staticmethod
    def print_success(text):
        print(f"{SpiderManTheme.GREEN}{SpiderManTheme.BOLD}{text}{SpiderManTheme.END}")
    
    @staticmethod
    def print_info(text):
        print(f"{SpiderManTheme.BLUE}{SpiderManTheme.BOLD}🕸️ {text}{SpiderManTheme.END}")
    
    @staticmethod
    def print_warning(text):
        print(f"{SpiderManTheme.YELLOW}{SpiderManTheme.BOLD}⚠️ {text}{SpiderManTheme.END}")
    
    @staticmethod
    def print_error(text):
        print(f"{SpiderManTheme.RED}{SpiderManTheme.BOLD}❌ {text}{SpiderManTheme.END}")
    
    @staticmethod
    def print_spider(text):
        print(f"{SpiderManTheme.PURPLE}{SpiderManTheme.BOLD}🕷️ {text}{SpiderManTheme.END}")
    
    @staticmethod
    def print_web(text):
        print(f"{SpiderManTheme.CYAN}{SpiderManTheme.BOLD}🕸️ {text}{SpiderManTheme.END}")
    
    @staticmethod
    def print_action(text):
        print(f"{SpiderManTheme.RED}{SpiderManTheme.BOLD}🎬 {text}{SpiderManTheme.END}")

# ========================================
# GITHUB ACTIONS CONFIGURATION
# ========================================
# Check if running on GitHub Actions
IS_GITHUB_ACTIONS = 'GITHUB_ACTIONS' in os.environ

def load_cookies():
    """Load cookies from GitHub Secrets or local file"""
    cookies = {}
    
    # Priority 1: GitHub Secrets (when running on GitHub Actions)
    if IS_GITHUB_ACTIONS:
        print("🚀 Running on GitHub Actions")
        print("🔍 Checking for cookies in GitHub Secrets...")
        COOKIES_JSON = os.getenv('QATAR_COOKIES')
        if COOKIES_JSON:
            try:
                cookies = json.loads(COOKIES_JSON)
                print(f"✅ Loaded {len(cookies)} cookies from GitHub Secrets")
                return cookies
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing cookies from GitHub Secrets: {e}")
        else:
            print("❌ QATAR_COOKIES not found in GitHub Secrets")
    
    # Priority 2: Local cookies file (for local development)
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
    print("💥 No cookies found from any source!")
    
    # Give specific instructions based on environment
    if IS_GITHUB_ACTIONS:
        print("📁 For GitHub Actions: Make sure you've set QATAR_COOKIES as a GitHub Secret")
        print("   Go to: Repository Settings → Secrets and variables → Actions")
        print("   Click 'New repository secret'")
        print("   Name: QATAR_COOKIES")
        print("   Value: Your cookies JSON (from the browser console)")
    else:
        print(f"📁 For local development: Create {local_cookie_file} with your cookies JSON")
        print("   Run the cookie extractor script in your browser console")
    
    return None

def load_bump_url():
    """Load bump URL from GitHub Secrets or local file"""
    bump_url = None
    
    # Priority 1: Check GitHub Secrets first (when running on GitHub Actions)
    if IS_GITHUB_ACTIONS:
        print("🚀 Running on GitHub Actions")
        print("🔍 Checking for bump URL in GitHub Secrets...")
        bump_url = os.getenv('BUMP_URL')
        if bump_url:
            print(f"✅ Loaded bump URL from GitHub Secrets: {bump_url[:60]}...")
            return bump_url
        else:
            print("❌ BUMP_URL not found in GitHub Secrets")
    
    # Priority 2: Check environment variable (for local development)
    bump_url = os.getenv('BUMP_URL')
    if bump_url:
        print(f"✅ Loaded bump URL from environment variable: {bump_url[:60]}...")
        return bump_url
    
    # Priority 3: Check local file (for local development)
    bump_file = "bump_url.txt"
    if os.path.exists(bump_file):
        try:
            with open(bump_file, 'r') as f:
                bump_url = f.read().strip()
            if bump_url:
                print(f"✅ Loaded bump URL from {bump_file}: {bump_url[:60]}...")
                return bump_url
        except Exception as e:
            print(f"❌ Error loading bump URL from {bump_file}: {e}")
    
    # Priority 4: Check JSON config file
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            if config.get('bump_url'):
                bump_url = config['bump_url']
                print(f"✅ Loaded bump URL from {config_file}: {bump_url[:60]}...")
                return bump_url
        except Exception as e:
            print(f"❌ Error loading config from {config_file}: {e}")
    
    # No bump URL found anywhere
    print("💥 No bump URL found from any source!")
    
    # Give specific instructions based on environment
    if IS_GITHUB_ACTIONS:
        print("📁 For GitHub Actions: Make sure you've set BUMP_URL as a GitHub Secret")
        print("   Go to: Repository Settings → Secrets and variables → Actions")
        print("   Click 'New repository secret'")
        print("   Name: BUMP_URL")
        print("   Value: Your full bump URL (e.g., https://www.qatarliving.com/bump/node/12345678?destination=...)")
    else:
        print("📁 For local development:")
        print("   1. Create bump_url.txt file with your bump URL")
        print("   2. Or set BUMP_URL environment variable")
        print("   3. Or create config.json with 'bump_url' field")
    
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
    SpiderManTheme.print_info(f"🔍 Checking cookie status...")
    
    # Count cookies
    SpiderManTheme.print_info(f"📊 Total cookies loaded: {len(COOKIES)}")
    
    # List important cookies
    important_cookies = ['qatarliving-sso-token', 'qat', '_ga', '_gid']
    for cookie in important_cookies:
        if cookie in COOKIES:
            value = COOKIES[cookie]
            preview = value[:50] + "..." if len(value) > 50 else value
            SpiderManTheme.print_info(f" {cookie}: {preview}")
        else:
            SpiderManTheme.print_warning(f" {cookie}: MISSING")
    
    # Check if cookies look valid
    if 'qatarliving-sso-token' in COOKIES and 'qat' in COOKIES:
        SpiderManTheme.print_info(" Essential cookies present")
        return True
    else:
        SpiderManTheme.print_warning(" Missing essential cookies")
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
            print(f"🔑 CSRF Token (form_token) found: {token[:20]}...")
            return token

        # Alternative: look for form_build_id
        build_id = soup.find("input", {"name": "form_build_id"})
        if build_id and build_id.get("value"):
            token = build_id["value"]
            print(f"🔑 Form Build ID (form_build_id) found: {token[:20]}...")
            return token
        
        # Try to find any hidden input with value
        hidden_inputs = soup.find_all("input", {"type": "hidden"})
        for hidden in hidden_inputs:
            if hidden.get("value") and len(hidden.get("value", "")) > 10:
                token = hidden["value"]
                name = hidden.get("name", "unknown")
                print(f"🔑 Found hidden input '{name}': {token[:20]}...")
                return token

        print("❌ No CSRF token or form_build_id found")
        print("   Looking for form structure...")
        
        # Debug: print form structure
        forms = soup.find_all("form")
        for i, form in enumerate(forms):
            action = form.get("action", "")
            if "bump" in action:
                print(f"   Found bump form (action: {action})")
                inputs = form.find_all("input")
                for inp in inputs:
                    name = inp.get("name", "")
                    value = inp.get("value", "")
                    if value:
                        print(f"     Input: {name} = {value[:30]}...")

        return None

    except Exception as e:
        print(f"❌ Error fetching CSRF: {e}")
        return None
    
# ========================================
# STEP 3: Perform Bump (POST with CSRF)
# ========================================

def refresh_post(url_info):
    SpiderManTheme.print_action("Thwip! Launching web to bump post...")
    csrf_token = get_csrf_token(url_info['destination'])
    if not csrf_token:
        SpiderManTheme.print_error("No CSRF token - Can't stick the landing!")
        return False

    # First, let's try a simple GET request to see if it works
    SpiderManTheme.print_action("Testing direct GET approach first...")
    get_url = f"{url_info['bump_url']}?destination={url_info['destination']}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.qatarliving.com{url_info['destination']}",
        "Upgrade-Insecure-Requests": "1",
    }
    
    # Try GET first (since we know it works)
    try:
        get_response = session.get(get_url, headers=headers, timeout=30)
        if any(word in get_response.text.lower() for word in ["bumped", "success", "refreshed"]) or url_info['destination'] in get_response.url:
            SpiderManTheme.print_success("🕷️  Web shot! Post bumped via GET!")
            return True
    except Exception as e:
        SpiderManTheme.print_warning(f"GET approach failed: {e}")

    # If GET doesn't work, try POST with better headers
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Improved headers for POST request
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://www.qatarliving.com{url_info['destination']}",
                "Origin": "https://www.qatarliving.com",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # Try POST with form data
            data = {
                "form_id": "classified_bump_form",
                "form_token": csrf_token,
                "form_build_id": csrf_token,
                "op": "Bump to top",
                "destination": url_info['destination'],
                "submit": "Bump to top"
            }

            SpiderManTheme.print_info(f"Spider-Sense tingling! Attempt {attempt}/{MAX_RETRIES} (POST bump)...")
            response = session.post(
                url_info['bump_url'],
                headers=headers,
                data=data,
                timeout=30,
                allow_redirects=True
            )

            SpiderManTheme.print_web(f"Status: {response.status_code}")
            
            # Debug info for 403 errors
            if response.status_code == 403:
                SpiderManTheme.print_warning("Got 403 Forbidden - Venom is blocking our way!")
                SpiderManTheme.print_info(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
                SpiderManTheme.print_info(f"   Location: {response.headers.get('Location', 'Not set')}")
                
                # Save response for debugging (truncated)
                if len(response.text) > 500:
                    response_preview = response.text[:500] + "..."
                else:
                    response_preview = response.text
                
                SpiderManTheme.print_info(f"   Response preview: {response_preview[:200]}...")
                
                # Check for specific error messages
                if "access denied" in response.text.lower():
                    SpiderManTheme.print_error("   Access denied - cookies might be invalid")
                elif "csrf" in response.text.lower():
                    SpiderManTheme.print_error("   CSRF token validation failed")
                elif "forbidden" in response.text.lower():
                    SpiderManTheme.print_error("   Forbidden - possible IP restriction or rate limiting")
            
            SpiderManTheme.print_web(f"Final URL: {response.url}")

            if response.status_code in [200, 302, 303]:
                # Check for success indicators
                success_indicators = [
                    "bumped", "success", "refreshed", "bump successful",
                    "ad has been bumped", "moved to the top"
                ]
                
                response_lower = response.text.lower()
                if any(word in response_lower for word in success_indicators):
                    SpiderManTheme.print_success("Bullseye! Post bumped via POST!")
                    logging.info("Post bumped successfully via POST")
                    return True
                
                # Check if redirected to job page
                if url_info['destination'] in response.url:
                    SpiderManTheme.print_success("Perfect landing! Redirected to job page after bump")
                    logging.info("Redirected to job page - bump likely succeeded")
                    return True
                
                # Check for form resubmission (means it worked)
                if "form" not in response_lower or "resubmit" in response_lower:
                    SpiderManTheme.print_success("Form processed - mission accomplished!")
                    return True

            # Fallback: Try GET with different parameters
            if response.status_code == 403:
                SpiderManTheme.print_warning("POST failed with 403, trying alternative web pattern...")
                
                # Try different GET variations
                get_variations = [
                    f"{url_info['bump_url']}?destination={url_info['destination']}&op=Bump+to+top",
                    f"{url_info['bump_url']}?destination={url_info['destination']}&form_id=classified_bump_form",
                    f"{url_info['bump_url']}?destination={url_info['destination']}&bump=Bump+to+top"
                ]
                
                for get_variant in get_variations:
                    try:
                        get_response = session.get(get_variant, headers=headers, timeout=30)
                        if any(word in get_response.text.lower() for word in success_indicators) or url_info['destination'] in get_response.url:
                            SpiderManTheme.print_success(f"Creative web work! Post bumped via GET variant!")
                            return True
                    except:
                        continue

        except Exception as e:
            SpiderManTheme.print_error(f"Error on attempt {attempt}: {e}")
            logging.error(f"Attempt {attempt} failed: {e}")

        if attempt < MAX_RETRIES:
            wait = random.uniform(5, MAX_WAIT)
            SpiderManTheme.print_info(f"Taking cover! Waiting {wait:.1f}s before next attempt...")
            time.sleep(wait)

    SpiderManTheme.print_error("All attempts failed - Green Goblin wins this round")
    
    # Final fallback: Try one more GET request
    SpiderManTheme.print_action("Trying one last web shot...")
    try:
        final_get_url = f"{url_info['bump_url']}?destination={url_info['destination']}"
        final_response = session.get(final_get_url, timeout=30)
        if url_info['destination'] in final_response.url:
            SpiderManTheme.print_success("Last second save! Post bumped via final web shot!")
            return True
    except Exception as e:
        SpiderManTheme.print_warning(f"Final attempt failed: {e}")
    
    return False

# ========================================
# MAIN
# ========================================
if __name__ == "__main__":
    # Print Spider-Man banner
    print(f"{SpiderManTheme.RED}{SpiderManTheme.BOLD}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║              🕷️  QATAR LIVING AUTO-REFRESH 🕷️              ║")
    print("║                           v2.7                           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{SpiderManTheme.END}")
    
    SpiderManTheme.print_header("Mission Started")
    print(f"{SpiderManTheme.BLUE}🕒 Mission Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{SpiderManTheme.END}")
    print(f"{SpiderManTheme.BLUE}{'─' * 60}{SpiderManTheme.END}")
    
    if not COOKIES:
        SpiderManTheme.print_error("No cookies available - With great power comes great responsibility!")
        if not IS_GITHUB_ACTIONS:
            SpiderManTheme.print_info("Need fresh cookies? Run this in browser console:")
            SpiderManTheme.print_warning(COOKIE_FINDER_SCRIPT)
        sys.exit(1)

    if not BUMP_URL:
        SpiderManTheme.print_error("No bump URL available - Can't swing without a destination!")
        SpiderManTheme.print_info("Example URL format:")
        SpiderManTheme.print_info("https://www.qatarliving.com/bump/node/46590548?destination=/jobseeker/username/job-name")
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
    if not test_cookies():
        SpiderManTheme.print_error("Authentication failed - Can't access the Daily Bugle!")
        SpiderManTheme.print_info("Try getting fresh cookies:")
        SpiderManTheme.print_info("1. Login to Qatar Living in browser")
        SpiderManTheme.print_info("2. Open Developer Tools (F12)")
        SpiderManTheme.print_info("3. Go to Console tab")
        SpiderManTheme.print_info("4. Paste the cookie extractor script from above")
        sys.exit(1)
    else:
        # Extract and display username
        username = extract_username()
        if username:
            SpiderManTheme.print_success(f"Identity verified: Peter Parker ({username})")
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
            SpiderManTheme.print_info("User is logged in (Secret identity protected)")

    print(f"🎯 Target URL: {BUMP_URL}")
    print("-" * 50)
    
    # Perform the bump
    if refresh_post(url_info):
        SpiderManTheme.print_success("🕷️  Refresh completed successfully! 🎉")
        SpiderManTheme.print_success("🕷️  Swinging away! 🕸️")
        SpiderManTheme.print_success("🕷️  A Maiz's System. 🕷️ ")
        sys.exit(0)
    else:
        SpiderManTheme.print_error("💥 Refresh failed")
        sys.exit(1)

    print("-" * 50)
    print(f"🕒 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")