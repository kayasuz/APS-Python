"""
Módulo contendo os contadores de exercícios dentro de seus próprios módulos,
funções para listagem, busca e instanciação de contadores de exercícios,
e classes base para criação de novos contadores.

NOTA: As funções antigas de listagem, registro e execução de contadores
      de exercícios baseados em funções ainda estão presentes nesse módulo,
      mas foram depreciadas e serão removidas na próxima versão. Não utilize
      elas em código novo.
"""

from abc import ABC, abstractmethod

import cv2

class ContadorExercicios(ABC):
    """
    Classe base abstrata para a implementação de classes contadoras de exercícios,
    com os requisitos mínimos de implementar a função _calc_progresso_exercicio,
    utilizada para saber o progresso de um exercício físico em um vídeo, e declaração
    do atributo de classe "NOME_EXERCICIO" contendo o nome do exercício contado
    pela classe
    """

    # registro de subclasses associadas a cada exercício
    registro = {}

    LIMIAR_EXERCICIO_MIN = 0.25
    LIMIAR_EXERCICIO_MAX = 0.75

    # índices dos filtros de vídeo para aplicação deles em ordem crescente
    FILTRO_NITIDEZ_IDX = 0
    FILTRO_GAUSS_IDX   = 1
    FILTRO_BORDAS_IDX  = 2

    # constantes para especificar o alinhamento de textos na renderização
    ALINHAR_ESQUERDA = 1
    ALINHAR_CENTRO   = 2
    ALINHAR_DIREITA  = 3
    ALINHAR_INFERIOR = 0
    ALINHAR_SUPERIOR = 4

    # constantes auxiliares para verificar valores de alinhamentos
    # ou extrair o alinhamento vertical e horizontal
    MASCARA_ALINHAMENTO_VERTICAL   = ALINHAR_SUPERIOR
    MASCARA_ALINHAMENTO_HORIZONTAL = (
        ALINHAR_ESQUERDA | ALINHAR_CENTRO | ALINHAR_DIREITA
    )
    MASCARA_ALINHAMENTO = MASCARA_ALINHAMENTO_HORIZONTAL | MASCARA_ALINHAMENTO_VERTICAL

    # constantes que afetam a aparência dos textos
    ESPACAMENTO_LINHA = 10
    FONTE_PADRAO = cv2.FONT_HERSHEY_SIMPLEX

    def __init_subclass__(cls, *args, **kwargs):
        """
        Registra novas classes de contagem de exercícios pela detecção da herança
        """
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
        """
        Cria um contador de exercícios para a contagem no vídeo fornecido pelo parâmetro "video",
        o título da janela mostrando o vídeo pode ser passado pelo parâmetro "título", NÃO UTILIZE
        títulos com acentuação, isso pode fazer com que a janela não seja criada e o contador falhe
        """

        # checagem de parâmetros
        if titulo is None:
            titulo = "Contador"
        elif not isinstance(titulo, str):
            raise TypeError(f"esperado str ou None para 'titulo', recebido tipo {type(titulo).__qualname__}")
        elif len(titulo) == 0:
            raise ValueError("'titulo' não pode ser uma string vazia")

        # imports locais
        import mediapipe as mp

        # atributos genéricos
        self._titulo         = titulo
        self._video          = video
        self._pausa          = False
        self._ajuda          = False
        self._mostrar_pontos = False
        self._frame          = None

        # atributos relacionados aos filtros
        from cntexercicios.filtros import kernel_nitidez, kernel_gauss, kernel_deteccao_borda
        self._filtros          = [None] * 3
        self._filtros_ativos   = [False] * 3
        self._filtro_contraste = False
        self._mostrar_filtro   = False

        # parâmetros dos filtros
        self._peso  = 0.5
        self._sigma = 1

        # configura os filtros
        self._filtros[self.FILTRO_NITIDEZ_IDX] = kernel_nitidez(peso=self._peso)
        self._filtros[self.FILTRO_GAUSS_IDX]   = kernel_gauss(3, sigma=self._sigma)
        self._filtros[self.FILTRO_BORDAS_IDX]  = kernel_deteccao_borda()

        # atributos relacionado as poses
        self._pose = mp.solutions.pose.Pose(
            min_tracking_confidence=0.5,
            min_detection_confidence=0.5
        )
        self._corpo = None
        self._pontos = None

        # atributos de renderização do texto
        self._fonte          = cv2.FONT_HERSHEY_SIMPLEX
        self._tamanho_fonte  = 0.60
        self._cor_fonte      = (0, 0, 0)
        self._grossura_fonte = 2

        # atributos de contagem de exercícios
        self._contagem = 0
        self._estado_exercicio = False

    def contar(self):
        """
        Faz a contagem dos exercícios no vídeo, chamando funções internas para
        detectar o corpo da pessoa, contar o exercício, renderizar a janela,
        processar eventos e detectar quando a janela é fechada
        """
        from cntexercicios.video import abrir_video, extrair_frames

        # processa os frames do vídeo, contando o exercício
        with abrir_video(self._video) as captura:
            frame_gen = extrair_frames(captura)

            while True:
                if self._pausa:
                    frame = self._frame
                else:
                    try:
                        frame = next(frame_gen)
                    except StopIteration:
                        break
                    else:
                        self._frame = frame

                # aplica os filtros ativos no frame
                frame_filtrado = self._aplicar_filtros(frame)
                # faz a detecção do corpo da pessoa presente no vídeo
                self._detectar_corpo(frame_filtrado)
                # detecta a transição entre estados do exercício,
                # aumentando a contagem dele em cada ciclo completo
                self._contar_exercicio()
                if self._mostrar_filtro:
                    self._renderizar_janela(frame_filtrado)
                else:
                    self._renderizar_janela(frame)

                self._processar_eventos()
                # verifica se o usuário fechou a janela
                if self._janela_fechada():
                    break

        # retorne o resultado
        return self._contagem

    def _aplicar_filtros(self, frame):
        # coleta os filtros a serem aplicados
        indices = [idx for idx, ativo in enumerate(self._filtros_ativos) if ativo]
        filtros = [self._filtros[idx] for idx in indices]

        # aplica o filtro de contraste primeiro
        if self._filtro_contraste:
            from cntexercicios.filtros import melhorar_contraste
            frame = melhorar_contraste(frame)

        # aplica os filtros ativos em sequência
        if filtros:
            from cntexercicios.filtros import convolucao
            for kernel in filtros:
                frame = convolucao(frame, kernel)

        # retorna o frame filtrado
        return frame

    def _detectar_corpo(self, frame):
        """
        Utiliza a biblioteca mediapipe para detecção dos pontos do corpo
        da pessoa presente no frame fornecido, salvando eles no contador
        """
        # processamento dos pontos do corpo humano
        if not self._pausa or self._corpo is None:
            self._corpo  = self._pose.process(frame)
            self._pontos = self._corpo.pose_landmarks

    def _posicao_landmark(self, landmark):
        # retorna a posição do ponto como array
        import numpy as np
        ponto = self._pontos.landmark[landmark]
        return np.array((ponto.x, 1-ponto.y, ponto.z))

    def _contar_exercicio(self):
        """
        Faz a contagem dos exercícios utilizando a função de cálculo do progresso
        do exercício para detectar a transição de estados no exercício
        """
        # evita contar exercícios caso um corpo não seja detectado
        if not self._pontos:
            return

        # calcula o progresso do exercício
        progresso, valido = self._calc_progresso_exercicio()

        # previne a contagem se o exercício não estiver sendo feito corretamente
        if not valido:
            return

        # conta o exercício com base em seu progresso
        if not self._estado_exercicio:
            if progresso < self.LIMIAR_EXERCICIO_MIN:
                self._estado_exercicio = True
                self._contagem += 1
        elif progresso > self.LIMIAR_EXERCICIO_MAX:
            self._estado_exercicio = False

    def _renderizar_texto(self, frame, posicao, texto, alinhamento=None):
        # checagem dos parâmetros
        try:
            x, y = posicao
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError
            if x < 0 or y < 0:
                raise ValueError
        except ValueError:
            raise ValueError("'posicao' deve conter dois números inteiros não negativos") from None

        if not isinstance(texto, str):
            raise TypeError(
                f"esperado str para o parâmetro 'texto', recebido tipo {type(texto).__qualname__}"
            )

        if alinhamento is None:
            alinhamento = self.ALINHAR_DIREITA | self.ALINHAR_INFERIOR
        elif not isinstance(alinhamento, int):
            raise TypeError(
                "esperado int ou None para o parâmetro 'alinhamento', "
                f"recebido tipo {type(alinhamento).__qualname__}"
            )
        elif (alinhamento & self.MASCARA_ALINHAMENTO) != alinhamento:
            raise ValueError("'alinhamento' deve ter uma constante de alinhamento válida")

        # alinhamento horizontal padrão
        if (alinhamento & self.MASCARA_ALINHAMENTO_HORIZONTAL) == 0:
            alinhamento |= self.ALINHAR_DIREITA

        # separação das linhas do texto e substituição de tabulações (tab)
        linhas = texto.expandtabs(4).split('\n')

        # cálculo do tamanho do texto e correção da posição com o alinhamento
        comprimento_texto = None
        alturas = []
        for linha in linhas:
            tamanho, _ = cv2.getTextSize(linha, self._fonte, self._tamanho_fonte, self._grossura_fonte)
            alturas.append(tamanho[1])
            if comprimento_texto is None or comprimento_texto < tamanho[0]:
                comprimento_texto = tamanho[0]

        alinhamento_horizontal = alinhamento & self.MASCARA_ALINHAMENTO_HORIZONTAL
        if alinhamento_horizontal == self.ALINHAR_ESQUERDA:
            x -= comprimento_texto
        elif alinhamento_horizontal == self.ALINHAR_CENTRO:
            x -= comprimento_texto // 2

        if (alinhamento & self.MASCARA_ALINHAMENTO_VERTICAL) == self.ALINHAR_SUPERIOR:
            # subtrai a altura da caixa de texto da posição y (coordenada de janela)
            y -= sum(alturas) + self.ESPACAMENTO_LINHA * (len(linhas) - 1)

        # ajuste da cor para o negativo dela quando o filtro de detecção de borda está
        # ativo (como o vídeo fica escuro com o filtro, uma fonte clara é mais visível)
        if not (self._filtros_ativos[self.FILTRO_BORDAS_IDX] and self._mostrar_filtro):
            cor_fonte = self._cor_fonte
        elif len(self._cor_fonte) == 3:
            cor_fonte = [255 - x for x in self._cor_fonte]
        else:
            cor_fonte = [255 - x for x in self._cor_fonte[:-1]] + [self._cor_fonte[-1]]

        # renderização
        for altura, linha in zip(alturas, linhas):
            cv2.putText(frame, linha, (x, y + altura), self._fonte, self._tamanho_fonte, cor_fonte, self._grossura_fonte)
            # ajuste da posição para a próxima linha
            y += altura + self.ESPACAMENTO_LINHA

    def _renderizar_janela(self, frame):
        """
        Renderiza a janela utilizando o frame fornecido como base,
        adicionando a contagem de exercícios a ele
        """
        # cópia para evitar que os filtros sejam aplicados ao texto
        frame = frame.copy()

        # renderização de textos
        h, w, *_ = frame.shape
        self._renderizar_texto(frame, (20, 20), f"Contagem: {self._contagem}")
        self._renderizar_texto(frame, (w - 20, 20), "h: ajuda", alinhamento=self.ALINHAR_ESQUERDA)

        # mostra cria e renderiza o texto de ajuda caso requisitado
        if self._ajuda:
            texto_esq = []
            texto_dir = [
                "j: mostrar pontos",
                "1: diminuir peso da nitidez  ",
                "2: aumentar peso da nitidez  ",
                "3: diminuir reducao de ruido  ",
                "4: aumentar reducao de ruido  "
            ]

            # linhas do texto exibido no canto inferior esquerdo
            if self._mostrar_filtro:
                texto_esq.append(f"* f: visualizar filtros")
            else:
                texto_esq.append(f"  f: visualizar filtros")
            if self._pausa:
                texto_esq.append(f"* p: pausar video")
            else:
                texto_esq.append(f"  p: pausar video")
            if self._filtro_contraste:
                texto_esq.append("* c: melhorar contraste")
            else:
                texto_esq.append("  c: melhorar contraste")

            for linha, idx_filtro in (
                ("n: melhoria de nitidez", self.FILTRO_NITIDEZ_IDX),
                ("g: reducao de ruido",    self.FILTRO_GAUSS_IDX),
                ("b: deteccao de bordas",  self.FILTRO_BORDAS_IDX)):
                if self._filtros_ativos[idx_filtro]:
                    linha = f"* {linha}"
                else:
                    linha = f"  {linha}"

                texto_esq.append(linha)

            # renderização dos textos de ajuda na tela
            self._renderizar_texto(frame, (20,     h - 20),
                '\n'.join(texto_esq), alinhamento=self.ALINHAR_SUPERIOR)
            self._renderizar_texto(frame, (w - 20, h - 20),
                '\n'.join(texto_dir), alinhamento=self.ALINHAR_SUPERIOR | self.ALINHAR_ESQUERDA)

        # renderiza os pontos do corpo
        if self._mostrar_pontos and self._pontos is not None:
            import mediapipe as mp
            mp.solutions.drawing_utils.draw_landmarks(
                frame, self._pontos, mp.solutions.pose.POSE_CONNECTIONS
            )

        # renderização da janela
        cv2.imshow(self._titulo, frame)

    def _processar_eventos(self):
        """
        Processa eventos de janela do OpenCV
        """
        tecla = (cv2.waitKey(2) & 0xFF)

        # pausa do vídeo
        if tecla in (ord("p"), ord("P"), ord(" ")):
            self._pausa = not self._pausa

        # mostra/oculta o texto de ajuda
        elif tecla in (ord("h"), ord("H")):
            self._ajuda = not self._ajuda
            print(f"texto de ajuda {'visivel' if self._ajuda else 'oculto'}")

        # ativa/desativa a visualização dos filtros
        elif tecla in (ord("f"), ord("F")):
            novo_estado = not self._mostrar_filtro
            self._mostrar_filtro = novo_estado
            print(f"visualização de filtros {'ativa' if novo_estado else 'inativa'}")

        # ativa/desativa a visualização dos pontos do corpo
        elif tecla in (ord("j"), ord("J")):
            novo_estado = not self._mostrar_pontos
            self._mostrar_pontos = novo_estado
            print(f"visualizacao de pontos {'ativa' if novo_estado else 'inativa'}")

        # ativa/desativa o filtro de melhoria contraste
        elif tecla in (ord("c"), ord("C")):
            novo_estado = not self._filtro_contraste
            self._filtro_contraste = novo_estado
            print(f"melhoria de contraste {'ativa' if novo_estado else 'inativa'}")

        # ativa/desativa o filtro de borrão gaussiano
        elif tecla in (ord("g"), ord("G")):
            novo_estado = not self._filtros_ativos[self.FILTRO_GAUSS_IDX]
            self._filtros_ativos[self.FILTRO_GAUSS_IDX] = novo_estado
            print(f"filtro gaussiano {'ativo' if novo_estado else 'inativo'}")

        # ativa/desativa o filtro de melhoria de nitidez
        elif tecla in (ord("n"), ord("N")):
            novo_estado = not self._filtros_ativos[self.FILTRO_NITIDEZ_IDX]
            self._filtros_ativos[self.FILTRO_NITIDEZ_IDX] = novo_estado
            print(f"realçamento de nitidez {'ativo' if novo_estado else 'inativo'}")

        # ativa/desativa o filtro de detecção de bordas
        elif tecla in (ord("b"), ord("B")):
            novo_estado = not self._filtros_ativos[self.FILTRO_BORDAS_IDX]
            self._filtros_ativos[self.FILTRO_BORDAS_IDX] = novo_estado
            print(f"deteção de bordas {'ativa' if novo_estado else 'inativa'}")

        # diminui o peso do kernel de nitidez
        elif tecla == ord("1"):
            from cntexercicios.filtros import kernel_nitidez
            self._peso = round(max(0, min(self._peso - 0.05, 1)), 3)
            print(f"nitidez (peso): {self._peso}")
            self._filtros[self.FILTRO_NITIDEZ_IDX] = kernel_nitidez(peso=self._peso)

        # aumenta o peso do kernel de nitidez
        elif tecla == ord("2"):
            from cntexercicios.filtros import kernel_nitidez
            self._peso = round(max(0, min(self._peso + 0.05, 1)), 3)
            print(f"nitidez (peso): {self._peso}")
            self._filtros[self.FILTRO_NITIDEZ_IDX] = kernel_nitidez(peso=self._peso)

        # diminui o desvio padrão do kernel de borragem gaussiana
        elif tecla == ord("3"):
            from cntexercicios.filtros import kernel_gauss
            self._sigma = round(max(0, min(self._sigma - 0.1, 10)), 2)
            print(f"gauss (sigma): {self._sigma}")
            self._filtros[self.FILTRO_GAUSS_IDX] = kernel_gauss(3, sigma=self._sigma)

        # aumenta o desvio padrão do kernel de borragem gaussiana
        elif tecla == ord("4"):
            from cntexercicios.filtros import kernel_gauss
            self._sigma = round(max(0, min(self._sigma + 0.1, 10)), 2)
            print(f"gauss (sigma): {self._sigma}")
            self._filtros[self.FILTRO_GAUSS_IDX] = kernel_gauss(3, sigma=self._sigma)

    def _janela_fechada(self):
        """
        Detecta se a janela foi fechada
        """
        if cv2.getWindowProperty(self._titulo, cv2.WND_PROP_VISIBLE) < 1:
            return True
        else:
            return False

    @abstractmethod
    def _calc_progresso_exercicio(self, frame):
        """
        Esse método deve ser implementado em subclasses para
        calcular o progresso entre estados do exercício sendo
        """
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
from cntexercicios.exercicios import flexoes, polichinelos

# módulos dos exercícios acessíveis via "from module import *"
__all__.extend(["flexoes"])

# modulo interno com as funções já importadas,
# seguro de remover a referência
del _registro

