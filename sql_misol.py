import sqlite3
import json
import os
import threading
import random
import string
import zipfile
import hashlib
from datetime import datetime
from typing import Any, List, Tuple, Optional
import time
import sys
from pyfiglet import Figlet
from termcolor import colored

def type_effect(text, color='green', delay=0.01):
    """Matnni harflab chiqarish effekti"""
    for ch in text:
        sys.stdout.write(colored(ch, color))
        sys.stdout.flush()
        time.sleep(delay)
    return print()

class SQLController:
    def __init__(self, db_name: str = "database.db", backup_dir: str = "backups"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
        self.table_hashes = {}  # Delta-backup uchun hash saqlanadi

        print(f"🗃️ SQLite bazaga ulandi: {self.db_name}")
        self._start_auto_backup()

    # =====================================================
    # === ASOSIY SQL FUNKSIYALAR ===
    # =====================================================

    def execute(self, query: str, params: Optional[Tuple[Any]] = None, fetch: bool = False) -> List[Tuple]:
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            if query.strip().lower().startswith(("insert", "update", "delete", "create", "drop", "alter")):
                self.conn.commit()
                self._update_table_hashes()

            if fetch:
                return self.cursor.fetchall()
            return []
        except sqlite3.Error as e:
            print(f"❌ SQL xatolik: {e}")
            return []

    def executemany(self, query: str, param_list: List[Tuple[Any]]):
        try:
            self.cursor.executemany(query, param_list)
            self.conn.commit()
            self._update_table_hashes()
        except sqlite3.Error as e:
            print(f"❌ SQL xatolik (executemany): {e}")

    # =====================================================
    # === FOYDALI METODLAR ===
    # =====================================================

    def show_tables(self) -> List[str]:
        tables = self.execute("SELECT name FROM sqlite_master WHERE type='table';", fetch=True)
        return [t[0] for t in tables]

    def describe_table(self, table: str):
        info = self.execute(f"PRAGMA table_info({table});", fetch=True)
        print(f"\n🧱 Jadval tuzilmasi: {table}")
        for col in info:
            print(f"  - {col[1]} ({col[2]})")

    # =====================================================
    # === JSON IMPORT / EXPORT ===
    # =====================================================

    def export_to_json(self, table: str, file_path: Optional[str] = None):
        try:
            rows = self.execute(f"SELECT * FROM {table}", fetch=True)
            if not rows:
                return None

            columns = [col[1] for col in self.execute(f"PRAGMA table_info({table});", fetch=True)]
            data = [dict(zip(columns, row)) for row in rows]

            if not file_path:
                file_path = os.path.join(self.backup_dir, f"{table}_export.json")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            return file_path
        except Exception as e:
            print(f"❌ JSON eksport xatosi: {e}")
            return None

    def import_from_json(self, table: str, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                return
            columns = data[0].keys()
            placeholders = ", ".join(["?" for _ in columns])
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            self.executemany(query, [tuple(item.values()) for item in data])
        except Exception as e:
            print(f"❌ JSON import xatosi: {e}")

    # =====================================================
    # === ZIP + PAROL ===
    # =====================================================

    def _generate_password(self, length: int = 32) -> str:
        chars = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(chars) for _ in range(length))

    def _zip_with_password(self, json_path: str, password: str) -> str:
        zip_name = json_path.replace(".json", ".zip")
        with zipfile.ZipFile(zip_name, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.setpassword(password.encode())
            zipf.write(json_path, os.path.basename(json_path))
        os.remove(json_path)
        return zip_name

    # =====================================================
    # === DELTA-BACKUP (faqat o‘zgargan jadvallar) ===
    # =====================================================

    def _hash_table(self, table: str) -> str:
        """Jadvaldagi barcha ma’lumotlardan hash yaratadi."""
        rows = self.execute(f"SELECT * FROM {table}", fetch=True)
        return hashlib.sha256(str(rows).encode()).hexdigest()

    def _update_table_hashes(self):
        """Har safar o‘zgarish bo‘lganda hashlarni yangilaydi."""
        for table in self.show_tables():
            self.table_hashes[table] = self._hash_table(table)

    def _detect_changed_tables(self) -> List[str]:
        """Oldingi hash bilan solishtirib, o‘zgargan jadvallarni qaytaradi."""
        changed = []
        for table in self.show_tables():
            new_hash = self._hash_table(table)
            if self.table_hashes.get(table) != new_hash:
                changed.append(table)
                self.table_hashes[table] = new_hash
        return changed

    # =====================================================
    # === AUTO-BACKUP (delta) ===
    # =====================================================

    def _auto_backup_job(self):
        """Har 24 soatda o‘zgargan jadvallarni zaxiralaydi."""
        today = datetime.now().strftime("%Y-%m-%d")
        changed_tables = self._detect_changed_tables()
        if not changed_tables:
            print(f"🕒 {today}: Hech qanday o‘zgarish yo‘q, backup o‘tkazib yuborildi.")
        else:
            for table in changed_tables:
                json_path = os.path.join(self.backup_dir, f"{table}_backup_{today}.json")
                exported = self.export_to_json(table, json_path)
                if exported:
                    password = self._generate_password()
                    zip_path = self._zip_with_password(exported, password)
                    log_path = os.path.join(self.backup_dir, "backup_log.txt")
                    with open(log_path, "a", encoding="utf-8") as log:
                        log.write(f"[{datetime.now()}] {zip_path} | PASSWORD: {password}\n")
                    print(f"🔐 Delta-backup: {table} -> {zip_path}")
        threading.Timer(86400, self._auto_backup_job).start()

    def _start_auto_backup(self):
        print("🧠 Delta-backup tizimi ishga tushdi (24 soatda 1 marta).")
        self._update_table_hashes()
        threading.Timer(5, self._auto_backup_job).start()

    def close(self):
        self.conn.close()
        print("🔒 Bazaga ulanish yopildi.")


# =====================================================
# === CLI QISMI (INTERAKTIV MIKRO-KONTROLLER) ===
# =====================================================

def animated_banner():
    """Asosiy banner funksiyasi"""
    f = Figlet(font='banner3-D')  # font: 'slant', 'standard', 'doom', 'banner3-D' va boshqalar
    banner = f.renderText("SQL Platform")

    # Asosiy banner
    type_effect(banner, color='cyan', delay=0.0004)

    # Pastki yozuvlar
    type_effect("🛒 Desktop CLI versiyasi 🖥️", color='yellow', delay=0.02)
    type_effect("🚀 100% Python | Professional Terminal Interface 🚀", color='green', delay=0.015)
    type_effect("==============================================", color='magenta', delay=0.005)
    print()  # Bo‘sh qatordan keyin dastur asosiy qismini boshlasangiz bo‘ladi.
    print(f"""
          {type_effect("1️⃣ Jadval yaratish", color='magenta', delay=0.005)}
          {type_effect("2️⃣ Ma'lumot qo‘shish", color='magenta', delay=0.005)}
          {type_effect("3️⃣ Ma'lumotlarni ko‘rish", color='magenta', delay=0.005)}
          {type_effect("4️⃣ Ma'lumotni yangilash", color='magenta', delay=0.005)}
          {type_effect("5️⃣ Ma'lumotni o‘chirish", color='magenta', delay=0.005)}
          {type_effect("6️⃣ Bazadagi jadvallar", color='magenta', delay=0.005)}
          {type_effect("7️⃣ Jadval tuzilmasini ko‘rish", color='magenta', delay=0.005)}
          {type_effect("8️⃣ SQL buyruqni bevosita yozish", color='magenta', delay=0.005)}
          {type_effect("9️⃣ JSON eksport/import", color='magenta', delay=0.005)}
          {type_effect("🔟 Chiqish", color='magenta', delay=0.005)}""")

def show_main_menu():
    animated_banner()
    
def create_default_table(db: SQLController):
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        balance REAL DEFAULT 0
    )
    """)
    print("✅ 'users' jadvali tayyor.")


def insert_data(db: SQLController):
    name = input("👤 Ism: ")
    balance = input("💰 Balans (ixtiyoriy): ")
    if balance.strip() == "":
        db.execute("INSERT INTO users (name) VALUES (?)", (name,))
    else:
        db.execute("INSERT INTO users (name, balance) VALUES (?, ?)", (name, float(balance))) # type: ignore
    print(f"✅ '{name}' foydalanuvchi qo‘shildi.")


def view_data(db: SQLController):
    rows = db.execute("SELECT * FROM users", fetch=True)
    if not rows:
        print("⚠️ Ma'lumot yo‘q.")
        return
    for row in rows:
        print(f"🆔 {row[0]} | 👤 {row[1]} | 💰 {row[2]}")


def update_data(db: SQLController):
    uid = input("🆔 ID: ")
    new_balance = input("💰 Yangi balans: ")
    db.execute("UPDATE users SET balance=? WHERE id=?", (float(new_balance), int(uid))) # type: ignore
    print("✅ Balans yangilandi.")


def delete_data(db: SQLController):
    uid = input("🗑️ O‘chiriladigan foydalanuvchi ID: ")
    db.execute("DELETE FROM users WHERE id=?", (int(uid),))
    print("🧹 O‘chirildi.")


def json_menu(db: SQLController):
    print("""
📦 JSON OPERATSIYALAR:
1️⃣ Eksport (bazadan JSON)
2️⃣ Import (JSON'dan bazaga)
3️⃣ Orqaga
""")
    choice = input("👉 Tanlang: ")
    if choice == "1":
        table = input("Jadval nomi: ")
        db.export_to_json(table)
    elif choice == "2":
        table = input("Jadval nomi: ")
        path = input("JSON fayl yo‘li: ")
        db.import_from_json(table, path)


def run_raw_query(db: SQLController):
    while True:
        query = input("sqlite> ")
        if query.lower() in ("exit", "back", "quit"):
            break
        rows = db.execute(query, fetch=True)
        for row in rows:
            print(row)


def main():
    db = SQLController("users.db")
    create_default_table(db)

    while True:
        show_main_menu()
        choice = input("👉 Bo‘lim tanlang: ").strip()

        if choice == "1":
            create_default_table(db)
        elif choice == "2":
            insert_data(db)
        elif choice == "3":
            view_data(db)
        elif choice == "4":
            update_data(db)
        elif choice == "5":
            delete_data(db)
        elif choice == "6":
            print(db.show_tables())
        elif choice == "7":
            print("Jadval tuzilmasini ko‘rish:")
            print("Mavjud jadvallar :", db.show_tables())
            db.describe_table(input("Jadval nomi: "))
        elif choice == "8":
            run_raw_query(db)
        elif choice == "9":
            json_menu(db)
        elif choice == "10":
            db.close()
            print("👋 Chiqildi.")
            break
        else:
            print("❌ Noto‘g‘ri tanlov.")


if __name__ == "__main__":
    main()
