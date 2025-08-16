#!/usr/bin/env python3
"""
Gmail OAuth Token Generator

This script helps you get a refresh token for Gmail API access.
Run this once to get the refresh token, then add it to your .env file.

Requirements: pip install requests
"""

import base64, json, threading, urllib.parse, webbrowser, os
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "https://www.googleapis.com/auth/gmail.send"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default HTTP server logging
        pass
        
    def do_GET(self):
        qs = urllib.parse.urlparse(self.path)
        if qs.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return
            
        params = urllib.parse.parse_qs(qs.query)
        code = params.get("code", [None])[0]
        error = params.get("error", [None])[0]
        
        if error:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"OAuth error: {error}".encode())
            print(f"\n❌ OAuth error: {error}")
            threading.Thread(target=httpd.shutdown, daemon=True).start()
            return
            
        if not code:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing authorization code")
            print("\n❌ Missing authorization code")
            threading.Thread(target=httpd.shutdown, daemon=True).start()
            return

        # Exchange code for tokens
        data = {
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        
        try:
            r = requests.post(TOKEN_URL, data=data)
            token_data = r.json()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if "refresh_token" in token_data:
                success_html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: green;">✅ Success!</h2>
                    <p>Gmail OAuth token obtained successfully.</p>
                    <p>You can close this tab and return to your terminal.</p>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode())
                
                print("\n🎉 Token response received!")
                print("=" * 50)
                print(json.dumps(token_data, indent=2))
                print("=" * 50)
                
                refresh_token = token_data.get("refresh_token")
                if refresh_token:
                    print(f"\n✅ Refresh Token: {refresh_token}")
                    print("\n📝 Add this to your .env file:")
                    print(f"GMAIL_REFRESH_TOKEN={refresh_token}")
                    
                    # Optionally update .env file automatically
                    try:
                        with open('.env', 'r') as f:
                            env_content = f.read()
                        
                        if 'GMAIL_REFRESH_TOKEN=' in env_content:
                            # Update existing line
                            lines = env_content.split('\n')
                            for i, line in enumerate(lines):
                                if line.startswith('GMAIL_REFRESH_TOKEN='):
                                    lines[i] = f'GMAIL_REFRESH_TOKEN={refresh_token}'
                                    break
                            env_content = '\n'.join(lines)
                        else:
                            # Add new line
                            env_content += f'\nGMAIL_REFRESH_TOKEN={refresh_token}\n'
                        
                        with open('.env', 'w') as f:
                            f.write(env_content)
                        
                        print("✅ .env file updated automatically!")
                        
                    except Exception as e:
                        print(f"⚠️  Could not update .env file automatically: {e}")
                        print("Please add the refresh token manually.")
                
            else:
                error_html = """
                <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: red;">❌ Error</h2>
                    <p>No refresh token received. Please try again.</p>
                    <p>Make sure you selected "offline access" during authorization.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode())
                print("\n❌ No refresh token received!")
                print("Response:", json.dumps(token_data, indent=2))
                
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error exchanging code: {e}".encode())
            print(f"\n❌ Error exchanging code: {e}")
        
        # Shut down the server after processing
        threading.Thread(target=httpd.shutdown, daemon=True).start()

def main():
    print("🔐 Gmail OAuth Token Generator")
    print("=" * 40)
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set in .env file")
        print("\nPlease add these to your .env file:")
        print("GMAIL_CLIENT_ID=your_client_id_here")
        print("GMAIL_CLIENT_SECRET=your_client_secret_here")
        return
    
    print(f"📱 Client ID: {CLIENT_ID[:20]}...")
    print(f"🔑 Client Secret: {'*' * 20}")
    print(f"🔗 Redirect URI: {REDIRECT_URI}")
    print(f"📧 Scope: {SCOPE}")
    
    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }
    
    url = AUTH_URL + "?" + urllib.parse.urlencode(auth_params)
    
    print(f"\n🌐 Opening authorization URL...")
    print(f"URL: {url}")
    
    global httpd
    httpd = HTTPServer(("localhost", 8080), Handler)
    
    try:
        webbrowser.open(url)
        print(f"\n⏳ Waiting for OAuth redirect on {REDIRECT_URI} ...")
        print("   (Complete the authorization in your browser)")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        httpd.server_close()
        print("\n🏁 OAuth flow completed.")

if __name__ == "__main__":
    main()
