# PL 2024/25 - TPC 5

## Problema proposto

Procura-se um programa Python que simule o funcionamento de uma máquina _vending_:

```
>> LISTAR

código | nome                 | quantidade | preço
 --------------------------------------------------
    A23 | Água 0.5L            |          8 |  0.7
    A24 | Compal Manga Laranja |          4 |  1.1
    B25 | Salame de chocolate  |          3 |  0.8

>> MOEDA 1e, 20c, 5c, 5c.
Saldo: 1.30€

>> SELECIONAR A23
Pode retirar o seu produto: Água 0.5L
Saldo: 0.60€

>> SELECIONAR A23
Saldo insuficiente

>> SAIR
Troco: 50c x 1,10c x 1
```

A informação dos produtos deve ser armazenada num ficheiro JSON como o
[`produtos.json`](produtos.json).

## Metodologia

O programa começa por ler o ficheiro JSON com os produtos presentes na máquina e definir o seu saldo
como 0. Depois, lê e analisa, uma a uma, cada linha de _input_ do utilizador. Esta análise é léxica
(com recurso ao `ply.lex`) e sintática (com recurso ao `ply.yacc`). Apesar desta última ferramenta
ainda não ter sido lecionada em aula, achei-a de fácil utilização após ler a sua documentação,
apesar de ainda não compreender completamente o funcionamento de um autómato LALR.

Na fase de análise sintática, são definidos os lexemas literais, `.` e `,`, as palavras reservadas
(`LISTAR`, `MOEDA`, `SELECIONAR` e `SAIR`), os identificadores (`ID`), e os valores das moedas
(`VALOR`). Apenas são definidas duas regras para a análise léxica, uma para `VALOR`
(`1c|2c|5c|10c|20c|50c|1e|2e`) e outra para `ID` (`[A-Za-z][A-Za-z0-9]*`). Para um melhor desempenho
do analisador léxico, dentro da definição desta regra como uma função, o tipo do lexema é mudado
caso o seu conteúdo coincida com o de uma palavra reservada.

Na análise sintática, definem-se as seguintes regras:

```yacc
comando : listar
        | sair
        | selecionar
        | moeda

listar     : LISTAR
sair       : SAIR
selecionar : SELECIONAR ID
moeda      : MOEDA lista_moeda '.'

lista_moeda : VALOR
            | VALOR ',' lista_moeda
```

Para cada uma destas regras, é definida uma função `p_nome_da_regra`, com os conteúdos da regra na
sua _docstring_. A regra `comando` é especial, definido todos os comandos possíveis, e deve
dar _match_ à sequência de lexemas total. As regras seguintes correspondem aos vários tipos de
comando. Por último, a regra `lista_moeda` define uma lista de lexemas de moedas separados por
vírgulas, com pelo menos uma moeda de comprimento.

Em vez de gerar uma árvore de sintaxe abstrata, optei por realizar a análise semântica já na fase de
análise sintática, para não complicar o código excessivamente. Logo, quando uma regra é encontrada,
uma operação é executada:

 - `listar`     - imprimir lista de produtos na máquina;
 - `sair`       - gerar o troco do utilizador (com um algoritmo guloso, da moeda de maior para a de
                  menor valor), e atualizar os conteúdos do JSON com os produtos;
 - `selecionar` - caso o produto selecionado exista (código válido e pelo menos uma unidade),
                  remover uma unidade da sua quantidade e atualizar o saldo; caso contrário,
                  imprimir um erro;
 - `listar`     - calcular a soma dos valores das moedas inseridas e incrementar o saldo.

## Resultados

O programa pedido foi desenvolvido e cumpre os requisitos do enunciado. Este pode ser testado do
seguinte modo:

<pre>
$ python3 <a href="TPC.py">TPC.py</a> <a href="produtos.json">produtos.json</a>
</pre>

A saída do programa coincide com o que é esperado. No entanto, o programa considera que a máquina
_vending_ tem um número ilimitado de cada tipo de moeda, algo que não é realista quando toca a fazer
o troco. Para tornar a máquina mais realista, o seguinte podia ser feito:

 - Adicionar ao esquema do ficheiro JSON o número de moedas de cada tipo que a máquina tem;
 - Limitar o algoritmo de geração de troco para não ultrapassar o número de moedas existentes de um
   dado tipo na máquina.
 - Recusar a venda de um produto ao cliente se o algoritmo de geração de troco falhar.

## Autoria

 - **Nome:** Humberto Gil Azevedo Sampaio Gomes
 - **Número mecanográfico:** A104348
 - **Data:** 2025/02/16

![A104348 - Humberto Gomes](../A104348.png)
