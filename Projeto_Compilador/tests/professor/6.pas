program BinarioParaInteiro;
var
    bin: string;
    i, valor, potencia: integer;
begin
    writeln('Introduza uma string binária:');
    readln(bin);
    valor := 0;
    potencia := 1;

    for i := length(bin) downto 1 do
    begin
        if bin[i] = '1' then
            valor := valor + potencia;
        potencia := potencia * 2;
    end;

    writeln('O valor inteiro correspondente é: ', valor);
end.
