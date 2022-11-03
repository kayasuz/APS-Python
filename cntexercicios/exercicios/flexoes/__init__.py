
# bibliotecas de terceiros
import cv2
import mediapipe as mp
import numpy as np
# biblioteca padrão
import os
import sys
import math
# biblioteca do programa
from cntexercicios.video import abrir_video, extrair_frames
from cntexercicios.exercicios import registrar_exercicio

@registrar_exercicio("flexões")
def contar_flexoes(video):
    """
    Aplica detecção de poses no vídeo passado como parâmetro,
    contando a quantidade de flexões feitas.

    Como essa função utiliza a funções do módulo cntexercicios.video,
    ela aceita tanto nomes de arquivos de vídeo como índices
    de dispositivos que o opencv-python ou pyopencv podem utilizar
    """

    # variável que traz os modelos do corpo humano
    pose = mp.solutions.pose
    # variável responsável pela detecção
    Pose = pose.Pose(min_tracking_confidence=0.5,min_detection_confidence=0.5)
    # variável para desenhar os pontos e suas ligações na imagem
    draw = mp.solutions.drawing_utils
    # contador de flexões
    contador = 0
    # variável para controlar a contagem de flexões
    check = True

    # lambda para simplificar a sintaxe
    ponto_para_array = lambda ponto: np.array((ponto.x, 1-ponto.y, ponto.z))
    posicao_landmark = lambda landmark: ponto_para_array(points.landmark[landmark])

    with abrir_video(video) as captura:
        for img in extrair_frames(captura):

            results = Pose.process(img)
            # pontos do corpo humano
            points = results.pose_landmarks
            # linhas no corpo
            draw.draw_landmarks(img,points,pose.POSE_CONNECTIONS)
            # variáveis da altura,largura e numero de canais da imagem
            h, w, _ = img.shape

            # variáveis para os pontos, com os pontos ajustados ao tamanho da tela
            if points:
                # posições do centro dos pés, da cintura e dos ombros (base do pescoço)
                pos_ombro_dir   = posicao_landmark(pose.PoseLandmark.RIGHT_SHOULDER)
                pos_ombro_esq   = posicao_landmark(pose.PoseLandmark.LEFT_SHOULDER)
                pos_cintura_dir = posicao_landmark(pose.PoseLandmark.RIGHT_HIP)
                pos_cintura_esq = posicao_landmark(pose.PoseLandmark.LEFT_HIP)
                pos_pe_dir      = posicao_landmark(pose.PoseLandmark.RIGHT_HEEL)
                pos_pe_esq      = posicao_landmark(pose.PoseLandmark.LEFT_HEEL)
                pos_pescoco     = ( pos_ombro_dir   + pos_ombro_esq   ) / 2
                pos_cintura     = ( pos_cintura_dir + pos_cintura_esq ) / 2
                pos_centro_pes  = ( pos_pe_dir      + pos_pe_esq      ) / 2

                # verificação se as pernas estão retas e o corpo está na horizontal
                vet_pes_pescoco = pos_pescoco - pos_centro_pes
                vet_pes_cintura = pos_cintura - pos_centro_pes
                dis_pes_pescoco = np.linalg.norm(vet_pes_pescoco)
                dis_pes_cintura = np.linalg.norm(vet_pes_cintura)

                # NOTE: o angulo é medido em relação ao eixo y dos frames
                prod_vet = np.dot(vet_pes_pescoco, vet_pes_cintura) / (dis_pes_pescoco * dis_pes_cintura)
                angulo   = np.degrees(np.fabs(np.arctan2(vet_pes_pescoco[0], vet_pes_pescoco[1])))
                if prod_vet > 0.9 and 60 < angulo < 120:
                    # verificação se a distância entre as mãos e os pés é próxima
                    # da distância entre os pés e a base do pescoço
                    pos_pulso_dir     = posicao_landmark(pose.PoseLandmark.RIGHT_WRIST)
                    pos_pulso_esq     = posicao_landmark(pose.PoseLandmark.LEFT_WRIST)
                    pos_centro_pulsos = ( pos_pulso_dir + pos_pulso_esq ) / 2

                    vet_pes_pulsos = pos_centro_pulsos - pos_centro_pes
                    dis_pes_pulsos = np.linalg.norm(vet_pes_pulsos)

                    if math.fabs(dis_pes_pulsos - dis_pes_pescoco) < (dis_pes_pulsos + dis_pes_pescoco) / 2:
                        # aproximação da altura da flexão normalizada em relação a altura aproximada da pessoa
                        # (distância entre os pés e a base do pescoço)
                        h_flexao = (np.linalg.norm(pos_centro_pulsos - pos_pescoco) /
                            np.linalg.norm(pos_pescoco - pos_centro_pes))

                        # contagem da flexão
                        if check:
                            if h_flexao < 0.30:
                                contador += 1
                                check = False

                        elif h_flexao >= 0.40:
                            check = True

                # texto na tela
                texto = f'Contagem = {contador}'
                cv2.putText(img,texto,(40,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,200,255),3)

            cv2.imshow('Resutado',img)
            # tecla para encerrar o loop e fechar o programa
            if cv2.waitKey(40) & 0xFF == ord('q'):
                break

