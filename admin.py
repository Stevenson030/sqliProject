from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

db = SQL("sqlite:///elibrary.db")

username = input("Username : ")
password = input("password : ")
email = input("Email : ")
hash = generate_password_hash(password)
fullname = input("Fullname : ")
address = input("Address : ")
birth = input("Birth : ")

reg = db.execute("INSERT INTO admin (username, email, password, fullname, address, birth) VALUES (?, ?, ?, ?, ?, ?)", username, email, hash, fullname, address, birth)

if reg:
    print("*" * 40)
    print(f"Username : {username}")
    print(f"Password : {password}")
    print(f"Email : {email}")
    print(f"Fullname : {fullname}")
    print(f"Address : {address}")
    print(f"Birth : {birth}")
else:
    print("fail")


