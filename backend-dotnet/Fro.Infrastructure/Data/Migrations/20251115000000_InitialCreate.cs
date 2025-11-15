using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Fro.Infrastructure.Data.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // Create users table
            migrationBuilder.CreateTable(
                name: "users",
                columns: table => new
                {
                    Id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    username = table.Column<string>(type: "varchar(50)", maxLength: 50, nullable: false),
                    email = table.Column<string>(type: "varchar(255)", maxLength: 255, nullable: false),
                    full_name = table.Column<string>(type: "varchar(200)", maxLength: 200, nullable: true),
                    password_hash = table.Column<string>(type: "TEXT", nullable: false),
                    role = table.Column<string>(type: "varchar(20)", maxLength: 20, nullable: false),
                    is_active = table.Column<bool>(type: "tinyint(1)", nullable: false, defaultValue: true),
                    is_verified = table.Column<bool>(type: "tinyint(1)", nullable: false, defaultValue: false),
                    created_at = table.Column<DateTime>(type: "DATETIME", nullable: false),
                    updated_at = table.Column<DateTime>(type: "DATETIME", nullable: false),
                    last_login = table.Column<DateTime>(type: "DATETIME", nullable: true),
                    reset_token = table.Column<string>(type: "varchar(255)", maxLength: 255, nullable: true),
                    reset_token_expires = table.Column<DateTime>(type: "DATETIME", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_users", x => x.Id);
                });

            // Create configuration_templates table
            migrationBuilder.CreateTable(
                name: "configuration_templates",
                columns: table => new
                {
                    Id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    name = table.Column<string>(type: "varchar(255)", maxLength: 255, nullable: false),
                    regenerator_type = table.Column<string>(type: "varchar(50)", maxLength: 50, nullable: false),
                    is_active = table.Column<bool>(type: "tinyint(1)", nullable: false, defaultValue: true),
                    created_at = table.Column<DateTime>(type: "DATETIME", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_configuration_templates", x => x.Id);
                });

            // Create regenerator_configurations table
            migrationBuilder.CreateTable(
                name: "regenerator_configurations",
                columns: table => new
                {
                    Id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    user_id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    name = table.Column<string>(type: "varchar(255)", maxLength: 255, nullable: false),
                    description = table.Column<string>(type: "TEXT", nullable: true),
                    regenerator_type = table.Column<string>(type: "varchar(50)", maxLength: 50, nullable: false),
                    configuration_version = table.Column<string>(type: "varchar(20)", maxLength: 20, nullable: true),
                    status = table.Column<string>(type: "varchar(20)", maxLength: 20, nullable: false),
                    current_step = table.Column<int>(type: "int", nullable: false, defaultValue: 1),
                    total_steps = table.Column<int>(type: "int", nullable: false, defaultValue: 8),
                    completed_steps = table.Column<string>(type: "JSON", nullable: true),
                    geometry_config = table.Column<string>(type: "JSON", nullable: true),
                    materials_config = table.Column<string>(type: "JSON", nullable: true),
                    thermal_config = table.Column<string>(type: "JSON", nullable: true),
                    flow_config = table.Column<string>(type: "JSON", nullable: true),
                    constraints_config = table.Column<string>(type: "JSON", nullable: true),
                    visualization_config = table.Column<string>(type: "JSON", nullable: true),
                    model_geometry = table.Column<string>(type: "JSON", nullable: true),
                    model_materials = table.Column<string>(type: "JSON", nullable: true),
                    is_validated = table.Column<bool>(type: "tinyint(1)", nullable: false, defaultValue: false),
                    validation_score = table.Column<double>(type: "double", nullable: true),
                    validation_errors = table.Column<string>(type: "JSON", nullable: true),
                    validation_warnings = table.Column<string>(type: "JSON", nullable: true),
                    based_on_template_id = table.Column<string>(type: "CHAR(36)", nullable: true),
                    is_template = table.Column<bool>(type: "tinyint(1)", nullable: false, defaultValue: false),
                    created_at = table.Column<DateTime>(type: "DATETIME", nullable: false),
                    updated_at = table.Column<DateTime>(type: "DATETIME", nullable: false),
                    completed_at = table.Column<DateTime>(type: "DATETIME", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_regenerator_configurations", x => x.Id);
                    table.ForeignKey(
                        name: "FK_regenerator_configurations_users_user_id",
                        column: x => x.user_id,
                        principalTable: "users",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_regenerator_configurations_templates_based_on_template_id",
                        column: x => x.based_on_template_id,
                        principalTable: "configuration_templates",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            // Create optimization_scenarios table
            migrationBuilder.CreateTable(
                name: "optimization_scenarios",
                columns: table => new
                {
                    Id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    user_id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    base_configuration_id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    name = table.Column<string>(type: "varchar(255)", maxLength: 255, nullable: false),
                    Description = table.Column<string>(type: "TEXT", nullable: true),
                    ScenarioType = table.Column<string>(type: "varchar(50)", maxLength: 50, nullable: true),
                    Status = table.Column<string>(type: "varchar(20)", maxLength: 20, nullable: false, defaultValue: "active"),
                    Objective = table.Column<string>(type: "varchar(100)", maxLength: 100, nullable: true),
                    algorithm = table.Column<string>(type: "varchar(50)", maxLength: 50, nullable: false),
                    optimization_config = table.Column<string>(type: "JSON", nullable: false),
                    ConstraintsConfig = table.Column<string>(type: "JSON", nullable: true),
                    BoundsConfig = table.Column<string>(type: "JSON", nullable: true),
                    design_variables = table.Column<string>(type: "JSON", nullable: false),
                    ObjectiveWeights = table.Column<string>(type: "JSON", nullable: true),
                    max_iterations = table.Column<int>(type: "int", nullable: false, defaultValue: 100),
                    MaxFunctionEvaluations = table.Column<int>(type: "int", nullable: true),
                    tolerance = table.Column<double>(type: "double", nullable: false, defaultValue: 1e-6),
                    MaxRuntimeMinutes = table.Column<int>(type: "int", nullable: true),
                    created_at = table.Column<DateTime>(type: "DATETIME", nullable: false),
                    updated_at = table.Column<DateTime>(type: "DATETIME", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_optimization_scenarios", x => x.Id);
                    table.ForeignKey(
                        name: "FK_optimization_scenarios_users_user_id",
                        column: x => x.user_id,
                        principalTable: "users",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_optimization_scenarios_configurations_base_configuration_id",
                        column: x => x.base_configuration_id,
                        principalTable: "regenerator_configurations",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            // Create optimization_jobs table
            migrationBuilder.CreateTable(
                name: "optimization_jobs",
                columns: table => new
                {
                    Id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    scenario_id = table.Column<string>(type: "CHAR(36)", nullable: false),
                    celery_task_id = table.Column<string>(type: "varchar(255)", maxLength: 255, nullable: true),
                    HangfireJobId = table.Column<string>(type: "varchar(255)", maxLength: 255, nullable: true),
                    status = table.Column<string>(type: "varchar(20)", maxLength: 20, nullable: false),
                    progress = table.Column<double>(type: "double", nullable: false, defaultValue: 0),
                    current_iteration = table.Column<int>(type: "int", nullable: true),
                    BestObjectiveValue = table.Column<double>(type: "double", nullable: true),
                    best_solution = table.Column<string>(type: "JSON", nullable: true),
                    results = table.Column<string>(type: "JSON", nullable: true),
                    error_message = table.Column<string>(type: "TEXT", nullable: true),
                    created_at = table.Column<DateTime>(type: "DATETIME", nullable: false),
                    started_at = table.Column<DateTime>(type: "DATETIME", nullable: true),
                    completed_at = table.Column<DateTime>(type: "DATETIME", nullable: true),
                    UpdatedAt = table.Column<DateTime>(type: "DATETIME", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_optimization_jobs", x => x.Id);
                    table.ForeignKey(
                        name: "FK_optimization_jobs_scenarios_scenario_id",
                        column: x => x.scenario_id,
                        principalTable: "optimization_scenarios",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            // Create indexes on users table
            migrationBuilder.CreateIndex(
                name: "IX_users_username",
                table: "users",
                column: "username",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_users_email",
                table: "users",
                column: "email",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_users_role",
                table: "users",
                column: "role");

            // Create indexes on regenerator_configurations table
            migrationBuilder.CreateIndex(
                name: "IX_regenerator_configurations_user_id",
                table: "regenerator_configurations",
                column: "user_id");

            migrationBuilder.CreateIndex(
                name: "IX_regenerator_configurations_based_on_template_id",
                table: "regenerator_configurations",
                column: "based_on_template_id");

            // Create indexes on optimization_scenarios table
            migrationBuilder.CreateIndex(
                name: "IX_optimization_scenarios_user_id",
                table: "optimization_scenarios",
                column: "user_id");

            migrationBuilder.CreateIndex(
                name: "IX_optimization_scenarios_base_configuration_id",
                table: "optimization_scenarios",
                column: "base_configuration_id");

            // Create indexes on optimization_jobs table
            migrationBuilder.CreateIndex(
                name: "IX_optimization_jobs_scenario_id",
                table: "optimization_jobs",
                column: "scenario_id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "optimization_jobs");

            migrationBuilder.DropTable(
                name: "optimization_scenarios");

            migrationBuilder.DropTable(
                name: "regenerator_configurations");

            migrationBuilder.DropTable(
                name: "configuration_templates");

            migrationBuilder.DropTable(
                name: "users");
        }
    }
}
