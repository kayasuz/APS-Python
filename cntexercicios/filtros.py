
import numpy as np

def espelhamento_vertical(imagem):
	"""
	Espelha a imagem na vertical
	"""
	return imagem[::-1, ...]

def espelhamento_horizontal(imagem):
	"""
	Espelha a imagem na horizontal
	"""
	return imagem[..., ::-1]

def estender_com_zeros(imagem, tamanho=None):
	"""
	Estende a imagem com zeros nas bordas
	"""
	# checagem de parâmetros
	if imagem.ndim < 2:
		raise ValueError(f"imagem inválida, número de dimensões não suportado: {imagem.ndim}")
	if tamanho is None:
		dx = 1
		dy = 1

	elif not isinstance(tamanho, (list, tuple)):
		raise TypeError(
			"esperado uma lista, tupla ou None para 'tamanho'"
			f"recebido tipo {type(tamanho).__qualname__}"
		)

	# verifica se 'tamanho' contém dois números inteiros não negativos
	elif len(tamanho) != 2 or any(map(lambda x: not isinstance(x, int) or x < 0, tamanho)):
		raise ValueError("'tamanho' deve ter conter dois números inteiros não negativos")

	else:
		dx, dy = tamanho

	w, h, *k = imagem.shape
	# cria uma imagem não inicializada e preenche as bordas com zero
	estendida = np.empty((w+(2*dx), h+(2*dy), *k), dtype=imagem.dtype)
	# gera os índices das bordas
	indices_x = [*range(dx), *range(-dx,0)]
	indices_y = [*range(dy), *range(-dy,0)]
	estendida[indices_x, ::] = 0
	estendida[::, indices_y] = 0

	# copia a imagem para o centro da nova imagem e retorna
	estendida[dx:-dx, dy:-dy] = imagem
	return estendida

def convolucao(imagem, kernel, reduzir=False):
	if imagem.ndim > 3 or imagem.ndim < 2:
		raise ValueError(f"imagem inválida, número de dimensões não suportado: {imagem.ndim}")
	if kernel.ndim != 2:
		raise ValueError(f"kernel de imagem inválido, número de dimensões não suportado: {kernel.ndim}")
	if kernel.shape[0] == 0 or kernel.shape[1] == 0:
		raise ValueError("kernel de imagem inválido, dimensão de comprimento nulo encontrado")

	# estende a imagem com zeros para aplicar o kernel,
	# a menos que a convolução deva reduzi-la
	k_w, k_h = kernel.shape
	f_w, f_h, *dim_extras = imagem.shape
	espacamento_x = (k_w - 1) // 2
	espacamento_y = (k_h - 1) // 2
	if not reduzir:
		imagem = estender_com_zeros(imagem, (espacamento_x, espacamento_y))
		dims_saida = (f_w, f_h, *dim_extras)
	else:
		dims_saida = (f_w - espacamento_x, f_h - espacamento_y, *dim_extras)

	# aplica o kernel
	# NOTE: isso pode provavelmente ser otimizado operando o kernel inteiro de uma vez,
	#       talvez com uma view ou o método numpy.broadcast
	if np.issubdtype(kernel.dtype, np.floating):
		dtype=float
	elif np.issubdtype(kernel.dtype, np.integer):
		dtype=int
	else:
		raise ValueError(f"kernel de imagem inválido, tipo não suportado: {kernel.dtype}")

	saida  = np.zeros(dims_saida, dtype=dtype)
	buffer = np.zeros(dims_saida, dtype=dtype)
	for j in range(k_h):
		for i in range(k_w):
			# multiplicação sem alocação de um novo array
			np.multiply(kernel[i,j], imagem[i:(f_w+i), j:(f_h+j)], out=buffer)
			# adiciona o resultado parcial à saída
			saida += buffer

	# trunca o resultado e retorna
	return saida.astype(np.uint8)
