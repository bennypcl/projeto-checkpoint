import mysql.connector #Instalar no terminal: pip install mysql-connector-python

# Conexão com o banco
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="checkpoint_base"
    )