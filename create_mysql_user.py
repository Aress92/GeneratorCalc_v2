#!/usr/bin/env python3
"""Script to create MySQL user for .NET backend"""

import mysql.connector
from mysql.connector import Error

def create_user():
    """Create fro_user for localhost connections"""
    try:
        # Connect as root
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root_password'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            print("Connected to MySQL server")

            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS fro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print("✓ Database fro_db created/verified")

            # Create user for localhost if not exists
            cursor.execute("CREATE USER IF NOT EXISTS 'fro_user'@'localhost' IDENTIFIED BY 'fro_password';")
            print("✓ User fro_user@localhost created")

            # Grant privileges
            cursor.execute("GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'localhost';")
            print("✓ Privileges granted to fro_user@localhost")

            # Flush privileges
            cursor.execute("FLUSH PRIVILEGES;")
            print("✓ Privileges flushed")

            # Test connection with new user
            test_connection = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='fro_user',
                password='fro_password',
                database='fro_db'
            )

            if test_connection.is_connected():
                print("\n✅ SUCCESS! User fro_user@localhost can connect to fro_db")
                test_connection.close()

            cursor.close()
            connection.close()
            print("\n.NET backend should now be able to connect to MySQL!")

    except Error as e:
        print(f"❌ Error: {e}")
        print("\nPossible solutions:")
        print("1. Make sure MySQL is running on localhost:3306")
        print("2. Check root password (currently: 'root_password')")
        print("3. If MySQL is in Docker, you may need to access it differently")

if __name__ == "__main__":
    create_user()
