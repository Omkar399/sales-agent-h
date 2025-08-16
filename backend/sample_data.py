#!/usr/bin/env python3
"""Sample data script to populate the database with initial customer cards."""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal, init_db
from app.models.cards import Card, CardStatus, CardPriority


def create_sample_data():
    """Create sample customer cards."""
    
    # Initialize database
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_cards = db.query(Card).count()
        if existing_cards > 0:
            print(f"Database already contains {existing_cards} cards. Skipping sample data creation.")
            return
        
        # Sample customer data
        sample_cards = [
            {
                "customer_name": "John Smith",
                "company": "TechCorp Solutions",
                "email": "john.smith@techcorp.com",
                "phone": "+1-555-0123",
                "status": CardStatus.TO_REACH,
                "priority": CardPriority.HIGH,
                "notes": "Interested in enterprise software solutions. Follow up on pricing discussion.",
                "assigned_to": "Sarah Johnson",
                "next_followup_date": datetime.now() + timedelta(days=2)
            },
            {
                "customer_name": "Emily Davis",
                "company": "Marketing Pro Inc",
                "email": "emily@marketingpro.com",
                "phone": "+1-555-0234",
                "status": CardStatus.IN_PROGRESS,
                "priority": CardPriority.MEDIUM,
                "notes": "Demo scheduled for next week. Needs integration with their current CRM.",
                "assigned_to": "Mike Chen",
                "next_followup_date": datetime.now() + timedelta(days=5)
            },
            {
                "customer_name": "Robert Wilson",
                "company": "Global Logistics Ltd",
                "email": "r.wilson@globallogistics.com",
                "phone": "+1-555-0345",
                "status": CardStatus.REACHED_OUT,
                "priority": CardPriority.HIGH,
                "notes": "Sent proposal last week. Waiting for decision from board meeting.",
                "assigned_to": "Sarah Johnson",
                "last_contact_date": datetime.now() - timedelta(days=3),
                "next_followup_date": datetime.now() + timedelta(days=7)
            },
            {
                "customer_name": "Lisa Anderson",
                "company": "Creative Designs Studio",
                "email": "lisa@creativedesigns.com",
                "phone": "+1-555-0456",
                "status": CardStatus.FOLLOWUP,
                "priority": CardPriority.LOW,
                "notes": "Interested but budget constraints. Revisit in Q2.",
                "assigned_to": "Tom Rodriguez",
                "last_contact_date": datetime.now() - timedelta(days=14),
                "next_followup_date": datetime.now() + timedelta(days=30)
            },
            {
                "customer_name": "David Thompson",
                "company": "FinanceFirst Bank",
                "email": "d.thompson@financefirst.com",
                "phone": "+1-555-0567",
                "status": CardStatus.TO_REACH,
                "priority": CardPriority.MEDIUM,
                "notes": "Referral from existing client. Interested in security features.",
                "assigned_to": "Mike Chen"
            },
            {
                "customer_name": "Jennifer Lee",
                "company": "Healthcare Solutions",
                "email": "j.lee@healthcaresol.com",
                "phone": "+1-555-0678",
                "status": CardStatus.IN_PROGRESS,
                "priority": CardPriority.HIGH,
                "notes": "HIPAA compliance is critical. Technical review in progress.",
                "assigned_to": "Sarah Johnson",
                "next_followup_date": datetime.now() + timedelta(days=3)
            },
            {
                "customer_name": "Mark Rodriguez",
                "company": "Retail Chain Plus",
                "email": "mark@retailchainplus.com",
                "phone": "+1-555-0789",
                "status": CardStatus.REACHED_OUT,
                "priority": CardPriority.MEDIUM,
                "notes": "Needs multi-location support. Pricing discussion completed.",
                "assigned_to": "Tom Rodriguez",
                "last_contact_date": datetime.now() - timedelta(days=1),
                "next_followup_date": datetime.now() + timedelta(days=4)
            },
            {
                "customer_name": "Amanda White",
                "company": "EduTech Academy",
                "email": "amanda@edutech.edu",
                "phone": "+1-555-0890",
                "status": CardStatus.FOLLOWUP,
                "priority": CardPriority.LOW,
                "notes": "Educational discount requested. Waiting for approval from procurement.",
                "assigned_to": "Mike Chen",
                "last_contact_date": datetime.now() - timedelta(days=7),
                "next_followup_date": datetime.now() + timedelta(days=14)
            },
            {
                "customer_name": "Chris Johnson",
                "company": "Manufacturing Corp",
                "email": "chris@manufacturingcorp.com",
                "phone": "+1-555-0901",
                "status": CardStatus.TO_REACH,
                "priority": CardPriority.HIGH,
                "notes": "Urgent requirement for production line integration. Hot lead!",
                "assigned_to": "Sarah Johnson",
                "next_followup_date": datetime.now() + timedelta(days=1)
            },
            {
                "customer_name": "Rachel Green",
                "company": "Consulting Partners",
                "email": "rachel@consultingpartners.com",
                "phone": "+1-555-1012",
                "status": CardStatus.IN_PROGRESS,
                "priority": CardPriority.MEDIUM,
                "notes": "Pilot project approved. Implementation timeline discussion needed.",
                "assigned_to": "Tom Rodriguez",
                "next_followup_date": datetime.now() + timedelta(days=6)
            }
        ]
        
        # Create and add cards to database
        created_cards = []
        for card_data in sample_cards:
            card = Card(**card_data)
            db.add(card)
            created_cards.append(card)
        
        # Commit all changes
        db.commit()
        
        print(f"✅ Successfully created {len(created_cards)} sample customer cards!")
        print("\nSample cards created:")
        for card in created_cards:
            print(f"  • {card.customer_name} ({card.company}) - {card.status.value}")
        
        print(f"\n🎯 Cards distribution:")
        status_counts = {}
        for status in CardStatus:
            count = len([c for c in created_cards if c.status == status])
            status_counts[status.value] = count
            print(f"  • {status.value.replace('_', ' ').title()}: {count}")
        
        print(f"\n🚀 Database is ready! Start the backend server to see your data.")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    print("📊 Creating sample data for Sales Agent Dashboard...")
    create_sample_data()
