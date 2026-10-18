import mysql.connector
from mysql.connector import Error

TABLES = {
    "student": {
        "table": "Student",
        "columns": ["id", "name", "spi"]
    },
    "course": {
        "table": "Course",
        "columns": ["id", "name"]
    },
    "registration": {
        "table": "CourseRegistration",
        "columns": ["student_id", "course_id"]
    }
}

JOINS = """
FROM Student s
JOIN CourseRegistration cr ON s.id = cr.student_id
JOIN Course c ON cr.course_id = c.id
"""

ALIASES = {
    "student": "s",
    "course": "c",
    "registration": "cr"
}

OPERATORS = {
    "=": "=",
    ">": ">",
    "<": "<",
    ">=": ">=",
    "<=": "<=",
    "LIKE": "LIKE",
    "!=": "!="
}

def validate_column(column):
    parts = column.strip().lower().split(".")

    if len(parts) != 2:
        raise ValueError("Invalid column format: " + column)

    table, field = parts

    if table not in TABLES or field not in TABLES[table]["columns"]:
        raise ValueError("Invalid column: " + column)

    return ALIASES[table] + "." + field

def build_query(columns, filters, order_column, direction, limit):
    if not columns:
        raise ValueError("Select at least one column.")

    if not 1 <= limit <= 1000:
        raise ValueError("Limit must be between 1 and 1000.")

    if direction.upper() not in ("ASC", "DESC"):
        raise ValueError("Sort direction must be ASC or DESC.")

    selected = [validate_column(col) for col in columns]
    conditions = []
    parameters = []

    for column, operator, value in filters:
        safe_column = validate_column(column)
        operator = operator.upper()

        if operator not in OPERATORS:
            raise ValueError("Invalid filter operator: " + operator)

        conditions.append(safe_column + " " + OPERATORS[operator] + " %s")
        parameters.append(value)

    safe_order_column = validate_column(order_column)

    sql = "SELECT " + ", ".join(selected) + " " + JOINS

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY " + safe_order_column + " " + direction.upper()
    sql += " LIMIT %s"
    parameters.append(limit)

    return sql, parameters

print("=== SQL Join Query Builder and Validator ===")

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

    print("\nAvailable columns:")
    print("student.id, student.name, student.spi")
    print("course.id, course.name")
    print("registration.student_id, registration.course_id")

    columns = input(
        "\nEnter selected columns separated by commas: "
    ).split(",")

    columns = [col.strip() for col in columns if col.strip()]

    count = int(input("Enter number of filters: "))
    filters = []

    for i in range(count):
        print(f"\nFilter {i + 1}")
        column = input("Column: ").strip()
        operator = input("Operator (=, !=, >, <, >=, <=, LIKE): ").strip()
        value = input("Value: ")
        filters.append((column, operator, value))

    order_column = input("\nEnter order column: ").strip()
    direction = input("Enter sort direction (ASC/DESC): ").strip()
    limit = int(input("Enter limit (1-1000): "))

    sql, parameters = build_query(
        columns,
        filters,
        order_column,
        direction,
        limit
    )

    print("\nSQL_OK")
    print("\nGenerated SQL:")
    print(sql)
    print("Parameters:", parameters)

    cursor.execute(sql, parameters)
    rows = cursor.fetchall()

    print("\nQuery Results:")
    for row in rows:
        print(*row)

except (ValueError, Error) as e:
    print("SQL_REJECTED")
    print("ERROR:", e)

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()