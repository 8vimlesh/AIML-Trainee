"""
Problem 1: API Data Retrieval and SQLite Storage
------------------------------------------------
Fetches book records from the Open Library REST API (Fantasy subject),
parses the JSON response, persists records into a local SQLite database (books.db)
using parameterized queries, retrieves stored records, and displays them in a clean
tabular format in the terminal.

Author: Vimlesh Tiwari
"""

import sqlite3
import sys
from typing import Any, Dict, List, Tuple
import requests

API_URL = "https://openlibrary.org/subjects/fantasy.json?limit=10"
DB_FILE = "books.db"


def fetch_books_from_api(url: str = API_URL, timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch book data from the external Open Library REST API.
    
    Args:
        url: The API endpoint URL to query.
        timeout: Request timeout in seconds.
        
    Returns:
        List of dictionaries containing parsed book information.
    """
    print(f"[*] Calling REST API: {url}")
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print("[ERROR] API request timed out.", file=sys.stderr)
        return []
    except requests.exceptions.ConnectionError:
        print("[ERROR] Network connection failed. Please check your internet connection.", file=sys.stderr)
        return []
    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error returned by API: {http_err}", file=sys.stderr)
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"[ERROR] Request failed: {req_err}", file=sys.stderr)
        return []
    except ValueError as json_err:
        print(f"[ERROR] Invalid JSON response received: {json_err}", file=sys.stderr)
        return []

    works = data.get("works", [])
    if not works or not isinstance(works, list):
        print("[WARNING] API returned an empty or invalid 'works' dataset.")
        return []

    books: List[Dict[str, Any]] = []
    for item in works:
        if not isinstance(item, dict):
            continue

        title = item.get("title", "").strip() or "Unknown Title"
        
        # Open Library provides authors as a list of dicts: [{'name': '...'}]
        authors_raw = item.get("authors", [])
        if isinstance(authors_raw, list) and authors_raw:
            author_names = [a.get("name", "").strip() for a in authors_raw if isinstance(a, dict) and a.get("name")]
            author = ", ".join(author_names) if author_names else "Unknown Author"
        else:
            author = "Unknown Author"
        
        pub_year = item.get("first_publish_year")
        publication_year = pub_year if isinstance(pub_year, int) else None

        books.append({
            "title": title,
            "author": author,
            "publication_year": publication_year
        })

    print(f"[SUCCESS] Retrieved and parsed {len(books)} books from API.")
    return books


def init_database(db_path: str = DB_FILE) -> None:
    """
    Initialize SQLite database and create the books table if it does not exist.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        publication_year INTEGER
    );
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        print(f"[+] Database verified: table 'books' ready in '{db_path}'.")
    except sqlite3.Error as err:
        print(f"[ERROR] Database initialization failed: {err}", file=sys.stderr)
        raise
    finally:
        if conn:
            conn.close()


def insert_books(db_path: str, books: List[Dict[str, Any]]) -> int:
    """
    Insert book records into the SQLite database using parameterized queries.
    """
    if not books:
        print("[!] No records available to insert into database.")
        return 0

    insert_query = """
    INSERT INTO books (title, author, publication_year)
    VALUES (?, ?, ?);
    """
    
    inserted_count = 0
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for book in books:
            cursor.execute(insert_query, (
                book.get("title"),
                book.get("author"),
                book.get("publication_year")
            ))
            inserted_count += 1
        conn.commit()
        print(f"[+] Inserted {inserted_count} record(s) into '{db_path}'.")
    except sqlite3.Error as err:
        print(f"[ERROR] Database insertion error: {err}", file=sys.stderr)
    finally:
        if conn:
            conn.close()
            
    return inserted_count


def fetch_stored_books(db_path: str = DB_FILE) -> List[Tuple[int, str, str, Any]]:
    """
    Retrieve all stored book records from SQLite.
    """
    select_query = "SELECT id, title, author, publication_year FROM books ORDER BY id ASC;"
    records: List[Tuple[int, str, str, Any]] = []
    conn = None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(select_query)
        records = cursor.fetchall()
    except sqlite3.Error as err:
        print(f"[ERROR] Failed to query database records: {err}", file=sys.stderr)
    finally:
        if conn:
            conn.close()
            
    return records


def display_books_table(books: List[Tuple[int, str, str, Any]]) -> None:
    """
    Display book records in a clean tabular terminal view.
    """
    if not books:
        print("[!] No records found in the database to display.")
        return

    print("\n" + "=" * 84)
    print(f"{'ID':<4} | {'Title':<42} | {'Author':<24} | {'Year':<6}")
    print("-" * 84)
    
    for row in books:
        book_id, title, author, year = row
        display_title = (title[:39] + "...") if title and len(title) > 42 else (title or "N/A")
        display_author = (author[:21] + "...") if author and len(author) > 24 else (author or "N/A")
        display_year = str(year) if year is not None else "N/A"
        
        print(f"{book_id:<4} | {display_title:<42} | {display_author:<24} | {display_year:<6}")
        
    print("=" * 84 + "\n")


def main() -> None:
    """
    Main orchestration function for Problem 1.
    """
    print("\n--- Problem 1: REST API Data Retrieval & SQLite Storage ---")
    
    # 1. Fetch data from external REST API
    books_data = fetch_books_from_api(API_URL)
    
    # Fallback to sample data if network/API is unavailable
    if not books_data:
        print("[*] API unreachable. Utilizing fallback dataset to demonstrate database persistence...")
        books_data = [
            {"title": "The Hobbit", "author": "J.R.R. Tolkien", "publication_year": 1937},
            {"title": "The Name of the Wind", "author": "Patrick Rothfuss", "publication_year": 2007},
            {"title": "A Game of Thrones", "author": "George R.R. Martin", "publication_year": 1996}
        ]

    # 2. Initialize Database & Table
    init_database(DB_FILE)

    # 3. Insert records using parameterized queries
    insert_books(DB_FILE, books_data)

    # 4. Read back records from SQLite
    stored_records = fetch_stored_books(DB_FILE)

    # 5. Display tabular terminal output
    print(f"\n[+] Total Books Stored in SQLite ({DB_FILE}):")
    display_books_table(stored_records)


if __name__ == "__main__":
    main()
