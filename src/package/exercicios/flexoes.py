import cv2
import mediapipe as mp
import math
video = cv2.VideoCapture('push-ups.mp4')
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
while True:
    sucess, img = video.read()
    # analisa o corpo da pessoa
    results = Pose.process(img)
    # pontos do corpo humano
    points = results.pose_landmarks
    # linhas no corpo
    draw.draw_landmarks(img,points,pose.POSE_CONNECTIONS)
    # variáveis da altura,largura e numero de canais da imagem
    h, w, _ = img.shape

    # variáveis para os pontos, com os pontos ajustados ao tamanho da tela
    if points:
        ombroDx = int(points.landmark[pose.PoseLandmark.RIGHT_SHOULDER].x * w)
        ombroDy = int(points.landmark[pose.PoseLandmark.RIGHT_SHOULDER].y * h)
        pulsoDx = int(points.landmark[pose.PoseLandmark.RIGHT_WRIST].x * w)
        pulsoDy = int(points.landmark[pose.PoseLandmark.RIGHT_WRIST].y * h)

        # distancia entre mão e o ombro
        distMaoxombro = math.hypot(ombroDx - pulsoDx, ombroDy - pulsoDy)

        # contagem da flexão
        if check == True and distMaoxombro <= 70:
            contador +=1
            check = False

        if distMaoxombro >=100 :
            check = True

        # texto na tela
        texto = f'Contagem = {contador}'
        cv2.putText(img,texto,(40,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,200,255),3)

    cv2.imshow('Resutado',img)
    # tecla para encerrar o loop e fechar o programa
    if cv2.waitKey(40) & 0xFF == ord('q'):
        break

