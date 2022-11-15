"""
Módulo com funções de filtragem e convolução de kernels em imagens,
assim como funções para gerar alguns tipos de kernels

As funções desse módulo operam em imagens assumindo que elas (e os kernels)
sejam arrays da biblioteca numpy (numpy.ndarray), ou listas ou tuplas convertíveis
para esses arrays
"""

import numpy as np

def espelhamento_vertical(imagem):
	"""
	Espelha a imagem fornecida pelo eixo horizontal, invertendo a orientação
	do eixo vertical, idependete dos canais presentes na imagem, assume que o
	eixo horizontal esteja no primeiro eixo do array fornecido
	"""
	return imagem[::-1, ...]

def espelhamento_horizontal(imagem):
	"""
	Espelha a imagem fornecida pelo eixo vertical, invertendo a orientação
	do eixo horizontal, idependete dos canais presentes na imagem, assume que o
	eixo vertical esteja no segundo eixo do array fornecido
	"""
	return imagem[..., ::-1]

def melhorar_contraste(imagem):
	"""
	Melhora o contraste de uma imagem BGR, normalizando a luminosidade dela
	no espaço de cores YPrPb e usando a diferença de luminosidade resultante
	para corrigir os valores dos canais B, G e R para a luminosidade normalizada.
	Isso evita uma conversão direta entre os espaços de cores BGR e YPrPb

	A imagem deve ser do tipo RGB e ter canais na ordem BGR, e deve ser fornecida
	como um array numpy (numpy.ndarray) de três dimensões, com a terceira dimensão
	sendo usada para armazenar os canais, ou uma lista ou tupla que seja convertível
	para um array desse tipo
	"""
	kr, kg, kb = (0.299, 0.587, 0.114)
	"""
	conversão RGB/BGR -> YPrPb
	Y  = Kr * R + Kg * G + Kb * B
	Pr = 1/2 * (B - Y) / (1 - Kb)
	Pb = 1/2 * (R - Y) / (1 - Kr)

	como os canais Pr e Pb não são alterados durante o ajuste de contraste,
	os valores adicionados aos canais B, G e R podem ser calculados:

	Pr = 1/2 * (Bi - Yi) / (1 - Kb) = 1/2 * (Bf - Yf) / (1 - Kb)
	Pb = 1/2 * (Ri - Yi) / (1 - Kr) = 1/2 * (Rf - Yf) / (1 - Kr)

	Bi - Yi = Bf - Yf
	Ri - Yi = Rf - Yf

	Bf - Bi = Yf - Yi
	Rf - Ri = Yf - Yi

	dB = dR = dY

	dY = Yf - Yi = (Kr * Rf + Kg * Gf + Kb * Bf) - (Kr * Ri + Kg * Gi + Kb * Bi)
	dY = Kr * dR + Kg * dG + Kb * dB
	dG = (dY - Kr * dR - Kb * dB) / Kg
	dG = dY * (1 - Kr - Kb) / Kg

	onde dB, dG, dR e dY são os valores adicionados ou subtraídos dos canais
	B, G, R e Y respectivamente após o ajuste de contraste, Yi, Ri, Bi são
	os valores iniciais dos canais Y, R e B, e Yf, Rf e Bf são os valores
	finais dos canais Y, R e B.
	"""
	# NOTE: como as constantes foram escolhidas para gerar valores
	#       no intervalo de 0 a 255, é seguro usar o truncamento
	Yi = np.dot(imagem, (kb, kg, kr)).astype(np.uint8)

	# correção na luminância
	ymin, ymax = Yi.min(), Yi.max()
	Yf = ((255 * (Yi - ymin).astype(int)) / (ymax - ymin)).astype(np.uint8)

	# cálculo da mudança dos níveis dos canais
	dR = dB = dY = np.subtract(Yf, Yi, dtype=np.int16)
	dG = dY * (1 - kr - kb) / kg
	np.clip(dG, -255, 255, out=dG)
	dG = dG.astype(np.int16)

	# aplicação das mudanças na imagem
	resultado = imagem.astype(np.int16)
	np.add(dB, resultado[..., 0], out=resultado[..., 0])
	np.add(dG, resultado[..., 1], out=resultado[..., 1])
	np.add(dR, resultado[..., 2], out=resultado[..., 2])
	np.clip(resultado, 0, 255, out=resultado)
	return resultado.astype(np.uint8)

def estender_com_zeros(imagem, tamanho=None):
	"""
	Estende a imagem bidimensional fornecida com zeros nas bordas,
	independente do número de canais.

	Por padrão adiciona uma borda com comprimento de um pixel à imagem,
	mas pode ser configurado pelo parâmetro 'tamanho' para adicionar
	outros comprimentos de bordas. Se fornecido, o tamanho deve ser uma
	lista ou tupla com dois inteiros não negativos.
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
	"""
	Aplica uma filtragem na imagem fornecida por meio da convolução dela com um kernel,
	que ocorre isoladamente em cada canal produzindo uma imagem resultante com as mesmas
	dimensões e número de canais, ou com uma quantidade reduzida de pixels caso um valor
	verdadeiro for passado ao parâmetro 'reduzir' (o tipo fornecido não importa, desde
	que o valor possa ser evaluado para True).

	O kernel fornecido deve ter duas dimensões não nulas e ser composto de valores dos
	tipos float ou int, caso um kernel com números inteiros for fornecido, essa função
	utilizará números inteiros nas contas a menos que isso cause erros de overflow.

	A convolução é feita primeiro achando o centro do kernel (que é a célula na diagonal
	superior esquerda mais próxima ao centro), estendendo a imagem com zeros caso necessário
	através da função estender_com_zeros desse módulo para que a convolução possa ser operada
	em todos os pixels. Em seguida os NxM vizinhos de cada píxel são multiplicados pelo
	kernel de dimensões MxN, gerando MxN imagens que são sendo somadas a um acumulador,
	que é truncado, convertido para armazenar canais de 8 bits e retornado como resultado.
	"""
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

	# calcula o tipo apropriado para utilizar no buffer intermediário
	if np.issubdtype(kernel.dtype, np.floating):
		dtype = float

	elif np.issubdtype(kernel.dtype, np.integer):
		vmax_a = np.sum(255 * np.clip(kernel, 0, np.inf).astype(float))
		vmax_b = -np.sum(255 * np.clip(kernel, -np.inf, 0).astype(float))
		vmax = max(vmax_a, vmax_b)
		# checagem de sinal
		if kernel.min() >= 0:
			if vmax > ((1 << 64) - 1):
				# overflow provável, use floats no cálculo pra prevenir erros
				dtype = float
			else:
				# sem risco de overflow, use unsigned ints para acelerar as contas
				dtype = np.uint64

		elif vmax > ((1 << 63) - 1):
			# overflow provável, use floats no cálculo pra prevenir erros
			dtype = float
		else:
			# sem risco de overflow, use ints para acelerar as contas
			dtype = np.int64
	else:
		raise ValueError(f"kernel de imagem inválido, tipo não suportado: {kernel.dtype}")

	# aplica o kernel
	# NOTE: isso pode provavelmente ser otimizado operando o kernel inteiro de uma vez,
	#       talvez com uma view ou o método numpy.broadcast
	saida  = np.zeros(dims_saida, dtype=dtype)
	buffer = np.zeros(dims_saida, dtype=dtype)
	for j in range(k_h):
		for i in range(k_w):
			# multiplicação sem alocação de um novo array
			np.multiply(kernel[i,j], imagem[i:(f_w+i), j:(f_h+j)], out=buffer, dtype=dtype)
			# adiciona o resultado parcial à saída
			saida += buffer

	# trunca o resultado e retorna
	return np.clip(saida, 0, 255).astype(np.uint8)

def kernel_nitidez(peso=1):
	"""
	Gera um kernel 3x3 para realçar a nitidez
	de imagens pela convolução delas com ele.

	A força do realce de nitidez pode ser configurada
	pelo parâmetro 'peso', com a única restrição sendo
	que ele seja valor não negativo.
	"""
	if isinstance(peso, int):
		dtype = int
	elif isinstance(peso, float):
		dtype = float
	else:
		raise TypeError(f"esperado int ou float para 'peso', recebido tipo {type(peso).__qualname__}")
	if peso < 0:
		raise ValueError("'peso' não pode ser um número negativo")

	a = -peso
	b = 1 + 4 * peso
	return np.array([
		[0, a, 0],
		[a, b, a],
		[0, a, 0]
	], dtype=dtype)

def kernel_deteccao_borda():
	"""
	Gera um kernel 3x3 para detecção de bordas
	em imagens pela convolução delas com ele.

	Esse tipo de kernel pode não funcionar bem
	com imagens coloridas, sendo melhor utilizado
	em imagens com tons de cinza.
	"""
	return np.array([
		[-1, -1, -1 ],
		[-1,  8, -1 ],
		[-1, -1, -1 ],
	], dtype=int)

def kernel_gauss(tamanho=None, sigma=1):
	"""
	Gera um kernel quadrado com um tamanho especificado contendo uma distribuição normal,
	que pode ser utilizado para borrar imagens pela convolução delas com o kernel.

	O tamanho do kernel padrão é 3x3, mas pode ser ajustado pelo parâmetro 'tamanho',
	que se fornecido deve ser um número entre 1 e 32 que será utilizado para a quantidade
	de linhas e colunas.

	Além disso, o desvio padrão da distribuição pode ser configurado
	pelo parâmetro 'sigma', que deve ser um número não negativo.

	NOTA: os kernels gerados respeitam a regra da distribuição normal,
	      onde a soma de todos os pontos deve ser sempre igual a 1
	"""
	import sys
	import math
	if tamanho is None:
		tamanho = 3
	elif not isinstance(tamanho, int) or isinstance(tamanho, bool):
		raise TypeError(
			f"esperado int ou None para 'tamanho', recebido tipo {type(tamanho).__qualname__}"
		)
	elif tamanho < 1:
		raise TypeError(f"'tamanho' deve ser um númeor positivo diferente de zero")
	elif tamanho > 32:
		# tamanho limitado por causa da precisão do algorítimo de geração do kernel
		raise TypeError(f"tamanho não suportado")
	if not isinstance(sigma, (int, float)):
		raise TypeError(f"esperado int ou float para 'sigma', recebido tipo {type(sigma).__qualname__}")
	if math.copysign(1, sigma) < 0:
		raise ValueError(f"'sigma' não pode ser um número negativo")

	# distribuição normal em uma dimensão
	if sigma < sys.float_info.epsilon:
		x = np.array([0, 1, 0], dtype=np.float)
	else:
		x = np.linspace(-(tamanho // 2), tamanho // 2, tamanho)
		x = (1 / (np.sqrt(2 * np.pi) * sigma)) * np.e ** (-np.power(x / sigma, 2) / 2)

	# extensão da distribuição fazendo o produto externo
	kernel = np.outer(x.T, x.T)

	# corrige kernel para que a soma dos valores seja 1
	# (evitando que a imagem escureça) e retorna o resultado
	kernel /= kernel.sum()
	return kernel
