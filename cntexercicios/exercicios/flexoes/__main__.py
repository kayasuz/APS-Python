"""
Módulo para a contagem de exercícios do tipo "flexão" diretamente pela linha de comando,
aceita tanto arquivos de vídeo ou índices de dispositivo de captura de vídeo como parâmetro

exemplo de usagem:
```
user@localhost: python -m cntexercicio.exercicios.flexao "Vídeos/Treino Flexões.mp4"
```
"""

if __name__ != "__main__":
    raise ImportError("esse módulo não deve ser importado diretamente")

# biblioteca padrão
import sys, os

# contador a ser executado
from cntexercicios.exercicios.flexoes import contar_flexoes

# mostra a ajuda caso necessário
if len(sys.argv) != 2:
    print(
        f"usagem: python -m cntexercicios.exercicios.flexao (arquivo ou índice de dispositivo)\n\n"
         "abre o arquivo de vídeo ou dispositivo indicado\n"
         "por seu índice e conta as flexões"
    )
    exit(1)

# processa o argumento de entrada (arquivo ou índice de dispositivo de vídeo)
try:
    arquivo = int(sys.argv[1])
except ValueError:
    arquivo = os.path.abspath(sys.argv[1])

# checa se o arquivo está correto
if isinstance(arquivo, str):
    if not os.path.exists(arquivo):
        print(f"erro: '{arquivo}' não pode ser encontrado", file=sys.stderr)
    if not os.path.isfile(arquivo):
        print(f"erro: '{arquivo}' não é um arquivo", file=sys.stderr)

# contagem das flexões
contar_flexoes(arquivo)

