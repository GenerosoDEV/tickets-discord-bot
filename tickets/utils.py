from sqlite3 import Error
import sqlite3
from unidecode import unidecode

def connectToDatabase():
    caminho = './tickets/data.db'
    con=None
    try:
        con=sqlite3.connect(caminho)
    except Error as ex:
        print(ex)
    return con

vcon = connectToDatabase()

def dbQuery(sql):
    conexao = vcon
    c=conexao.cursor()
    c.execute(sql)
    resultado=c.fetchall()
    if resultado == []:
        return None
    else:
        return resultado

def dbExec(sql):
    conexao = vcon
    try:
        c = conexao.cursor()
        c.execute(sql)
        conexao.commit()
    except Exception as ex:
        print(ex)

def formatToSQL(text):
    text = str(text)
    if "'" in text:
        text = text.replace("'", "")
        text = unidecode(text)
        return text
    else:
        return text
