# db.py

import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123456',
    database='url_shortener'
)

cursor = db.cursor()

# Create table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INT NOT NULL AUTO_INCREMENT,
    shortening_url VARCHAR(255) NOT NULL,
    full_url VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY (shortening_url)
)
""")