"""
Módulo contendo os contadores de exercícios dentro de seus próprios módulos
e funções para listagem dos contadores conhecidos, registro de novos contadores
e execução dos contadores de exercícios pelo nome do exercício
"""

from abc import ABC, abstractmethod

import cv2

class ContadorExercicios(ABC):

    registro = {}

    LIMIAR_EXERCICIO_MIN = 0.25
    LIMIAR_EXERCICIO_MAX = 0.75

    FONTE_PADRAO = cv2.FONT_HERSHEY_SIMPLEX

    def __init_subclass__(cls, *args, **kwargs):
        # previne herança em classes sem um nome de exercício
        if not hasattr(cls, "NOME_EXERCICIO"):
            raise TypeError(
                f"a classe {cls.__qualname__} não pode herdar ContadorExercicios, "
                "atributo 'NOME_EXERCICIO' não definido"
            )

        # previne registro de duas classes para contar o mesmo exercício
        if cls.NOME_EXERCICIO in ContadorExercicios.registro:
            raise AttributeError(
                f"a classe {cls.__qualname__} não pode herdar ContadorExercicios, "
                f"o atributo '' define um exercício já registrado: {cls.NOME_EXERCICIO}"
            )

        # inicializa e registra a subclasse do contador
        super().__init__(cls, *args, **kwargs)
        ContadorExercicios.registro[cls.NOME_EXERCICIO] = cls

    def __init__(self, video, titulo=None):
        if titulo is None:
            titulo = "Contador"
        elif not isinstance(titulo, str):
            raise TypeError(f"esperado str ou None para 'titulo', recebido tipo {type(titulo).__qualname__}")
        elif len(titulo) == 0:
            raise ValueError("'titulo' não pode ser uma string vazia")

        # imports locais
        import mediapipe as mp

        # atributos genéricos
        self._titulo = titulo
        self._video  = video

        # atributos relacionado as poses
        self._pose = mp.solutions.pose.Pose(
            min_tracking_confidence=0.5,
            min_detection_confidence=0.5
        )
        self._corpo = None
        self._pontos = None

        # atributos de renderização do texto
        self._fonte          = cv2.FONT_HERSHEY_SIMPLEX
        self._tamanho_fonte  = 1
        self._cor_fonte      = (255, 200, 255)
        self._grossura_fonte = 3

        # atributos de contagem de exercícios
        self._contagem = 0
        self._estado_exercicio = False

    def contar(self):
        from cntexercicios.video import abrir_video, extrair_frames

        # processa os frames do vídeo, contando o exercício
        with abrir_video(self._video) as captura:
            for frame in extrair_frames(captura):
                self._detectar_corpo(frame)
                # detecta a transição entre estados do exercício,
                # aumentando a contagem dele em cada ciclo completo
                self._contar_exercicio()
                self._renderizar_janela(frame)
                self._processar_eventos()
                # verifica se o usuário fechou a janela
                if self._janela_fechada():
                    break

        # retorne o resultado
        return self._contagem

    def _detectar_corpo(self, frame):
        # processamento dos pontos do corpo humano
        self._corpo  = self._pose.process(frame)
        self._pontos = self._corpo.pose_landmarks

    def _posicao_landmark(self, landmark):
        # retorna a posição do ponto como array
        import numpy as np
        ponto = self._pontos.landmark[landmark]
        return np.array((ponto.x, 1-ponto.y, ponto.z))

    def _contar_exercicio(self):
        # evita contar exercícios caso um corpo não seja detectado
        if not self._pontos:
            return

        # cálcula o progresso do exercício
        progresso, valido = self._calc_progresso_exercicio()

        # previne a contagem se o exercício não estiver sendo feito corretamente
        if not valido:
            return

        # conta o exercicio com base em seu progresso
        if not self._estado_exercicio:
            if progresso < self.LIMIAR_EXERCICIO_MIN:
                self._estado_exercicio = True
                self._contagem += 1
        elif progresso > self.LIMIAR_EXERCICIO_MAX:
            self._estado_exercicio = False

    def _renderizar_janela(self, frame):
        # renderização de textos
        cv2.putText(frame, f"Contagem: {self._contagem}", (40, 50),
            self._fonte, self._tamanho_fonte, self._cor_fonte, self._grossura_fonte)

        # renderização da janela
        cv2.imshow(self._titulo, frame)

    def _processar_eventos(self):
        tecla = cv2.waitKey(2)

    def _janela_fechada(self):
        if cv2.getWindowProperty(self._titulo, cv2.WND_PROP_VISIBLE) < 1:
            return True
        else:
            return False

    @abstractmethod
    def _calc_progresso_exercicio(self, frame):
        pass

def listar_contadores():
    """
    Retorna uma lista dos nomes de exercícios conhecidos que possuem uma classe contadora,
    ou seja, uma subclasse da classe ContadorExercicios que implemente a contagem de um
    determinado tipo de exercício físico
    """
    return list(ContadorExercicios.registro.keys())

def buscar_contador(exercicio):
    """
    Procura nas subclasses da classe ContadorExercicios uma classe que implemente o contador
    para o exercício físico especificado, retornando None caso a classe não seja encontrada
    """
    return ContadorExercicios.registro.get(exercicio, None)

def instanciar_contador(exercicio, *args, **kwargs):
    """
    Cria uma nova instância de contador para o exercício físico especificado, usa internamente
    a função buscar_contador para procurar a classe que implementa o contador desejado
    """
    classe = buscar_contador(exercicio)
    if classe is None:
        raise ValueError(f"contador para o tipo de exercício '{exercicio}' não encontrado")

    return classe(*args, **kwargs)

# importa as funções de registro e listagem de exercícios
from cntexercicios.exercicios import _registro
from cntexercicios.exercicios._registro import *

# funções de registro acessíveis via "from module import *"
__all__ = ["ContadorExercicios", *_registro.__all__]

# import dos exercícios
# NOTE: não mova os imports pra antes dos imports
#       das funções de registro de exercícios,
#       isso causará um erro de import circular
from cntexercicios.exercicios import flexoes

# módulos dos exercícios acessíveis via "from module import *"
__all__.extend(["flexoes"])

# modulo interno com as funções já importadas,
# seguro de remover a referência
del _registro

