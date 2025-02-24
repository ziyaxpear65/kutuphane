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


# Üye silme fonksiyonu
def delete_member(member_id):
    c.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()


# Üye güncelleme fonksiyonu
def update_member(member_id, name, email, phone):
    c.execute("UPDATE members SET name = ?, email = ?, phone = ? WHERE id = ?", (name, email, phone, member_id))
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


# Streamlit arayüzü
st.title("📚 Kütüphane Yönetim Sistemi")
menu = st.sidebar.selectbox("Menü", ["Kitaplar", "Üyeler", "İşlemler", "İstatistikler", "Kitap Ara", "Arama",
                                     "Gelişmiş Raporlar"])

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
        books = pd.read_sql("SELECT * FROM books", conn)
        book_to_delete = st.selectbox("Silmek İstediğiniz Kitabı Seçin", books['title'])
        confirm = st.checkbox("Bu kitabı silmek istediğinize emin misiniz?")
        if st.button("Sil"):
            if confirm:
                book_id = books[books['title'] == book_to_delete]['id'].values[0]
                delete_book(book_id)
                st.success(f"{book_to_delete} adlı kitap silindi!")
                # Kitaplar listesini güncelle
                books = pd.read_sql("SELECT * FROM books", conn)
                st.dataframe(books)
            else:
                st.warning("Silme işlemi iptal edildi.")

    else:
        books = pd.read_sql("SELECT * FROM books", conn)
        st.dataframe(books)

elif menu == "Üyeler":
    st.subheader("👤 Üye Yönetimi")

    # Üye ekleme
    st.write("Yeni Üye Ekle")
    name = st.text_input("Üye Adı")
    email = st.text_input("E-posta")
    phone = st.text_input("Telefon")
    if st.button("Üye Ekle"):
        add_member(name, email, phone)
        st.success("Üye eklendi!")

    # Üye silme ve güncelleme
    st.write("Mevcut Üyeleri Yönet")
    members = pd.read_sql("SELECT * FROM members", conn)
    member_to_update = st.selectbox("Güncellemek veya Silmek İstediğiniz Üyeyi Seçin", members['name'])

    if member_to_update:
        member_id = members[members['name'] == member_to_update]['id'].values[0]
        selected_member = members[members['id'] == member_id].iloc[0]

        # Üye bilgilerini güncelleme
        new_name = st.text_input("Yeni Üye Adı", value=selected_member['name'])
        new_email = st.text_input("Yeni E-posta", value=selected_member['email'])
        new_phone = st.text_input("Yeni Telefon", value=selected_member['phone'])

        if st.button("Güncelle"):
            update_member(member_id, new_name, new_email, new_phone)
            st.success("Üye bilgileri güncellendi!")

        # Üye silme
        confirm_delete = st.checkbox("Bu üyeyi silmek istediğinize emin misiniz?")
        if st.button("Sil"):
            if confirm_delete:
                delete_member(member_id)
                st.success(f"{member_to_update} adlı üye silindi!")
                # Üyeler listesini güncelle
                members = pd.read_sql("SELECT * FROM members", conn)
                st.dataframe(members)
            else:
                st.warning("Silme işlemi iptal edildi.")

    # Üyeleri görüntüleme
    st.write("Üye Listesi")
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

