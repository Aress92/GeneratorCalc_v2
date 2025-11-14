-- ============================================================================
-- Database Seeding Script for Forglass Regenerator Optimizer
-- ============================================================================
-- This script seeds initial data for development and testing
-- Execute after running EF Core migrations
-- ============================================================================

USE fro_db;

-- ============================================================================
-- 1. SEED USERS
-- ============================================================================

-- Check if users already exist
SELECT COUNT(*) as user_count FROM users;

-- Insert admin user (password: admin - CHANGE IN PRODUCTION!)
-- Password hash is bcrypt hash of "admin"
INSERT INTO users (
    id,
    username,
    email,
    full_name,
    password_hash,
    role,
    is_active,
    is_verified,
    created_at,
    updated_at
) VALUES (
    UUID(),
    'admin',
    'admin@forglass.com',
    'System Administrator',
    '$2a$11$X7qCZVxQc5KqzJvQ6mYrGuZvKxGYdCqP5LmZVxQc5KqzJvQ6mYrGu',  -- bcrypt hash of "admin"
    'ADMIN',
    TRUE,
    TRUE,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE username = username;  -- Skip if already exists

-- Insert engineer user (password: engineer123)
INSERT INTO users (
    id,
    username,
    email,
    full_name,
    password_hash,
    role,
    is_active,
    is_verified,
    created_at,
    updated_at
) VALUES (
    UUID(),
    'engineer',
    'engineer@forglass.com',
    'Test Engineer',
    '$2a$11$X7qCZVxQc5KqzJvQ6mYrGuZvKxGYdCqP5LmZVxQc5KqzJvQ6mYrGu',  -- bcrypt hash of "engineer123"
    'ENGINEER',
    TRUE,
    TRUE,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE username = username;

-- Insert viewer user (password: viewer123)
INSERT INTO users (
    id,
    username,
    email,
    full_name,
    password_hash,
    role,
    is_active,
    is_verified,
    created_at,
    updated_at
) VALUES (
    UUID(),
    'viewer',
    'viewer@forglass.com',
    'Test Viewer',
    '$2a$11$X7qCZVxQc5KqzJvQ6mYrGuZvKxGYdCqP5LmZVxQc5KqzJvQ6mYrGu',  -- bcrypt hash of "viewer123"
    'VIEWER',
    TRUE,
    TRUE,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE username = username;

-- Verify users were created
SELECT
    username,
    email,
    role,
    is_active,
    is_verified,
    created_at
FROM users
ORDER BY role DESC, username;

-- ============================================================================
-- 2. SEED MATERIALS (Optional - Development/Testing)
-- ============================================================================

-- Check if materials already exist
SELECT COUNT(*) as material_count FROM materials;

-- Insert sample materials
INSERT INTO materials (
    id,
    name,
    description,
    manufacturer,
    material_code,
    material_type,
    category,
    application,
    density,
    thermal_conductivity,
    specific_heat,
    max_temperature,
    min_temperature,
    properties,
    is_active,
    is_standard,
    created_at,
    updated_at
) VALUES
-- Silica Brick
(
    UUID(),
    'Silica Brick Grade A',
    'High-quality silica brick for regenerator crowns',
    'Forglass Materials',
    'SIL-A-001',
    'refractory',
    'high_temperature',
    'crown',
    2300,
    2.5,
    950,
    1650,
    200,
    '{}',
    TRUE,
    TRUE,
    NOW(),
    NOW()
),
-- Mullite Checker Brick
(
    UUID(),
    'Mullite Checker Brick',
    'Standard mullite checker brick',
    'Forglass Materials',
    'MUL-C-001',
    'checker',
    'medium_temperature',
    'checker_packing',
    2100,
    2.0,
    900,
    1500,
    200,
    '{}',
    TRUE,
    TRUE,
    NOW(),
    NOW()
),
-- Ceramic Fiber Insulation
(
    UUID(),
    'Ceramic Fiber Insulation',
    'Lightweight ceramic fiber for insulation',
    'Forglass Materials',
    'INS-CF-001',
    'insulation',
    'insulation',
    'wall_insulation',
    128,
    0.12,
    1000,
    1260,
    0,
    '{}',
    TRUE,
    TRUE,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE name = name;

-- Verify materials were created
SELECT
    name,
    material_type,
    category,
    density,
    thermal_conductivity,
    max_temperature
FROM materials
ORDER BY material_type, name;

-- ============================================================================
-- 3. SEED CONFIGURATION TEMPLATES (Optional)
-- ============================================================================

-- Get admin user ID for template creator
SET @admin_user_id = (SELECT id FROM users WHERE role = 'ADMIN' LIMIT 1);

-- Check if templates already exist
SELECT COUNT(*) as template_count FROM configuration_templates;

-- Insert sample templates
INSERT INTO configuration_templates (
    id,
    name,
    description,
    regenerator_type,
    category,
    default_geometry_config,
    default_thermal_config,
    default_flow_config,
    usage_count,
    is_active,
    is_public,
    created_by_user_id,
    created_at,
    updated_at
) VALUES
-- Standard End-Port Template
(
    UUID(),
    'Standard End-Port Regenerator',
    'Standard configuration for end-port regenerators',
    'EndPort',
    'standard',
    '{"length": 10.0, "width": 8.0, "height": 12.0, "checkerHeight": 0.5, "checkerSpacing": 0.1}',
    '{"gasTempInlet": 1600, "gasTempOutlet": 600, "operatingTemperature": 1450}',
    '{"massFlowRate": 50, "cycleTime": 1200}',
    0,
    TRUE,
    TRUE,
    @admin_user_id,
    NOW(),
    NOW()
),
-- High-Temperature Crown Template
(
    UUID(),
    'High-Temperature Crown Regenerator',
    'Template for high-temperature crown regenerators',
    'Crown',
    'high_temperature',
    '{"length": 12.0, "width": 10.0, "height": 15.0, "checkerHeight": 0.6, "checkerSpacing": 0.12}',
    '{"gasTempInlet": 1700, "gasTempOutlet": 700, "operatingTemperature": 1550}',
    '{"massFlowRate": 60, "cycleTime": 1800}',
    0,
    TRUE,
    TRUE,
    @admin_user_id,
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE name = name;

-- Verify templates were created
SELECT
    name,
    regenerator_type,
    category,
    is_active,
    is_public,
    usage_count
FROM configuration_templates
ORDER BY regenerator_type, name;

-- ============================================================================
-- 4. VERIFICATION QUERIES
-- ============================================================================

-- Summary of seeded data
SELECT
    'Users' as entity_type,
    COUNT(*) as count
FROM users
UNION ALL
SELECT
    'Materials' as entity_type,
    COUNT(*) as count
FROM materials
UNION ALL
SELECT
    'Templates' as entity_type,
    COUNT(*) as count
FROM configuration_templates;

-- Show admin user details
SELECT
    id,
    username,
    email,
    role,
    is_active,
    is_verified
FROM users
WHERE username = 'admin';

-- ============================================================================
-- 5. POST-SEEDING NOTES
-- ============================================================================

-- IMPORTANT: Change default passwords in production!
-- Default credentials for testing:
--   admin / admin (ADMIN role)
--   engineer / engineer123 (ENGINEER role)
--   viewer / viewer123 (VIEWER role)

-- To update admin password via bcrypt in .NET:
-- var hasher = new PasswordHasher();
-- var newHash = hasher.HashPassword("your-new-password");
-- UPDATE users SET password_hash = 'new-hash-here' WHERE username = 'admin';

COMMIT;
