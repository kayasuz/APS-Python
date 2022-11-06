# APS-Python
Projeto de processamento digital de imagens para a contagem de exercícios físicos
utilizando a biblioteca OpenCV para a APS (Atividade Prática Supervisionada) do curso de Ciência da Computação.

Essa biblioteca foi desenvolvida como aplicação para contagem de exercícios físicos em vídeos, seja em arquivos
ou diretamente de uma webcam, mas pode ser usada também diretamente como biblioteca, o que permite que ela seja
estendida com mais tipos contadores ou outras funções que não estão presentes nela.

###### Observação: O projeto foi desenvolvido e testado utilizando o interpretador Python versão 3.10, podendo funcionar nas versões anteriores, mas não há garantia que o código funcione

## Instalação da biblioteca opencv-python

Para que o programa funcione a biblioteca opencv-python precisa estar instalada manualmente,
já que a instalação pode variar dependendo do sistema
```sh
# Windows
pip install opencv-python

# Ubuntu
sudo apt-get install python3-opencv

# openSUSE
sudo zypper install python3-opencv
```

Caso esteja usando um ambiente virtual, a biblioteca opencv-python pode ser instalada no Linux de forma similar ao Windows
```sh
pip3 install opencv-python
```

## Instalação via URL (recomendado)

No terminal, execute o seguinte comando para a instalação do programa:
```sh
# Windows
pip install https://github.com/kayasuz/APS-Python

# Linux & OSX
pip3 install https://github.com/kayasuz/APS-Python
```

## Instalação via Arquivo Wheel ou Tarball

Baixe o arquivo wheel (extensão .whl) ou tarball (extensão .tar.gz) da versão desejada do programa,
em seguida abra a pasta que contém o arquivo baixado e execute no terminal para instalar o pacote:

* Arquivo wheel
  ```sh
  # Windows
  pip install contador_exercicios-0.1.0-py3-none-any.whl

  # Linux e OSX
  pip3 install contador_exercicios-0.1.0-py3-none-any.whl
  ```

* Arquivo tarball
  ```sh
  # Windows
  pip install contador_exercicios-0.1.0.tar.gz

  # Linux e OSX
  pip3 install contador_exercicios-0.1.0.tar.gz
  ```

AVISO: o nome do arquivo baixado irá mudar dependendo da versão a ser instalada

## Instalação via Código Fonte

Para instalar o programa a partir do código fonte é recomendado configurar um ambiente virtual para gerar
um pacote do programa para que ele seja instalado, caso já tenha um ambiente virtual configurado ou saiba
o que está fazendo, pule a etapa seguinte e vá direto para a clonagem do repositório

### Criação do Ambiente Virtual

Em um terminal, execute os seguintes comandos para criar um ambiente virtual e ativá-lo
```sh
# Windows cmd.exe
python -m venv venv-contador-exercicios
cd venv-contador-exercicios
Scripts/activate.bat

# Windows PowerShell
python -m venv venv-contador-exercicios
cd venv-contador-exercicios
Scripts/activate.ps1

# Linux & OSX
python3 -m venv venv-contador-exercicios
cd venv-contador-exercicios
source bin/activate
```
AVISO: o nome do script de ativação pode ser diferente no Linux dependendo do shell usado (bash, zsh, csh, etc.)

### Clonagem do Repositório

Clone o repositório para dentro da pasta venv-contador-exercicios, entre na pasta criada
e mude para a branch contendo a versão mais recente do programa
```sh
git clone git@github.com:kayasuz/APS-Python.git
cd APS-Python
git checkout main
```

### Empacotamento e Instalação do Programa

Use o script setup.py presente no repositório clonado para criar o pacote para a instalação,
e depois disso instale o pacote dentro do ambiente virtual, ou no próprio sistema seguindo as
regras da instalação via arquivo wheel ou tarball, porém em um novo terminal e com o arquivo
gerado ao invés do presente no repositório

* Arquivo wheel
  ```sh
  # Windows
  python setup.py bdist_wheel
  pip install dist/contador_exercicios-0.1.0-py3-none-any.whl

  # Linux & OSX
  python3 setup.py bdist_wheel
  pip3 install dist/contador_exercicios-0.1.0-py3-none-any.whl
  ```

* Arquivo tarball
  ```sh
  # Windows, arquivo tarball
  python setup.py sdist
  pip install dist/contador_exercicios-0.1.0.tar.gz
  
  # Linux & OSX, arquivo tarball
  python3 setup.py sdist
  pip3 install dist/contador_exercicios-0.1.0.tar.gz
  ```

AVISO: o nome do arquivo baixado irá mudar dependendo da versão a ser instalada

## Execução do Programa

Após a instalação, o programa pode ser executado de duas formas: abrindo um diálogo para a seleção
do exercício a ser contado e o vídeo a ser utilizado, ou execução do contador de exercícios diretamente,
ambos pela linha de comando. O vídeo pode ser fornecido tanto como arquivo ou como índice de dispositivo,
não há uma forma portátil de saber qual dispositivo foi atribuído a qual índice, mas o índice zero costuma
ser atribuído para a webcam principal do sistema caso uma exista, ou uma webcam externa.

Ambas as formas suportam um nome de tema opcional do Ttk fornecido pela opção --tema (--tema="tema")
que altera a aparência da janela, os temas clam, alt, default e classic são geralmente suportados,
e os temas adicionais vista, xpnative e winnative podem estar disponíveis no Windows.

* Método principal
  ```sh
  # Windows
  python -m cntexercicios

  # Linux & OSX
  python3 -m cntexercicios
  ```

* Método direto (exemplo)
  ```sh
  # Windows
  python -m cntexercicios.exercicios.flexoes "Vídeos\Treino Flexões.mp4"

  # Linux & OSX
  python3 -m cntexercicios.exercicios.flexoes "Vídeos/Treino Flexões.mp4"
  ```

___

## Integrantes
- Gabriel Pavan de Moura
- Giovani Giaqueto de Oliveira
- João Paulo da Silva Nodari
- Leonardo Figueiredo do Nascimento
- Luciana Balsaneli Scabini
- Vinicius Silva Maturo
