import tkinter as tk
from tkinter import ttk, messagebox
from models import inserir_aula, listar_professores, inserir_professor, listar_salas, inserir_sala, listar_sala_por_nome
from reconhecimento import iniciar_reconhecimento
import cv2
import os

# ===============================================
# Funções de eventos
# ===============================================

def abrir_camera():
    sala = combo_sala.get()  # pega a sala selecionada no combobox
    resultado = iniciar_reconhecimento(sala_selecionada=sala, mostrar_janela=True)

    if resultado['status'] == 'Permitido':
        messagebox.showinfo("Acesso", f"✅ Acesso permitido.\n{resultado['mensagem']}")
        # Aqui você pode acionar a porta física (GPIO/Arduino) se tiver integração
    elif resultado['status'] == 'Negado':
        messagebox.showwarning("Acesso", f"⛔ Acesso negado.\n{resultado['mensagem']}")
    elif resultado['status'] == 'NenhumRosto':
        messagebox.showinfo("Acesso", "Nenhum rosto reconhecido.")
    else:
        messagebox.showerror("Erro", resultado.get('mensagem', 'Erro desconhecido.'))

def abrir_cadastro_professor():
    janela_professor = tk.Toplevel()
    janela_professor.title("Cadastro de professor")
    janela_professor.geometry("400x400")
    janela_professor.configure(bg="white")

    # Título
    tk.Label(janela_professor, text="Cadastro de Professor", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

     # Nome
    tk.Label(janela_professor, text="Nome:", bg="white", anchor="w").pack(padx=20, fill="x")
    entry_nome = tk.Entry(janela_professor)
    entry_nome.pack(padx=20, fill="x", pady=5)

    # CPF
    tk.Label(janela_professor, text="CPF:", bg="white", anchor="w").pack(padx=20, fill="x")
    entry_cpf = tk.Entry(janela_professor)
    entry_cpf.pack(padx=20, fill="x", pady=5)

    # Disciplina
    tk.Label(janela_professor, text="Disciplina:", bg="white", anchor="w").pack(padx=20, fill="x")
    entry_disciplina = tk.Entry(janela_professor)
    entry_disciplina.pack(padx=20, fill="x", pady=5)

    foto_path = [None]  # lista para permitir modificação dentro da função

    # Função para capturar a foto
    def capturar_foto():
        nome = entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Digite o nome do professor antes de capturar a foto.")
            return

        if not os.path.exists("imagens"):
            os.makedirs("imagens")

        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            messagebox.showerror("Erro", "Não foi possível acessar a câmera.")
            return

        messagebox.showinfo("Captura", "Pressione 'Espaço' para tirar a foto, ou 'ESC' para cancelar.")

        while True:
            ret, frame = camera.read()
            if not ret:
                break
            cv2.imshow("Captura de Foto", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
            elif key == 32:  # Espaço
                foto_nome = f"{nome.replace(' ', '_')}.jpg"
                foto_caminho = os.path.join("imagens", foto_nome)
                cv2.imwrite(foto_caminho, frame)
                foto_path[0] = foto_caminho
                messagebox.showinfo("Sucesso", f"Foto salva como: {foto_nome}")
                break

        camera.release()
        cv2.destroyAllWindows()

    # Função para salvar no banco
    def salvar_professor():
        nome = entry_nome.get().strip()
        cpf = entry_cpf.get().strip()
        disciplina = entry_disciplina.get().strip()

        if not nome or not cpf or not disciplina:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos antes de salvar.")
            return

        inserir_professor(nome, cpf, disciplina, foto_path[0])
        messagebox.showinfo("Sucesso", "Professor cadastrado com sucesso!")
        janela_professor.destroy()

    # Botões
    tk.Button(janela_professor, text="📸 Capturar Foto", bg="#0078D7", fg="white",
              font=("Arial", 11), width=20, command=capturar_foto).pack(pady=10)

    tk.Button(janela_professor, text="💾 Salvar Professor", bg="#28a745", fg="white",
              font=("Arial", 11), width=20, command=salvar_professor).pack(pady=10)


#Cadastrar salas
def abrir_cadastro_salas():
    janela_sala = tk.Toplevel()
    janela_sala.title("Cadastro de Sala")
    janela_sala.geometry("400x420")
    janela_sala.configure(bg="white")

    tk.Label(janela_sala, text="Cadastro de Sala", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    tk.Label(janela_sala, text="Nome:", bg="white", anchor="w").pack(padx=20, fill="x")
    entry_nome = tk.Entry(janela_sala)
    entry_nome.pack(padx=20, fill="x", pady=5)

    def salvar_sala():
        nome = entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos antes de salvar.")
            return
        
        inserir_sala(nome)
        messagebox.showinfo("Sucesso", "Sala cadastrada com sucesso!")
        janela_sala.destroy()

    #Botoes:
    tk.Button(janela_sala, text="💾 Salvar sala", bg="#28a745", fg="white",
              font=("Arial", 11), width=20, command=salvar_sala).pack(pady=10)


#Cadastrar aulas
def abrir_cadastro_aula():
    janela_aula = tk.Toplevel()
    janela_aula.title("Cadastro de Aula")
    janela_aula.geometry("400x420")
    janela_aula.configure(bg="white")

    tk.Label(janela_aula, text="Cadastro de Aula", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    # Lista de professores
    professores = listar_professores()
    if not professores:
        messagebox.showwarning("Aviso", "Nenhum professor cadastrado. Cadastre um professor antes.")
        janela_aula.destroy()
        return

    tk.Label(janela_aula, text="Professor:", bg="white", anchor="w").pack(padx=20, fill="x")
    combo_professor = ttk.Combobox(janela_aula, state="readonly", width=30)
    combo_professor["values"] = [f"{p[0]} - {p[1]}" for p in professores]
    combo_professor.set(combo_professor["values"][0])
    combo_professor.pack(padx=20, fill="x", pady=5)

    #Sala
    salas = listar_salas()
    if not salas:
        messagebox.showwarning("Aviso", "Nenhuma sala cadastrada. Cadastre uma sala antes.")
        janela_aula.destroy()
        return
    
    tk.Label(janela_aula, text="Sala:", bg="white", anchor="w").pack(padx=20, fill="x")
    combo_sala = ttk.Combobox(janela_aula, state="readonly", width=30)
    combo_sala["values"] = [f"{s}" for s in salas]
    combo_sala.set(combo_sala["values"][0])
    combo_sala.pack(padx=20, fill="x", pady=5)

    # Dia da semana
    tk.Label(janela_aula, text="Dia da Semana:", bg="white", anchor="w").pack(padx=20, fill="x")
    combo_dia = ttk.Combobox(janela_aula, state="readonly", width=30)
    combo_dia["values"] = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]
    combo_dia.set("Segunda-feira")
    combo_dia.pack(padx=20, fill="x", pady=5)

    # Horário início
    tk.Label(janela_aula, text="Horário de Início (HH:MM):", bg="white", anchor="w").pack(padx=20, fill="x")
    entry_inicio = tk.Entry(janela_aula)
    entry_inicio.insert(0, "08:00")
    entry_inicio.pack(padx=20, fill="x", pady=5)

    # Horário fim
    tk.Label(janela_aula, text="Horário de Término (HH:MM):", bg="white", anchor="w").pack(padx=20, fill="x")
    entry_fim = tk.Entry(janela_aula)
    entry_fim.insert(0, "10:00")
    entry_fim.pack(padx=20, fill="x", pady=5)

    def salvar_aula():
        professor_id = int(combo_professor.get().split(" - ")[0])
        sala_id = listar_sala_por_nome(combo_sala.get())[0]
        dia_semana = combo_dia.get()
        hora_inicio = entry_inicio.get()
        hora_fim = entry_fim.get()

        if not dia_semana or not hora_inicio or not hora_fim:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
            return

        inserir_aula(professor_id, sala_id, dia_semana, hora_inicio, hora_fim)
        messagebox.showinfo("Sucesso", "Aula cadastrada com sucesso!")
        janela_aula.destroy()

    tk.Button(janela_aula, text="💾 Salvar Aula", bg="#28a745", fg="white",
              font=("Arial", 11), width=20, command=salvar_aula).pack(pady=15)



# ===============================================
# Interface Principal
# ===============================================
def atualizar_salas(combo_salas):
    """Atualiza as opções de sala no combobox."""
    salas = listar_salas()
    combo_salas['values'] = [f"{s}" for s in salas] if salas else ["Nenhuma sala cadastrada"]
    if salas:
        combo_salas.current(0)

janela = tk.Tk()
janela.title("Sistema de Porta Inteligente  - Reconhecimento Facial")
janela.geometry("800x600")
janela.configure(bg="#f0f0f0")

# Frame principal
frame_principal = tk.Frame(janela, bg="white", bd=2, relief="groove")
frame_principal.pack(pady=40, padx=40, fill="both", expand=True)

# Título
titulo = tk.Label(frame_principal, text="Sistema de Porta Inteligente", font=("Arial", 22, "bold"), bg="white")
titulo.pack(pady=20)

# Área da câmera
frame_camera = tk.Frame(frame_principal, bg="#d9d9d9", width=500, height=300, relief="ridge", bd=3)
frame_camera.pack(pady=20)
frame_camera.pack_propagate(False)

label_camera = tk.Label(frame_camera, text="📷 Câmera / Reconhecimento Facial", bg="#d9d9d9", font=("Arial", 14))
label_camera.pack(expand=True)

# Combobox de seleção de sala
frame_sala = tk.Frame(frame_principal, bg="white")
frame_sala.pack(pady=10)

label_sala = tk.Label(frame_sala, text="Selecione a Sala:", bg="white", font=("Arial", 12))
label_sala.pack(side="left", padx=5)

salas = listar_salas()
combo_sala = ttk.Combobox(frame_sala, values=salas, state="readonly", width=20)
combo_sala.pack(side="left", padx=5)
atualizar_salas(combo_sala)

# Botão de reconhecimento
btn_reconhecer = tk.Button(frame_principal, text="Abrir Câmera / Reconhecimento Facial", font=("Arial", 14, "bold"),
                           bg="#0078D7", fg="white", width=35, height=2, command=abrir_camera)
btn_reconhecer.pack(pady=20)

# Frame inferior com botões menores
frame_botoes = tk.Frame(frame_principal, bg="white", padx=10)
frame_botoes.pack(pady=20)

btn_cadastro_professor = tk.Button(frame_botoes, text="Cadastro de Professores", font=("Arial", 11),
                                   bg="#28a745", fg="white", width=22, height=2, command=abrir_cadastro_professor)
btn_cadastro_professor.grid(row=1, column=0, padx=5, pady=5)

btn_cadastro_aula = tk.Button(frame_botoes, text="Cadastro de Aulas", font=("Arial", 11),
                              bg="#17a2b8", fg="white", width=22, height=2, command=abrir_cadastro_aula)
btn_cadastro_aula.grid(row=1, column=1, padx=5, pady=5)

btn_cadastro_sala = tk.Button(frame_botoes, text="Cadastro de Salas", font=("Arial", 11),
                              bg="#17a2b8", fg="white", width=22, height=2, command=abrir_cadastro_salas)
btn_cadastro_sala.grid(row=1, column=2, padx=5, pady=5)

# Rodapé
rodape = tk.Label(janela, text="© 2025 Sistema de Porta Inteligente", bg="#f0f0f0", font=("Arial", 9))
rodape.pack(side="bottom", pady=10)

janela.mainloop()