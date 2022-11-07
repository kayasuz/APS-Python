"""
Aviso: esso módulo foi depreciado e será removido em uma versão futura,
a nova classe ContadorExercicios do módulo cntexercicios.exercicios deverá
ser usada na implementação de contadores de exercícios de agora em diante

Módulo interno para o registro, listagem e execução de contadores de exercícios,
não deve ser importado diretamente, ao invés disso use o módulo cntexercicios.exercicios
que importa as funções desse módulo para que elas sejam usadas pelo resto da biblioteca

Contém funções para registrar contadores de exercícios com base
no nome do exercício, listagem dos nomes de exercícios já registrados,
e execução dos contadores apenas com o nome do exercício, sem precisar
saber o nome da função ou o módulo onde ela reside
"""

__exercicios = {}

__all__ = []
def exportar(funcao):
    global __all__
    __all__.append(funcao.__name__)
    return funcao

@exportar
def registrar_exercicio(nome_exercicio):
    """
    Aviso: essa função foi depreciada em favor da implementação de uma classe
    contadora de exercícios, que deverá herdar a classe ContadorExercicios.
    Suporte à contagem de exercícios baseada em funções será removido
    em uma versão futura

    Registra a função seguinte como um contador de exercício usando
    um decorador, o parâmetro deve ser o nome do exercício e a função
    retornada deve ser chamada no contador de exercício

    exemplo:
    ```
    @registrar_exercicio("polichinelo")
    def contar_polichinelos(video):
        ... implementação ...
    ```

    """

    if nome_exercicio in __exercicios:
        raise RuntimeError(f"um exercício com o nome '{nome_exercicio}' já foi registrado")

    # cria e retorna o decorador
    def decorador(funcao):
        global __exercicios
        __exercicios[nome_exercicio] = funcao

        # aviso de depreciação (será removido no release após o release atual)
        import warnings
        warnings.warn(
            "funções de contagem estão sendo depreciadas e não vão ser mais suportadas, "
            "uma subclasse da classe ContadorExercicios deve ser implementada ao invés disso",
            DeprecationWarning, stacklevel=2
        )
        return funcao

    return decorador

@exportar
def listar_exercicios():
    """
    Retorna uma lista dos nomes de exercícios conhecidos, sejam eles registrados
    pela própria biblioteca, ou por qualquer código que use ela e queira definir
    um novo contador
    """
    return list(__exercicios.keys())

@exportar
def contar_exercicios(exercicio, video):
    """
    Aviso: essa função foi depreciada em favor da utilização de contadores
    de exercícios implementados como classes, que devem herdar a classe
    ContadorExercicios. Suporte à contagem de exercícios baseada em funções
    será removido em uma versão futura

    Conta a quantidade de exercícios do tipo feitos no vídeo fornecido

    O exercício passado pelo parâmetro "exercicio" deve ser um nome de exercício
    conhecido previamente registrado usando o decorador registrar_exercicios
    (presente no módulo cntexercicios.exercicios), e o vídeo passado pelo parâmetro
    "video" deve ser um nome de arquivo de vídeo ou um número não negativo representando
    um índice de dispositivo de captura de vídeo

    Pode gerar uma exceção do tipo ValueError caso o exercício não seja conhecido,
    ou uma exceção do tipo RuntimeError caso o contador de exercícios gere uma exceção
    """

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

# evite que essa variável seja importada
# acidentalmente por outros módulos
del exportar

