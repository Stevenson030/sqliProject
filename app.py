import re
import os
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_session import Session
from cs50 import SQL
from werkzeug.utils import secure_filename
from helper import error, success
from werkzeug.security import check_password_hash, generate_password_hash

#configure application
app = Flask(__name__)

#session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///elibrary.db")

#Upload Folder path
UPLOAD_FOLDER = 'static/upload'
#allow extensions
ALLOWED_EXTENSIONS = {'png','pdf', 'jpg', 'jpeg', 'gif', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect("/login")
    #show books from the database
    data = db.execute("SELECT * FROM books")
    #to get the number of books
    count = db.execute("SELECT COUNT(*) FROM books")
    count_num = count[0]["COUNT(*)"]
    #return the book number and books
    return render_template("index.html", data=data, count=count_num)

@app.route("/register", methods=["POST","GET"])
def register():

    if request.method == "POST":
        #get user information
        username = request.form.get("username")
        email = request.form.get("email")
        fullname = request.form.get("fullname")
        address = request.form.get("address")
        birth = request.form.get("birth")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        #check user input
        # if not username:
        #     return error("Username is required!")
        # elif not email:
        #     return error("Email is required!")
        # elif not password:
        #     return error("Password is required!")
        # elif not confirm_password:
        #     return error("Confirm Password is required!")

        #check the passwords are match or not
        if password != confirm_password:
            return error("Password do not match!")

        #change password to hash
        hash = generate_password_hash(password)

        #insert into database
        create = db.execute("INSERT INTO users (username, email, password, fullname, address, birth) VALUES (?, ?, ?, ?, ?, ?)",username, email, hash, fullname, address, birth)
        if create:
            return success("Account created successfully!")
        else:
            return error("Account has already been registered!")
    else:
        return render_template("register.html")

@app.route("/login", methods=["POST","GET"])
def login():

    #clear session
    session.clear()

    if request.method == "POST":
        #get user input
        username = request.form.get("username")
        password = request.form.get("password")

        #check user name
       
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        #check password
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return error("Username or Password is wrong!")

        #remember which user has logged in
        session["user_id"] = rows[0]["id"]
        #redirect into homepage
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/account")
def account():
    #check user login or not
    if not session.get("user_id"):
        return redirect("/login")
    
    #get user id
    user = session.get("user_id")
    #get user data from database
    user_info = db.execute("SELECT * FROM users WHERE id = ?", user)
    return render_template("account.html", userInfo = user_info)

@app.route("/change-password", methods=["POST","GET"])
def changePassword():
    if not session.get("user_id"):
        return redirect("/login")
    user_id = session.get("user_id")
    user_info = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    if request.method == "POST":
        #to get the current password
        current_password = request.form.get("current-password")
        #to get new password
        new_password = request.form.get("new-password")
        confirm_password = request.form.get("confirm-password")

        rows = db.execute("SELECT password FROM users WHERE id = ? ", user_id)
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], current_password):
            return error("Current password is wrong!")

        #check new password
        if new_password != confirm_password:
            return error("Password do not match!")
        else:
            hash = generate_password_hash(confirm_password)
            change_password = db.execute("UPDATE users SET password = ? WHERE id = ?", hash, user_id)
            if change_password:
                return success("Password changed successfully!")
            else:
                return error("Failed!")
    return render_template("account.html", userInfo = user_info)
    
@app.route("/change-userinfo", methods=["POST","GET"])
def changeUserInfo():
    #check user session
    if not session.get("user_id"):
        return redirect("/login")
    #get user id
    user_id = session.get("user_id")
    #get user data
    user_info = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    if request.method == "POST":
        #get user data form 
        username = request.form.get("username")
        email = request.form.get("email")
        fullname = request.form.get("fullname")
        birth = request.form.get("birth")
        address = request.form.get("address")
        #update the data
        row = db.execute("UPDATE users SET username =  ?, email = ?, fullname = ?, birth = ?, address = ? WHERE id = ?", username, email, fullname, birth, address, user_id)
        #check update is success or not
        if row:
            return success("Update Successfully!")
        else:
            return error("Failed! Please Try Again!")
    #return the account template with user data
    return render_template("account.html", userInfo = user_info)

@app.route("/admin-login", methods=["POST","GET"])
def admin():
    #clear session
    session.clear()

    if request.method == "POST":
        #get username and password
        username = request.form.get("username")
        password = request.form.get("password")
        #SELECT data from table
        rows = db.execute("SELECT * FROM admin WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return error("Username or Password is wrong!")

        session["admin_id"] = rows[0]["id"]
        
        #redirect into dashboard
        return redirect("/dashboard")

    else:
        return render_template("admin.html")

@app.route("/profile")
def profile():
    if not session.get("admin_id"):
        return redirect("/admin-login")
    admin_id = session.get("admin_id")
    #show books from the database
    data = db.execute("SELECT * FROM books")
    #to get the number of books
    count = db.execute("SELECT COUNT(*) FROM books")
    count_num = count[0]["COUNT(*)"]

    #get information
    info = db.execute("SELECT * FROM admin WHERE id = ?", admin_id)
    
    return render_template("profile.html", books=data, count=count_num, info = info)

@app.route("/dashboard")
def dashboard():
    if not session.get("admin_id"):
        return redirect("/admin-login")
    data = db.execute("SELECT * FROM books")
    count = db.execute("SELECT COUNT(*) FROM books")
    count_num = count[0]["COUNT(*)"]
    return render_template("dashboard.html", books=data, count=count_num)

@app.route("/admin-logout")
def admin_logout():
    #forget session
    session.clear()

    #redirect to home page
    return redirect("/")

def allowed_file(file_name):
    return '.' in file_name and \
        file_name.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods = ["POST","GET"])
def upload():
    if not session.get("admin_id"):
        return redirect("/admin-login")

    if request.method == "POST":
        book_name = request.form.get("book_name")
        description = request.form.get("description")
        author = request.form.get("author")
        category = request.form.get("categories")
        link = request.form.get("link")

        if "book_image" not in request.files:
            flash("No File Part")
            return redirect(request.url)
        book_image = request.files["book_image"] 

        if book_image.filename == "":
            flash("No selected file")
            return redirect(request.url)
        
        if book_image and allowed_file(book_image.filename):
            book_image_name = secure_filename(book_image.filename)
            book_image.save(os.path.join(app.config["UPLOAD_FOLDER"], book_image_name))
        else:
            return error("Allowed image type are - png, jpg, jpeg, gif, pdf, svg")
        
        add_book = db.execute("INSERT INTO books (book_name, description, categories, author, link, image) VALUES (?, ?, ?, ?, ?, ?)", book_name, description, category, author, link, book_image_name)
        if add_book:
            return success("Upload Successfully!")
        else:
            return error("Failed!")
    return render_template("upload.html")

@app.route("/edit/<id>")
def edit(id):
    if not session.get("admin_id"):
        return redirect("/admin-login")
    #print book data with id
    book_data = db.execute("SELECT * FROM books WHERE id = ?", id)
    #return data for edit
    return render_template("edit.html", id=id, book=book_data)

@app.route("/edit-book", methods=["POST","GET"])
def editBook():
    if not session.get("admin_id"):
        return redirect("/admin-login")
    
    if request.method == "POST":
        #get book data
        id = request.form.get("id")
        book_name = request.form.get("book_name")
        description = request.form.get("description")
        author = request.form.get("author")
        category = request.form.get("categories")
        link = request.form.get("link")

        if "book_image" not in request.files:
            flash("No File Part")
            return redirect(request.url)
        book_image = request.files["book_image"] 

        if book_image.filename == "":
            flash("No selected file")
            return redirect(request.url)
        
        if book_image and allowed_file(book_image.filename):
            book_image_name = secure_filename(book_image.filename)
            book_image.save(os.path.join(app.config["UPLOAD_FOLDER"], book_image_name))
        else:
            return error("Allowed image type are - png, jpg, jpeg, gif, pdf, svg")        
        
        add_book = db.execute("UPDATE books SET book_name = ?, description = ?, categories = ?, author = ?, link = ?, image = ? WHERE id = ?", book_name, description, category, author, link, book_image_name, id)
        if add_book:
            return success("Upload Successfully!")
        else:
            return error("Failed!")


    return redirect("/dashboard")

@app.route("/delete/<id>", methods=["POST","GET"])
def delete(id):
    if not session.get("admin_id"):
        return redirect("/admin-login")
    
    delete = db.execute("DELETE FROM books WHERE id = ?", id)
    if delete:
        return success("Deleted!")
    else:
        return error("Failed!")

    return redirect("/dashboard")

@app.route("/change-pw", methods=["POST","GET"])
def changeAdminPassword():
    if not session.get("admin_id"):
        return redirect("/admin-login")
    admin_id = session.get("admin_id")
    if request.method == "POST":
        #to get the current password
        current_password = request.form.get("current_password")
        #to get new password
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        rows = db.execute("SELECT password FROM admin WHERE id = ? ", admin_id)
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], current_password):
            return error("Current password is wrong!")

        #check new password
        if new_password != confirm_password:
            return error("Password do not match!")
        else:
            hash = generate_password_hash(confirm_password)
            change_password = db.execute("UPDATE admin SET password = ? WHERE id = ?", hash, admin_id)
            if change_password:
                return success("Password changed successfully!")
            else:
                return error("Failed!")
    return render_template("profile.html")

@app.route("/details/<id>")
def details(id):
    
    book_id = id
    data = db.execute("SELECT * FROM books WHERE id = ?", book_id)
    return render_template("details.html", book=data)

