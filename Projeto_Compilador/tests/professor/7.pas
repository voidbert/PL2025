{-
CHANGES MADE:
 - Move var block to the beginning of the program (other orders aren't allowed in Standard Pascal)
-}

program BinarioParaInteiro;

var
    bin: string;
    valor: integer;

function BinToInt(bin: string): integer;
var
    i, valor, potencia: integer;
begin
    valor := 0;
    potencia := 1;
    for i := length(bin) downto 1 do
    begin
        if bin[i] = '1' then
            valor := valor + potencia;
        potencia := potencia * 2;
    end;

    BinToInt := valor;
end;

begin
    writeln('Introduza uma string binária:');
    readln(bin);
    valor := BinToInt(bin);
    writeln('O valor inteiro correspondente é: ', valor);
end.
