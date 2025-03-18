# PL 2024/25 - TPC 6

## Problema proposto

Procura-se um programa Python que seja capaz de calcular o valor correto de expressões matemáticas
como as seguintes:

```
>> 10 * 3 + 2
32

>> 5 - 1 / 4
4.75
```

## Metodologia

Em primeiro lugar, foi construído um analisador léxico para estas expressões. Os literais foram
identificados como sendo os seguintes: `'+', '-', '*', '/'`. Ademais, há um tipo de lexema para os
valores numéricos: `[0-9]+`.

Em primeiro lugar, foi construída uma gramática para estas expressões:

```yacc
expr : NUMBER '+' expr
     | NUMBER '-' expr
     | NUMBER '*' expr
     | NUMBER '/' expr
```

Para permitir que esta linguagem seja analisada por um autómato LL(1), é necessário que não haja
várias regras de produção para o mesmo símbolo terminal a começar com o mesmo símbolo não terminal.
Por esse motivo, a gramática foi convertida na seguinte:

```yacc
expr : NUMBER exprCont

exprCont : '+' NUMBER exprCont
         | '-' NUMBER exprCont
         | '*' NUMBER exprCont
         | '/' NUMBER exprCont
         | ε
```

De seguida, um analisador sintático recursivo descendente foi desenvolvido para esta gramática. No
entanto, a árvore de sintaxe abstrata gerada não é a mais útil para calcular o valor das expressões,
visto que não tem em atenção a ordem das operações. Por exemplo:

```
2 * 2 / 8 + 3 * 3 -> (2, ('*', (2, ('/', (8, ('+', (3, ('*', (3, None)))))))))
```

Logo, para calcular o valor destas operações, em primeiro lugar, os valores de todas as sequências
de multiplicações e divisões são calculadas. Para o exemplo acima, tem-se:

```
(0.5, ('+', (9, None)))
```

Depois, o mesmo é feito para adições e subtrações, e o valor final da expressão é calculado.

## Resultados

O programa criado é interativo: o utilizador pode escrever as expressões cujo valor deseja calcular
no terminal, depois de executar o programa do seguinte modo: 

<pre>
$ python3 <a href="TPC.py">TPC.py</a>
</pre>

Devido às várias possíveis fórmulas cujo valor é possível calcular, foi criado um programa para
testagem automática da calculadora desenvolvida ([`fuzzer.py`](fuzzer.py)). Este gera várias
expressões aleatórias, dá-las ao programa, e compara os resultados obtidos com os resultados
esperados, calculados através da função Python `eval`. Após corrigir alguns erros na calculadora,
a calculadora desenvolvida apresenta o mesmo comportamento que o Python.

## Autoria

 - **Nome:** Humberto Gil Azevedo Sampaio Gomes
 - **Número mecanográfico:** A104348
 - **Data:** 2025/02/16

![A104348 - Humberto Gomes](../A104348.png)
