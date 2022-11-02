
# importa as funções de registro e listagem de exercícios
from package.exercicios import _registro
from package.exercicios._registro import *

# funções de registro acessíveis via "from module import *"
__all__ = [*_registro.__all__]

# import dos exercícios
# NOTE: não mova os imports pra antes dos imports
#       das funções de registro de exercícios,
#       isso causará um erro de import circular
from package.exercicios import flexoes

# módulos dos exercícios acessíveis via "from module import *"
__all__.extend(["flexoes"])

# modulo interno com as funções já importadas,
# seguro de remover a referência
del _registro

