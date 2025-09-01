import csv,os,uuid,dot_env
from _datetime import datetime
from werkzeug.security import generate_password_hash

def init_csv_files():
    # Users CSV
    if not os.path.exists(dot_env.DB_STORAGE_USER):
        with open(dot_env.DB_STORAGE_USER, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['user_id', 'username', 'email', 'password_hash', 'created_at'])
        print("Created users.csv")

    # Predictions CSV
    if not os.path.exists(dot_env.DB_STORAGE_PREDICTION):
        with open(dot_env.DB_STORAGE_PREDICTION, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['prediction_id', 'user_id', 'username', 'symptoms', 'predicted_diseases', 'top_n', 'timestamp'])
        print("Created predictions.csv")


# User management functions
def get_user_by_username(username):
    try:
        with open(dot_env.DB_STORAGE_USER, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'].strip() == username.strip():
                    return row
    except FileNotFoundError:
        print("users.csv not found")
        return None
    except Exception as e:
        print(f"Error reading users.csv: {e}")
        return None
    return None


def create_user(username, email, password):
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)
    timestamp = datetime.now().strftime("%d/%m/%Y at %I:%M:%S %p")

    try:
        with open(dot_env.DB_STORAGE_USER, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([user_id, username.strip(), email.strip(), password_hash, timestamp])
        print(f"User created: {username} with ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def email_exists(email):
    try:
        with open(dot_env.DB_STORAGE_USER, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['email'].strip().lower() == email.strip().lower():
                    return True
    except FileNotFoundError:
        return False
    return False

