import psycopg2
from config import logger


# Database connection parameters
DB_PARAMS = {
    'dbname': 'moniDB',
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


def load_domains_DB(username):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('''
                    SELECT s.url, s.status_code, s.ssl_status, s.expiration_date, s.issuer
                    FROM scans s 
                    JOIN users u ON s.user_id = u.user_id
                    WHERE u.username = %s''', (username,))
        results = cur.fetchall()
        domains = []
        if results:
            for result in results:
                  domains.append({
                    'url': result[0],
                    'status_code': result[1],
                    'ssl_status': result[2],
                    'expiration_date': result[3],
                    'issuer': result[4]
                })
            return domains
        else:
            return []
    except Exception as e:
        logger.error(f"Error loading domains: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_domains_DB(domains, username):
    try:
        conn = connect_db()
        cur = conn.cursor()
        for domain in domains:
            cur.execute('''
                        INSERT INTO scans (url, status_code, ssl_status, expiration_date, issuer, user_id)
                        VALUES (%s, %s, %s, %s, %s,(SELECT user_id FROM users WHERE username = %s))
                        ON CONFLICT (user_id, url) DO UPDATE
                        SET status_code = EXCLUDED.status_code,
                            ssl_status = EXCLUDED.ssl_status,
                            expiration_date = EXCLUDED.expiration_date,
                            issuer = EXCLUDED.issuer
                        ''', (domain['url'], domain['status_code'], domain['ssl_status'], domain['expiration_date'], domain['issuer'],username))
        
        conn.commit()
        return True
    except Exception as e:  
        logger.error(f"Error updating domains: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()    

def remove_domain_DB(domain_to_remove, username):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('''
                    DELETE FROM scans
                    WHERE url = %s AND user_id = (SELECT user_id FROM users WHERE username = %s)
                    ''', (domain_to_remove, username))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error removing domain: {e}")
        return False
    finally:    
        if cur:
            cur.close()
        if conn:
            conn.close()