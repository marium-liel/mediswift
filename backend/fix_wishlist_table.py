#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_platform.settings')
django.setup()

from django.db import connection

def create_wishlist_table():
    """Create the products_wishlistitem table manually"""
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='products_wishlistitem';
        """)
        
        if cursor.fetchone():
            print("Table products_wishlistitem already exists")
            return
        
        # Create the table
        cursor.execute("""
            CREATE TABLE "products_wishlistitem" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "created_at" datetime NOT NULL,
                "user_id" bigint NOT NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED,
                "product_id" bigint NOT NULL REFERENCES "products_product" ("id") DEFERRABLE INITIALLY DEFERRED
            );
        """)
        
        # Create unique constraint
        cursor.execute("""
            CREATE UNIQUE INDEX "products_wishlistitem_user_id_product_id_uniq" 
            ON "products_wishlistitem" ("user_id", "product_id");
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX "products_wishlistitem_user_id_idx" 
            ON "products_wishlistitem" ("user_id");
        """)
        
        cursor.execute("""
            CREATE INDEX "products_wishlistitem_product_id_idx" 
            ON "products_wishlistitem" ("product_id");
        """)
        
        print("Successfully created products_wishlistitem table")

if __name__ == '__main__':
    create_wishlist_table()
