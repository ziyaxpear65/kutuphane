import datetime

class User:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role  # 'student' or 'teacher'
        self.borrowed_books = []

    def borrow_book(self, book, library):
        if book in library.books and book.available:
            book.available = False
            self.borrowed_books.append(book)
            library.log_transaction(self, book, "borrowed")
        else:
            print(f"{book.title} is not available.")

    def return_book(self, book, library):
        if book in self.borrowed_books:
            book.available = True
            self.borrowed_books.remove(book)
            library.log_transaction(self, book, "returned")
        else:
            print("You don't have this book.")

class Book:
    def __init__(self, book_id, title, author, category):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.category = category
        self.available = True

class Library:
    def __init__(self):
        self.books = []
        self.users = []
        self.transactions = []

    def add_book(self, book):
        self.books.append(book)

    def remove_book(self, book):
        if book in self.books:
            self.books.remove(book)

    def add_user(self, user):
        self.users.append(user)

    def log_transaction(self, user, book, action):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {user.name} ({user.role}) {action} '{book.title}'"
        self.transactions.append(log_entry)

    def search_books(self, query):
        return [book for book in self.books if query.lower() in book.title.lower() or query.lower() in book.author.lower()]

    def list_books(self):
        for book in self.books:
            status = "Available" if book.available else "Checked Out"
            print(f"{book.title} by {book.author} [{status}]")

# Example Usage
library = Library()
user1 = User(1, "Ali", "student")
book1 = Book(101, "Python Programming", "Guido van Rossum", "Programming")

library.add_user(user1)
library.add_book(book1)

user1.borrow_book(book1, library)
user1.return_book(book1, library)

library.list_books()
print("\nTransaction Logs:")
for log in library.transactions:
    print(log)
