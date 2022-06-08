# Keywords
# General
KEYWORD_BLOCK = "blk"
KEYWORD_END = ["end", '\}']
KEYWORD_BGN = ["bgn", '\{']
KEYWORD_NAME = ".name:"

# Alias
KEYWORD_ALIAS = "als"

# Loop
KEYWORD_LOOP = "lp"
KEYWORD_BREAK = "brk"

# Progam
KEYWORD_PROGRAM = "prg"
KEYWORD_JUMP = "jp"
KEYWORD_JUMP_RELATIVE = "jr"

# Functions
KEYWORD_FUNCTION = "fn"
KEYWORD_CALL = "call"
KEYWORD_RETURN = "ret"
KEYWORD_RETURN_I = "reti"

# Conditions
KEYWORD_IF = "if"
KEYWORD_ELSE = "else"
KEYWORD_CND = ".cnd:"

# Structs/vars
KEYWORD_DATA_STRUCT = "ds"
KEYWORD_ATTRIBUTE = "attr"
KEYWORD_BYTE = "byte"
KEYWORD_HALF = "half"
KEYWORD_WORD = "word"
KEYWORD_LONG = "long"

# Assembler
KEYWORD_DEF = "def"
KEYWORD_EQU = "equ"

# Regex Templates
ALIAS_REGEX = r"^(\s)*" + KEYWORD_ALIAS + "(\s)*(\w)+,(.)*$"
BLOCK_HEADER_BLK_REGEX = r"(\s)*blk(\s)*"
BLOCK_HEADER_PRG_REGEX = r"(\s)*blk(\s)+prg(\s)*"
BLOCK_HEADER_LP_REGEX =  r"(\s)*blk(\s)+lp(\s)*"
BLOCK_HEADER_IF_REGEX =  r"(\s)*blk(\s)+if(\s)*"
BLOCK_HEADER_FN_REGEX =  r"(\s)*blk(\s)+fn(\s)*"
BLOCK_HEADER_DS_REGEX =  r"(\s)*blk(\s)+ds(\s)*"

IDENTIFIER_REGEX = r"([a-zA-Z_$][a-zA-Z_$0-9]*)"

BLOCK_BLK_REGEX = r"(\s)*blk(\s)+(bgn|\{)"
BLOCK_PRG_REGEX = r"(\s)*blk(\s)+prg(\s)+\.name:(\s)+"+IDENTIFIER_REGEX+"+(\s)*(bgn|\{)"
BLOCK_LP_REGEX =  r"(\s)*blk(\s)+lp(\s)+(bgn|\{)"
BLOCK_IF_REGEX =  r"(\s)*blk(\s)+if(\s)+(\.cnd:(.*)(\s)*)*(bgn|\{)"
BLOCK_FN_REGEX =  r"(\s)*blk(\s)+fn(\s)+\.name:(\s)+"+IDENTIFIER_REGEX+"+(\s)*(bgn|\{)"
BLOCK_DS_REGEX =  r"(\s)*blk(\s)+ds(\s)+\.name:(\s)+"+IDENTIFIER_REGEX+"+(\s)*(bgn|\{)"

ATTRIBUTE_DECLARATION_REGEX = r"^(\s)*" + KEYWORD_ATTRIBUTE + "(\s)+" + IDENTIFIER_REGEX + "(\s)*,(\s)*(\w)+(\s)*$"

NAME_REGEX = r"^(\s)*" + KEYWORD_NAME + "(\s)*"+ IDENTIFIER_REGEX +"(\s)*$"
END_REGEX = r"^(\s)*(end|\})" + "(\s)*$"
BGN_REGEX = r"^(\s)*(bgn|\{)" + "(\s)*$"
CONDITION_REGEX = r"^(\s)*\.cnd:(\s)+\$?((\[)?(.*)(\])?)(\s)+" +\
                  r"(ge|gt|eq|ne|le|lt|\=\=|\!\=|\>|\<|\<\=|\>\=)(\s)+" +\
                  r"\$?((\[)?(.*)(\])?)(\s)*(and|or|\&\&|\|\|)?(\s)*$"
INCLUDE_REGEX = r"^(include)(\s)*\"((\w)+|(\/)*|(\w+)*|(.))+\"(\s)*$"
MEMORY_ALIAS_REGEX = r"^(\s)*(DEF|def)?(_|\w)*(\s)+(EQU|equ)(\s)*"
MACRO_REGEX = r"^(\s)*((_|(\w)*))(\s)*(:)(\s)*(macro|MACRO)(\s)*$"
LABEL_REGEX = r"^(\s)*(\.)?((_|(\w)*))(\s)*(:)(\s)*$"
NUMBER_REGEX = r"((\$|\&|%)?([0-9A-F]|[0-9a-f]))+"
IDENTIFIER_NAME_REGEX = r"^" + IDENTIFIER_REGEX + "$"
CONDITIONAL_OPERATORS = ["ge", "gt", "eq", "ne",
                         "le", "lt", "==", "!=",
                         ">" , "<" , ">=", "<="]
TOKEN_EQUAL = ["eq", "EQ", "=="]
TOKEN_NOT_EQUAL = ["ne", "NE", "!="]
TOKEN_LESS_THAN = ["lt", "LT", "<"]
TOKEN_LESS_THAN_EQ_TO = ["le", "LE", "<="]
TOKEN_GREATER_THAN = ["gt", "GT", ">"]
TOKEN_GREATER_THAN_EQ_TO = ["ge", "GE", ">="]
LOGICAL_OPERATORS = ["and", "or", "&&", "||"]
TOKEN_REGISTER_A = ["a", "A"]
TOKEN_REGISTER_B = ["b", "B"]
TOKEN_REGISTER_C = ["c", "C"]
TOKEN_REGISTER_D = ["d", "D"]
TOKEN_REGISTER_E = ["e", "E"]
TOKEN_REGISTER_H = ["h", "H"]
TOKEN_REGISTER_L = ["l", "L"]
TOKEN_REGISTER_AF = ["af", "AF"]
TOKEN_REGISTER_BC = ["bc", "BC"]
TOKEN_REGISTER_DE = ["de", "DE"]
TOKEN_REGISTER_HL = ["hl", "HL"]
TOKEN_REGISTER =  ["a", "A", "b", "B", "c", "C", "d", "D", "e", "E",
                   "h", "H", "l", "L", "af", "AF", "bc", "BC", "de",
                   "DE", "hl", "HL",]
KEYWORDS = ["DEF", "BANK", "ALIGN", "SIZEOF" , "STARTOF", "SIN" , "COS" , "TAN",
            "ASIN" , "ACOS" , "ATAN" , "ATAN2", "FDIV", "FMUL", "POW", "LOG",
            "ROUND", "CEIL" , "FLOOR", "HIGH" , "LOW", "ISCONST", "STRCMP",
            "STRIN", "STRRIN", "STRSUB", "STRLEN", "STRCAT", "STRUPR",
            "STRLWR", "STRRPL", "STRFMT", "CHARLEN", "CHARSUB", "EQU", "SET",
            "=", "EQUS", "+=", "-=", "*=", "/=" , "%=", "|=", "^=", "&=", "<<=",
            ">>=", "INCLUDE", "PRINT" , "PRINTLN", "IF", "ELIF" , "ELSE" ,
            "ENDC", "EXPORT", "DB" , "DS" , "DW" , "DL", "SECTION" , "FRAGMENT",
            "RB , RW", "MACRO", "ENDM", "RSRESET" , "RSSET", "UNION" , "NEXTU" ,
            "ENDU", "INCBIN" , "REPT" , "FOR", "CHARMAP", "NEWCHARMAP",
            "SETCHARMAP", "PUSHC", "POPC", "SHIFT", "ENDR", "BREAK",
            "LOAD", "ENDL", "FAIL", "WARN", "FATAL", "ASSERT",  "STATIC_ASSERT",
            "PURGE", "REDEF", "POPS", "PUSHS", "POPO", "PUSHO", "OPT", "ROM0" ,
            "ROMX", "WRAM0" , "WRAMX" , "HRAM", "VRAM" , "SRAM" , "OAM", "ADC" ,
            "ADD" , "AND", "BIT" , "BIT", "BIT", "CALL" , "CCF" , "CP" , "CPL",
            "DAA" , "DEC" , "DI", "EI", "HALT", "INC", "JP" , "JR", "LD", "LDI",
            "LDD", "LDH", "NOP", "OR", "POP" , "PUSH", "RES" , "RET" , "RETI" ,
            "RST", "RL" , "RLA" , "RLC" , "RLCA", "RR" , "RRA" , "RRC" , "RRCA",
            "SBC" , "SCF" , "STOP", "SLA", "SRA", "SRL" , "SUB", "SWAP", "XOR",
            "A", "B" , "C", "D" , "E", "H" , "L", "AF" , "BC" , "DE" , "SP",
            "HL" ,  "HLD/HL-" ,  "HLI/HL+", "NZ" , "Z", "NC", "def", "bank",
            "align", "sizeof" , "startof", "sin" , "cos" , "tan", "asin" ,
            "acos" , "atan" , "atan2", "fdiv", "fmul", "pow", "log", "round",
            "ceil" , "floor", "high" , "low", "isconst", "strcmp", "strin",
            "strrin", "strsub", "strlen", "strcat", "strupr", "strlwr",
            "strrpl", "strfmt", "charlen", "charsub", "equ", "set", "=",
            "equs", "+=", "-=", "*=", "/=" , "%=", "|=", "^=", "&=", "<<=",
            ">>=", "include", "print" , "println", "if", "elif" , "else" ,
            "endc", "export", "db" , "ds" , "dw" , "dl", "section" , "fragment",
            "rb , rw", "macro", "endm", "rsreset" , "rsset", "union" , "nextu" ,
            "endu", "incbin" , "rept" , "for", "charmap", "newcharmap",
            "setcharmap", "pushc", "popc", "shift", "endr", "break", "load",
            "endl", "fail", "warn", "fatal", "assert",  "static_assert",
            "purge", "redef", "pops", "pushs", "popo", "pusho", "opt", "rom0" ,
            "romx", "wram0" , "wramx" , "hram", "vram" , "sram" , "oam", "adc" ,
            "add" , "and", "bit" , "bit", "bit", "call" , "ccf" , "cp" , "cpl",
            "daa" , "dec" , "di", "ei", "halt", "inc", "jp" , "jr", "ld", "ldi",
            "ldd", "ldh", "nop", "or", "pop" , "push", "res" , "ret" , "reti" ,
            "rst", "rl" , "rla" , "rlc" , "rlca", "rr" , "rra" , "rrc" , "rrca",
            "sbc" , "scf" , "stop", "sla", "sra", "srl" , "sub", "swap", "xor",
            "a", "b" , "c", "d" , "e", "h" , "l", "af" , "bc" , "de" , "sp",
            "hl" ,  "hld/hl-" ,  "hli/hl+", "nz" , "z", "nc,", "ne", "NE", "!=", "eq", "EQ", "==", "lt", "LT", "<", "le", "LE", "<=", "gt", "GT", ">", "ge", "GE", ">=", "and", "or", "&&", "||",
            KEYWORD_BLOCK, KEYWORD_BLOCK.upper(), KEYWORD_END[0], KEYWORD_END[0].upper(), KEYWORD_END[1],
            KEYWORD_BGN[0], KEYWORD_BGN[0].upper(), KEYWORD_BGN[1], KEYWORD_NAME, KEYWORD_NAME.upper(),
KEYWORD_ALIAS, KEYWORD_ALIAS.upper(), KEYWORD_LOOP, KEYWORD_LOOP.upper(), KEYWORD_BREAK, KEYWORD_BREAK.upper(),
KEYWORD_PROGRAM, KEYWORD_PROGRAM.upper(), KEYWORD_JUMP, KEYWORD_JUMP.upper(), KEYWORD_JUMP_RELATIVE, KEYWORD_JUMP_RELATIVE.upper(),
KEYWORD_FUNCTION, KEYWORD_FUNCTION.upper(), KEYWORD_CALL, KEYWORD_CALL.upper(), KEYWORD_RETURN, KEYWORD_RETURN.upper(),
KEYWORD_RETURN, KEYWORD_RETURN.upper(), KEYWORD_RETURN_I, KEYWORD_RETURN_I.upper(), KEYWORD_IF, KEYWORD_IF.upper(),
KEYWORD_ELSE, KEYWORD_ELSE.upper(), KEYWORD_CND, KEYWORD_CND.upper(), KEYWORD_DATA_STRUCT, KEYWORD_DATA_STRUCT.upper(),
KEYWORD_DEF, KEYWORD_DEF.upper(), KEYWORD_EQU, KEYWORD_EQU.upper(), ]
