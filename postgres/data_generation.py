from dotenv import load_dotenv
import psycopg2
import os
from faker import Faker
faker = Faker("en_US")
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

db_connection = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    database=POSTGRES_DB
)

db_connection.autocommit = True # Set autocommit to True to avoid the need for explicit commit statements

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

def create_all_tables():
    create_users_table()
    create_patients_table()
    create_doctors_table()
    create_services_table()
    create_appointments_table()
    print(f"==> Number of tables in the database: {count_tables()}")

def create_user(first_name, last_name, password, email, city, gender, is_doctor, optional_param=None):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, password, email, city, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (first_name, last_name, password, email, city, gender)
        )

        user_id = cursor.fetchone()[0]  # Get the ID of the newly created user
        print(f"==> User created successfully with ID: {user_id}")
        if is_doctor:
            create_doctor(user_id, optional_param)  # Create a doctor for the user with specialization 'Radiology'
        else:
            create_patient(user_id, optional_param)  # Create a patient for the user with age 30

def create_patient(user_id, age):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO patients (user_id, age)
            VALUES (%s, %s)
            """,
            (user_id, age)
        )
        print("==> Patient created successfully.")

def create_doctor(user_id, specialization):
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO doctors (user_id, specialization)
            VALUES (%s, %s)
            """,
            (user_id, specialization)
        )
        print("==> Doctor created successfully.")

def generate_fake_users(num_users):
    for _ in range(num_users):
        first_name = faker.first_name()
        last_name = faker.last_name()
        password = faker.password(length=10)
        email = faker.unique.email()
        city = faker.city()
        gender = faker.random_element(elements=('Male', 'Female'))
        is_doctor = faker.boolean(chance_of_getting_true=10)  # Randomly decide if the user is a doctor or not
        doctor_specialization = faker.random_element(elements=('Radiology', 'Cardiology', 'Dermatology', 'Neurology', 'Pediatrics')) if is_doctor else None
        patient_age = faker.date_of_birth(minimum_age=0, maximum_age=100).strftime("%Y/%m/%d") if not is_doctor else None
        optional_param = doctor_specialization if is_doctor else patient_age
        create_user(first_name, last_name, password, email, city, gender, is_doctor, optional_param)

def generate_services():
    services = [
        {"service_name": "General Consultation", "price": 50.00, "duration": 30},
        {"service_name": "Dental Cleaning", "price": 80.00, "duration": 45},
        {"service_name": "Eye Examination", "price": 60.00, "duration": 30},
        {"service_name": "Physical Therapy", "price": 100.00, "duration": 60},
        {"service_name": "Vaccination", "price": 40.00, "duration": 15},
        {"service_name": "Cardiology Checkup", "price": 120.00, "duration": 60},
        {"service_name": "Dermatology Consultation", "price": 90.00, "duration": 45},
        {"service_name": "Neurology Assessment", "price": 150.00, "duration": 60},
        {"service_name": "Pediatric Consultation", "price": 70.00, "duration": 30},
        {"service_name": "Radiology Imaging", "price": 200.00, "duration": 90}
    ]
    for service in services:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO services (service_name, price, duration)
                VALUES (%s, %s, %s)
                """,
                (service["service_name"], service["price"], service["duration"])
            )
            print(f"==> Service '{service['service_name']}' created successfully.")  

def generate_appointments(num_appointments):
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT id FROM patients")
        patient_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM doctors")
        doctor_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM services")
        service_ids = [row[0] for row in cursor.fetchall()]

    for _ in range(num_appointments):
        patient_id = faker.random_element(elements=patient_ids)
        doctor_id = faker.random_element(elements=doctor_ids)
        service_id = faker.random_element(elements=service_ids)
        appointment_date = faker.date_time_between(start_date='-1y', end_date='now')

        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO appointments (patient_id, doctor_id, service_id, appointment_date)
                VALUES (%s, %s, %s, %s)
                """,
                (patient_id, doctor_id, service_id, appointment_date)
            )
            print(f"==> Appointment created successfully for patient ID {patient_id} with doctor ID {doctor_id} on {appointment_date}.")

with db_connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    if cursor.fetchone() == (1,):
        print(f"==> Database connection successful at {POSTGRES_HOST}:{POSTGRES_PORT}")
        create_all_tables()
        generate_fake_users(5)
        # generate_services()
        generate_appointments(10)
    else:
        print(f"==> Database connection failed at {POSTGRES_HOST}:{POSTGRES_PORT}")



