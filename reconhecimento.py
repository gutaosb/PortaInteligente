import cv2
import os
import numpy as np
from datetime import datetime, time as dtime
from models import listar_aula_professor, registrar_acesso, listar_professor_por_nome
from database import conectar

# Caminhos
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
IMG_DIR = "imagens"
RECOGNIZER_MODEL_PATH = "models/lbph_model.yml"

# Parâmetros
FACE_IMG_SIZE = (200, 200)

WEEKDAY_PT = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}


def _extrair_nome_de_filename(fname):
    base = os.path.splitext(fname)[0]
    return base.replace("_", " ")


def treinar_recognizer():
    if not os.path.exists(IMG_DIR):
        raise FileNotFoundError(f"Pasta '{IMG_DIR}' não encontrada.")

    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    faces = []
    labels = []
    label_to_name = {}

    label_id = 0
    for fname in os.listdir(IMG_DIR):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        nome_professor = _extrair_nome_de_filename(fname)
        caminho = os.path.join(IMG_DIR, fname)
        img = cv2.imread(caminho)

        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rostos = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(rostos) == 0:
            roi = cv2.resize(gray, FACE_IMG_SIZE)
        else:
            x, y, w, h = max(rostos, key=lambda r: r[2]*r[3])
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, FACE_IMG_SIZE)

        faces.append(roi)
        labels.append(label_id)
        label_to_name[label_id] = nome_professor
        label_id += 1

    if not faces:
        raise RuntimeError("Nenhuma face válida encontrada em 'imagens/'.")

    recognizer.train(faces, np.array(labels))
    os.makedirs(os.path.dirname(RECOGNIZER_MODEL_PATH), exist_ok=True)
    recognizer.write(RECOGNIZER_MODEL_PATH)

    return recognizer, label_to_name


def _hora_str_para_time(hora_str):
    try:
        hora_str = hora_str.strip()
        h, m = hora_str.split(":")
        return dtime(int(h), int(m))
    except Exception as e:
        print(f"Erro ao converter hora '{hora_str}': {e}")
        return None


def professor_tem_aula_no_horario(nome_professor, sala_selecionada):
    professor = listar_professor_por_nome(nome_professor)
    if not professor:
        return False, None

    professor_id = professor[0]
    aulas = listar_aula_professor(professor_id)
    if not aulas:
        return False, None

    now = datetime.now()
    dia_hoje = WEEKDAY_PT[now.weekday()]
    hora_atual = now.time()

    for a in aulas:
        dia_semana, hora_inicio_str, hora_fim_str, sala = a
        if sala_selecionada and sala_selecionada != sala:
            continue
        if dia_semana != dia_hoje:
            continue

        inicio = _hora_str_para_time(hora_inicio_str)
        fim = _hora_str_para_time(hora_fim_str)
        if not (inicio and fim):
            continue

        if inicio <= hora_atual <= fim:
            return True, a

    return False, None


def iniciar_reconhecimento(sala_selecionada=None, mostrar_janela=True):
    try:
        recognizer, label_to_name = treinar_recognizer()
    except Exception as e:
        return {'status': 'Erro', 'professor': None, 'mensagem': str(e)}

    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return {'status': 'Erro', 'professor': None, 'mensagem': 'Câmera não disponível.'}

    resultado_final = {'status': 'NenhumRosto', 'professor': None, 'mensagem': 'Nenhum rosto reconhecido.'}
    reconhecimento_feito = False

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostos = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in rostos:
                roi = gray[y:y+h, x:x+w]
                roi = cv2.resize(roi, FACE_IMG_SIZE)

                # Aqui não usamos mais confiança, apenas reconhecemos o rosto
                label, _ = recognizer.predict(roi)
                nome_professor = label_to_name.get(label, "Desconhecido")

                # Verifica aula do professor
                tem_aula, aula_info = professor_tem_aula_no_horario(nome_professor, sala_selecionada)
                if tem_aula:
                    registrar_acesso(nome_professor, "Permitido")
                    resultado_final = {'status': 'Permitido', 'professor': nome_professor,
                                       'mensagem': f'✅ {nome_professor} reconhecido. Aula confirmada.'}
                    color = (0, 255, 0)
                else:
                    registrar_acesso(nome_professor, "Negado")
                    resultado_final = {'status': 'Negado', 'professor': nome_professor,
                                       'mensagem': f'⚠️ {nome_professor} reconhecido, mas sem aula agora.'}
                    color = (0, 128, 255)

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, nome_professor, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                reconhecimento_feito = True

            if mostrar_janela:
                cv2.imshow("Reconhecimento Facial - Pressione ESC para sair", frame)

            if reconhecimento_feito:
                if mostrar_janela:
                    cv2.waitKey(1500)
                break

            key = cv2.waitKey(1)
            if key == 27:
                break

    finally:
        cam.release()
        cv2.destroyAllWindows()

    return resultado_final
