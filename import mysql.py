import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Maman143*",
    database="supply_chain"
)

cursor = conn.cursor()

# Insert new row
insert_query = "INSERT INTO myTable (column1, column2) VALUES (%s, %s)"
values = ("Banana", "Fruit")
cursor.execute(insert_query, values)
conn.commit()

print("✅ New row inserted.")

# Optional: Show all rows
cursor.execute("SELECT * FROM myTable")
for row in cursor.fetchall():
    print(row)

conn.close()

