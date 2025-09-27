-- Initial database setup for Forglass Regenerator Optimizer
-- This script runs only on first MySQL container startup

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS fro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE fro_db;

-- Grant permissions to user
GRANT ALL PRIVILEGES ON fro_db.* TO 'fro_user'@'%';
FLUSH PRIVILEGES;

-- Create initial indexes for performance
-- Additional indexes will be created via Alembic migrations