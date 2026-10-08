"""
Problem 3: CSV Import to SQLite
-------------------------------
Reads user records from `users.csv` using Python's standard `csv` module,
creates an SQLite database (`users.db`) with a `users` table enforcing an auto-incrementing
primary key and unique email constraint, inserts records using parameterized SQL queries,
gracefully handles duplicate email entries and edge cases, and displays stored users.

Author: Vimlesh Tiwari
"""

import csv
import os
import sqlite3
import sys
from typing import Dict, List, Tuple

CSV_FILE = "users.csv"
DB_FILE = "users.db"


def init_database(db_path: str = DB_FILE) -> None:
    """
    Initialize SQLite database and create the users table:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - name: TEXT NOT NULL
    - email: TEXT NOT NULL UNIQUE
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        print(f"[+] Database verified: table 'users' ready in '{db_path}'.")
    except sqlite3.Error as err:
        print(f"[ERROR] Database initialization failed: {err}", file=sys.stderr)
        raise
    finally:
        if conn:
            conn.close()


def read_users_from_csv(csv_path: str = CSV_FILE) -> List[Dict[str, str]]:
    """
    Read user records from a CSV file using Python's standard csv module.
    Validates file existence, header presence, and non-empty values.
    
    Args:
        csv_path: Path to the CSV file.
        
    Returns:
        List of dictionaries with 'name' and 'email' fields.
    """
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found at: '{csv_path}'", file=sys.stderr)
        return []

    users: List[Dict[str, str]] = []

    try:
        with open(csv_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            
            # Validate headers
            fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]
            if "name" not in fieldnames or "email" not in fieldnames:
                print(f"[ERROR] Missing required columns ('name', 'email') in CSV. Found: {reader.fieldnames}", file=sys.stderr)
                return []

            for row_num, row in enumerate(reader, start=2):
                name = row.get("name", "").strip() if row.get("name") else ""
                email = row.get("email", "").strip().lower() if row.get("email") else ""

                # Handle empty values
                if not name or not email:
                    print(f"[WARNING] Skipping row {row_num}: Missing name or email (name='{name}', email='{email}')")
                    continue

                users.append({"name": name, "email": email})

        print(f"[SUCCESS] Successfully read {len(users)} record(s) from '{csv_path}'.")
    except (csv.Error, OSError) as err:
        print(f"[ERROR] Error reading CSV file '{csv_path}': {err}", file=sys.stderr)

    return users


def import_users_to_db(db_path: str, users: List[Dict[str, str]]) -> Tuple[int, int]:
    """
    Insert user records into SQLite using parameterized queries.
    Gracefully handles duplicate email constraint violations.
    
    Args:
        db_path: Path to the SQLite database.
        users: List of user dicts.
        
    Returns:
        Tuple of (inserted_count, duplicate_count).
    """
    if not users:
        print("[!] No user records available to insert.")
        return 0, 0

    insert_query = """
    INSERT INTO users (name, email)
    VALUES (?, ?);
    """

    inserted_count = 0
    duplicate_count = 0
    conn = None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for user in users:
            name = user["name"]
            email = user["email"]
            try:
                cursor.execute(insert_query, (name, email))
                inserted_count += 1
            except sqlite3.IntegrityError:
                # Catch UNIQUE constraint on email column
                print(f"[NOTICE] Duplicate email ignored: '{email}' for user '{name}'.")
                duplicate_count += 1
            except sqlite3.Error as row_err:
                print(f"[ERROR] Could not insert record ({name}, {email}): {row_err}", file=sys.stderr)
        
        conn.commit()
        print(f"[+] Import finished: {inserted_count} record(s) inserted, {duplicate_count} duplicate(s) skipped.")
    except sqlite3.Error as db_err:
        print(f"[ERROR] Database transaction failed: {db_err}", file=sys.stderr)
    finally:
        if conn:
            conn.close()

    return inserted_count, duplicate_count


def fetch_all_users(db_path: str = DB_FILE) -> List[Tuple[int, str, str]]:
    """
    Retrieve all user records from SQLite.
    """
    select_query = "SELECT id, name, email FROM users ORDER BY id ASC;"
    records: List[Tuple[int, str, str]] = []
    conn = None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(select_query)
        records = cursor.fetchall()
    except sqlite3.Error as err:
        print(f"[ERROR] Failed to query users table: {err}", file=sys.stderr)
    finally:
        if conn:
            conn.close()

    return records


def display_users_table(users: List[Tuple[int, str, str]]) -> None:
    """
    Display users in a clean tabular terminal view.
    """
    if not users:
        print("[!] No user records found in the database.")
        return

    print("\n" + "=" * 60)
    print(f"{'ID':<6} | {'Name':<22} | {'Email':<26}")
    print("-" * 60)
    
    for user_id, name, email in users:
        display_name = (name[:19] + "...") if len(name) > 22 else name
        display_email = (email[:23] + "...") if len(email) > 26 else email
        print(f"{user_id:<6} | {display_name:<22} | {display_email:<26}")

    print("=" * 60 + "\n")


def main() -> None:
    """
    Main orchestration function for Problem 3.
    """
    print("\n--- Problem 3: CSV Import to SQLite ---")

    # 1. Initialize SQLite Database & Table
    init_database(DB_FILE)

    # 2. Ingest records from CSV file
    user_records = read_users_from_csv(CSV_FILE)
    if not user_records:
        print("[ERROR] No valid CSV records found to import.", file=sys.stderr)
        return

    # 3. Import records into SQLite with duplicate email protection
    inserted, duplicates = import_users_to_db(DB_FILE, user_records)

    # 4. Fetch and display all records currently in SQLite
    stored_users = fetch_all_users(DB_FILE)
    print(f"\n[+] Total Users in SQLite ({DB_FILE}):")
    display_users_table(stored_users)


if __name__ == "__main__":
    main()
