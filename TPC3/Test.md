# Teste do conversor de Markdown

## Q1

Indique qual das seguintes proposições é **falsa**:

1. A gramática de HTML é regular
2. É possível converter qualquer autómato finito não determinístico num autómato finito determinístico
3. O regente da UC de Processamento de Linguagens é dono de uma empresa
4. Dois professores da UC de Processamento de Linguagens vão-se reformar para o ano

Pode encontrar a resposta a estas perguntas [aqui](https://orcid.org/0000-0002-8574-1574).

## Q2

Analise a minha expressão facial durante o tempo em que não estou a fazer TPCs de PL. Numa escala de 0 a 10, quanto contente estou?

![A104348 - Humberto Gomes](../A104348.png)

## Factos interessantes

### Este parser não é horrível de todo

Este *parser* consegue suportar ***texto itálico* dentro de texto negrito** e *vice-**versa***

### Não consegui avariar este parser

Nesta secção, procuro dar cabo do meu parser de Markdown, começando por alguns *headings* mal-formatados:

#Isto não deve dar
####### nem isto

Depois, vamos testar umas listas esquisitas:

1. Elementos
2. devem
3. estar
4. por
5. ordem
6. e
7. começar
8. em
9. 1
10. Além
11. disso
12. vamos
13. ver
14. o
15. que
16. acontece
17. quando
18. a
19. lista
20. fica
21. muito
22. grande

1. quando a lista
3. não está por ordem
7. dá nisto

Depois, tentei testar uns links (e imagens) estranhos:

![Ataque de HTML"> nem vale a pena](....)
![**Negrito no alt text não é possível**](....)
[**mas num link deve ser**](https://wikipedia.org)
[e quando o link é estranho?](")

E, por último, uns **bolds** e itálicos

*
multilinha
talvez?
*

**
e um *bold* inacabado? (ah, conta como um itálico)
