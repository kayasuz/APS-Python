
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--tema", action="store", type="string",
    help="configura o tema a ser usado nas janelas de diálogo")

opcoes, argumentos = parser.parse_args()
if argumentos:
    parser.print_help()
    exit()

if opcoes.tema is not None and len(opcoes.tema) == 0:
    opcoes.tema = None

from cntexercicios.dialogos import selecao_exercicio, selecao_video
exercicio = selecao_exercicio(tema=opcoes.tema)
if exercicio is not None:
    print(f"exercíco: {exercicio}")
    video = selecao_video(tema=opcoes.tema)
else:
    video = None

if video is not None:
    if isinstance(video, int):
        print(f"video: dispositivo {video}")
    else:
        print(f"video: {video}")

    from cntexercicios.exercicios import contar_exercicios
    contar_exercicios(exercicio, video)

