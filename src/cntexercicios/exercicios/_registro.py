
__exercicios = {}

__all__ = []
def exportar(funcao):
    global __all__
    __all__.append(funcao.__name__)
    return funcao

@exportar
def registrar_exercicio(nome_exercicio):
    """
    registra a função seguinte como um contador de exercício
    usando um decorador, o parâmetro deve ser o nome do exercício,
    e a função retornada deve ser chamada no contador de exercício

    exemplo:

    @registrar_exercicio("polichinelo")
    def contar_polichinelos(video):
        ... implementação ...

    """

    if nome_exercicio in __exercicios:
        raise RuntimeError(f"um exercício com o nome '{nome_exercicio}' já foi registrado")

    # cria e retorna o decorador
    def decorador(funcao):
        global __exercicios
        __exercicios[nome_exercicio] = funcao
        return funcao

    return decorador

@exportar
def listar_exercicios():
    """
    retorna uma lista de exercícios conhecidos
    """
    return list(__exercicios.keys())

@exportar
def contar_exercicios(exercicio, video):
    # checagem de tipos
    if not isinstance(exercicio, str):
        raise TypeError("esperado uma str para o parâmetro 'exercicio', "
                        f"recebido um valor do tipo {type(exercicio).__qualname__}")
    if not isinstance(video, (str, int)):
        raise TypeError("esperado uma str ou int para o parâmetro 'video', "
                        f"recebido um valor do tipo {type(exercicio).__qualname__}")

    # checagem de valor
    if isinstance(video, int) and video < 0:
        raise ValueError(f"o parâmetro 'video' não pode ser um número negativo")

    # contador do exercício
    try:
        contador = __exercicios[exercicio]
    except KeyError:
        raise ValueError("exercício desconhecido: '{exercicio}'") from None

    # contagem do exercício
    try:
        contador(video)
    except Exception as error:
        # formata o tipo de vídeo de entrada
        if isinstance(video, str):
            repr_video = "o arquivo '{video}'"
        elif isinstance(video, int):
            repr_video = "o dispositivo com índice {video}"

        # gera uma exceção com 'error' como causa
        raise RuntimeError("falha ao contar o exercício '{}' usando {repr_video} como entrada") from error

# limpeza
del exportar

