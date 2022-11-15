"""
Módulo com funções e classes para auxiliar a entrada de vídeo e o processamento de seus frames
"""

import cv2

class ContextoVideoCapture:
    """
    Classe de suporte que abre o gerenciador de captura VideoCapture
    e fecha ele após o uso, implementando um gerenciador de contexto
    (usável com o "with statement").
    """

    def __init__(self, parametro):
        """
        Cria um gerenciador de contexto que abre e retorna uma captura de vídeo,
        fechando a captura automaticamente quando o contexto e terminado.

        O parâmetro 'parametro' é utilizado para abrir a captura de vídeo no
        vídeo especificado, e deve ser um caminho válido para um arquivo de vídeo
        ou um índice de dispositivo, fornecidos como string e int respectivamente
        """
        # NOTE: checagem adicional de bool necessária porque o
        #       isinstance(para, (int, str)) retorna True para
        #       valores do tipo bool
        if not isinstance(parametro, (int, str)) or isinstance(parametro, bool):
            raise TypeError(f"esperado int ou str para 'parâmetro', recebido tipo {type(parametro)}")

        self._parametro = parametro
        self._captura   = cv2.VideoCapture()

    def __enter__(self):
        """
        Função executada na entrada do gerenciador de contexto, tenta abrir o vídeo
        fornecido para captura, gerando uma exceção do tipo RuntimeError em caso de falha
        """
        # tenta abrir a captura de vídeo usando um arquivo
        # ou índice de dispositivo de captura (ex: webcam)
        captura, parametro = self._captura, self._parametro
        if not captura.open(parametro):
            # gera um erro de falha de abertura do arquivo ou índice de dispositivo
            if isinstance(parametro, str):
                raise RuntimeError(f"falha ao abrir o arquivo de vídeo '{parametro}'")
            else:
                # NOTE: assume que o tipo da variável self._parametro
                #       foi validada a ser uma string ou um int
                raise RuntimeError(f"falha ao abrir o dispositivo {parametro} para captura de vídeo")

        return captura

    def __exit__(self, *ignorado):
        """
        Função executada na saída do gerenciador de contexto, fecha a captura de vídeo
        aberta durante a entrada do contexto e propaga qualquer exceção gerada dentro
        do contexto.
        """
        # fecha a captura de vídeo se ela ainda estiver aberta
        captura = self._captura
        if captura.isOpened():
            captura.release()

def abrir_video(parametro):
    """
    Cria e retorna um gerenciador de contexto para a captura de vídeo
    a partir do arquivo ou índice de dispositivo fornecido. Caso não
    seja possível abrir o arquivo ou dispositivo, um erro do tipo
    RuntimeError será gerado.

    Retorna um objeto do tipo ContextoVideoCapture
    """
    return ContextoVideoCapture(parametro)

def extrair_frames(video_capture, preprocessamento=None):
    """
    Lê e retorna os frames do vídeo dado pelo parâmetro "video_capture"
    em forma de generator, opcionalmente processando cada um deles usando
    uma função, se fornecida, pelo parâmetro "preprocessamento", que deve
    aceitar um frame e retornar o frame processado.

    Aviso: tanto o frame retornado quanto o frame passado para a função de
    preprocessamento NÃO DEVEM SER MODIFICADOS, essa restrição está descrita
    na documentação da função VideoCapture.read do pyopencv e opencv-python
    (ambas fornecem "bindings" ao opencv)

    Aviso: não fecha automaticamente o vídeo fornecido,
    isso deve ser feito após a função caso for necessário
    """
    while True:
        # lê o próximo frame
        ret, frame = video_capture.read()
        if not ret:
            break

        # aplica o preprocessamento se requisitado
        if callable(preprocessamento):
            try:
                frame = preprocessamento(frame)
            except Exception as erro:
                # encapsula o erro em uma exceção RuntimeError
                raise RuntimeError("falha ao preprocessar frame") from erro
            if frame is None:
                raise RuntimeError("frame não retornado pela função de preprocessamento")

        # retorna o frame
        yield frame

