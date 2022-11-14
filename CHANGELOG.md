
## Adições

* Novo módulo `cntexercicios.filtros` contendo funções para filtragem de imagens
  * Filtros de correção de contraste, melhoria de nitidez,
    borragem gaussiana (Gaussian Blur) e detecção de bordas
  * Filtragem de imagens pela convolução de kernels

* Contadores de exercícios
  * Adição de alguns dos filtros do novo módulo `filtros`
  * Ativação/desativação de cada filtro de forma independente
  * Texto de ajuda expansível que explica o que cada tecla faz
  * Possibilidade de exibição do vídeo filtrado ou antes da filtragem
  * Adição de função de renderização de texto com suporte à textos multilinha e alinhamento da caixa de texto,  
    que pode ser utilizada por subclasses para abstrair a renderização de textos do OpenCV

## Melhorias

* Função de pausar o vídeo durante a contagem de exercícios através da tecla P ou da barra de espaço
* Melhoria da aparência dos textos nos contadores de exercícios
* Adição de documentação em alguns métodos sem documentação
* Melhoria na documentação dos módulos `cntexercicios.video`, `cntexercicios.dialogo` e `cntexercicios.exercícios.flexoes`

## Mudanças

* Reformulação dos contadores de exercícios
  * Adição de nova classe base `ContadorExercicios` para criação de contadores de exercícios com registro automático
  * Funções para listagem de nomes exercícios implementados, busca, instanciação e execução de contadores baseados na nova classe

* Depreciação de código
  * Depreciação de contadores de exercícios baseados em funções em favor da implementação de contadores usando a nova classe base abstrata
  * Depreciação das funções de registro, listagem e execução associadas a contadores de exercícios implementados por funções

## Correções

* Algumas correções em comentários em partes variadas do código
