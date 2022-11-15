"""
Módulo contendo um contador de exercícios para a contagem de flexões,
é recomendado que não se utilize a função de contagem ou a classe do
contador de flexões diretamente, mas sim as funções do módulo
cntexercicios.exercicios para executar a função indiretamente,
ou instanciar a classe do contador de flexões
"""

# biblioteca do programa
from cntexercicios.exercicios import registrar_exercicio as _registrar_exercicio
from cntexercicios.exercicios import ContadorExercicios

__all__ = ["contar_flexoes"]

class ContadorFlexoes(ContadorExercicios):
    """
    Contador de flexões em vídeos utilizando a classe ContadorExercicios como base
    """

    LIMIAR_EXERCICIO_MIN = 0.30
    LIMIAR_EXERCICIO_MAX = 0.40

    NOME_EXERCICIO = "flexões"

    def _calc_progresso_exercicio(self):
        """
        Calcula o progresso da flexão utilizando os pontos do corpo detectados pela classe base
        """
        # cálculo vetorial e algébrico
        import math
        import numpy as np

        # índices dos landmarks
        import mediapipe as mp
        landmark = mp.solutions.pose.PoseLandmark

        # posições do centro dos pés, da cintura e dos ombros (base do pescoço)
        pos_ombro_dir   = self._posicao_landmark(landmark.RIGHT_SHOULDER)
        pos_ombro_esq   = self._posicao_landmark(landmark.LEFT_SHOULDER)
        pos_cintura_dir = self._posicao_landmark(landmark.RIGHT_HIP)
        pos_cintura_esq = self._posicao_landmark(landmark.LEFT_HIP)
        pos_pe_dir      = self._posicao_landmark(landmark.RIGHT_HEEL)
        pos_pe_esq      = self._posicao_landmark(landmark.LEFT_HEEL)
        pos_pescoco     = ( pos_ombro_dir   + pos_ombro_esq   ) / 2
        pos_cintura     = ( pos_cintura_dir + pos_cintura_esq ) / 2
        pos_centro_pes  = ( pos_pe_dir      + pos_pe_esq      ) / 2

        # verificação se as pernas estão retas e o corpo está na horizontal
        vet_pes_pescoco = pos_pescoco - pos_centro_pes
        vet_pes_cintura = pos_cintura - pos_centro_pes
        dis_pes_pescoco = np.linalg.norm(vet_pes_pescoco)
        dis_pes_cintura = np.linalg.norm(vet_pes_cintura)

        # NOTE: o angulo é medido em relação ao eixo y dos frames
        #       e o produto vetorial está normalizado (entre -1 e 1)
        prod_vet = np.dot(vet_pes_pescoco, vet_pes_cintura) / (dis_pes_pescoco * dis_pes_cintura)
        angulo   = np.degrees(np.fabs(np.arctan2(vet_pes_pescoco[0], vet_pes_pescoco[1])))
        if prod_vet > 0.9 and 60 < angulo < 120:
            # verificação se a distância entre as mãos e os pés é próxima
            # da distância entre os pés e a base do pescoço
            pos_pulso_dir     = self._posicao_landmark(landmark.RIGHT_WRIST)
            pos_pulso_esq     = self._posicao_landmark(landmark.LEFT_WRIST)
            pos_centro_pulsos = ( pos_pulso_dir + pos_pulso_esq ) / 2

            vet_pes_pulsos = pos_centro_pulsos - pos_centro_pes
            dis_pes_pulsos = np.linalg.norm(vet_pes_pulsos)

            # NOTE: talvez seja necessário limitar a diferença com um valor menor
            if math.fabs(dis_pes_pulsos - dis_pes_pescoco) < (dis_pes_pulsos + dis_pes_pescoco) / 2:
                # aproximação da altura da flexão normalizada em relação a altura aproximada da pessoa
                # (distância entre os pés e a base do pescoço)
                h_flexao = (np.linalg.norm(pos_centro_pulsos - pos_pescoco) /
                    np.linalg.norm(pos_pescoco - pos_centro_pes))

                return h_flexao, True

        return 0, False

@_registrar_exercicio("flexões")
def contar_flexoes(video):
    """
    Instancia a classe ContadorFlexoes para contagem de flexões
    no vídeo fornecido e inicia a contagem imediatamente
    """
    contador = ContadorFlexoes(video, titulo="Resultado")
    contador.contar()
