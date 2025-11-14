using System;
using MySqlConnector;

class CreateDb
{
    static void Main()
    {
        Console.WriteLine("Creating database fro_db...");
        try
        {
            using var conn = new MySqlConnection("Server=localhost;Port=3306;User=root;Password=;");
            conn.Open();

            using var cmd = new MySqlCommand("CREATE DATABASE IF NOT EXISTS fro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci", conn);
            cmd.ExecuteNonQuery();
            Console.WriteLine("✓ Database created");

            // Test with fro_user
            using var testConn = new MySqlConnection("Server=localhost;Port=3306;Database=fro_db;User=fro_user;Password=fro_password;");
            testConn.Open();
            Console.WriteLine("✓ fro_user can connect!");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
