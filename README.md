# 📚 Library Management System

## 📌 Project Overview

This is a **Library Management System** developed using Python and Flask framework.
The system allows both **Admin and Users** to manage books, issue/return books, and maintain records efficiently.

This project is created for **Academic purposes (HCI & Web Development)** and demonstrates real-world application development.

---

## 🎯 Features

### 👩‍💼 Admin Panel

* Admin Login with security (bcrypt + reCAPTCHA)
* Add / Edit / Delete Books
* Manage Users
* View issued books
* Dashboard with statistics

### 👤 User Panel

* User Registration & Login
* View available books
* Search books
* Reserve / Issue books
* Return books
* View issued books & history
* Profile management

---

## 🛠️ Technologies Used

* Python
* Flask (Web Framework)
* MongoDB (Database)
* HTML, CSS
* Bootstrap (UI Design)
* JavaScript
* bcrypt (Password hashing)

---

## 📂 Project Structure

```
Library-Management-System/
│── app.py
│── admin_password.py
│── templates/
│   ├── add_book.html
│   ├── add_user.html
│   ├── admin_dashboard.html
│   ├── admin_login.html
│   ├── edit_book.html
│   ├── edit_profile.html
│   ├── edit_user.html
│   ├── issue_book.html
│   ├── issue_history.html
│   ├── issued_books.html
│   ├── manage_books.html
│   ├── manage_users.html
│   ├── menu.html
│   ├── profile.html
│   ├── user_dashboard.html
│   ├── user_login.html
│   ├── user_register.html
│   ├── view_available_books.html
│   ├── view_books.html
│   ├── view_issued_books.html
│   ├── welcome.html
```

---

## ⚙️ Installation & Setup

### 🔹 1. Clone Repository

```
git clone https://github.com/your-username/Library-Management-System.git
cd Library-Management-System
```

### 🔹 2. Install Dependencies

```
pip install flask pymongo bcrypt requests
```

### 🔹 3. Start MongoDB

Make sure MongoDB is running on:

```
mongodb://localhost:27017/
```

### 🔹 4. Run the Application

```
python app.py
```

### 🔹 5. Open in Browser

```
http://127.0.0.1:5000/
```

---

## 🔐 Security Features

* Password hashing using bcrypt
* Google reCAPTCHA verification
* Session-based authentication

---

## 📸 Screenshots

### 🟢 Admin Dashboard

![Admin Dashboard](image1.png)

### 🔵 User Dashboard

![User Dashboard](image2.png)

---

## 🚀 Future Improvements

* Email notifications 📧
* Fine payment integration 💳
* Book recommendation system 🤖
* Mobile responsive UI improvements

---

## 👩‍💻 Author

**Samra Ramzan**
BSCS Student

---

## ⭐ Conclusion

This project demonstrates a complete **web-based system** integrating:

* Backend (Flask)
* Database (MongoDB)
* Frontend (HTML/CSS/Bootstrap)

It reflects strong understanding of **HCI principles, user interaction, and system design**.

---

✨ *Thank you for using Library Management System!*
