import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thelab.settings")

django.setup()

sql_file_path = 'TestData.sql'

with open(sql_file_path, 'r') as sql_file:
    sql_script = sql_file.read()

# Split the SQL script into individual statements
sql_statements = sql_script.split(';')

# Execute each statement
with connection.cursor() as cursor:
    for statement in sql_statements:
        # Skip empty statements
        if statement.strip():
            try:
                cursor.execute(statement)
            except Exception as e:
                print(f"Error executing statement: {statement}\nError: {e}")

print("SQL script executed successfully.")