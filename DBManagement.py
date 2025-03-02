import psycopg2
from config import logger


# Database connection parameters
DB_PARAMS = {
    'dbname': 'postgres',
    'user': 'myuser',
    'password': 'mypassword',
    'host': 'localhost',
    'port': 5432
}

# Function to connect to the database
def connect_db():
    return psycopg2.connect(**DB_PARAMS)

def register_DB(newuser):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password, full_name, is_google_user, picture) VALUES (%s, %s, %s, %s, %s)', 
                   (newuser["username"], newuser["password"], newuser["full_name"], 
                    newuser["is_google_user"], newuser["profile_picture"]))
               
        conn.commit()
        # Check rowcount to verify success
        if cur.rowcount > 0:
            logger.info(f"User {newuser['username']} added successfully")
            return True
        else:
            logger.info(f"Error adding user {newuser['username']}")
            return False
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
def login_DB (username, password):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        true_login = cur.fetchone()
        if true_login:
            return True
        else:
            return False
    except Exception as e:
        print("An error occurred:", e)
    finally:    
        cur.close()
        conn.close()    

def check_username_DB (username):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        username_exists = cur.fetchone()
        if username_exists:
            return False
        else:
            return True
    except Exception as e:  
        print("An error occurred:", e)
    finally:
        cur.close()
        conn.close()