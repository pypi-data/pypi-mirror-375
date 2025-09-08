"""
Enhanced expense data generator with data enrichment.

This module generates realistic expense data with enriched descriptions
for improved vector search accuracy.
"""

import os
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .enrichment import DataEnricher


class EnhancedExpenseGenerator:
    """Enhanced expense generator with data enrichment for better vector search."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the enhanced expense generator."""
        self.database_url = database_url or os.getenv('DATABASE_URL', "cockroachdb://root@localhost:26257/banko_ai?sslmode=disable")
        self._engine = None
        self.enricher = DataEnricher()
        self._embedding_model = None
        self._merchants = None
        self._categories = None
        self._payment_methods = None
        self._user_ids = None
    
    @property
    def engine(self):
        """Get SQLAlchemy engine (lazy import)."""
        if self._engine is None:
            from sqlalchemy import create_engine
            self._engine = create_engine(self.database_url)
        return self._engine
    
    @property
    def embedding_model(self):
        """Get embedding model (lazy import)."""
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._embedding_model
    
    @property
    def merchants(self):
        """Get merchants data (lazy load)."""
        if self._merchants is None:
            self._init_merchants_and_categories()
        return self._merchants
    
    @property
    def categories(self):
        """Get categories data (lazy load)."""
        if self._categories is None:
            self._init_merchants_and_categories()
        return self._categories
    
    @property
    def payment_methods(self):
        """Get payment methods (lazy load)."""
        if self._payment_methods is None:
            self._init_merchants_and_categories()
        return self._payment_methods
    
    @property
    def user_ids(self):
        """Get user IDs (lazy load)."""
        if self._user_ids is None:
            self._init_merchants_and_categories()
        return self._user_ids
    
    def _init_merchants_and_categories(self):
        """Initialize merchants and categories data."""
        # Enhanced merchant and category data
        self._merchants = {
            "grocery": [
                "Whole Foods Market", "Trader Joe's", "Kroger", "Safeway", "Publix", 
                "Walmart", "Target", "Costco", "Local Market", "Food Lion"
            ],
            "retail": [
                "Amazon", "Best Buy", "Apple Store", "Home Depot", "Lowes", 
                "Target", "Walmart", "Macy's", "Nordstrom", "TJ Maxx"
            ],
            "dining": [
                "Starbucks", "McDonald's", "Chipotle", "Subway", "Pizza Hut", 
                "Domino's", "Panera Bread", "Dunkin' Donuts", "Taco Bell", "KFC"
            ],
            "transportation": [
                "Shell Gas Station", "Exxon", "Chevron", "Uber", "Lyft", 
                "Metro", "Parking Garage", "Toll Road", "Car Wash", "Auto Repair"
            ],
            "healthcare": [
                "CVS Pharmacy", "Walgreens", "Rite Aid", "Hospital", "Clinic", 
                "Dentist", "Optometrist", "Pharmacy", "Medical Center", "Urgent Care"
            ],
            "entertainment": [
                "Netflix", "Spotify", "Movie Theater", "Concert Hall", "Gaming Store", 
                "Bookstore", "Museum", "Theme Park", "Sports Venue", "Theater"
            ],
            "utilities": [
                "Electric Company", "Internet Provider", "Phone Company", "Water Company", 
                "Gas Company", "Cable Company", "Trash Service", "Security System", "Insurance", "Bank"
            ]
        }
        
        self._categories = {
            "Groceries": {
                "items": ["Fresh produce", "Dairy products", "Meat and poultry", "Pantry staples", "Organic foods", "Beverages", "Snacks"],
                "merchants": self.merchants["grocery"],
                "amount_range": (10, 150)
            },
            "Transportation": {
                "items": ["Gas fill-up", "Uber ride", "Metro card reload", "Parking fee", "Car maintenance", "Toll payment", "Car wash"],
                "merchants": self.merchants["transportation"],
                "amount_range": (5, 100)
            },
            "Dining": {
                "items": ["Coffee and pastry", "Lunch meeting", "Dinner date", "Fast food", "Food delivery", "Restaurant meal", "Catering"],
                "merchants": self.merchants["dining"],
                "amount_range": (8, 80)
            },
            "Entertainment": {
                "items": ["Movie tickets", "Streaming service", "Concert tickets", "Gaming", "Books", "Magazine subscription", "Music"],
                "merchants": self.merchants["entertainment"],
                "amount_range": (5, 200)
            },
            "Healthcare": {
                "items": ["Prescription medication", "Doctor visit", "Dental cleaning", "Vitamins", "Health insurance", "Medical test", "Therapy"],
                "merchants": self.merchants["healthcare"],
                "amount_range": (15, 500)
            },
            "Shopping": {
                "items": ["Clothing", "Electronics", "Home goods", "Personal care", "Gifts", "Furniture", "Appliances"],
                "merchants": self.merchants["retail"],
                "amount_range": (20, 1000)
            },
            "Utilities": {
                "items": ["Electric bill", "Internet service", "Phone bill", "Water bill", "Trash service", "Cable TV", "Security system"],
                "merchants": self.merchants["utilities"],
                "amount_range": (30, 300)
            }
        }
        
        self._payment_methods = ["Credit Card", "Debit Card", "Cash", "Mobile Payment", "Bank Transfer", "Check"]
        self._user_ids = [str(uuid.uuid4()) for _ in range(100)]  # Generate 100 user IDs
    
    def generate_expense(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a single enriched expense record."""
        # Select category and get associated data
        category = random.choice(list(self.categories.keys()))
        category_data = self.categories[category]
        
        # Select merchant from category-specific merchants
        merchant = random.choice(category_data["merchants"])
        
        # Generate amount within category range
        amount = round(random.uniform(*category_data["amount_range"]), 2)
        
        # Select item from category items
        item = random.choice(category_data["items"])
        
        # Generate basic description
        basic_description = f"Bought {item.lower()}"
        
        # Generate date (last 90 days)
        days_ago = random.randint(0, 90)
        expense_date = (datetime.now() - timedelta(days=days_ago)).date()
        
        # Generate additional metadata
        payment_method = random.choice(self.payment_methods)
        recurring = random.choice([True, False]) if category in ["Utilities", "Entertainment"] else False
        tags = [category.lower(), merchant.lower().replace(" ", "_")]
        
        # Enrich the description
        enriched_description = self.enricher.enrich_expense_description(
            description=basic_description,
            merchant=merchant,
            amount=amount,
            category=category,
            payment_method=payment_method,
            date=expense_date,
            tags=tags
        )
        
        # Create searchable text for embedding
        searchable_text = self.enricher.create_searchable_text(
            description=basic_description,
            merchant=merchant,
            amount=amount,
            category=category,
            payment_method=payment_method,
            tags=tags
        )
        
        # Generate embedding
        embedding = self.embedding_model.encode([searchable_text])[0].tolist()
        
        return {
            "expense_id": str(uuid.uuid4()),
            "user_id": user_id or random.choice(self.user_ids),
            "expense_date": expense_date,
            "expense_amount": amount,
            "shopping_type": category,
            "description": enriched_description,
            "merchant": merchant,
            "payment_method": payment_method,
            "recurring": recurring,
            "tags": tags,
            "embedding": embedding,
            "searchable_text": searchable_text  # Store for debugging
        }
    
    def generate_expenses(self, count: int, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate multiple enriched expense records."""
        expenses = []
        
        for _ in range(count):
            expense = self.generate_expense(user_id)
            expenses.append(expense)
        
        return expenses
    
    def save_expenses_to_database(self, expenses: List[Dict[str, Any]]) -> int:
        """Save expenses to the database."""
        try:
            import pandas as pd
            with self.engine.connect() as conn:
                # Prepare data for insertion
                data_to_insert = []
                for expense in expenses:
                    data_to_insert.append({
                        'expense_id': expense['expense_id'],
                        'user_id': expense['user_id'],
                        'expense_date': expense['expense_date'],
                        'expense_amount': expense['expense_amount'],
                        'shopping_type': expense['shopping_type'],
                        'description': expense['description'],
                        'merchant': expense['merchant'],
                        'payment_method': expense['payment_method'],
                        'recurring': expense['recurring'],
                        'tags': expense['tags'],
                        'embedding': expense['embedding']
                    })
                
                # Insert in batches
                batch_size = 100
                total_inserted = 0
                
                for i in range(0, len(data_to_insert), batch_size):
                    batch = data_to_insert[i:i + batch_size]
                    
                    # Use pandas to insert the batch
                    df = pd.DataFrame(batch)
                    df.to_sql('expenses', conn, if_exists='append', index=False, method='multi')
                    total_inserted += len(batch)
                
                return total_inserted
                
        except Exception as e:
            print(f"Error saving expenses to database: {e}")
            return 0
    
    def clear_expenses(self) -> bool:
        """Clear all expenses from the database."""
        try:
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text("DELETE FROM expenses"))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error clearing expenses: {e}")
            return False
    
    def get_expense_count(self) -> int:
        """Get the current number of expenses in the database."""
        try:
            from sqlalchemy import text
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM expenses"))
                return result.scalar()
        except Exception as e:
            print(f"Error getting expense count: {e}")
            return 0
    
    def generate_and_save(
        self, 
        count: int, 
        user_id: Optional[str] = None, 
        clear_existing: bool = False
    ) -> int:
        """Generate and save expenses to the database."""
        if clear_existing:
            self.clear_expenses()
        
        expenses = self.generate_expenses(count, user_id)
        return self.save_expenses_to_database(expenses)
    
    def create_user_specific_indexes(self) -> bool:
        """Create user-specific vector indexes for CockroachDB."""
        try:
            with self.engine.connect() as conn:
                # Create user-specific vector index
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_expenses_user_embedding 
                    ON expenses (user_id, embedding) 
                    USING ivfflat (embedding vector_cosine_ops) 
                    WITH (lists = 100)
                """))
                
                # Create regional index if supported
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_expenses_user_embedding_regional 
                        ON expenses (user_id, embedding) 
                        LOCALITY REGIONAL BY ROW AS region
                    """))
                except Exception:
                    # Regional indexing might not be supported in all deployments
                    pass
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating user-specific indexes: {e}")
            return False
