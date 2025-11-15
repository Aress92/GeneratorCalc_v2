#!/usr/bin/env python3
"""
Apply EF Core migration to MySQL database.
This script executes the InitialCreate migration SQL file.

Usage:
    python apply_migration.py

Requirements:
    pip install pymysql
"""

import sys
import json
from pathlib import Path
import pymysql
from pymysql.cursors import DictCursor


def load_connection_string():
    """Load MySQL connection string from appsettings.json"""
    appsettings_path = Path(__file__).parent / "Fro.Api" / "appsettings.json"

    if not appsettings_path.exists():
        print(f"❌ Error: appsettings.json not found at {appsettings_path}")
        sys.exit(1)

    with open(appsettings_path, 'r') as f:
        config = json.load(f)

    conn_str = config.get("ConnectionStrings", {}).get("DefaultConnection", "")

    if not conn_str:
        print("❌ Error: DefaultConnection not found in appsettings.json")
        sys.exit(1)

    # Parse connection string: Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;
    parts = {}
    for part in conn_str.split(';'):
        if '=' in part:
            key, value = part.split('=', 1)
            parts[key.strip().lower()] = value.strip()

    return {
        'host': parts.get('server', 'localhost'),
        'port': int(parts.get('port', 3306)),
        'database': parts.get('database', 'fro_db'),
        'user': parts.get('user', 'fro_user'),
        'password': parts.get('password', '')
    }


def test_connection(conn_params):
    """Test MySQL connection"""
    print("\n🔍 Testing MySQL connection...")
    print(f"   Host: {conn_params['host']}")
    print(f"   Port: {conn_params['port']}")
    print(f"   Database: {conn_params['database']}")
    print(f"   User: {conn_params['user']}")

    try:
        connection = pymysql.connect(
            host=conn_params['host'],
            port=conn_params['port'],
            user=conn_params['user'],
            password=conn_params['password'],
            database=conn_params['database'],
            charset='utf8mb4',
            cursorclass=DictCursor,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
            print(f"✅ Connected to MySQL {result['version']}")

        connection.close()
        return True

    except pymysql.Error as e:
        print(f"❌ Connection failed: {e}")
        return False


def check_existing_tables(conn_params):
    """Check if tables already exist"""
    try:
        connection = pymysql.connect(**conn_params, charset='utf8mb4', cursorclass=DictCursor)

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[f'Tables_in_{conn_params["database"]}'] for row in cursor.fetchall()]

        connection.close()

        if tables:
            print(f"\n⚠️  Warning: Database already contains {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")

            response = input("\nDo you want to continue? This may cause errors if tables already exist. (yes/no): ")
            return response.lower() in ['yes', 'y']

        return True

    except pymysql.Error as e:
        print(f"❌ Error checking tables: {e}")
        return False


def apply_migration(conn_params):
    """Execute the InitialCreate migration SQL script"""
    migration_file = Path(__file__).parent / "Fro.Infrastructure" / "Data" / "Migrations" / "20251115000000_InitialCreate.sql"

    if not migration_file.exists():
        print(f"❌ Error: Migration file not found at {migration_file}")
        sys.exit(1)

    print(f"\n📄 Reading migration file: {migration_file.name}")

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    # Split script into individual statements (separated by semicolons)
    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip() and not stmt.strip().startswith('--')]

    print(f"   Found {len(statements)} SQL statements")

    try:
        connection = pymysql.connect(**conn_params, charset='utf8mb4', cursorclass=DictCursor)

        print("\n🚀 Executing migration...")

        with connection.cursor() as cursor:
            for i, statement in enumerate(statements, 1):
                # Skip comments and empty statements
                if not statement or statement.startswith('--'):
                    continue

                try:
                    cursor.execute(statement)

                    # Show progress for table creation
                    if 'CREATE TABLE' in statement.upper():
                        table_name = statement.split('`')[1] if '`' in statement else 'unknown'
                        print(f"   ✅ Created table: {table_name}")
                    elif 'CREATE INDEX' in statement.upper() or 'CREATE UNIQUE INDEX' in statement.upper():
                        index_name = statement.split('`')[1] if '`' in statement else 'unknown'
                        print(f"   ✅ Created index: {index_name}")
                    elif 'INSERT INTO' in statement.upper():
                        print(f"   ✅ Inserted migration record")

                except pymysql.Error as e:
                    # Ignore "table already exists" errors for idempotency
                    if e.args[0] == 1050:  # Table already exists
                        table_name = statement.split('`')[1] if '`' in statement else 'unknown'
                        print(f"   ⏭️  Table already exists: {table_name}")
                    elif e.args[0] == 1061:  # Duplicate key name
                        print(f"   ⏭️  Index already exists")
                    elif e.args[0] == 1062:  # Duplicate entry
                        print(f"   ⏭️  Migration record already exists")
                    else:
                        raise

        connection.commit()
        connection.close()

        print("\n✅ Migration applied successfully!")
        return True

    except pymysql.Error as e:
        print(f"\n❌ Migration failed: {e}")
        return False


def verify_migration(conn_params):
    """Verify migration was applied correctly"""
    print("\n🔍 Verifying migration...")

    try:
        connection = pymysql.connect(**conn_params, charset='utf8mb4', cursorclass=DictCursor)

        with connection.cursor() as cursor:
            # Check migration history
            cursor.execute("""
                SELECT MigrationId, ProductVersion
                FROM __EFMigrationsHistory
                WHERE MigrationId = '20251115000000_InitialCreate'
            """)
            migration = cursor.fetchone()

            if migration:
                print(f"   ✅ Migration record found: {migration['MigrationId']} (EF Core {migration['ProductVersion']})")
            else:
                print("   ❌ Migration record not found in __EFMigrationsHistory")
                return False

            # Check tables
            expected_tables = [
                'users',
                'configuration_templates',
                'regenerator_configurations',
                'optimization_scenarios',
                'optimization_jobs',
                '__EFMigrationsHistory'
            ]

            cursor.execute("SHOW TABLES")
            existing_tables = [row[f'Tables_in_{conn_params["database"]}'] for row in cursor.fetchall()]

            print(f"\n   Tables created: {len(existing_tables)}")
            for table in expected_tables:
                if table in existing_tables:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} (missing)")

        connection.close()
        return True

    except pymysql.Error as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def main():
    print("=" * 80)
    print("EF Core Migration Applier - InitialCreate")
    print("=" * 80)

    # Load connection parameters
    try:
        conn_params = load_connection_string()
    except Exception as e:
        print(f"❌ Error loading connection string: {e}")
        sys.exit(1)

    # Test connection
    if not test_connection(conn_params):
        print("\n❌ Cannot proceed without database connection.")
        print("\nPlease ensure:")
        print("  1. MySQL is running (docker compose up -d mysql)")
        print("  2. Connection string in appsettings.json is correct")
        print("  3. Database exists (or create it with: CREATE DATABASE fro_db;)")
        sys.exit(1)

    # Check existing tables
    if not check_existing_tables(conn_params):
        print("\n⏹️  Migration cancelled by user")
        sys.exit(0)

    # Apply migration
    if not apply_migration(conn_params):
        sys.exit(1)

    # Verify migration
    if not verify_migration(conn_params):
        print("\n⚠️  Migration applied but verification failed")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("✅ Migration completed successfully!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Run database seeder to create admin user and test data")
    print("  2. Verify schema compatibility with Python backend")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Migration cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
