"""
Módulo contendo os contadores de exercícios dentro de seus próprios módulos
e funções para listagem dos contadores conhecidos, registro de novos contadores
e execução dos contadores de exercícios pelo nome do exercício
"""

# importa as funções de registro e listagem de exercícios
from cntexercicios.exercicios import _registro
from cntexercicios.exercicios._registro import *

# funções de registro acessíveis via "from module import *"
__all__ = [*_registro.__all__]

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

