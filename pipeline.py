import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def extract_data():
    print("[INFO] Starting the Extraction phase...")
    url = "http://books.toscrape.com/"
    response = requests.get(url)
    
    # Karakter bozulmalarını önlemek için encoding'i utf-8 yapıyoruz
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
    
    # ÇÖZÜM: Sadece sayıları (\d) ve noktayı (.) tut, geri kalan her şeyi ('Â' dahil) sil!
    df['price'] = df['price'].str.replace(r'[^\d.]', '', regex=True).astype(float)
    
    df['availability'] = df['availability'].str.strip()
    df = df.dropna(subset=['title', 'price'])
    df['extracted_at'] = datetime.now()
    
    print(f"[SUCCESS] Successfully transformed {len(df)} rows.")
    return df

if __name__ == "__main__":
    raw_books = extract_data()
    cleaned_df = transform_data(raw_books)
    
    print("\n--- Cleaned Data Preview ---")
    print(cleaned_df.head())