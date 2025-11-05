import sqlite3
import json
import os
import threading
import random
import string
import zipfile
import hashlib
from datetime import datetime
import time
import sys
from pyfiglet import Figlet
from termcolor import colored


# =================== BANNER FUNKSIYALARI ===================

def type_effect(text, color='green', delay=0.01):
    for ch in text:
        sys.stdout.write(colored(ch, color))
        sys.stdout.flush()
        time.sleep(delay)
    print()


def animated_banner():
    f = Figlet(font='banner3-D')
    banner = f.renderText("Online Shop Platform")
    type_effect(banner, color='cyan', delay=0.0004)
    type_effect("🛒 Desktop CLI versiyasi 🖥️", color='yellow', delay=0.02)
    type_effect("🚀 100% Python | Professional Terminal Interface 🚀", color='green', delay=0.015)
    type_effect("==============================================", color='magenta', delay=0.005)
    print("""
    1️⃣ Mahsulotlar ro‘yxati
    2️⃣ Yangi buyurtma
    3️⃣ Loglarni ko‘rish
    4️⃣ SQL buyruq yozish
    5️⃣ Chiqish
    6️⃣ Mahsulot qo‘shish
    """)


# =================== BAZA KONTROLLER ===================

class SQLController:
    def __init__(self, db_name="onlineshop.db", backup_dir="backups"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
        print(f"🗃️ Bazaga ulandi: {self.db_name}")

    def execute(self, query, params=None, fetch=False):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            if query.strip().lower().startswith(("insert", "update", "delete", "create", "drop", "alter", "replace")):
                self.conn.commit()
            if fetch:
                return self.cursor.fetchall()
            return []
        except sqlite3.Error as e:
            print(f"❌ SQL xatolik: {e}")
            return []

    def executemany(self, query, param_list):
        try:
            self.cursor.executemany(query, param_list)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"❌ SQL xatolik (executemany): {e}")

    def close(self):
        self.conn.close()
        print("🔒 Bazaga ulanish yopildi.")


# =================== BAZA JADVALLAR VA TRIGGERLAR ===================

def setup_online_shop(db: SQLController):
    print("🛠️ Online Shop Database jadvallar yaratilmoqda...")

    # --- Mahsulotlar ---
    db.execute("""
    CREATE TABLE IF NOT EXISTS Mahsulotlar (
        MahsulotID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nomi TEXT,
        Narx REAL,
        Miqdor INTEGER
    );
    """)

    # --- Buyurtmalar ---
    db.execute("""
    CREATE TABLE IF NOT EXISTS Buyurtmalar (
        BuyurtmaID INTEGER PRIMARY KEY AUTOINCREMENT,
        Foydalanuvchi TEXT,
        MahsulotID INTEGER,
        Miqdor INTEGER,
        Sana TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (MahsulotID) REFERENCES Mahsulotlar(MahsulotID)
    );
    """)

    # --- Loglar ---
    db.execute("""
    CREATE TABLE IF NOT EXISTS Loglar (
        LogID INTEGER PRIMARY KEY AUTOINCREMENT,
        Amal TEXT,
        Sana TEXT DEFAULT (datetime('now'))
    );
    """)

    # --- TRIGGER: Buyurtma qo‘shilganda log yozish ---
    db.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_BuyurtmaQoshildi
    AFTER INSERT ON Buyurtmalar
    BEGIN
        INSERT INTO Loglar (Amal)
        VALUES (
            (SELECT Foydalanuvchi FROM Buyurtmalar WHERE BuyurtmaID = NEW.BuyurtmaID)
            || ' foydalanuvchi '
            || NEW.Miqdor || ' dona mahsulot (ID:' || NEW.MahsulotID || ') buyurtma qildi.'
        );
    END;
    """)

    # --- 🆕 TRIGGER: Mahsulot qo‘shilganda log yozish ---
    db.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_MahsulotQoshildi
    AFTER INSERT ON Mahsulotlar
    BEGIN
        INSERT INTO Loglar (Amal)
        VALUES (
            '🆕 Yangi mahsulot qo‘shildi: ' 
            || NEW.Nomi || ', narxi: ' || NEW.Narx || ' so‘m, miqdor: ' || NEW.Miqdor || '.'
        );
    END;
    """)

    # --- Agar jadval bo‘sh bo‘lsa, namunaviy ma’lumotlar ---
    rows = db.execute("SELECT COUNT(*) FROM Mahsulotlar;", fetch=True)
    if rows and rows[0][0] == 0:
        db.executemany("INSERT INTO Mahsulotlar (Nomi, Narx, Miqdor) VALUES (?, ?, ?);", [
            ("Laptop", 8500.00, 10),
            ("Sichqoncha", 120.00, 50),
            ("Klaviatura", 300.00, 30),
            ("Monitor", 1500.00, 15),
            ("Quloqchin", 200.00, 40),
            ("Printer", 700.00, 8),
            ("USB fleshka", 80.00, 100),
            ("Smartfon", 6000.00, 20),
            ("Planshet", 4000.00, 25),
            ("Wi-Fi router", 250.00, 35),
            ("Web-kamera", 180.00, 45),
            ("Zaryadlovchi", 90.00, 60),
            ("Qog‘oz", 15.00, 200),
            ("Ruchka", 5.00, 500),
            ("Kalkulyator", 50.00, 80),
            ("Projektor", 3000.00, 5),
            ("Tashqi qattiq disk", 400.00, 22),
            ("SD karta", 70.00, 75),
            ("Bluetooth naushnik", 150.00, 33),
            ("Smart soat", 350.00, 18),
            ("Elektron kitob o‘quvchi", 1200.00, 12),
            ("Grafik planshet", 2200.00, 7),
            ("VR ko‘zoynak", 2800.00, 9),
            ("Ovoz tizimi", 500.00, 14),
            ("Kabel to‘plami", 40.00, 150),
            ("Docking station", 600.00, 11),
            ("Qulay stul", 1300.00, 6),
            ("Ish stoli", 2500.00, 4),
            ("Monitor stendi", 200.00, 27),
            ("Simsiz quloqchin", 220.00, 29),
            ("Portativ zaryadlovchi", 180.00, 55),
            ("Smartfon aksessuarlari to‘plami", 90.00, 65),
            ("Kompyuter o‘yinlari to‘plami", 75.00, 85),
            ("Multimedia proyektori", 3200.00, 3),
            ("3D printer", 4500.00, 2),
            ("Kompakt disklar to‘plami", 25.00, 120),
            ("Kengaytirilgan klaviatura", 350.00, 28),
            ("Ergonomik sichqoncha", 160.00, 38),
            ("Yuqori sifatli mikrofon", 400.00, 16),
            ("Ovoz kartasi", 550.00, 13),
            ("Grafik karta", 7000.00, 5),
            ("Protsessor", 9000.00, 4),
            ("Operativ xotira (RAM)", 3000.00, 10),
            ("Qattiq disk (HDD)", 2500.00, 15),
            ("Solishtirilgan qattiq disk (SSD)", 4000.00, 12),
            ("Onlayn o‘yin obunasi", 150.00, 100),
            ("Bulutli saqlash xizmati obunasi", 200.00, 80),
            ("Antivirus dasturi litsenziyasi", 100.00, 90),
        ])
        print("✅ Dastlabki mahsulotlar kiritildi.")

    print("✅ Online Shop bazasi tayyor.\n")


# =================== CLI FUNKSIYALAR ===================

def show_products(db: SQLController):
    rows = db.execute("SELECT * FROM Mahsulotlar;", fetch=True)
    print("\n📦 Mahsulotlar:")
    for r in rows:
        print(f"🆔 {r[0]} | {r[1]} | 💰 {r[2]} so‘m | 🧮 {r[3]} dona")


def make_order(db: SQLController):
    user = input("👤 Foydalanuvchi: ")
    show_products(db)
    pid = int(input("Mahsulot ID: "))
    qty = int(input("Miqdor: "))

    prod = db.execute("SELECT Miqdor FROM Mahsulotlar WHERE MahsulotID=?;", (pid,), fetch=True)
    if not prod:
        print("❌ Bunday mahsulot topilmadi.")
        return
    if prod[0][0] < qty:
        print("⚠️ Yetarli mahsulot yo‘q.")
        return

    db.execute("INSERT INTO Buyurtmalar (Foydalanuvchi, MahsulotID, Miqdor) VALUES (?, ?, ?);", (user, pid, qty))
    db.execute("UPDATE Mahsulotlar SET Miqdor = Miqdor - ? WHERE MahsulotID = ?;", (qty, pid))
    print("✅ Buyurtma qo‘shildi (trigger orqali log yozildi).")


def view_logs(db: SQLController):
    logs = db.execute("SELECT * FROM Loglar ORDER BY LogID DESC;", fetch=True)
    print("\n🧾 Loglar:")
    for log in logs:
        print(f"🕓 {log[2]} | {log[1]}")


def run_sql_shell(db: SQLController):
    print("🧩 SQL shell (chiqish uchun 'quit')")
    while True:
        q = input("sqlite> ")
        if q.lower() in ("exit", "quit", "back"):
            break
        rows = db.execute(q, fetch=True)
        for r in rows:
            print(r)


# 🆕 Mahsulot qo‘shish (trigger avtomatik log yozadi)
def add_product(db: SQLController):
    print("\n➕ Yangi mahsulot qo‘shish:")
    name = input("🛍️ Mahsulot nomi: ").strip()
    price = float(input("💰 Narxi: "))
    qty = int(input("🧮 Miqdori: "))

    db.execute("INSERT INTO Mahsulotlar (Nomi, Narx, Miqdor) VALUES (?, ?, ?);", (name, price, qty))
    print(f"✅ '{name}' mahsulot bazaga qo‘shildi (log yozildi).")


# =================== MAIN ===================

def main():
    db = SQLController()
    #setup_online_shop(db)

    while True:
        animated_banner()
        tanlov = input("👉 Bo‘lim tanlang: ").strip()
        if tanlov == "1":
            show_products(db)
        elif tanlov == "2":
            make_order(db)
        elif tanlov == "3":
            view_logs(db)
        elif tanlov == "4":
            run_sql_shell(db)
        elif tanlov == "5":
            db.close()
            print("👋 Dasturdan chiqildi.")
            break
        elif tanlov == "6":
            add_product(db)
        else:
            print("❌ Noto‘g‘ri tanlov.")
        input("\n⏎ Davom etish uchun Enter bosing...")


if __name__ == "__main__":
    main()
