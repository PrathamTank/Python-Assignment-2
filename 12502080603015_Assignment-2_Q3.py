import csv
import mysql.connector
from mysql.connector import Error

print("=== MySQL Student-Course Analytics Engine ===")

connection = None
cursor = None

try:
    host = input("Enter MySQL host: ").strip()
    user = input("Enter MySQL username: ").strip()
    password = input("Enter MySQL password: ")
    database = input("Enter database name: ").strip()

    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Student (
            student_id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            spi DECIMAL(3,1) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CourseRegistration (
            student_id INT NOT NULL,
            course_id VARCHAR(30) NOT NULL,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES Student(student_id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_course_id
        ON CourseRegistration(course_id)
    """)

    student_file = input("Enter student CSV file path: ").strip()
    registration_file = input("Enter registration CSV file path: ").strip()

    student_rows = []

    with open(student_file, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            student_id = int(row["student_id"])
            name = row["name"].strip()
            spi = float(row["spi"])

            if not name or not 0 <= spi <= 10:
                raise ValueError("Invalid student name or SPI.")

            student_rows.append((student_id, name, spi))

            if len(student_rows) >= 1000:
                cursor.executemany("""
                    INSERT INTO Student (student_id, name, spi)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    name = VALUES(name), spi = VALUES(spi)
                """, student_rows)
                connection.commit()
                student_rows.clear()

    if student_rows:
        cursor.executemany("""
            INSERT INTO Student (student_id, name, spi)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            name = VALUES(name), spi = VALUES(spi)
        """, student_rows)
        connection.commit()

    registration_rows = []

    with open(registration_file, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            student_id = int(row["student_id"])
            course_id = row["course_id"].strip()

            if not course_id:
                raise ValueError("Course ID cannot be empty.")

            registration_rows.append((student_id, course_id))

            if len(registration_rows) >= 1000:
                cursor.executemany("""
                    INSERT IGNORE INTO CourseRegistration
                    (student_id, course_id)
                    VALUES (%s, %s)
                """, registration_rows)
                connection.commit()
                registration_rows.clear()

    if registration_rows:
        cursor.executemany("""
            INSERT IGNORE INTO CourseRegistration
            (student_id, course_id)
            VALUES (%s, %s)
        """, registration_rows)
        connection.commit()

    course_id = input("Enter course ID: ").strip()
    spi_threshold = float(input("Enter SPI threshold: "))

    if not 0 <= spi_threshold <= 10:
        raise ValueError("SPI threshold must be between 0 and 10.")

    cursor.execute("""
        SELECT s.student_id, s.name, s.spi, cr.course_id
        FROM Student AS s
        JOIN CourseRegistration AS cr
            ON s.student_id = cr.student_id
        WHERE cr.course_id = %s AND s.spi > %s
        ORDER BY s.spi DESC, s.student_id ASC
    """, (course_id, spi_threshold))

    print("\nStudent ID  Name  SPI  Course ID")

    for student_id, name, spi, course in cursor:
        print(student_id, name, f"{spi:.1f}", course)

except (Error, OSError, ValueError, KeyError) as e:
    print("ERROR:", e)

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()

    print("Database connection closed.")