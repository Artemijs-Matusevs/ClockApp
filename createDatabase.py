import sqlite3

con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS
            documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_name TEXT NOT NULL,
                department_name TEXT NOT NULL)
            """)

#Create user table
cur.execute("""
CREATE TABLE IF NOT EXISTS
            users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                hashed_badge TEXT UNIQUE,
                department TEXT)
            """)


#Create check-in table
cur.execute("""
CREATE TABLE IF NOT EXISTS
            checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                intime DATETIME,
                outtime DATETIME,
                documents_accessed TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id))
            """)

#Commit changes
con.commit()
con.close()
