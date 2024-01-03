def insert_user(cursor, conn, email, password):
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
    conn.commit()
    
def check_user(cursor, email, password):
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    result = cursor.fetchone()

    if result:
        return True
    else:
        return False