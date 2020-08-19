from flask import Flask
import pypyodbc
connection = pypyodbc.connect('Driver={SQL Server}; Server=MSI; Database=Справочник_болезней;')

cursor = connection.cursor()

for row in result:
    print(row)