import sqlite3
import pandas as pd

con = sqlite3.connect("database.db", check_same_thread=False)
cur = con.cursor()

#documents = [(1, "Fire Safety Manual", "IT"), (2, "HR Onboarding Guide", "HR"), (3, "Annual Report 2023", "Finance"), (4, "Fire Safety Manual 2", "IT"), (5, "HR Onboarding Guide 2", "HR"), (6, "Annual Report 2023 2", "Finance")]

#cur.executemany("INSERT INTO documents(id, document_name, department_name) VALUES (?, ?, ?)", documents)

df = pd.read_excel('Updated Department List.xlsx', sheet_name='Sheet1')


df.to_sql('documents', con, if_exists="replace", index=True)


#con.commit()
#con.close()
