# PL 2024/25 - TPC 1

## Problema proposto

Procura-se um programa Python que:

 1. Some todas as sequências de dígitos num texto;
 2. Sempre que encontrar a string `Off`, em qualquer combinação de maiúsculas e minúsculas, o
    comportamento de soma é desligado;
 3. Sempre que encontrar a string `On`, em qualquer combinação de maiúsculas e minúsculas, o
    comportamento de soma é ligado;
 4. Sempre que encontrar o caráter `=`, o resultado da soma é colocado na saída.

Não é permitido o uso de expressões regulares.

## Exemplos

Perante a seguinte fonte:

<pre>
12@~00of<b>on</b>01ff<b>off</b>01<b>on=off</b>??15<b>on</b>1<b>=</b>
</pre>

A saída do programa deve ser:

```
13
14
```

## Metodologia

Para criar um programa que cumpre os requisitos colocados, utilizou-se a _pipeline_ clássica de
processamento de linguagens:

 - Um analisador léxico extrai os lexemas (`=`, `On`, `Off`, e literais numéricos);
 - Um analisado sintático constrói uma árvore de sintaxe abstrata (ASA);
 - Um analisador semântico, no caso, um interpretador, faz uma travessia da ASA para implementar o
   comportamento do programa;

O uso desta _pipeline_ pode ser um pouco excessivo para este problema simples, mas queria entender
em detalhe o seu funcionamento, pelo que a implementei.

### Analisador léxico

O analisador léxico é responsável por identificar no texto fonte palavras reservadas
(`=`, `On`, `Off`) e literais numéricos. Logo, definiram-se dois tipos de lexema, apresentados
abaixo em notação de tipo de dados algébrico:

```
Token = LiteralToken str
      | KeywordToken str
```

O analisador léxico itera pelo texto fonte caráter a caráter. A cada iteração, verifica se alguma
palavra reservada conhecida é um prefixo do texto, tendo em conta questões de maiúsculas ou
minúsculas. Por exemplo, para verificar se o texto começa com `On`, o analisador léxico isola os
seus dois primeiros caráteres, converte-os para minúsculas, e compara essa _string_ com a _string_
`on`:

```python
text[i:(i + 2)].lower() == 'on'
```

Quando uma palavra reservada é encontrada, o analisador léxico devolve-a (utilizando geradores de
Python) e avança o iterador para o fim da palavra. Caso não seja encontrada nenhuma palavra
reservada, o analisador léxico verifica se existe algum literal numérico na posição do texto em
análise. Para isso, analisa o cáratere atual e outros posteriores, até estes deixarem de ser
dígitos. Caso tenha sido encontrado pelo menos um dígito, o literal numérico é registado como um
lexema e o iterador é avançado para o seu final. Caso contrário, o iterador é avançado apenas uma
unidade e nenhum lexema é devolvido, o que corresponde ao descarte do caráter atual.

### Analisador sintático

A sintaxe da linguagem definida é bastante simples e não apresenta qualquer forma de hierarquia,
sendo completamente sequencial. Logo, a ASA foi representada como uma espinha, ou seja, uma
sequência de nós. Logo, o analisador sintático não passa de uma simples operação `map` na sequência
de lexemas, que gera uma lista de nós. Abaixo, apresentam-se os vários tipos de nós:

```
Node = EqualNode
     | OnNode
     | OffNode
     | NumberNode int
```

### Analisador semântico

Tendo a ASA, a implementação da soma dos números é trivial. Com um acumulador e uma _flag_ on/off,
itera-se pelos nós da ASA pela ordem em que surgem na fonte, executando-se uma ação diferente a cada
nó:

 - `EqualNode`: apresenta-se o valor do acumulador no ecrã;
 - `OnNode`: a _flag_ on/off é definida como verdadeira;
 - `OffNode`: a _flag_ on/off é definida como falsa;
 - `NumberNode`: o valor inteiro é adicionado ao acumulador.

## Resultados

O programa desenvolvido foi testado para o exemplo dado e confirmou-se que este funcionava
corretamente. Por fim, visto que vários conceitos de programação funcional (tipos de dados
algébricos, `map`s, _etc._) foram utilizados, o mesmo programa foi reimplementado em Haskell. A
implementação em Haskell apresenta o mesmo funcionamento que a de Python, mas é muito mais concisa.

## Autoria

 - **Nome:** Humberto Gil Azevedo Sampaio Gomes
 - **Número mecanográfico:** A104348
 - **Data:** 2025/02/08

![A104348 - Humberto Gomes](../A104348.png)
