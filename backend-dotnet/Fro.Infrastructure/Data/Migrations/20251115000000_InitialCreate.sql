-- Initial Create Migration
-- Generated from: 20251115000000_InitialCreate.cs
-- Database: MySQL 8.0
-- Date: 2025-11-15

-- =============================================================================
-- 1. Create users table
-- =============================================================================

CREATE TABLE IF NOT EXISTS `users` (
    `Id` CHAR(36) NOT NULL,
    `username` VARCHAR(50) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(200) NULL,
    `password_hash` TEXT NOT NULL,
    `role` VARCHAR(20) NOT NULL,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `is_verified` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    `last_login` DATETIME NULL,
    `reset_token` VARCHAR(255) NULL,
    `reset_token_expires` DATETIME NULL,
    CONSTRAINT `PK_users` PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 2. Create configuration_templates table
-- =============================================================================

CREATE TABLE IF NOT EXISTS `configuration_templates` (
    `Id` CHAR(36) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NULL,
    `regenerator_type` VARCHAR(50) NOT NULL,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL,
    CONSTRAINT `PK_configuration_templates` PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 3. Create regenerator_configurations table
-- =============================================================================

CREATE TABLE IF NOT EXISTS `regenerator_configurations` (
    `Id` CHAR(36) NOT NULL,
    `user_id` CHAR(36) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NULL,
    `regenerator_type` VARCHAR(50) NOT NULL,
    `configuration_version` VARCHAR(20) NULL,
    `status` VARCHAR(20) NOT NULL,
    `current_step` INT NOT NULL DEFAULT 1,
    `total_steps` INT NOT NULL DEFAULT 8,
    `completed_steps` JSON NULL,
    `geometry_config` JSON NULL,
    `materials_config` JSON NULL,
    `thermal_config` JSON NULL,
    `flow_config` JSON NULL,
    `constraints_config` JSON NULL,
    `visualization_config` JSON NULL,
    `model_geometry` JSON NULL,
    `model_materials` JSON NULL,
    `is_validated` TINYINT(1) NOT NULL DEFAULT 0,
    `validation_score` DOUBLE NULL,
    `validation_errors` JSON NULL,
    `validation_warnings` JSON NULL,
    `based_on_template_id` CHAR(36) NULL,
    `is_template` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    `completed_at` DATETIME NULL,
    CONSTRAINT `PK_regenerator_configurations` PRIMARY KEY (`Id`),
    CONSTRAINT `FK_regenerator_configurations_users_user_id`
        FOREIGN KEY (`user_id`) REFERENCES `users` (`Id`) ON DELETE CASCADE,
    CONSTRAINT `FK_regenerator_configurations_templates_based_on_template_id`
        FOREIGN KEY (`based_on_template_id`) REFERENCES `configuration_templates` (`Id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 4. Create optimization_scenarios table
-- =============================================================================

CREATE TABLE IF NOT EXISTS `optimization_scenarios` (
    `Id` CHAR(36) NOT NULL,
    `user_id` CHAR(36) NOT NULL,
    `base_configuration_id` CHAR(36) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `Description` TEXT NULL,
    `ScenarioType` VARCHAR(50) NULL,
    `Status` VARCHAR(20) NOT NULL DEFAULT 'active',
    `Objective` VARCHAR(100) NULL,
    `algorithm` VARCHAR(50) NOT NULL,
    `optimization_config` JSON NOT NULL,
    `ConstraintsConfig` JSON NULL,
    `BoundsConfig` JSON NULL,
    `design_variables` JSON NOT NULL,
    `ObjectiveWeights` JSON NULL,
    `max_iterations` INT NOT NULL DEFAULT 100,
    `MaxFunctionEvaluations` INT NULL,
    `tolerance` DOUBLE NOT NULL DEFAULT 0.000001,
    `MaxRuntimeMinutes` INT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    CONSTRAINT `PK_optimization_scenarios` PRIMARY KEY (`Id`),
    CONSTRAINT `FK_optimization_scenarios_users_user_id`
        FOREIGN KEY (`user_id`) REFERENCES `users` (`Id`) ON DELETE CASCADE,
    CONSTRAINT `FK_optimization_scenarios_configurations_base_configuration_id`
        FOREIGN KEY (`base_configuration_id`) REFERENCES `regenerator_configurations` (`Id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 5. Create optimization_jobs table
-- =============================================================================

CREATE TABLE IF NOT EXISTS `optimization_jobs` (
    `Id` CHAR(36) NOT NULL,
    `scenario_id` CHAR(36) NOT NULL,
    `celery_task_id` VARCHAR(255) NULL,
    `HangfireJobId` VARCHAR(255) NULL,
    `status` VARCHAR(20) NOT NULL,
    `progress` DOUBLE NOT NULL DEFAULT 0,
    `current_iteration` INT NULL,
    `BestObjectiveValue` DOUBLE NULL,
    `best_solution` JSON NULL,
    `results` JSON NULL,
    `error_message` TEXT NULL,
    `created_at` DATETIME NOT NULL,
    `started_at` DATETIME NULL,
    `completed_at` DATETIME NULL,
    `UpdatedAt` DATETIME NOT NULL,
    CONSTRAINT `PK_optimization_jobs` PRIMARY KEY (`Id`),
    CONSTRAINT `FK_optimization_jobs_scenarios_scenario_id`
        FOREIGN KEY (`scenario_id`) REFERENCES `optimization_scenarios` (`Id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 6. Create indexes on users table
-- =============================================================================

CREATE UNIQUE INDEX `IX_users_username` ON `users` (`username`);
CREATE UNIQUE INDEX `IX_users_email` ON `users` (`email`);
CREATE INDEX `IX_users_role` ON `users` (`role`);

-- =============================================================================
-- 7. Create indexes on regenerator_configurations table
-- =============================================================================

CREATE INDEX `IX_regenerator_configurations_user_id` ON `regenerator_configurations` (`user_id`);
CREATE INDEX `IX_regenerator_configurations_based_on_template_id` ON `regenerator_configurations` (`based_on_template_id`);

-- =============================================================================
-- 8. Create indexes on optimization_scenarios table
-- =============================================================================

CREATE INDEX `IX_optimization_scenarios_user_id` ON `optimization_scenarios` (`user_id`);
CREATE INDEX `IX_optimization_scenarios_base_configuration_id` ON `optimization_scenarios` (`base_configuration_id`);

-- =============================================================================
-- 9. Create indexes on optimization_jobs table
-- =============================================================================

CREATE INDEX `IX_optimization_jobs_scenario_id` ON `optimization_jobs` (`scenario_id`);

-- =============================================================================
-- 10. Create EF Core migrations history table
-- =============================================================================

CREATE TABLE IF NOT EXISTS `__EFMigrationsHistory` (
    `MigrationId` VARCHAR(150) NOT NULL,
    `ProductVersion` VARCHAR(32) NOT NULL,
    CONSTRAINT `PK___EFMigrationsHistory` PRIMARY KEY (`MigrationId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 11. Insert migration record
-- =============================================================================

INSERT INTO `__EFMigrationsHistory` (`MigrationId`, `ProductVersion`)
VALUES ('20251115000000_InitialCreate', '8.0.2')
ON DUPLICATE KEY UPDATE `ProductVersion` = '8.0.2';

-- Migration complete
SELECT 'Migration 20251115000000_InitialCreate applied successfully' AS Result;
