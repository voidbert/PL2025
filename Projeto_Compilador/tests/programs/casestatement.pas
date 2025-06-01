program casestatement;
var
    grade: char;
begin
    read(grade);
    case grade of
        'A' : writeln('Excellent!');
        'B', 'C': writeln('Well done');
        'D' : writeln('You passed');
        'F' : writeln('Better try again');
   end; 
end.
