
# importação da biblioteca tkinter
try:
    import tkinter, tkinter.filedialog, tkinter.messagebox
    from tkinter import ttk
except ImportError:
    # python 2.x
    import Tkinter as tkinter
    import Tkinter.filedialog, Tkinter.messagebox
    del Tkinter

class DialogoSelecaoExercicio(tkinter.Frame):
    """
    Classe da janela de seleção do exercício a ser contado
    """

    def __init__(self, parent, *exercicios):
        super().__init__(parent)
        self.parent = parent
        self.exercicio_selecionado = None

        # cálculo da quantidade de linhas e colunas
        linhas, colunas = self._estimar_tamanho_grade_botoes(len(exercicios))

        # ajuste das colunas quando a janela for redimensionada
        for coluna in range(colunas):
            self.columnconfigure(coluna, weight=999, minsize=150)

        # criação dos botões para selecionar os exercícios a serem contados
        for indice, exercicio in enumerate(exercicios):
            # NOTE: o parâmetro "ex" é usado para evitar referenciar uma variável local,
            #       que quando alterada iria alterar a chamada da função lambda
            btn = tkinter.Button(self, text=exercicio,
                command=lambda *ignorado, ex=exercicio: self.selecionar_exercicio(ex)
            )

            # linha=quociente, coluna=resto
            linha, coluna = divmod(indice, colunas)
            btn.grid(row=linha, column=coluna, padx=10, pady=10, sticky=tkinter.EW)

    @staticmethod
    def _estimar_tamanho_grade_botoes(qtd_exercicios):
        """
        estima as dimensões da grade de botões dada uma quantidade de botões
        """
        # testa de 1 a 8 colunas (ou até a quantidade de exercícios),
        # retornando as dimensões que minimizam espaços em branco
        import math
        sobra_minima   = None
        tamanho_minimo = None
        for colunas in range(1, min(qtd_exercicios, 8)+1):
            linhas   = int(math.ceil(qtd_exercicios / colunas))
            sobrando = linhas * colunas - qtd_exercicios
            # atualiza o tamanho mínimo que minimiza os espaços em branco
            if sobrando < 0:
                raise RuntimeError("erro de cálculo")
            if sobra_minima is None or sobra_minima > sobrando:
                sobra_minma    = sobrando
                tamanho_minimo = (linhas, colunas)

        if tamanho_minimo is not None:
            return tamanho_minimo
        else:
            return (0,0)

    def selecionar_exercicio(self, exercicio):
        """
        seleciona o exercício a ser contado
        """
        self.exercicio_selecionado = exercicio
        self.fechar()

    def fechar(self, evento=None):
        """
        fecha a janela principal
        """
        self.parent.destroy()

class DialogoSelecaoVideo(tkinter.Frame):
    """
    Classe para seleção da entrada de vídeo a ser usado para contar os exercícios
    """

    def __init__(self, parent):
        super().__init__(parent, borderwidth=4, relief="raised")
        self.parent = parent
        self.video  = None

        self._var_arquivo_str     = tkinter.StringVar(parent)
        self._var_dispositivo_str = tkinter.StringVar(parent)
        self._var_tipo_entrada    = tkinter.IntVar(parent, 0)

        # frames
        self._frame_interno           = tkinter.Frame(self)
        self._frame_entradas          = tkinter.Frame(self._frame_interno)
        self._frame_video_arquivo     = tkinter.Frame(self._frame_entradas)
        self._frame_video_dispositivo = tkinter.Frame(self._frame_entradas)
        self._frame_espacamento_label = tkinter.Frame(self._frame_video_arquivo, width=15)

        # radiobuttons
        from functools import partial
        comando_radiobtn = partial(self._on_mudanca_tipo_entrada, self)
        self._radiobtn_video_arquivo = tkinter.Radiobutton(
            self._frame_entradas, text="arquivo", variable=self._var_tipo_entrada,
            value=0, command=comando_radiobtn
        )
        self._radiobtn_video_dispositivo = tkinter.Radiobutton(
            self._frame_entradas, text="dispositivo", variable=self._var_tipo_entrada,
            value=1, command=comando_radiobtn
        )

        # entrada do índice de dispositivo de vídeo
        callback_validacao = parent.register(self._validar_indice_dispositivo)
        self._entrada_video_indice = tkinter.Entry(
            self._frame_video_dispositivo, validate="key", validatecommand=(callback_validacao, "%P"),
            textvariable=self._var_dispositivo_str
        )

        # entrada de vídeo como arquivo
        self._btn_abrir_arquivo = tkinter.Button(
            self._frame_video_arquivo, text="Abrir...", command=self._abrir_arquivo
        )
        self._label_arquivo = tkinter.Label(
            self._frame_video_arquivo, width=50, justify="right", anchor="w"
        )

        # botão de conclusão
        self._btn_concluir = tkinter.Button(
            self._frame_interno, text="Concluir", command=self._concluir
        )

        # posição dos widgets
        self._entrada_video_indice.pack(anchor="e", expand=True, fill="x", side="left")
        self._btn_abrir_arquivo.pack(anchor="w", side="left")
        self._frame_espacamento_label.pack(anchor="center", side="left", expand=True, fill="y")
        self._label_arquivo.pack(anchor="e", side="left", expand=True, fill="x")

        self._radiobtn_video_arquivo.grid(row=0, column=0, sticky="w", padx=5)
        self._radiobtn_video_dispositivo.grid(row=1, column=0, sticky="w", padx=5)

        self._frame_video_arquivo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self._frame_video_dispositivo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self._frame_entradas.pack(side="top", anchor="n", expand=True, fill="both", padx=5, pady=5)
        self._btn_concluir.pack(side="top", anchor="s", expand=True, fill="x", padx=5, pady=5)

        # ajuste das colunas quando a janela for redimensionada
        self._frame_entradas.columnconfigure(0, weight=0,   minsize=25)
        self._frame_entradas.columnconfigure(1, weight=999, minsize=150)
        self.rowconfigure(0, weight=999)
        self.rowconfigure(1, weight=0)

        self._frame_interno.pack(anchor="center", expand=True, fill="both")

        # configura o estado inicial da janela
        self._radiobtn_video_arquivo.invoke()
        self._label_arquivo.configure(text=f"arquivo: {self._var_arquivo_str.get()}")

    def _on_mudanca_tipo_entrada(self, *ignorado):
        if self._var_tipo_entrada.get() == 0:
            self.focus()
            self._btn_abrir_arquivo.configure(state="normal")
            self._entrada_video_indice.configure(state="disabled")
        else:
            self._btn_abrir_arquivo.configure(state="disabled")
            self._entrada_video_indice.configure(state="normal")

    @staticmethod
    def _validar_indice_dispositivo(texto):
        return texto.isdigit() or len(texto) == 0

    def _abrir_arquivo(self):
        arquivo = tkinter.filedialog.askopenfilename()
        if isinstance(arquivo, str):
            self._var_arquivo_str.set(arquivo)
            self._label_arquivo.config(text=f"arquivo: {arquivo}")

    def _concluir(self):
        video = None
        if self._var_tipo_entrada.get() == 0:
            # seleção de arquivo de vídeo
            arquivo = self._var_arquivo_str.get()
            if len(arquivo) > 0:
                video = arquivo
            else:
                tkinter.messagebox.showerror("Erro", "o arquivo de vídeo não foi selecionado")
        else:
            # seleção de dispositivo de vídeo
            dispositivo = self._var_dispositivo_str.get()
            if len(dispositivo) > 0:
                try:
                    video = int(dispositivo)
                except ValueError:
                    tkinter.messagebox.showerror("Erro", "o dispositivo de vídeo fornecido é inválido")
            else:
                tkinter.messagebox.showerror("Erro", "o dispositivo de vídeo não foi especificado")

        # salva o vídeo selecionado e fecha o dialogo
        if video is not None:
            self.video = video
            self.fechar()

    def fechar(self, evento=None):
        """
        fecha o dialogo
        """
        self.parent.destroy()

def selecao_exercicio():
    # listagem de exercícios
    from cntexercicios.exercicios import listar_exercicios
    exercicios = listar_exercicios()

    # janela principal
    app = tkinter.Tk()
    app.title("Seleção do Tipo de Exercício")
    janela = DialogoSelecaoExercicio(app, *exercicios)
    janela.pack(expand=True, fill=tkinter.BOTH)

    # configuração do tamanho mínimo da janela
    app.update()
    app.minsize(app.winfo_width(), app.winfo_height())

    # seta o callback para fechar a janela e inicia o loop do tkinter
    app.protocol("WM_DELETE_WINDOW", janela.fechar)
    app.mainloop()

    return janela.exercicio_selecionado

def selecao_video():
    # janela principal
    app = tkinter.Tk()
    app.title("Seleção do Vídeo")
    janela = DialogoSelecaoVideo(app)
    janela.pack(expand=True, fill=tkinter.BOTH)

    # configuração do tamanho mínimo da janela
    app.update()
    app.minsize(app.winfo_width(), app.winfo_height())

    # seta o callback para fechar a janela e inicia o loop do tkinter
    app.protocol("WM_DELETE_WINDOW", janela.fechar)
    app.mainloop()

    return janela.video

