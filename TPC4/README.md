# PL 2024/25 - TPC 3

## Problema proposto

Procura-se um programa Python que faça a análise léxica de interrogações SPARQL, como a do seguinte
exemplo:

```
# DBPedia: obras de Chuck Berry

select ?nome ?desc where {
    ?s a dbo:MusicalArtist.
    ?s foaf:name "Chuck Berry"@en .
    ?w dbo:artist ?s.
    ?w foaf:name ?nome.
    ?w dbo:abstract ?desc
} LIMIT 1000
```

## Metodologia

O módulo `ply.lex` foi utilizado para a geração automática de um analisador léxico. Segue a lista de
_tokens_ definidos, com as expressões regulares que os definem, ordenados da maior para a menor
prioridade:

1. Comentários: `r'\#.*'`;
2. Palavras reservadas: `r'SELECT'`, `r'WHERE'` e `r'LIMIT'`;
3. Pontuação: `r'{'`, `r'}'` e `r'\.'`;
4. Literais numéricos e de _strings_: `r'\d+'` e `r'"(?P<LIT>.*?)"(?:@(?P<LANG>\w{2,}))?'`;
5. Variáveis: `r'\?\w+'`;
6. Predicados: `r'a|(?:\w|:)+'`.

Para ordenar estes _tokens_ por prioridade, para cada _token_, é definida uma função `t_NOME`, e
estas funções são ordenadas pela ordem das prioridades acima: `t_COMMENT`, `t_SELECT`, `t_WHERE`,
_etc._

A maior parte destas funções são simples, têm na sua _docstring_ a expressão regular correspondente
ao _token_ que definem, e devolvem o _token_ que recebem como argumento sem o modificar. Por
exemplo:

```python
def t_COMMENT(t):
    r'\#.*'
    return t
```

No entanto, há duas exceções. Em primeiro lugar, a função associada a literais numéricos converte a
o valor do _token_ para um número (`t.value = int(t.value)`). É mais complexo lidar com literais de
_strings_. Neste caso, a expressão regular do _token_ é utilizada para isolar os seus grupos de
captura: os conteúdos da _string_ e a linguagem.

```python
def t_STRLIT(t):
    r'"(?P<LIT>.*?)"(?:@(?P<LANG>\w{2,}))?'
    t.value = re.match(t_STRLIT.__doc__, t.value).groupdict()
    return t

# "Chuck Berry"@en -> {'LIT': 'Chuck Berry', 'LANG': 'en'}
```

Por último, foram definidas as entidades especiais `t_newline`, `t_ignore` e `t_error`, que definem
a ação a tomar pelo analisador léxico quando uma nova linha é encontrada (incrementar o número da
linha atual), que caráteres devem ser ignorados (espaços e tabulações horizontais) e o que fazer em
caso de erro (imprimir um erro e ignorar o caráter), respetivamente.

## Resultados

O programa pedido foi desenvolvido e cumpre os requisitos do enunciado. Para o testar, a
interrogação apresentada em [Problema proposto](#Problema_proposto) foi passada ao programa
pelo `stdin` do seguinte modo:

<pre>
$ python3 <a href="TPC.py">TPC.py</a> &lt; <a href="query.txt">query.txt</a>
</pre>

A saída do programa coincide com o esperado:

```python
LexToken(COMMENT,'# DBPedia: obras de Chuck Berry',1,0)
LexToken(SELECT,'select',3,33)
LexToken(VARIABLE,'?nome',3,40)
LexToken(VARIABLE,'?desc',3,46)
# ...
```

No entanto, é de notar que este analisador léxico suporta apenas uma pequena fração de SPARQL,
não suportando várias palavras reservadas, escape de caráteres em _strings_, entre muitas outras
funcionalidades.

## Autoria

 - **Nome:** Humberto Gil Azevedo Sampaio Gomes
 - **Número mecanográfico:** A104348
 - **Data:** 2025/02/16

![A104348 - Humberto Gomes](../A104348.png)
