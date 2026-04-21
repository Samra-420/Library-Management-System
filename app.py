from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
import bcrypt
import os
import requests
from bson.objectid import ObjectId
from datetime import datetime,timedelta
import math
app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["library"]
admin_collection = db["admins"]
users_collection = db["users"]
books_collection = db["books"]
issued_books_collection = db['issued_books']

# reCAPTCHA keys
RECAPTCHA_SITE_KEY = '6LeICTwrAAAAAJ1_xLjsSbt3gNLQqzo5oqyfwFmR'
RECAPTCHA_SECRET_KEY = '6LeICTwrAAAAAPrk_Y-qthVuBewRoSiwKh4vkAFY'

def verify_recaptcha(response_token):
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    payload = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': response_token
    }
    try:
        response = requests.post(verify_url, data=payload)
        return response.json().get('success', False)
    except:
        return False

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        recaptcha_response = request.form.get('g-recaptcha-response')

        if not username or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('admin_login'))

        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            flash('reCAPTCHA verification failed! Please try again.', 'danger')
            return redirect(url_for('admin_login'))

        user = admin_collection.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            flash('Admin Login Successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Failed. Invalid username or password.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html', site_key=RECAPTCHA_SITE_KEY)

@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not name or not email or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('user_register'))

        if users_collection.find_one({'email': email}):
            flash('Email already registered! Please login.', 'danger')
            return redirect(url_for('user_login'))

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            'name': name,
            'email': email,
            'password': hashed_pw
        })

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('user_login'))

    return render_template('user_register.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        recaptcha_response = request.form.get('g-recaptcha-response')

        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('user_login'))

        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            flash('reCAPTCHA verification failed! Please try again.', 'danger')
            return redirect(url_for('user_login'))

        user = users_collection.find_one({'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = user['name']
            session['user_id'] = str(user['_id'])
            flash('User Login Successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Login Failed. Invalid email or password.', 'danger')
            return redirect(url_for('user_login'))

    return render_template('user_login.html', site_key=RECAPTCHA_SITE_KEY)

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session.get('username', 'User')  # Optional

    issued_books = issued_books_collection.find({'user_id': user_id})

    overdue_books = 0
    returned_books = 0
    total_fine = 0

    for book in issued_books:
        status = book.get('status')
        issue_date = book.get('issue_date')
        return_date = book.get('return_date', None)

        # Calculate due_date = issue_date + 7 days (or whatever your policy is)
        due_date = issue_date + timedelta(days=7)

        if status == 'returned':
            returned_books += 1
        else:
            if datetime.utcnow() > due_date:
                overdue_books += 1
                days_late = (datetime.utcnow() - due_date).days
                total_fine += days_late * 10

    return render_template(
        'user_dashboard.html',
        username=username,
        overdue_books=overdue_books,
        returned_books=returned_books,
        total_fine=total_fine
    )
@app.route('/admin_dashboard')
def admin_dashboard():
    total_books = books_collection.count_documents({})
    total_users = users_collection.count_documents({})
    issued_books = books_collection.count_documents({"status": "issued"})

    return render_template('admin_dashboard.html',
                           total_books=total_books,
                           issued_books=issued_books,
                           total_users=total_users)
@app.route('/manage_books')
def manage_books():
    books = list(books_collection.find())
    return render_template('manage_books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        year = request.form.get('year')
        genre = request.form.get('genre')
        quantity = request.form.get('quantity')

        if not title or not author or not isbn or not year or not quantity:
            flash("All fields are required!", "danger")
            return redirect(url_for('add_book'))

        try:
            books_collection.insert_one({
                'title': title,
                'author': author,
                'isbn': isbn,
                'year': int(year),
                'genre': genre,
                'quantity': int(quantity)
            })
            flash("Book added successfully!", "success")
            return redirect(url_for('manage_books'))
        except Exception as e:
            flash(f"Error adding book: {e}", "danger")
            return redirect(url_for('add_book'))

    return render_template('add_book.html')

@app.route('/edit_book/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = books_collection.find_one({'_id': ObjectId(book_id)})
    if not book:
        flash("Book not found!", "danger")
        return redirect(url_for('manage_books'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        year = request.form.get('year')
        genre = request.form.get('genre')
        quantity = request.form.get('quantity')

        if not title or not author or not isbn or not year or not quantity:
            flash("All fields are required!", "danger")
            return redirect(url_for('edit_book', book_id=book_id))

        try:
            books_collection.update_one(
                {'_id': ObjectId(book_id)},
                {'$set': {
                    'title': title,
                    'author': author,
                    'isbn': isbn,
                    'year': int(year),
                    'genre': genre,
                    'quantity': int(quantity)
                }}
            )
            flash("Book updated successfully!", "success")
            return redirect(url_for('manage_books'))
        except Exception as e:
            flash(f"Error updating book: {e}", "danger")
            return redirect(url_for('edit_book', book_id=book_id))

    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<book_id>', methods=['POST'])
def delete_book(book_id):
    try:
        books_collection.delete_one({'_id': ObjectId(book_id)})
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting book: {e}', 'danger')
    return redirect(url_for('manage_books'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('welcome'))

@app.route('/view_books')
def view_books():
    genres = books_collection.distinct('genre')
    books_by_genre = {}
    for genre in genres:
        books_by_genre[genre] = list(books_collection.find({'genre': genre}))
    return render_template("view_books.html", books_by_genre=books_by_genre)

@app.route('/manage_users')
def manage_users():
    users = list(users_collection.find())
    return render_template('manage_users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not name or not email or not password:
            flash('Please fill all fields.', 'danger')
            return redirect(url_for('add_user'))

        if users_collection.find_one({'email': email}):
            flash('Email already exists!', 'danger')
            return redirect(url_for('add_user'))

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            'name': name,
            'email': email,
            'password': hashed_pw
        })
        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('add_user.html')

@app.route('/edit_user/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('manage_users'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form.get('password')

        if not name or not email:
            flash('Name and email are required.', 'danger')
            return redirect(url_for('edit_user', user_id=user_id))

        existing_user = users_collection.find_one({'email': email, '_id': {'$ne': ObjectId(user_id)}})
        if existing_user:
            flash('Email is already used by another user.', 'danger')
            return redirect(url_for('edit_user', user_id=user_id))

        update_data = {'name': name, 'email': email}
        if password:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            update_data['password'] = hashed_pw

        users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        users_collection.delete_one({'_id': ObjectId(user_id)})
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {e}', 'danger')
    return redirect(url_for('manage_users'))
@app.route('/issued_books')
def issued_books():
    issued_books_list = list(books_collection.find({'status': 'issued'}))
    return render_template('issued_books.html', books=issued_books_list)
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')

        # Validation
        if book_id not in books:
            flash('Book ID does not exist.', 'danger')
            return redirect(url_for('issue_book'))

        if not books[book_id]['available']:
            flash('Sorry, this book is already issued.', 'warning')
            return redirect(url_for('issue_book'))

        # Issue the book
        books[book_id]['available'] = False
        issued_books.append({'user_id': user_id, 'book_id': book_id})
        flash(f"Book '{books[book_id]['title']}' issued successfully to User ID {user_id}.", 'success')
        return redirect(url_for('user_dashboard'))

    # GET request - show form
    return render_template('issue_book.html')
@app.route('/issue_history')
def issue_history():
    if 'user_id' not in session:
        flash('Please log in to view issue history.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    history = list(db.issued_books.find({"user_id": user_id}).sort("issue_date", -1))
    return render_template('issue_history.html', history=history)


@app.route('/view_available_books')
def view_available_books():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    search_query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 6  # books per page

    # Base query: books with quantity > 0
    query = {"quantity": {"$gt": 0}}

    # Add search filter if query exists
    if search_query:
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"author": {"$regex": search_query, "$options": "i"}},
            {"genre": {"$regex": search_query, "$options": "i"}},
        ]

    # Count total matching books for pagination
    total_books = books_collection.count_documents(query)
    total_pages = math.ceil(total_books / per_page)

    # Fetch paginated books
    books = list(
        books_collection.find(query)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    return render_template(
        'view_available_books.html',
        books=books,
        page=page,
        total_pages=total_pages,
        search_query=search_query
    )

@app.route('/reserve_book/<book_id>', methods=['POST'])
def reserve_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    book = books_collection.find_one({"_id": ObjectId(book_id)})

    if book and book['quantity'] > 0:
        # Decrease book quantity by 1
        books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$inc": {"quantity": -1}}
        )

        # Log reservation
        issued_books_collection.insert_one({
            "user_id": session['user_id'],
            "book_id": book['_id'],
            "title": book['title'],
            "author": book['author'],
            "issue_date": datetime.now(),
            "status": "issued"
        })

        flash(f"You reserved \"{book['title']}\" successfully!", "success")
    else:
        flash("Sorry, this book is no longer available.", "danger")

    return redirect(url_for('view_available_books'))
@app.route('/view_issued_books')
def view_issued_books():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    issued_books = list(issued_books_collection.find({
        "user_id": user_id,
        "status": "issued"
    }))
    return render_template('view_issued_books.html', issued_books=issued_books)


@app.route('/return_book/<issued_id>', methods=['POST'])
def return_book(issued_id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    issued_record = issued_books_collection.find_one({"_id": ObjectId(issued_id), "user_id": session['user_id']})
    if not issued_record or issued_record['status'] != "issued":
        flash("Invalid book return request.", "danger")
        return redirect(url_for('view_issued_books'))

    # Increment book quantity
    books_collection.update_one(
        {"_id": issued_record['book_id']},
        {"$inc": {"quantity": 1}}
    )

    # Update issued record status and return date
    issued_books_collection.update_one(
        {"_id": ObjectId(issued_id)},
        {"$set": {"status": "returned", "return_date": datetime.now()}}
    )

    flash(f'Book "{issued_record["title"]}" returned successfully!', "success")
    return redirect(url_for('view_issued_books'))
@app.route('/profile')
def profile():
    # Fetch user profile from database based on logged-in user (e.g., session)
    username = session.get('username')  # or however you track user login
    if not username:
        return redirect(url_for('login'))  # redirect if not logged in

    user = users_collection.find_one({'username': username})  # Adjust collection name if needed
    return render_template('profile.html', profile=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Please log in to edit your profile.', 'warning')
        return redirect(url_for('user_login'))

    user = users_collection.find_one({'_id': ObjectId(session['user_id'])})

    if request.method == 'POST':
        name = request.form['name'].strip()
        password = request.form['password']

        update_data = {"name": name}
        if password:  # agar password diya gaya ho toh update karo
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            update_data['password'] = hashed_pw

        users_collection.update_one({'_id': ObjectId(session['user_id'])}, {'$set': update_data})
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=user)



if __name__ == '__main__':
    app.run(debug=True)
