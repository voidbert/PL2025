# PL 2024/25 - TPC 3

## Problema proposto

Procura-se um programa Python que leia um ficheiro Markdown e o converta para HTML. Apenas o
seguinte subconjunto de funcionalidades Markdown devem ser suportadas:

```markdown
# Headers
## Vários outros níveis de headers

1. Listas
2. ordenadas

[hiperligações](https://omeusite.com)
![imagens](https://omeusite.com/favicon.ico)

**Texto a negrito**
*Texto a itálico*
```

## Metodologia

Perante a complexidade do problema, este foi resolvido através da aplicação de sucessivas operações
envolvendo expressões regulares. Deste modo, itera-se pela fonte várias vezes, o que prejudica o
desempenho do programa, mas o código Python escrito é mais conciso do que o de um analisador léxico
escrito de raiz.

A primeira substituição feita é a dos _headers_. Estes são detetados pela expressão regular
`^(#{1,6}) (.*)`. A função `re.sub` é chamada, levando como argumento esta expressão regular e uma
função de substituição que gera o código HTML desejado, escolhendo a _tag_ correta conforme o
comprimento do grupo de captura. Por exemplo, `### ABC` é transformado em `<h3>ABC</h3>`.

De seguida, a expressão regular `(?:(^|\n)\d+\. .*)+` apanha as sequências de linhas começadas com
sequências de dígitos, um ponto e um espaço. Cada sequência de linhas é passada a uma função, que
começa, com a expressão regular `^\d+`, por isolar os números no início de cada linha. Se verifica
que o primeiro número é 1, e este valor é incrementado em uma unidade a cada linha, então a lista é
válida. Nesse caso, as _tags_ `<ol>` e `</ol>` são colocadas no início e no fim da lista, e cada
entrada na lista, capturada com a expressão regular `^\d+\. (.*)`, é substituída por `<li>\1</li>`,
onde `\1` representa o texto capturado.

Depois, tanto hiperligações como imagens são detetadas com o padrão `(!?)\[(.*)?\]\((.*)?\)`. No
entanto, neste caso, não se faz uma substituição destas expressões, mas sim uma separação da fonte
por elas. Deste modo, é possível separar conteúdos textuais e hiperligações, e apenas substituir
marcações de itálico e negrito nos conteúdos textuais (não se deve mexer nas URLs, que podem conter
o caráter `*`). Após aplicar as transformações a texto itálico e negrito, as hiperligações e as
imagens dão origem a _tags_ `<a>` e `<img>`, respetivamente.

É devido a esta divisão da fonte que a ordem de aplicação das substituições é importante: marcações
de itálico e negrito não podem ser processadas antes das hiperligações e imagens. No entanto, esta
metodologia adotada não suporta alguma sintaxe que, apesar de não especificada, faz sentido. Por
exemplo, não é possível estilizar o _alt text_ de uma imagem, visto que a sintaxe abaixo não é
aceite:

`**![alt text negrito](imagem.png)**`

Por último, é feito o processamento das marcações de negrito e itálico, por esta ordem, visto que
uma marcação de negrito também é uma marcação de itálico válida (com mais dois asterisco à volta).
Caso as marcações de itálico fossem processadas em primeiro lugar, não seria possível fazer _match_ 
nenhuma marcação de negrito.

## Resultados

O programa pedido foi desenvolvido e cumpre os requisitos do enunciado. Para o testar, o ficheiro
[Test.md](Test.md) foi criado. Para executar o programa com este ficheiro, dando origem a um outro
ficheiro, `Test.html`, o seguinte comando deve ser executado.

<pre>
$ python3 <a href="TPC.py">TPC.py</a> &lt; Test.md &gt; Test.html
</pre>

Como se pode observar na página Web gerada, são detetados os vários _headers_, listas ordenadas,
hiperligações e imagens, e texto a negrito e itálico. O ficheiro de teste inclui também algum
Markdown inválido (listas com números desordenados, hiperligações mal formatadas, ...), que o
conversor desenvolvido reconhece, sendo capaz de os apresentar como texto plano.

No entanto, é de notar que o programa desenvolvido apenas suporta um subconjunto muito pequeno da
sintaxe de Markdown, tendo em falta algumas funcionalidades essenciais mas que não constam no
enunciado, como, por exemplo, a separação de parágrafos (`<p></p>`). Ademais, adicionar estas
funcionalidades não seria fácil, tendo em conta a fragilidade do _parser_ atual: a procura e
substituição de _tokens_ deve ser feita numa ordem muito específica, dificultando a adição de
novas funcionalidades.

No futuro, seria ideal a definição de uma gramática formal para melhorar o _parser_ de Markdown.
Ademais, seria possível nela definir se alguns casos extremos constituem ou não Markdown válido,
como por exemplo:

 - `**![alt](link)**` (HTML inválido ou `alt` a negrito?)
 - `![**alt**](linl)` (`alt` a negrito ou `**alt**`?)
 - ...

## Autoria

 - **Nome:** Humberto Gil Azevedo Sampaio Gomes
 - **Número mecanográfico:** A104348
 - **Data:** 2025/02/16

![A104348 - Humberto Gomes](../A104348.png)
