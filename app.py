from mcp.server.fastmcp import FastMCP
import requests
import json
from typing import Dict, List, Any

# MCP sunucusunu başlat
mcp = FastMCP("Open Library MCP Server")

@mcp.tool()
def get_book_by_olid(olid: str) -> str:
    """
    Open Library ID (OLID) kullanarak kitap bilgilerini getir.
    Örnek: OL1M, OL23919A gibi
    """
    try:
        url = f"https://openlibrary.org/books/{olid}.json"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            result = {
                "title": data.get("title", "Bilinmiyor"),
                "authors": data.get("authors", []),
                "publish_date": data.get("publish_date", "Bilinmiyor"),
                "publishers": data.get("publishers", []),
                "isbn_10": data.get("isbn_10", []),
                "isbn_13": data.get("isbn_13", []),
                "number_of_pages": data.get("number_of_pages", "Bilinmiyor"),
                "subjects": data.get("subjects", []),
                "url": f"https://openlibrary.org/books/{olid}"
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return f"Kitap bulunamadı. Status Code: {response.status_code}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@mcp.tool()
def get_book_by_isbn(isbn: str) -> str:
    """
    ISBN numarası kullanarak kitap bilgilerini getir.
    """
    try:
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            book_key = f"ISBN:{isbn}"
            
            if book_key in data:
                book_info = data[book_key]
                result = {
                    "title": book_info.get("title", "Bilinmiyor"),
                    "authors": [author.get("name", "") for author in book_info.get("authors", [])],
                    "publishers": [pub.get("name", "") for pub in book_info.get("publishers", [])],
                    "publish_date": book_info.get("publish_date", "Bilinmiyor"),
                    "number_of_pages": book_info.get("number_of_pages", "Bilinmiyor"),
                    "subjects": book_info.get("subjects", []),
                    "isbn": isbn,
                    "url": book_info.get("url", "")
                }
                return json.dumps(result, indent=2, ensure_ascii=False)
            else:
                return "ISBN ile eşleşen kitap bulunamadı."
        else:
            return f"Hata oluştu. Status Code: {response.status_code}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@mcp.tool()
def search_books(query: str, limit: int = 10) -> str:
    """
    Kitap arama yapar. Başlık, yazar veya genel arama yapabilir.
    """
    try:
        url = f"https://openlibrary.org/search.json?q={query}&limit={limit}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            books = []
            
            for doc in data.get("docs", []):
                book = {
                    "title": doc.get("title", "Bilinmiyor"),
                    "author_name": doc.get("author_name", []),
                    "first_publish_year": doc.get("first_publish_year", "Bilinmiyor"),
                    "isbn": doc.get("isbn", []),
                    "publisher": doc.get("publisher", []),
                    "key": doc.get("key", ""),
                    "url": f"https://openlibrary.org{doc.get('key', '')}" if doc.get('key') else ""
                }
                books.append(book)
            
            result = {
                "found": data.get("numFound", 0),
                "showing": len(books),
                "books": books
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return f"Arama başarısız. Status Code: {response.status_code}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@mcp.tool()
def search_books_by_author(author: str, limit: int = 10) -> str:
    """
    Yazar adına göre kitap arama yapar.
    """
    try:
        url = f"https://openlibrary.org/search.json?author={author}&limit={limit}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            books = []
            
            for doc in data.get("docs", []):
                book = {
                    "title": doc.get("title", "Bilinmiyor"),
                    "author_name": doc.get("author_name", []),
                    "first_publish_year": doc.get("first_publish_year", "Bilinmiyor"),
                    "isbn": doc.get("isbn", []),
                    "publisher": doc.get("publisher", []),
                    "key": doc.get("key", ""),
                    "url": f"https://openlibrary.org{doc.get('key', '')}" if doc.get('key') else ""
                }
                books.append(book)
            
            result = {
                "author": author,
                "found": data.get("numFound", 0),
                "showing": len(books),
                "books": books
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return f"Arama başarısız. Status Code: {response.status_code}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@mcp.tool()
def get_author_info(author_olid: str) -> str:
    """
    Yazar OLID'i kullanarak yazar bilgilerini getir.
    Örnek: OL23919A
    """
    try:
        url = f"https://openlibrary.org/authors/{author_olid}.json"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            result = {
                "name": data.get("name", "Bilinmiyor"),
                "birth_date": data.get("birth_date", "Bilinmiyor"),
                "death_date": data.get("death_date", "Bilinmiyor"),
                "bio": data.get("bio", "Biyografi mevcut değil"),
                "wikipedia": data.get("wikipedia", ""),
                "website": data.get("website", ""),
                "url": f"https://openlibrary.org/authors/{author_olid}"
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return f"Yazar bulunamadı. Status Code: {response.status_code}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@mcp.tool()
def get_work_info(work_olid: str) -> str:
    """
    Work OLID'i kullanarak eser bilgilerini getir.
    Örnek: OL45883W
    """
    try:
        url = f"https://openlibrary.org/works/{work_olid}.json"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            result = {
                "title": data.get("title", "Bilinmiyor"),
                "description": data.get("description", "Açıklama mevcut değil"),
                "subjects": data.get("subjects", []),
                "authors": data.get("authors", []),
                "first_publish_date": data.get("first_publish_date", "Bilinmiyor"),
                "covers": data.get("covers", []),
                "url": f"https://openlibrary.org/works/{work_olid}"
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return f"Eser bulunamadı. Status Code: {response.status_code}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

# MCP sunucusunu çalıştır
if __name__ == '__main__':
    mcp.run()
