from postgres.db_connection import db_connection


def count_tables():
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
                AND table_schema NOT IN ('pg_catalog', 'information_schema')
            """
        )
        return cursor.fetchone()[0]

def create_users_table():
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                password VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                city VARCHAR(100) NOT NULL,
                gender VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        print("==> Users table created successfully.")

def create_patients_table():
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                age DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        print("==> Patients table created successfully.")

def create_doctors_table():
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS doctors (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                specialization VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        print("==> Doctors table created successfully.")

def create_services_table():
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                service_name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                duration INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        print("==> Services table created successfully.")

def create_appointments_table():
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                appointment_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        print("==> Appointments table created successfully.")
        
create_users_table()
create_patients_table()
create_doctors_table()
create_services_table()
create_appointments_table()

print(f"==> Number of tables in the database: {count_tables()}")
