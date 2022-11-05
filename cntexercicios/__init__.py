"""
Biblioteca para contagem de exercícios físicos em vídeos, podendo contar exercícios
em arquivos de vídeo ou dispositivos de captura de vídeo como webcams

Os contadores estão disponíveis através do módulo "exercícios", que fornece funções
para listagem de exercícios que a biblioteca pode contar, contagem de exercícios em
vídeos usando o nome do exercício sem necessidade de usar o contador diretamente,
e registro de novos contadores caso uma aplicação deseje estender o número
de exercícios suportados

Além disso, fornece dois módulos auxiliares "vídeo" e "diálogos", o primeiro com
classes e funções para abertura de vídeos e extração de frames usando a biblioteca
cv2 (do pacote opencv-python) internamente, mas com sintaxe simples e fechamento
automático da captura de vídeo após sua utilização com gerenciadores de contexto
da classe ContextoVideoCapture. E o segundo com classes e funções para geração de
diálogos em tkinter para que o usuário forneça o tipo de exercício a ser contado
e o vídeo a ser utilizado para a contagem
"""

# import dos módulos comumente usados
from cntexercicios import exercicios

# modulos a serem importados com "from cntexercicios import *"
__all__ = ["exercicios", "dialogos"]
