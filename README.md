# HubSpot Contact Dashboard

A clean, simple dashboard that pulls real contact data from your HubSpot account.

## Features

- 🔗 **Direct HubSpot Integration** - Connects to your HubSpot account using Personal Access Token
- 📋 **Real Contact Data** - Displays your actual HubSpot contacts (no demo data)
- 🎨 **Clean Interface** - Professional, responsive design
- 📊 **Contact Details** - Shows name, email, company, phone, job title, and location
- 🚀 **Simple Setup** - Just add your HubSpot token and run

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure HubSpot Access
1. Go to your HubSpot account
2. Settings → Integrations → Private Apps
3. Create a new private app called "Contact Dashboard"
4. Enable scopes: `crm.objects.contacts.read`
5. Copy your access token

### 3. Setup Environment
```bash
cp .env.example .env
```

Edit `.env` and add your HubSpot token:
```
HUBSPOT_ACCESS_TOKEN=your_token_here
```

### 4. Run Dashboard
```bash
python app.py
```

Visit: http://localhost:5000

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/contacts` - JSON API for contacts

## Requirements

- Python 3.7+
- HubSpot account with contacts
- HubSpot Personal Access Token

## What You'll See

The dashboard displays all contacts from your HubSpot account with:
- Contact name
- Email address
- Company
- Phone number
- Job title
- Location (city, state)
- HubSpot contact ID

## Clean & Simple

This is a minimal, clean implementation focused on:
- Real data only (no dummy/demo data)
- Simple setup and configuration
- Professional interface
- Direct HubSpot integration

Perfect for quickly viewing and accessing your HubSpot contact database.