{ Please compile this with optimizations (-Og) and check if they are being applied }

program optimizatons;
var
    b, c : boolean;
    x, y : integer;
    xf, yf : real;
begin
    x := (1 + (3 * 2)) + x;
    y := -((1 + 1) + y);

    b := not (not (not (not b)));
    b := (not b) and (not c);
    b := (not b) or (not c);
    b := (not b) or c;
    b := not (x > y);
    b := not (xf < yf);
end.
