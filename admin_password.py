import bcrypt
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["library"]
admin_collection = db["admins"]

# Clear existing admins if needed (optional)
# admin_collection.delete_many({})

# Admin user data
admins = [
    {"username": "admin1", "password": "Admin@678"},
    {"username": "admin2", "password": "Admin#123*"}
]

# Insert encrypted passwords
for admin in admins:
    hashed_pw = bcrypt.hashpw(admin["password"].encode('utf-8'), bcrypt.gensalt())
    admin_collection.insert_one({"username": admin["username"], "password": hashed_pw})

print("Admin users added successfully with encrypted passwords.")
