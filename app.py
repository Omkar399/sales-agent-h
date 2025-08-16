#!/usr/bin/env python3
"""
Clean HubSpot Contact Dashboard
Only real data from your HubSpot account - no dummy data
"""

import os
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from hubspot import HubSpot

load_dotenv()

app = Flask(__name__)

class HubSpotClient:
    def __init__(self):
        self.access_token = os.getenv('HUBSPOT_ACCESS_TOKEN')
        self.client = None
        self.connected = False
        
        if self.access_token:
            try:
                self.client = HubSpot(access_token=self.access_token)
                # Test connection
                test = self.client.crm.contacts.basic_api.get_page(limit=1)
                self.connected = True
                print("✅ HubSpot connected successfully")
            except Exception as e:
                print(f"❌ HubSpot connection failed: {e}")
    
    def get_contacts(self):
        """Get real contacts from HubSpot - no dummy data"""
        if not self.connected:
            return []
        
        try:
            response = self.client.crm.contacts.basic_api.get_page(
                limit=50,
                properties=[
                    "firstname", 
                    "lastname", 
                    "email", 
                    "company", 
                    "phone",
                    "jobtitle",
                    "city",
                    "state"
                ]
            )
            
            contacts = []
            for contact in response.results:
                props = contact.properties
                
                # Only add contacts with actual data (skip empty contacts)
                name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
                email = props.get('email', '')
                
                if name or email:  # Only include if has name or email
                    contacts.append({
                        'id': contact.id,
                        'name': name if name else 'No Name',
                        'email': email if email else '',
                        'company': props.get('company', ''),
                        'phone': props.get('phone', ''),
                        'job_title': props.get('jobtitle', ''),
                        'city': props.get('city', ''),
                        'state': props.get('state', '')
                    })
            
            print(f"📋 Retrieved {len(contacts)} real contacts from HubSpot")
            return contacts
            
        except Exception as e:
            print(f"❌ Error retrieving contacts: {e}")
            return []

# Initialize
hubspot = HubSpotClient()

@app.route('/')
def dashboard():
    """Clean dashboard with only real HubSpot data"""
    contacts = hubspot.get_contacts()
    return render_template('dashboard.html', 
                         contacts=contacts,
                         connected=hubspot.connected)

@app.route('/api/contacts')
def api_contacts():
    """API endpoint for contacts"""
    contacts = hubspot.get_contacts()
    return jsonify({
        'connected': hubspot.connected,
        'count': len(contacts),
        'contacts': contacts
    })

if __name__ == '__main__':
    print("🚀 Clean HubSpot Contact Dashboard")
    print("=" * 40)
    
    if hubspot.connected:
        count = len(hubspot.get_contacts())
        print(f"✅ Connected to HubSpot")
        print(f"✅ Found {count} real contacts")
    else:
        print("❌ Not connected to HubSpot")
        print("💡 Check HUBSPOT_ACCESS_TOKEN in .env")
    
    print("🌐 http://localhost:5000")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=5000, debug=True)