-- Setup MySQL user for .NET backend
-- Run this script as root user

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS fro_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create user for localhost connections (for .NET backend running outside Docker)
CREATE USER IF NOT EXISTS 'fro_user'@'localhost' IDENTIFIED BY 'fro_password';
CREATE USER IF NOT EXISTS 'fro_user'@'127.0.0.1' IDENTIFIED BY 'fro_password';
CREATE USER IF NOT EXISTS 'fro_user'@'%' IDENTIFIED BY 'fro_password';

-- Grant all privileges on fro_db to fro_user
GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'localhost';
GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'127.0.0.1';
GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Show created users
SELECT User, Host FROM mysql.user WHERE User = 'fro_user';
