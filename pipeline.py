import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

def extract_data():
    print("[INFO] Starting the Extraction phase...")
    url = "http://books.toscrape.com/"
    response = requests.get(url)
    
    # Set encoding to utf-8 to prevent character distortion
    response.encoding = 'utf-8'
    
    if response.status_code != 200:
        print(f"[ERROR] Could not fetch data. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    books = soup.find_all('article', class_='product_pod')
    
    scraped_books = []
    for book in books:
        title = book.h3.a['title']
        price = book.find('p', class_='price_color').text
        availability = book.find('p', class_='instock availability').text.strip()
        
        book_info = {
            "title": title,
            "price": price,
            "availability": availability
        }
        scraped_books.append(book_info)
        
    print(f"[SUCCESS] Successfully extracted {len(scraped_books)} books.")
    return scraped_books

def transform_data(raw_data):
    print("[INFO] Starting the Transformation phase...")
    if not raw_data:
        print("[WARNING] No data found to transform.")
        return pd.DataFrame()
    
    df = pd.DataFrame(raw_data)
    
    # Regex clean: Keep only numbers and dots to fix encoding errors like 'Â51.77'
    df['price'] = df['price'].str.replace(r'[^\d.]', '', regex=True).astype(float)
    
    # Trim whitespaces from availability column
    df['availability'] = df['availability'].str.strip()
    
    # Handle missing values by dropping incomplete rows
    df = df.dropna(subset=['title', 'price'])
    
    # Add execution timestamp for tracking
    df['extracted_at'] = datetime.now()
    
    print(f"[SUCCESS] Successfully transformed {len(df)} rows.")
    return df

def load_data(df):
    print("[INFO] Starting the Loading phase...")
    if df.empty:
        print("[WARNING] No data to load into the database.")
        return 0

    # PostgreSQL database connection URI targeting Docker port 5433
    DATABASE_URI = "postgresql://myuser:mypassword@localhost:5433/mydatabase"
    engine = create_engine(DATABASE_URI)
    
    inserted_count = 0
    
    with engine.connect() as conn:
        # Create table schema with a PRIMARY KEY constraint to prevent duplicates
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS books (
                title VARCHAR PRIMARY KEY,
                price FLOAT,
                availability VARCHAR,
                extracted_at TIMESTAMP
            );
        """))
        conn.commit()
        
        # Perform UPSERT logic for strict idempotency rule
        for _, row in df.iterrows():
            upsert_query = text("""
                INSERT INTO books (title, price, availability, extracted_at)
                VALUES (:title, :price, :availability, :extracted_at)
                ON CONFLICT (title) 
                DO UPDATE SET 
                    price = EXCLUDED.price,
                    availability = EXCLUDED.availability,
                    extracted_at = EXCLUDED.extracted_at;
            """)
            conn.execute(upsert_query, {
                "title": row['title'],
                "price": row['price'],
                "availability": row['availability'],
                "extracted_at": row['extracted_at']
            })
            inserted_count += 1
            
        conn.commit()
    
    print(f"[SUCCESS] Successfully loaded data into PostgreSQL.")
    return inserted_count

# Main workflow orchestration
if __name__ == "__main__":
    print("=== STARTING ETL PIPELINE ===")
    
    # 1. EXTRACT
    raw_books = extract_data()
    
    # 2. TRANSFORM
    cleaned_df = transform_data(raw_books)
    
    # 3. LOAD
    total_inserted = load_data(cleaned_df)
    
    # 4. EXECUTION LOG SUMMARY
    print("\n=============================================")
    print("        ETL PIPELINE EXECUTION SUMMARY       ")
    print("=============================================")
    print(f"Total Rows Extracted   : {len(raw_books)}")
    print(f"Total Rows Transformed : {len(cleaned_df)}")
    print(f"Total Rows Loaded (DB) : {total_inserted}")
    print("Status                 : SUCCESS")
    print("=============================================")