
from cntexercicios.dialogos import selecao_exercicio, selecao_video
exercicio = selecao_exercicio()
if exercicio is not None:
    print(f"exercíco: {exercicio}")
    video = selecao_video()
else:
    video = None

if video is not None:
    if isinstance(video, int):
        print(f"video: dispositivo {video}")
    else:
        print(f"video: {video}")

    from cntexercicios.exercicios import contar_exercicios
    contar_exercicios(exercicio, video)

