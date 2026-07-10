import requests
from bs4 import BeautifulSoup

def extract_data():
    print("[INFO] Starting the Extraction phase...")
    url = "http://books.toscrape.com/"
    
    # Web sitesine istek gönderiyoruz
    response = requests.get(url)
    
    # Eğer siteye erişim başarılıysa (Status Code 200) işlemlere başla
    if response.status_code != 200:
        print(f"[ERROR] Could not blood data from site. Status code: {response.status_code}")
        return []

    # Sitenin HTML içeriğini BeautifulSoup ile anlamlandırıyoruz
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Sitedeki tüm kitap kutularını buluyoruz
    books = soup.find_all('article', class_='product_pod')
    
    scraped_books = []
    
    for book in books:
        # 1. Alan: Kitap Adı (Product Name)
        title = book.h3.a['title']
        
        # 2. Alan: Fiyat (Price)
        price = book.find('p', class_='price_color').text
        
        # 3. Alan: Stok Durumu (Availability)
        availability = book.find('p', class_='instock availability').text.strip()
        
        # Toplanan verileri bir sözlük (dictionary) yapısında saklıyoruz
        book_info = {
            "title": title,
            "price": price,
            "availability": availability
        }
        scraped_books.append(book_info)
        
    print(f"[SUCCESS] Successfully extracted {len(scraped_books)} books from the website.")
    return scraped_books

# Test etmek için fonksiyonu çalıştırıp terminalde görelim
if __name__ == "__main__":
    extracted_data = extract_data()
    # İlk 3 kitabı terminale yazdırıp kontrol edelim
    for item in extracted_data[:3]:
        print(item)