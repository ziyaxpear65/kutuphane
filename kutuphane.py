import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Veritabanı bağlantısı
conn = sqlite3.connect("library.db", check_same_thread=False)
c = conn.cursor()

# Gelişmiş Kütüphane Veritabanı Tabloları
c.execute('''CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, author TEXT,
                genre TEXT, year INTEGER,
                available INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, email TEXT UNIQUE, phone TEXT, join_date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER, member_id INTEGER,
                issue_date TEXT, return_date TEXT,
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(member_id) REFERENCES members(id))''')
conn.commit()


# Kitap ekleme fonksiyonu
def add_book(title, author, genre, year, quantity):
    existing_book = c.execute("SELECT * FROM books WHERE title = ? AND author = ?", (title, author)).fetchone()
    if existing_book:
        new_available = existing_book[5] + quantity
        c.execute("UPDATE books SET available = ? WHERE id = ?", (new_available, existing_book[0]))
        conn.commit()
    else:
        c.execute("INSERT INTO books (title, author, genre, year, available) VALUES (?, ?, ?, ?, ?)",
                  (title, author, genre, year, quantity))
        conn.commit()


# Kitap silme fonksiyonu
def delete_book(book_id):
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()


# Üye ekleme fonksiyonu
def add_member(name, email, phone):
    c.execute("INSERT INTO members (name, email, phone, join_date) VALUES (?, ?, ?, ?)",
              (name, email, phone, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()


# Kitap ödünç alma fonksiyonu
def borrow_book(book_id, member_id):
    c.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
    c.execute("INSERT INTO transactions (book_id, member_id, issue_date) VALUES (?, ?, ?)",
              (book_id, member_id, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()


# Kitap iade etme fonksiyonu
def return_book(book_id):
    c.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
    c.execute("UPDATE transactions SET return_date = ? WHERE book_id = ? AND return_date IS NULL",
              (datetime.now().strftime("%Y-%m-%d"), book_id))
    conn.commit()


def delete_member(member_id):
    borrowed = c.execute("SELECT * FROM transactions WHERE member_id = ? AND return_date IS NULL",
                         (member_id,)).fetchone()

    if borrowed:
        st.error("Bu üyenin aktif ödünç aldığı kitaplar var. Önce iade edilmelidir!")
    else:
        c.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        st.success("Üye başarıyla silindi!")


# Üye güncelleme fonksiyonu
def update_member(member_id, name, email, phone):
    c.execute("UPDATE members SET name = ?, email = ?, phone = ? WHERE id = ?", (name, email, phone, member_id))
    conn.commit()
    st.success("Üye bilgileri başarıyla güncellendi!")


# Streamlit arayüzü
st.title("📚 Kütüphane Yönetim Sistemi")
menu = st.sidebar.selectbox("Menü", ["Kitaplar", "Üyeler", "İşlemler", "İstatistikler", "Kitap Ara", "Arama",
                                     "Gelişmiş Raporlar","Üye Kitap Hareketleri"])

if menu == "Kitaplar":
    st.subheader("📖 Kitap Yönetimi")
    action = st.radio("İşlem Seçin", ["Kitap Ekle", "Kitapları Görüntüle", "Kitap Sil"])

    if action == "Kitap Ekle":
        title = st.text_input("Kitap Adı")
        author = st.text_input("Yazar")
        genre = st.text_input("Tür")
        year = st.number_input("Yıl", min_value=1000, max_value=2025, step=1)
        quantity = st.number_input("Adet", min_value=1, step=1)
        if st.button("Ekle"):
            add_book(title, author, genre, year, quantity)
            st.success("Kitap eklendi veya güncellendi!")

    elif action == "Kitap Sil":
        book_id = st.number_input("Silinecek Kitap ID", min_value=1)
    if st.button("Sil"):
        delete_book(book_id)
        st.success("Kitap silindi!")
    else:
        books = pd.read_sql("SELECT * FROM books", conn)
        st.dataframe(books)

if menu == "Üyeler":
    st.subheader("👤 Üye Yönetimi")
    action = st.radio("İşlem Seçin", ["Üye Ekle", "Üyeleri Görüntüle", "Üye Sil", "Üye Güncelle"])
    if action == "Üye Ekle":
        name = st.text_input("Üye Adı")
        email = st.text_input("E-posta")
        phone = st.text_input("Telefon", max_chars=11)
        if st.button("Ekle"):
            if phone.isdigit() and len(phone) == 11:
                add_member(name, email, phone)
                st.success("Üye eklendi!")
                st.rerun()
            else:
                st.error("Telefon numarası 11 haneli olmalı ve sadece rakam içermelidir!")

    elif action == "Üye Güncelle":
        member_id = st.number_input("Güncellenecek Üye ID", min_value=1)
        name = st.text_input("Yeni Ad")
        email = st.text_input("Yeni E-posta")
        phone = st.text_input("Yeni Telefon", max_chars=11)
        if st.button("Güncelle"):
            if phone.isdigit() and len(phone) == 11:
                update_member(member_id, name, email, phone)
                st.success("Üye güncellendi!")
                st.rerun()
            else:
                st.error("Telefon numarası 11 haneli olmalı ve sadece rakam içermelidir!")
        members = pd.read_sql("SELECT * FROM members", conn)
        st.dataframe(members)

    elif action == "Üye Sil":
        member_id = st.number_input("Silinecek Üye ID", min_value=1)
        if st.button("Sil"):
            delete_member(member_id)
            st.success("Üye silindi!")
        members = pd.read_sql("SELECT * FROM members", conn)
        st.dataframe(members)

    elif action == "Üyeleri Görüntüle":
        members = pd.read_sql("SELECT * FROM members", conn)
        st.dataframe(members)
elif menu == "İşlemler":
    st.subheader("🔄 Kitap Ödünç Ver & İade Et")
    action = st.radio("İşlem Seç", ["Kitap Ödünç Ver", "Kitap İade Al"])
    if action == "Kitap Ödünç Ver":
        book_id = st.number_input("Kitap ID", min_value=1)
        member_id = st.number_input("Üye ID", min_value=1)
        if st.button("Ödünç Ver"):
            borrow_book(book_id, member_id)
            st.success("Kitap ödünç verildi!")
    else:
        book_id = st.number_input("Kitap ID", min_value=1)
        if st.button("İade Al"):
            return_book(book_id)
            st.success("Kitap iade edildi!")

elif menu == "İstatistikler":
    st.subheader("📊 Kütüphane İstatistikleri")
    total_books = c.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    borrowed_books = c.execute("SELECT COUNT(*) FROM books WHERE available=0").fetchone()[0]
    total_members = c.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    st.metric("Toplam Kitap Sayısı", total_books)
    st.metric("Ödünç Verilen Kitap Sayısı", borrowed_books)
    st.metric("Toplam Üye Sayısı", total_members)

elif menu == "Kitap Ara":
    st.subheader("🔍 Kitap Arama")
    search_title = st.text_input("Kitap Adını Girin")
    if st.button("Ara"):
        c.execute("SELECT * FROM books WHERE title = ?", (search_title,))
        book = c.fetchone()
        if book:
            st.write(f"**Kitap ID:** {book[0]}")
            st.write(f"**Adı:** {book[1]}")
            st.write(f"**Yazar:** {book[2]}")
            st.write(f"**Tür:** {book[3]}")
            st.write(f"**Yıl:** {book[4]}")
            st.write(f"**Durum:** {'Mevcut' if book[5] else 'Ödünçte'}")
        else:
            st.warning("Bu kitap kütüphanemizde mevcut değil.")

elif menu == "Arama":
    st.subheader("🔍 Kitap ve Üye Arama")
    search_type = st.radio("Arama Türü Seçin", ["Kitap Ara", "Üye Ara"])
    search_text = st.text_input("Aranacak Kelime")
    if st.button("Ara"):
        if search_type == "Kitap Ara":
            results = pd.read_sql("SELECT * FROM books WHERE title LIKE ?", conn, params=(f'%{search_text}%',))
        else:
            results = pd.read_sql("SELECT * FROM members WHERE name LIKE ?", conn, params=(f'%{search_text}%',))
        st.dataframe(results)
elif menu == "Üye Kitap Hareketleri":
    st.subheader("📘 Üyelerin Aldığı Kitaplar")
    member_id = st.number_input("Üye ID Girin", min_value=1)
    if st.button("Göster"):
        query = '''SELECT books.title AS kitap_adi, transactions.issue_date AS odunc_alma_tarihi, transactions.return_date AS iade_tarihi
                   FROM transactions
                   JOIN books ON transactions.book_id = books.id
                   WHERE transactions.member_id = ?'''
        user_books = pd.read_sql(query, conn, params=(member_id,))
        if not user_books.empty:
            st.dataframe(user_books)
        else:
            st.warning("Bu üyenin herhangi bir ödünç alınmış kitabı bulunmamaktadır.")
elif menu == "Gelişmiş Raporlar":
    st.subheader("📑 Gelişmiş Raporlar")

    # En çok okunan kitap
    most_read_book = c.execute(
        "SELECT books.title, COUNT(transactions.book_id) AS count FROM transactions JOIN books ON transactions.book_id = books.id GROUP BY transactions.book_id ORDER BY count DESC LIMIT 1").fetchone()
    if most_read_book:
        st.write(f"📖 **En Çok Okunan Kitap:** {most_read_book[0]} ({most_read_book[1]} kez okunmuş)")
    else:
        st.write("📖 En çok okunan kitap bilgisi bulunamadı.")

    # Kütüphanede en çok bulunan kitap türü
    most_common_genre = c.execute(
        "SELECT genre, COUNT(*) as count FROM books GROUP BY genre ORDER BY count DESC LIMIT 1").fetchone()
    if most_common_genre:
        st.write(f"📚 **En Çok Bulunan Kitap Türü:** {most_common_genre[0]} ({most_common_genre[1]} adet)")
    else:
        st.write("📚 En çok bulunan kitap türü bilgisi bulunamadı.")

    # En çok kitap okuyan üye bilgisi
    most_active_member = c.execute(
        "SELECT members.name, members.email, COUNT(transactions.member_id) AS count FROM transactions JOIN members ON transactions.member_id = members.id GROUP BY transactions.member_id ORDER BY count DESC LIMIT 1").fetchone()
    if most_active_member:
        st.write(
            f"👤 **En Çok Kitap Okuyan Üye:** {most_active_member[0]} - {most_active_member[1]} ({most_active_member[2]} kitap okumuş)")
    else:
        st.write("👤 En çok kitap okuyan üye bilgisi bulunamadı.")

