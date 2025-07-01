# seed.py
import sys
import os
from sqlalchemy.orm import Session
from models import Switch, Channel, User, Base
from database import engine, SessionLocal
import database

def seed_database():
    # Create all tables if they don't exist
    db = next(database.get_db())
    
    try:
        # Clear existing data (optional, for testing purposes)
        db.query(Channel).delete()
        db.query(Switch).delete()
        db.query(User).delete()
        db.commit()
        
        # Create sample users
        user1 = User(
            firstName="John",
            lastName="Doe",
            username="johndoe",
            age=30,
            institution="University X",
            email="john.doe@example.com",
            hash_password="hashed_password",  # In production, store a properly hashed password
            disabled=False
        )
        user2 = User(
            firstName="Jane",
            lastName="Smith",
            username="janesmith",
            age=25,
            institution="University Y",
            email="jane.smith@example.com",
            hash_password="hashed_password",  # In production, store a properly hashed password
            disabled=False
        )
        db.add_all([user1, user2])
        db.commit()
        
        # Create sample switches
        switch1 = Switch(channels_count=5, active=True)
        switch2 = Switch(channels_count=3, active=True)
        db.add_all([switch1, switch2])
        db.commit()
        
        # Create sample channels for each switch.
        channels = []
        # Create channels for switch1
        for i in range(switch1.channels_count):
            channels.append(
                Channel(
                    channel_number=i + 1,
                    channel_active=False,
                    channel_user=None,
                    switch_id=switch1.id
                )
            )
        # Create channels for switch2
        for i in range(switch2.channels_count):
            channels.append(
                Channel(
                    channel_number=i + 1,
                    channel_active=False,
                    channel_user=None,
                    switch_id=switch2.id
                )
            )
        db.add_all(channels)
        db.commit()
        
        print("Seed data inserted successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
