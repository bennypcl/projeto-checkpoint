import mysql.connector #Instalar no terminal: pip install mysql-connector-python

# Conexão com o banco
def conectar():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="123",
        database="checkpoint_base"
    )