
from database import conectar
from datetime import datetime

# ============================================================
#  FUNÇÕES DO CRUD DE PROFESSORES
# ============================================================

def inserir_professor(nome, cpf, disciplina, foto_path=None):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO professores (nome, cpf, disciplina, foto_path)
        VALUES(?, ?, ?, ?)
    """, (nome, cpf, disciplina, foto_path))

    conn.commit()
    conn.close()

    print(f"Professor {nome} cadastrado com sucesso!")



def listar_professores():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM professores")
    professores = cursor.fetchall()

    conn.close()
    return professores


def listar_professor_por_id(professor_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM professores WHERE id = ?", (professor_id))
    professor = cursor.fetchone()

    conn.close()
    return professor

def editar_professor(professor_id, nome=None, cpf=None, disciplina=None, foto_path=None):
    conn = conectar()
    cursor = conn.cursor()

    campos = []
    valores = []

    if nome:
        campos.append("nome = ?")
        valores.append(nome)
    if cpf:
        campos.append("cpf = ?")
        valores.append(cpf)
    if disciplina:
        campos.append("disciplina = ?")
        valores.append(disciplina)
    if foto_path:
        campos.append("foto_path = ?")
        valores.append(foto_path)

    valores.append(professor_id)
    sql = f"UPDATE professores SET {', '.join(campos)} WHERE ID = ?"

    cursor.execute(sql, valores)
    conn.commit()
    conn.close()
    print(f"Professor id {professor_id} atualizado com sucesso!")

def deletar_professor(professor_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM professores WHERE id = ?", (professor_id,))

    conn.commit()
    conn.close()

    print(f"Professor id {professor_id} deletado com sucesso!")

def listar_professor_por_nome(nome):
    """
    Retorna o professor cujo nome corresponde ao fornecido.
    Retorna None se não encontrar.
    """
    conn = conectar()
    cursor = conn.cursor()

    # Usamos LIKE para permitir buscar com parte do nome ou nome completo
    cursor.execute("SELECT * FROM professores WHERE nome LIKE ?", (nome,))
    professor = cursor.fetchone()

    conn.close()
    return professor

# ============================================================
#  FUNÇÕES DO CRUD DE AULAS
# ============================================================

def inserir_aula(professor_id, dia_semana, hora_inicio, hora_fim, sala):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO aulas (professor_id, dia_semana, hora_inicio, hora_fim, sala)
        VALUES (?, ?, ?, ?, ?)
    """, (professor_id, dia_semana, hora_inicio, hora_fim, sala))

    conn.commit()
    conn.close()
    print(f"Aula cadastrada para o professor de id {professor_id}")

def listar_aulas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.id, p.nome, a.dia_semana, a.hora_inicio, a.hora_fim, a.sala
        FROM aulas a
        JOIN professores p ON a.professor_id = p.id
    """)
    aulas = cursor.fetchall()

    conn.close()
    return aulas

def listar_aula_professor(professor_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dia_semana, hora_inicio, hora_fim, sala
        FROM aulas
        WHERE professor_id = ?
    """, (professor_id,))
    aulas = cursor.fetchall()

    conn.close()
    return aulas

def deletar_aula(aula_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM aulas WHERE id = ?", (aula_id))

    conn.commit()
    conn.close()

    print(f"Aula de id {aula_id} deletada com sucesso!")


# ============================================================
#  FUNÇÕES DO CRUD DE ACESSOS
# ============================================================

def registrar_acesso(professor_id, resultado):
    """
    Registra tentativa de acesso na tabela acessos.
    resultado: "Permitido" ou "Negado"
    """
    conn = conectar()
    cur = conn.cursor()
    now = datetime.now().isoformat(sep=' ', timespec='seconds')
    cur.execute("""
        INSERT INTO acessos (professor_id, data_hora, resultado)
        VALUES (?, ?, ?)
    """, (professor_id, now, resultado))
    conn.commit()
    conn.close()
