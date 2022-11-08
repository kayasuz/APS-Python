"""
Módulo que pergunta ao usuário por meio de diálogos (janelas) o tipo de exercício
a ser contado e o arquivo ou dispositivo de vídeo que o contador usará para a contagem,
contando a quantidade de exercícios do tipo selecionado no vídeo quando a biblioteca é
executada como módulo pela linha de comando (exemplo: python -m cntexercicios)

Usa as funções do módulo cntexercicios.dialogos internamente para gerar os diálogos,
podendo receber um nome de tema do Ttk para ser usado nos diálogos pela linha de comando
através da opção "--tema". geralmente os temas clam, alt, default e classic são suportados,
e adicionalmente os temas winnative, vista e xpnative no windows dependendo da versão do
sistema, porém, não há garantia que todos esses temas existam ou que eles sejam os únicos
"""

# definição das opções de linha de comando
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--tema", action="store", type="string",
    help="configura o tema a ser usado nas janelas de diálogo")

# processamento das opções da linha de comando
opcoes, argumentos = parser.parse_args()
if argumentos:
    parser.print_help()
    exit()

# evite que uma string vazia seja passada como tema
if opcoes.tema is not None and len(opcoes.tema) == 0:
    opcoes.tema = None

# diálogo para seleção do exercício
from cntexercicios.dialogos import selecao_exercicio, selecao_video
exercicio = selecao_exercicio(tema=opcoes.tema)
if exercicio is not None:
    print(f"exercíco: {exercicio}")
    video = selecao_video(tema=opcoes.tema)
else:
    video = None

# diálogo para seleção do vídeo e contagem dos exercícios no vídeo
if video is not None:
    if isinstance(video, int):
        print(f"video: dispositivo {video}")
    else:
        print(f"video: {video}")

    from cntexercicios.exercicios import contar_exercicios
    contar_exercicios(exercicio, video)

