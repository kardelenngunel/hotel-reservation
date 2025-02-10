import mysql.connector
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime
from PIL import Image, ImageTk  

# bağlantı
def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",  
        user="root",  
        database="reservation_system"  
    )

# Fetch hotel names from the database
def get_hotels():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = "SELECT HotelID, HotelName FROM Hotels;"
        cursor.execute(query)
        hotels = cursor.fetchall()
        return hotels  
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

# Fetch available rooms for the selected hotel
def get_available_rooms(hotel_id, check_in_date, check_out_date):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = (
            "SELECT RoomID, RoomType, Price FROM Rooms WHERE HotelID = %s AND IsAvailable = TRUE AND RoomID NOT IN "
            "(SELECT RoomID FROM Reservations WHERE HotelID = %s AND (CheckInDate < %s AND CheckOutDate > %s));"
        )
        cursor.execute(query, (hotel_id, hotel_id, check_out_date, check_in_date))
        rooms = cursor.fetchall()
        return rooms  
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

# Add a reservation
def make_reservation(user_id, hotel_id, room_id, check_in_date, check_out_date, total_amount):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = """INSERT INTO Reservations (UserID, HotelID, RoomID, CheckInDate, CheckOutDate, TotalAmount)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (user_id, hotel_id, room_id, check_in_date, check_out_date, total_amount)
        cursor.execute(query, values)
        conn.commit()

        reservation_id = cursor.lastrowid  

        messagebox.showinfo("Success", "Reservation created successfully!")

        # Redirect to payment page
        payment_page(total_amount, reservation_id)

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    finally:
        cursor.close()
        conn.close()

# Add a user to the database
def add_user(username, password, email, phone):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO Users (Username, Password, Email, Phone) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (username, password, email, phone))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful. You can now log in!")
        login_page()  
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
    finally:
        cursor.close()
        conn.close()

# User authentication
def authenticate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        query = "SELECT UserID FROM Users WHERE Username = %s AND Password = %s;"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        return user[0] if user else None
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"An error occurred: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# Set background image
def set_background(root):
    img = Image.open("images/hotel1.jpg")
    img = img.resize((400, 600), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(img)
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_image

# giriş
def login_page():
    for widget in root.winfo_children():
        widget.destroy()

    username_label = tk.Label(root, text="Username:")
    username_label.pack(pady=5)

    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:")
    password_label.pack(pady=5)

    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()
        global current_user_id
        current_user_id = authenticate_user(username, password)
        if current_user_id:
            messagebox.showinfo("Success", "Login successful!")
            main_page()  
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    login_button = tk.Button(root, text="Login", command=login)
    login_button.pack(pady=10)

    register_button = tk.Button(root, text="Register", command=register_page)
    register_button.pack(pady=10)

# kayıt sayfa
def register_page():
    for widget in root.winfo_children():
        widget.destroy()

    username_label = tk.Label(root, text="Username:")
    username_label.pack(pady=5)

    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:")
    password_label.pack(pady=5)

    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    email_label = tk.Label(root, text="Email:")
    email_label.pack(pady=5)

    email_entry = tk.Entry(root)
    email_entry.pack(pady=5)

    phone_label = tk.Label(root, text="Phone:")
    phone_label.pack(pady=5)

    phone_entry = tk.Entry(root)
    phone_entry.pack(pady=5)

    def register():
        username = username_entry.get()
        password = password_entry.get()
        email = email_entry.get()
        phone = phone_entry.get()
        if not all([username, password, email, phone]):
            messagebox.showerror("Error", "Please fill in all fields.")
        else:
            add_user(username, password, email, phone)

    register_button = tk.Button(root, text="Register", command=register)
    register_button.pack(pady=10)

    back_button = tk.Button(root, text="Back", command=login_page)
    back_button.pack(pady=10)

# ana sayfa
def main_page():
    for widget in root.winfo_children():
        widget.destroy()

    welcome_label = tk.Label(root, text="HOTEL RESERVATION SYSTEM", font=("Arial", 16))
    welcome_label.pack(pady=20)

    reserve_button = tk.Button(root, text="Make a Reservation", command=select_hotel_page)
    reserve_button.pack(pady=20)

# Hotel secim
def select_hotel_page():
    for widget in root.winfo_children():
        widget.destroy()

    hotel_label = tk.Label(root, text="Select a Hotel:")
    hotel_label.pack(pady=5)

    hotels = get_hotels()
    hotel_names = [f"{hotel[0]}: {hotel[1]}" for hotel in hotels]
    hotel_combobox = ttk.Combobox(root, values=hotel_names)
    hotel_combobox.pack(pady=5)

    next_button = tk.Button(root, text="Next", command=lambda: select_dates_page(hotel_combobox.get()))
    next_button.pack(pady=20)

# Date selection page
def select_dates_page(hotel):
    if not hotel:
        messagebox.showerror("Error", "Please select a hotel.")
        return

    hotel_id = hotel.split(":")[0]

    for widget in root.winfo_children():
        widget.destroy()

    def confirm_dates():
        check_in_date = check_in_calendar.get_date()
        check_out_date = check_out_calendar.get_date()

        if check_in_date >= check_out_date:
            messagebox.showerror("Error", "Check-out date cannot be earlier than check-in date.")
        else:
            select_room_page(hotel_id, check_in_date, check_out_date)

    check_in_label = tk.Label(root, text="Check-in Date:")
    check_in_label.pack(pady=5)

    check_in_calendar = Calendar(root, date_pattern="yyyy-mm-dd")
    check_in_calendar.pack(pady=5)

    check_out_label = tk.Label(root, text="Check-out Date:")
    check_out_label.pack(pady=5)

    check_out_calendar = Calendar(root, date_pattern="yyyy-mm-dd")
    check_out_calendar.pack(pady=5)

    next_button = tk.Button(root, text="Next", command=confirm_dates)
    next_button.pack(pady=20)

# Room selection page
def select_room_page(hotel_id, check_in_date, check_out_date):
    for widget in root.winfo_children():
        widget.destroy()

    rooms = get_available_rooms(hotel_id, check_in_date, check_out_date)

    if not rooms:
        messagebox.showerror("Error", "No available rooms for the selected dates.")
        main_page()
        return

    room_label = tk.Label(root, text="Select a Room:")
    room_label.pack(pady=5)

    room_names = [f"{room[0]}: {room[1]} - {room[2]} TL" for room in rooms]
    room_combobox = ttk.Combobox(root, values=room_names)
    room_combobox.pack(pady=5)

    total_amount_label = tk.Label(root, text="Total Amount:")
    total_amount_label.pack(pady=5)

    total_amount_var = tk.StringVar()
    total_amount_entry = tk.Entry(root, textvariable=total_amount_var, state="readonly")
    total_amount_entry.pack(pady=5)

    # Calculating daily price and total amount
    def calculate_total():
        if not room_combobox.get():
            total_amount_var.set("")
            return

        room_details = room_combobox.get().split(" - ")
        daily_price = float(room_details[1].split()[0])  

        # Calculate the number of days between check-in and check-out dates
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        days = (check_out - check_in).days

        total_amount_var.set(f"{daily_price * days:.2f}")  # Calculate

    room_combobox.bind("<<ComboboxSelected>>", lambda e: calculate_total())

    next_button = tk.Button(root, text="Next", command=lambda: make_reservation(current_user_id, hotel_id, room_combobox.get().split(":")[0], check_in_date, check_out_date, total_amount_var.get()))
    next_button.pack(pady=20)

# Payment page
def payment_page(total_amount, reservation_id):
    for widget in root.winfo_children():
        widget.destroy()

    payment_label = tk.Label(root, text="Payment Page", font=("Arial", 16))
    payment_label.pack(pady=20)

    amount_label = tk.Label(root, text=f"Total Payment Amount: {total_amount} TL")
    amount_label.pack(pady=10)

    # Function to start the payment process
    def process_payment():
        messagebox.showinfo("Success", f"Payment successfully processed! Reservation ID: {reservation_id}")
        main_page()  

    pay_button = tk.Button(root, text="Complete Payment", command=process_payment)
    pay_button.pack(pady=20)

    back_button = tk.Button(root, text="Back", command=main_page)
    back_button.pack(pady=10)

# Starting the main window
root = tk.Tk()
root.title("Hotel Reservation System")
root.geometry("400x600")
login_page()
root.mainloop()
