import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import mysql.connector

# MySQL connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="LibraryDB"
    )

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("900x650")
        
        # Set theme
        style = ttk.Style(theme="cosmo")

        # Header Label
        ttk.Label(self.root, text="Library Management System", bootstyle="primary", font=("Helvetica", 24)).pack(pady=20)

        # Button Frame
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        ttk.Button(self.button_frame, text="Add Book", bootstyle="success", command=self.add_book_window).grid(row=0, column=0, padx=10)
        ttk.Button(self.button_frame, text="Borrow Book", bootstyle="info", command=self.borrow_book_window).grid(row=0, column=1, padx=10)
        ttk.Button(self.button_frame, text="Return Book", bootstyle="dark", command=self.return_book_window).grid(row=0, column=2, padx=10)
        ttk.Button(self.button_frame, text="Show Available Books", bootstyle="warning", command=self.show_available_books).grid(row=0, column=3, padx=10)
        ttk.Button(self.button_frame, text="Show History", bootstyle="secondary", command=self.show_borrow_history).grid(row=0, column=4, padx=10)

        # Book Table
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        self.book_table = ttk.Treeview(
            self.table_frame,
            columns=("ISBN", "Title", "Available"),
            show="headings",
            bootstyle="info",
            height=15
        )
        self.book_table.heading("ISBN", text="ISBN")
        self.book_table.heading("Title", text="Title")
        self.book_table.heading("Available", text="Available")
        self.book_table.column("ISBN", width=150)
        self.book_table.column("Title", width=400)
        self.book_table.column("Available", width=100)
        self.book_table.pack(fill=BOTH, expand=True)

        self.show_available_books()

    # Add Book Window
    def add_book_window(self):
        def add_book():
            isbn = isbn_entry.get().strip()
            title = title_entry.get().strip()

            if not isbn or not title:
                messagebox.showerror("Error", "ISBN and Title are required")
                return

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO books (isbn, title, available) VALUES (%s, %s, TRUE)", (isbn, title))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Book added successfully")
                add_window.destroy()
                self.show_available_books()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

        add_window = ttk.Toplevel(self.root)
        add_window.title("Add Book")
        add_window.geometry("400x250")

        ttk.Label(add_window, text="Add Book Details", bootstyle="primary", font=("Helvetica", 16)).pack(pady=10)

        form_frame = ttk.Frame(add_window)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="ISBN:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        isbn_entry = ttk.Entry(form_frame, width=30)
        isbn_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="Title:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        title_entry = ttk.Entry(form_frame, width=30)
        title_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(add_window, text="Add Book", bootstyle="success", command=add_book).pack(pady=10)

    # Borrow Book Window
    def borrow_book_window(self):
        def borrow_book():
            student_id = student_id_entry.get().strip()
            isbn = isbn_entry.get().strip()

            if not student_id or not isbn:
                messagebox.showerror("Error", "Student ID and ISBN are required")
                return

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, available FROM books WHERE isbn = %s", (isbn,))
                book = cursor.fetchone()
                if not book:
                    messagebox.showerror("Error", "Book not found")
                elif not book[1]:
                    messagebox.showerror("Error", "Book is already borrowed")
                else:
                    cursor.execute("INSERT INTO borrows (student_id, book_id, borrow_date) VALUES (%s, %s, NOW())", (student_id, book[0]))
                    cursor.execute("UPDATE books SET available = FALSE WHERE id = %s", (book[0],))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Book borrowed successfully")
                    borrow_window.destroy()
                    self.show_available_books()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

        borrow_window = ttk.Toplevel(self.root)
        borrow_window.title("Borrow Book")
        borrow_window.geometry("400x250")

        ttk.Label(borrow_window, text="Borrow Book", bootstyle="primary", font=("Helvetica", 16)).pack(pady=10)

        form_frame = ttk.Frame(borrow_window)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        student_id_entry = ttk.Entry(form_frame, width=30)
        student_id_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="ISBN:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        isbn_entry = ttk.Entry(form_frame, width=30)
        isbn_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(borrow_window, text="Borrow Book", bootstyle="info", command=borrow_book).pack(pady=10)

    # Return Book Window
    def return_book_window(self):
        def return_book():
            student_id = student_id_entry.get().strip()
            isbn = isbn_entry.get().strip()

            if not student_id or not isbn:
                messagebox.showerror("Error", "Student ID and ISBN are required")
                return

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT b.id FROM books b JOIN borrows br ON b.id = br.book_id WHERE b.isbn = %s AND br.student_id = %s AND br.return_date IS NULL",
                    (isbn, student_id),
                )
                borrow_record = cursor.fetchone()
                if not borrow_record:
                    messagebox.showerror("Error", "No such borrowed book found")
                else:
                    cursor.execute("UPDATE borrows SET return_date = NOW() WHERE book_id = %s AND student_id = %s AND return_date IS NULL", 
                                   (borrow_record[0], student_id))
                    cursor.execute("UPDATE books SET available = TRUE WHERE id = %s", (borrow_record[0],))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Book returned successfully")
                    return_window.destroy()
                    self.show_available_books()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

        return_window = ttk.Toplevel(self.root)
        return_window.title("Return Book")
        return_window.geometry("400x250")

        ttk.Label(return_window, text="Return Book", bootstyle="primary", font=("Helvetica", 16)).pack(pady=10)

        form_frame = ttk.Frame(return_window)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        student_id_entry = ttk.Entry(form_frame, width=30)
        student_id_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="ISBN:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        isbn_entry = ttk.Entry(form_frame, width=30)
        isbn_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(return_window, text="Return Book", bootstyle="dark", command=return_book).pack(pady=10)

    # Show Available Books
    def show_available_books(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT isbn, title, available FROM books")
            rows = cursor.fetchall()
            conn.close()

            self.book_table.delete(*self.book_table.get_children())
            for row in rows:
                self.book_table.insert("", END, values=(row[0], row[1], "Yes" if row[2] else "No"))
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

    # Show Borrow History
    def show_borrow_history(self):
        def fetch_history():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT br.id, br.student_id, b.title, br.borrow_date, br.return_date
                    FROM borrows br
                    JOIN books b ON br.book_id = b.id
                """)
                rows = cursor.fetchall()
                conn.close()

                history_table.delete(*history_table.get_children())
                for row in rows:
                    history_table.insert("", END, values=(row[0], row[1], row[2], row[3], row[4] or "Not Returned"))
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

        history_window = ttk.Toplevel(self.root)
        history_window.title("Borrow History")
        history_window.geometry("800x400")

        ttk.Label(history_window, text="Borrow History", bootstyle="secondary", font=("Helvetica", 16)).pack(pady=10)

        history_table_frame = ttk.Frame(history_window)
        history_table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        history_table = ttk.Treeview(
            history_table_frame,
            columns=("ID", "Student ID", "Book Title", "Borrow Date", "Return Date"),
            show="headings",
            bootstyle="secondary"
        )
        history_table.heading("ID", text="ID")
        history_table.heading("Student ID", text="Student ID")
        history_table.heading("Book Title", text="Book Title")
        history_table.heading("Borrow Date", text="Borrow Date")
        history_table.heading("Return Date", text="Return Date")

        history_table.column("ID", width=50)
        history_table.column("Student ID", width=100)
        history_table.column("Book Title", width=300)
        history_table.column("Borrow Date", width=150)
        history_table.column("Return Date", width=150)

        history_table.pack(fill=BOTH, expand=True)

        fetch_history()

# Run Application
if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = LibraryApp(root)
    root.mainloop()
