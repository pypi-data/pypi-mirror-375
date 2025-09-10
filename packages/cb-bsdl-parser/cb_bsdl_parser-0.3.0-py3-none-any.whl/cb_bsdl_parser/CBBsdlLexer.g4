lexer grammar CBBsdlLexer;

// Keywords
ENTITY           : 'entity' ;
END              : 'end' ;
IS               : 'is' ;
GENERIC          : 'generic' ;
STRING           : 'string' ;
PHYSICAL_PIN_MAP : 'PHYSICAL_PIN_MAP' ;
ATTRIBUTE        : 'attribute' ;
BS_LEN           : 'BOUNDARY_LENGTH' ;
BS_REG           : 'BOUNDARY_REGISTER' ;
OF               : 'of' ;
USE              : 'use' ;

PORT             : 'port' ;
INOUT            : 'inout' ;
IN               : 'in' ;
OUT              : 'out' ;
LINKAGE          : 'linkage' ;
BIT              : 'bit' ;
BIT_VECTOR       : 'bit_vector';
TO               : 'to' ;
DOWNTO           : 'downto' ;


// SPECIAL CHARS
DOT                  : '.' ;
COMMA                : ',' ;
COLON                : ':' ;
SEMICOLON            : ';' ;
BRACKET_OPEN         : '(' ;
BRACKET_CLOSE        : ')' ;
AMPERSAND            : '&' ;
QUOTES               : '"' ;
EQUALS               : ':=' ;
ASTERISK             : '*' ;
UNDERLINE            : '_' ;
SQUARE_OPEN          : '[' ;
SQUARE_CLOSE         : ']' ;






// lexer rules
ID: [a-zA-Z_][a-zA-Z0-9_]*;



REAL_LITERAL
    : INTEGER '.' INTEGER (EXPONENT)?
    ;

INTEGER
    : DIGIT ('_' | DIGIT)*
    ;

DIGIT
    : '0' ..'9'
    ;

EXPONENT
    : 'E' ('+' | '-')? INTEGER
    ;




// Whitespace
WS: [ \t\n\r]+ -> skip;

// Comments
COMMENT: '--' ~[\r\n]* -> skip;

