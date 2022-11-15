"""
Módulo contendo um contador de exercícios para a contagem de polichinelos,
é recomendado que não se utilize a função de contagem ou a classe do
contador de flexões diretamente, mas sim as funções do módulo
cntexercicios.exercicios para executar a função indiretamente,
ou instanciar a classe do contador de flexões
"""

# biblioteca do programa
from cntexercicios.exercicios import ContadorExercicios

__all__ = ["ContadorPolichinelos"]

class ContadorPolichinelos(ContadorExercicios):
    """
    Contador de polichinelos em vídeos utilizando a classe ContadorExercicios como base
    """

    LIMIAR_EXERCICIO_MIN = 0.25
    LIMIAR_EXERCICIO_MAX = 0.75

    NOME_EXERCICIO = "polichinelos"

    def _calc_progresso_exercicio(self):
        """
        Calcula o progresso do polichinelo utilizando os pontos do corpo detectados pela classe base
        """
        # cálculo vetorial e algébrico
        import math
        import numpy as np

        # índices dos landmarks
        import mediapipe as mp
        landmark = mp.solutions.pose.PoseLandmark

        # posições dos pés, da cintura e dos ombros (base do pescoço)
        pos_ombro_dir   = self._posicao_landmark(landmark.RIGHT_SHOULDER)
        pos_ombro_esq   = self._posicao_landmark(landmark.LEFT_SHOULDER)
        pos_cintura_dir = self._posicao_landmark(landmark.RIGHT_HIP)
        pos_cintura_esq = self._posicao_landmark(landmark.LEFT_HIP)
        pos_pe_dir      = self._posicao_landmark(landmark.RIGHT_HEEL)
        pos_pe_esq      = self._posicao_landmark(landmark.LEFT_HEEL)
        pos_pulso_dir   = self._posicao_landmark(landmark.RIGHT_WRIST)
        pos_pulso_esq   = self._posicao_landmark(landmark.LEFT_WRIST)
        pos_pescoco     = ( pos_ombro_dir   + pos_ombro_esq   ) / 2
        pos_cintura     = ( pos_cintura_dir + pos_cintura_esq ) / 2

        # verificação se as pernas estão abaixo da cintura e o corpo está na vertical
        vet_cintura_pe_dir    = pos_cintura_dir - pos_pe_dir
        vet_cintura_pe_esq    = pos_cintura_esq - pos_pe_esq
        vet_cintura_ombro_dir = pos_cintura_dir - pos_ombro_dir
        vet_cintura_ombro_esq = pos_cintura_esq - pos_ombro_esq
        vet_cintura_pescoco = pos_pescoco - pos_cintura
        # NOTE: o angulo é medido em relação ao eixo y dos frames
        #       e o produto vetorial está normalizado (entre -1 e 1)
        angulo = np.degrees(np.fabs(np.arctan2(vet_cintura_pescoco[0], vet_cintura_pescoco[1])))
        if (np.dot(vet_cintura_pe_esq, vet_cintura_ombro_esq) > 0 or
            np.dot(vet_cintura_pe_dir, vet_cintura_ombro_dir) > 0 or
            np.abs(angulo) > 15):
            return 0, False

        # cálculo da normal do torso
        vet_cintura_esq_dir_norm    = pos_cintura_dir - pos_cintura_esq
        vet_ombro_dir_esq_norm      = pos_ombro_esq - pos_ombro_dir
        vet_cintura_ombro_dir_norm  = vet_cintura_ombro_dir.copy()
        vet_ombro_cintura_esq_norm  = -vet_cintura_ombro_esq.copy()
        vet_cintura_esq_dir_norm   /= np.linalg.norm(vet_cintura_esq_dir_norm)
        vet_ombro_dir_esq_norm     /= np.linalg.norm(vet_ombro_dir_esq_norm)
        vet_cintura_ombro_dir_norm /= np.linalg.norm(vet_cintura_ombro_dir_norm)
        vet_ombro_cintura_esq_norm /= np.linalg.norm(vet_ombro_cintura_esq_norm)
        norm_torso = (
            np.cross(vet_cintura_esq_dir_norm, vet_cintura_ombro_dir_norm) +
            np.cross(vet_ombro_dir_esq_norm, vet_ombro_cintura_esq_norm)
        ) / 2
        norm_torso /= np.linalg.norm(norm_torso)

        # comprimento e vetores normalizados das pernas
        mag_cintura_pe_dir = np.linalg.norm(vet_cintura_pe_dir)
        mag_cintura_pe_esq = np.linalg.norm(vet_cintura_pe_esq)
        vet_cintura_pe_dir_norm = vet_cintura_pe_dir / mag_cintura_pe_dir
        vet_cintura_pe_esq_norm = vet_cintura_pe_esq / mag_cintura_pe_esq

        # verificação se as pernas estão no plano correto
        sin30 = np.sin(np.pi / 3)
        epsilon = np.finfo(np.float64).eps
        if ((sin30 - np.abs(np.linalg.norm(np.cross(norm_torso, vet_cintura_pe_esq_norm)) - 1) < epsilon) and
            (sin30 - np.abs(np.linalg.norm(np.cross(norm_torso, vet_cintura_pe_dir_norm)) - 1) < epsilon)):
            return 0, False

        # comprimento e vetores normalizados dos braços
        vet_ombro_pulso_dir = pos_pulso_dir - pos_ombro_dir
        vet_ombro_pulso_esq = pos_pulso_esq - pos_ombro_esq
        mag_ombro_pulso_dir = np.linalg.norm(vet_ombro_pulso_dir)
        mag_ombro_pulso_esq = np.linalg.norm(vet_ombro_pulso_esq)
        vet_ombro_pulso_dir_norm = vet_ombro_pulso_dir / mag_ombro_pulso_dir
        vet_ombro_pulso_esq_norm = vet_ombro_pulso_esq / mag_ombro_pulso_esq

        # verificação se os braços estão no plano correto
        if ((sin30 - np.abs(np.linalg.norm(np.cross(norm_torso, vet_ombro_pulso_esq_norm)) - 1) < epsilon) and
            (sin30 - np.abs(np.linalg.norm(np.cross(norm_torso, vet_ombro_pulso_dir_norm)) - 1) < epsilon)):
            return 0, False

        # cálculo da angulo de abertura dos braços e entre as pernas
        angulo_pernas    = np.arccos(np.dot(vet_cintura_pe_dir_norm, vet_cintura_pe_esq_norm))
        angulo_braco_dir = np.arccos(+np.dot(vet_ombro_pulso_dir_norm, vet_cintura_ombro_dir_norm))
        angulo_braco_esq = np.arccos(-np.dot(vet_ombro_pulso_esq_norm, vet_ombro_cintura_esq_norm))

        # normalização e combinação dos fatores para um intervalo entre -1 e 1
        z = 2 * (np.clip(6 * angulo_pernas / np.pi, -1, 1) + (angulo_braco_dir + angulo_braco_esq) / np.pi) / 3 - 1

        # 'smooth-step' normalizado do resultado
        z = np.arctan(z) / np.arctan(1)

        # mapeamento de [-1,1] para [0,1]
        return (z + 1) / 2, True
