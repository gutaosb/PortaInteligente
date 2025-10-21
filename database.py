import sqlite3
import os

DB_PATH = os.path.join("data", "porta.db")

def conectar():
    """Retorna uma conexão ativa com o banco."""
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # Criação das tabelas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            disciplina TEXT,
            foto_path TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aulas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            professor_id INTEGER NOT NULL,
            sala_id INTEGER NOT NULL,
            dia_semana TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL,
            FOREIGN KEY (professor_id) REFERENCES professores (id),
            FOREIGN KEY (sala_id) REFERENCES salas (id)
        )
    """)

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            professor_id INTEGER,
            sala_id INTEGER, 
            data_hora TEXT,
            resultado TEXT,
            FOREIGN KEY (professor_id) REFERENCES professores (id),
            FOREIGN KEY (sala_id) REFERENCES salas (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Banco de dados criado/atualizado com sucesso!")

if __name__ == "__main__":
    criar_tabelas()
