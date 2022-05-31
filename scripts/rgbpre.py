#!/usr/bin/env python3

from ast import keyword
from calendar import c
from multiprocessing import Condition
import os
import re
import argparse
import sys

from enum import Enum
from turtle import clear
from typing import List, Tuple
from xml.etree.ElementInclude import include

# sys.tracebacklimit = 0

# Keywords
# General
KEYWORD_BLOCK = "blk"
KEYWORD_END = "end"
KEYWORD_NAME = "name"

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
KEYWORD_CND = "cnd"

# Structs
KEYWORD_DATA_STRUCT = "ds"

# Assembler
KEYWORD_DEF = "def"
KEYWORD_EQU = "equ"

# Regex Templates
ALIAS_REGEX = r"^(\s)*" + KEYWORD_ALIAS + "(\s)*(\w)+,(.)*$"
BLOCK_REGEX = r"^(\s)*" + KEYWORD_BLOCK + "(\s)*(" + KEYWORD_PROGRAM + "|" + \
                                     KEYWORD_LOOP + "|" + \
                                     KEYWORD_FUNCTION + "|" + \
                                     KEYWORD_IF + "|" + \
                                     KEYWORD_DATA_STRUCT + ")?(\s)*$"
NAME_REGEX = r"^(\s)*" + KEYWORD_NAME + "(\s)*(\w)+(\s)*$"
END_REGEX = r"^(\s)*" + KEYWORD_END +"(\s)*$"
CONDITION_REGEX = r"^(\s)*cnd(\s)+\$?((\[)?\b(\w)+\b(\])?)(\s)+" +\
                  r"(ge|gt|eq|ne|le|lt|\=\=|\!\=|\>|\<|\<\=|\>\=)(\s)+" +\
                  r"\$?((\[)?\b(\w)+\b(\])?)(\s)*(and|or|\&\&|\|\|)?(\s)*$"
INCLUDE_REGEX = r"^(include)(\s)*\"((\w)+|(\/)*|(\w+)*|(.))+\"(\s)*$"
MEMORY_ALIAS_REGEX = r"^(\s)*(DEF|def)?(_|\w)*(\s)+(EQU|equ)(\s)*"
MACRO_REGEX = r"^(\s)*((_|(\w)*))(\s)*(:)(\s)*(macro|MACRO)(\s)*$"
LABEL_REGEX = r"^(\s)*(\.)?((_|(\w)*))(\s)*(:)(\s)*$"
NUMBER_REGEX = r"(\$|\&|%)?([0-9A-F]|[0-9a-f])+"
IDENTIFIER_NAME_REGEX = r"^[a-zA-Z_][a-zA-Z_0-9]*$"
CONDITIONAL_OPERATORS = ["ge", "gt", "eq", "ne",
                         "le", "lt", "==", "!=",
                         ">" , "<" , ">=", "<="]
TOKEN_EQUAL = ["eq", "EQ", "=="]
TOKEN_NOT_EQUAL = ["ne", "NE", "!="]
TOKEN_LESS_THAN = ["lt", "LT", "<"]
TOKEN_LESS_THAN_EQ_TO = ["le", "LE", "<="]
TOKEN_GREATER_THAN = ["gt", "GT", ">"]
TOKEN_GREATER_THAN_EQ_TO = ["ge", "GE", ">="]
BOOLEAN_OPERATORS = ["and", "or", "&&", "||"]
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

            KEYWORD_BLOCK, KEYWORD_BLOCK.upper(), KEYWORD_END, KEYWORD_END.upper(), KEYWORD_NAME, KEYWORD_NAME.upper(),
KEYWORD_ALIAS, KEYWORD_ALIAS.upper(), KEYWORD_LOOP, KEYWORD_LOOP.upper(), KEYWORD_BREAK, KEYWORD_BREAK.upper(),
KEYWORD_PROGRAM, KEYWORD_PROGRAM.upper(), KEYWORD_JUMP, KEYWORD_JUMP.upper(), KEYWORD_JUMP_RELATIVE, KEYWORD_JUMP_RELATIVE.upper(),
KEYWORD_FUNCTION, KEYWORD_FUNCTION.upper(), KEYWORD_CALL, KEYWORD_CALL.upper(), KEYWORD_RETURN, KEYWORD_RETURN.upper(),
KEYWORD_RETURN, KEYWORD_RETURN.upper(), KEYWORD_RETURN_I, KEYWORD_RETURN_I.upper(), KEYWORD_IF, KEYWORD_IF.upper(),
KEYWORD_ELSE, KEYWORD_ELSE.upper(), KEYWORD_CND, KEYWORD_CND.upper(), KEYWORD_DATA_STRUCT, KEYWORD_DATA_STRUCT.upper(),
KEYWORD_DEF, KEYWORD_DEF.upper(), KEYWORD_EQU, KEYWORD_EQU.upper(), ]

class LabelOperation(Enum):
  DEF_LABEL = "DEF_LABEL"
  UNDEF_LABEL = "UNDEF_LABEL"

class BlockMarkerType(Enum):
  BLOCK_START = "BLOCK_START"
  BLOCK_END = "BLOCK_END"

class BlockType(Enum):
  GENERIC_BLOCK = "GENERIC_BLOCK"
  IF_BLOCK = "IF_BLOCK"
  LP_BLOCK = "LP_BLOCK"
  FNC_BLOCK = "FNC_BLOCK"
  DS_BLOCK = "DS_BLOCK"
  PRG_BLOCK = "PRG_BLOCK"
  NONE_BLOCK = "NONE_BLOCK" # Used to mark an 'end' token

class FunctionArgumentType(Enum):
  IN_ARG = "IN_ARG"
  OUT_ARG = "OUT_ARG"

class IdentifierType(Enum):
  NAMED_CONSTANT = "NAMED_CONSTANT"
  MACRO = "MACRO"
  LABEL = "LABEL"

class ConditionalOperand(Enum):
  REGISTER = "REGISTER"
  MEMORY_ALIAS = "MEMORY_ALIAS"
  NUMBER = "NUMBER"
  INVALID = "INVALID"

class AssemblerIdentifier:
  def __init__(self, identifier_name: str, file_name: str, line: int, type: IdentifierType):
    self._identifier_name = identifier_name
    self._file_name = file_name
    self._line = line
    self._type = type

  @property
  def identifier_name(self) -> str:
    return self._identifier_name

  @property
  def file_name(self) -> str:
    return self._file_name

  @property
  def line(self) -> int:
    return self._line

  @property
  def type(self) -> IdentifierType:
    return self._type

class Block:
  def __init__(self, start: int, end: int,  type: BlockType, id: int):
    self._start = start
    self._end = end
    self._type = type
    self._id = id

  @property
  def start(self) -> int:
    return self._start

  @property
  def end(self) -> int:
    return self._end

  @property
  def id(self) -> int:
    return self._id

  @property
  def type(self) -> BlockType:
    return self._type

class BlockMarker:
  def __init__(self, position: int, type: BlockMarkerType):
    self._position = position
    self._type = type

  @property
  def position(self) -> int:
    return self._position

  @property
  def type(self) -> BlockMarkerType:
    return self._type

class Alias:
  def __init__(self, position: int, name: str, register: str,
                 op: LabelOperation, parent_block_id: int):
    self._position = position
    self._name = name
    self._register = register
    self._op = op
    self._parent_block_id = parent_block_id

  @property
  def position(self) -> int:
    return self._position

  @property
  def parent_block_id(self) -> int:
    return self._parent_block_id

  @property
  def name(self) -> str:
    return self._name

  @property
  def register(self) -> str:
    return self._register

  @property
  def operation(self) -> LabelOperation:
    return self._op

class FunctionArgument:
  def __init__(self,
               name:str,
               is_reference: bool) -> None:
    self._name = name
    self._is_reference = is_reference

  @property
  def name(self) -> str:
    return self._name

  @property
  def is_reference(self) -> bool:
    return self._is_reference

  @property
  def position(self) -> int:
    return self._pos

class Function:
  def __init__(self, name: str, block: Block):
    self._name = name
    self._block = block
    self._label = f"fn__{self._name}"

  @property
  def name(self) -> str:
    return self._name

  @property
  def block(self) -> Block:
    return self._block

  @property
  def label(self) -> str:
    return self._label

class Utils:
  @staticmethod
  def extract_line_no_comments(line: str) -> str:
    index = line.find(';')
    return line if index == -1 else line[:index]

  @staticmethod
  def extract_code_fragment_no_comment(lines: List[str], start: int, end: int) -> str:
    fragment = ""

    for line in range(start, end):
      fragment += Utils.extract_line_no_comments(lines[line])
    return fragment

  @staticmethod
  def get_flat_text(text: List[str]) -> str:
    flat_text = ""
    for line in text:
      flat_text += line

    return flat_text

  @staticmethod
  def split_tokens(text: str) -> List[str]:
    tokens = re.split('\s+', text)
    tokens = [x for x in tokens if len(x) != 0]
    return tokens

  @staticmethod
  def get_alignment(line: str) -> str:
    alignment = ""
    for char in range(0,len(line) - 1):
      if line[char:char+1].isspace():
        alignment += line[char:char+1]
    return alignment

  @staticmethod
  def load_file_source(file_path: str, include_path: List[str]) -> List[str]:
    contents = []
    os_path = ""
    try:
      os_path = os.path.abspath(file_path)
      with open(os_path) as f:
        contents = f.readlines()
    except:
      raise RuntimeError(f"Unable to open file {os_path}")

    return contents

  @staticmethod
  def locate_file(include_path: str,
                  cmd_include_path: List[str],
                  source: str,
                  line: int) -> str:
    os_path = ""
    for path in cmd_include_path:
      os_path = os.path.join(os.path.abspath(path), include_path)
      if os.path.exists(os_path):
        return os_path

    raise RuntimeError(f"Unable to locate file {os_path} found in '{source}' line {line}")

  @staticmethod
  def is_identifier_unique(identifier_list: List[AssemblerIdentifier],
                           target_identifier: str) -> bool:
    for id in identifier_list:
      if id.identifier_name == target_identifier:
        return False
    return True

  @staticmethod
  def is_assembler_identifier(identifier_list: List[AssemblerIdentifier],
                           target_identifier: str) -> bool:
    for id in identifier_list:
      if id.identifier_name == target_identifier:
        return True
    return False

  @staticmethod
  def is_valid_identifier(identifier: str) -> bool:
    if identifier in KEYWORDS:
      return False
    elif not re.match(IDENTIFIER_NAME_REGEX, identifier):
      return False

    return True

  @staticmethod
  def find_parent_block_id(line_number: int, blocks: List[Block]) -> int:
    min_diff = sys.maxsize
    min_id = -1

    for block in blocks:
      if line_number >= block.start and line_number <= block.end:
        diff = abs(block.start - line_number)
        if min_diff >= diff:
          min_diff = diff
          min_id = block.id

    return min_id

class FindIncludesPass:
  def __init__(self, input_file: str, source: List[str], include_path: List[str]):
    self._input_file = input_file
    self._raw_source = source
    self._cmd_include_path = include_path
    self._identifier_list = []

  def process(self) -> Tuple[List[str], List[AssemblerIdentifier]]:
    top_level_source = Utils.locate_file(self._input_file,
                                         self._cmd_include_path,
                                         self._input_file,
                                         1)
    print(f"Top level include {top_level_source}")
    self._include_list = [top_level_source]

    self._extract_includes(self._raw_source)
    self._extract_memory_aliasses()
    self._extract_macros()
    self._extract_labels()

    return [self._include_list, self._identifier_list]

  def _extract_memory_aliasses(self) -> None:
    for file in self._include_list:
      source = Utils.load_file_source(file, self._cmd_include_path)
      for idx, line in enumerate(source):
        clear_line = Utils.extract_line_no_comments(line)

        if re.match(MEMORY_ALIAS_REGEX, clear_line):
          tokens = Utils.split_tokens(line)

          if tokens[0].upper() == KEYWORD_DEF:
            self._identifier_list.append(AssemblerIdentifier(tokens[1],
                                                        file,
                                                        idx,
                                                        IdentifierType.NAMED_CONSTANT))
          else:
            self._identifier_list.append(AssemblerIdentifier(tokens[0],
                                                        file,
                                                        idx,
                                                        IdentifierType.NAMED_CONSTANT))

  def _extract_macros(self) -> None:
    for file in self._include_list:
      source = Utils.load_file_source(file, self._cmd_include_path)
      for idx, line in enumerate(source):
        clear_line = Utils.extract_line_no_comments(line)

        if re.match(MACRO_REGEX, clear_line):
          tokens = Utils.split_tokens(line)

          if ':' in tokens[0]:
            id = tokens[0].split(':')[0]
            self._identifier_list.append(AssemblerIdentifier(id,
                                                            file,
                                                            idx,
                                                            IdentifierType.MACRO))
          else:
            self._identifier_list.append(AssemblerIdentifier(tokens[0],
                                                            file,
                                                          idx,
                                                          IdentifierType.MACRO))

  def _extract_labels(self) -> None:
    for file in self._include_list:
      source = Utils.load_file_source(file, self._cmd_include_path)
      for idx, line in enumerate(source):
        clear_line = Utils.extract_line_no_comments(line)

        if re.match(LABEL_REGEX, clear_line):
          tokens = Utils.split_tokens(line)

          id = tokens[0]
          if ':' in id:
            id = id.split(':')[0]
          if '.' in id:
            id = id.split('.')[1]

          self._identifier_list.append(AssemblerIdentifier(id,
                                                           file,
                                                           idx,
                                                           IdentifierType.LABEL))

  def _extract_includes(self, source : List[str]) -> None:
    local_includes = []
    for idx, line in enumerate(source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(INCLUDE_REGEX, clear_line):
        include_path = self._extract_included_path(clear_line)
        os_included_path = Utils.locate_file(include_path,
                                             self._cmd_include_path,
                                             self._input_file,
                                             idx)

        if not self._path_already_exist(os_included_path):
          self._include_list.append(os_included_path)
          local_includes.append(os_included_path)

    self._extract_sub_includes(local_includes)

  def _extract_sub_includes(self, input_local_includes: List[str]) -> None:
    if len(input_local_includes) != 0:
      local_includes = []
      for include in input_local_includes:
        source = Utils.load_file_source(include, self._cmd_include_path)

        for idx, line in enumerate(source):
          clear_line = Utils.extract_line_no_comments(line)

          if re.match(INCLUDE_REGEX, clear_line):
            include_path = self._extract_included_path(clear_line)
            os_included_path = Utils.locate_file(include_path,
                                                  self._cmd_include_path,
                                                  self._input_file,
                                                  idx)

            if not self._path_already_exist(os_included_path):
              self._include_list.append(os_included_path)
              local_includes.append(os_included_path)

      self._extract_sub_includes(local_includes)

  def _path_already_exist(self, path: str) -> bool:
    for include_path in self._include_list:
      if (os.path.samefile(path, include_path)):
        return True

    return False

  def _extract_included_path(self, clear_line: str) -> str:
    include_path = ""
    path_started = False
    for char in clear_line:
      if path_started == False and char == '\"':
        path_started = True
        continue
      elif path_started == True and char == '\"':
        break

      if path_started == True:
        include_path += char

    return include_path

class BlocksMappingPass:
  def __init__(self, input_file: str, source: List[str]):
    self._raw_source = source
    self._input_file = input_file

  def process(self) -> Tuple[List[str], List[Block]]:
    self._processed_source = self._raw_source
    self._detect_blocks()
    self._validate_blocks()
    blocks = self._generate_blocks()
    return self._processed_source, blocks

  def _detect_blocks(self) -> None:
    self._block_list = []
    self._block_type_list = []

    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      if re.match(BLOCK_REGEX, clear_line):
        self._processed_source[idx] = f"; {line}"
        self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_START))
        self._block_type_list.append(self._detect_block_type(clear_line, idx))
      elif re.match(END_REGEX, clear_line):
        self._processed_source[idx] = f"; {line}"
        self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_END))
        self._block_type_list.append(self._detect_block_type(clear_line, idx))

  def _detect_block_type(self, line: str, idx: int) -> BlockType:
    # This function assumes a clear line as input (no comments)
    tokens = Utils.split_tokens(line)

    if len(tokens) == 1:
      return BlockType.GENERIC_BLOCK
    elif len(tokens) == 2:
      if tokens[1] == KEYWORD_LOOP:
        return BlockType.LP_BLOCK
      elif tokens[1] == KEYWORD_IF:
        return BlockType.IF_BLOCK
      elif tokens[1] == KEYWORD_FUNCTION:
        return BlockType.FNC_BLOCK
      elif tokens[1] == KEYWORD_DATA_STRUCT:
        return BlockType.DS_BLOCK
      elif tokens[1] == KEYWORD_PROGRAM:
        return BlockType.PRG_BLOCK
      else:
        raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: invalid block type")
    else:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: invalid block structure")

  def _validate_blocks(self) -> None:
    block_stack = []

    for block in self._block_list:
      if block.type == BlockMarkerType.BLOCK_START:
        block_stack.append(1)
      elif block.type == BlockMarkerType.BLOCK_END:
        if len(block_stack) == 0:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{block.position + 1}: unexpected 'end'")
        block_stack.pop()

    if len(block_stack) != 0:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{len(self._processed_source)}: 'end' expected")

  def _generate_blocks(self) -> List[Block]:
    blocks = []
    blocks_start = []
    block_start = []
    blocks_type = []
    block_end = 0

    for idx, block in enumerate(self._block_list):
      if block.type == BlockMarkerType.BLOCK_START:
        blocks_start.append(block.position)
        blocks_type.append(self._block_type_list[idx])
      elif block.type == BlockMarkerType.BLOCK_END:
        block_start = blocks_start.pop()
        block_type = blocks_type.pop()
        block_end = block.position

        new_block = Block(block_start, block_end, block_type, len(blocks))
        blocks.append(new_block)

    for block in blocks:
      if (block.type == BlockType.IF_BLOCK or \
          block.type == BlockType.LP_BLOCK) and \
         (block.start == 0 or \
         Utils.find_parent_block_id(block.start - 1, blocks) == -1):
        block_type = "if" if block.type == BlockType.IF_BLOCK else "lp"
        raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                           f"{block.start + 1}: unexpected '{block_type}' block found")

    return blocks

class RegisterAliasPass:
  def __init__(self,
               input_file: str,
               source: List[str],
               blocks: List[Block],
               identifiers: List[AssemblerIdentifier],
               functions: List[Block]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks
    self._identifiers = identifiers
    self._functions = functions

  @property
  def processed_source(self) -> List[str]:
    return self._processed_source

  def process(self) -> None:
    aliasses = self._locate_alias_operations()

    self._process_source(aliasses)
    self._correct_remaining_aliases(aliasses)

    return self._processed_source

  def _locate_alias_operations(self) -> List[Alias]:
    aliasses = []
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(ALIAS_REGEX, clear_line):
        self._raw_source[idx] = f"; {line}"

        proper_command = re.split(KEYWORD_ALIAS, clear_line)[1]
        target_alias = re.split(',', proper_command)[1].strip()
        target_register = re.split(',', proper_command)[0].strip()
        parent_block_id = Utils.find_parent_block_id(idx, self._blocks)

        if not Utils.is_valid_identifier(target_alias):
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                              f"{idx + 1}: Invalid identifier '{target_alias}' " +
                              f"detected")

        if not Utils.is_identifier_unique(self._identifiers, target_alias):
          identifier = [x for x in self._identifiers if x.identifier_name == target_alias][0]
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                              f"{idx + 1}: identifier '{target_alias}' " +
                              f"already defined in {identifier.file_name}, line {identifier.line + 1}")

        for alias in [x for x in aliasses if x.parent_block_id == parent_block_id]:
          if alias.name == target_alias:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: alias '{target_alias}' " +
                                "has already been defined in this scope")

        if parent_block_id == -1:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                              f"{idx + 1}: Aliasses must be declared inside of 'blk' scopes")

        aliasses.append(Alias(idx, target_alias,
                              target_register,
                              LabelOperation.DEF_LABEL, parent_block_id))
    return aliasses

  def _find_decendent_blocks(self, line_number: int) -> List[Block]:
    blocks = []
    for block in self._blocks:
      if line_number >= block.start and line_number <= block.end:
        blocks.append(block)

    return blocks

  def _process_source(self, aliasses: List[Alias]) -> None:
    self._processed_source = []
    names = [x.name for x in aliasses]
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)
      split_line = Utils.split_tokens(clear_line)

      for line_token in split_line:
        if line_token not in KEYWORDS and Utils.is_valid_identifier(line_token) and \
           not Utils.is_assembler_identifier(self._identifiers, line_token) and \
           line_token not in names and line_token not in self._functions:
            print (f"{os.path.basename(self._input_file)} line " +
                   f"{idx + 1}: Warning: Undeclared identifier '{line_token}'")

      line_text = line
      for line_token in split_line:
        for target_alias in [x for x in aliasses]:
          if re.search(r"\b" + (target_alias.name) + r"\b" , line_token):
            if target_alias.position > idx:
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                f"{idx + 1}: Undeclared alias '{target_alias.name}'")
            line_text = line.replace(target_alias.name, target_alias.register)
            break

      self._processed_source.append(line_text)

  def _correct_remaining_aliases(self, aliasses: List[Alias]) -> None:
    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      for target_alias in aliasses:
        if re.search(r"\b" + (target_alias.name) + r"\b" , clear_line):
          decendent = [x.id for x in self._find_decendent_blocks(idx)]
          allowed_aliases = []
          for alias in aliasses:
            if idx >= alias.position and \
                alias.parent_block_id in decendent and \
                alias.name == target_alias.name:
                allowed_aliases.append(alias)

          if len(allowed_aliases) == 0:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                            f"{idx + 1}: Undeclared alias '{target_alias.name}'")
          else:
            candidate_alias = [x for x in allowed_aliases if x.name == target_alias.name]
            closest_index = -1
            min_diff = sys.maxsize
            for alias_index, alias in enumerate(candidate_alias):
              diff = abs(idx - alias.position)
              if min_diff >= diff:
                min_diff = diff
                closest_index = alias_index

            line_text = line.replace(target_alias.name, candidate_alias[closest_index].register)
            self._processed_source[idx] = line_text

class FunctionPass:
  def __init__(self, input_file: str, source: List[str], blocks: List[Block]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks

  def process(self) -> None:
    self._processed_source = self._raw_source
    functions_blocks = self._find_functions()
    functions = self._process_function(functions_blocks)
    self._emit_function_body(functions)
    self._correct_calls(functions)
    self._issue_warnings(functions)
    return functions, self._processed_source

  def _find_functions(self) -> List[Block]:
    return [x for x in self._blocks if x.type == BlockType.FNC_BLOCK]

  def _process_function(self, func_blocks: List[Block]) -> Function:
    functions = []

    for block in func_blocks:
      self._validate_function_body(block)
      name = self._extract_function_name(block)

      function = Function(name, block)
      functions.append(function)
    return functions

  def _validate_function_body(self, blk: Block) -> None:
    name_found = False
    function_body = False

    for line in range(blk.start, blk.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line])

      if re.match(NAME_REGEX, clear_line) and function_body == False:
        if name_found == False:
          name_found = True
        else:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{line + 1}: only one 'name' allowed per function body")
      else:
          if name_found == True and function_body == False:
            function_body = True
          else:
            if re.match(NAME_REGEX, clear_line):
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: unexpected '{clear_line.strip()}' found")

  def _extract_function_name(self, blk: Block) -> str:
    name = ""
    for line in range(blk.start, blk.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line])
      if re.match(NAME_REGEX, clear_line):
        tokens = Utils.split_tokens(clear_line)

        if name != "":
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: unexpected keyword 'name' " +
                               f"in function '{name}'")
        self._processed_source[line] = f"; {self._raw_source[line]}"
        name = tokens[1]

    return name

  def _emit_function_body(self, functions: List[Function]) -> None:
    for func in functions:
      self._processed_source[func.block.start] =\
        f"{func.label}: {self._processed_source[func.block.start]}"

  def _correct_calls(self, functions: List[Function]) -> None:
    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      tokens = Utils.split_tokens(clear_line)
      if KEYWORD_CALL in tokens:
        for func in functions:
          if func.name in tokens:
            self._processed_source[idx] = line.replace(func.name, func.label)

  def _issue_warnings(self, functions) -> None:
    for func in functions:
      has_return = False
      for line in range(func.block.start, func.block.end):
        clear_line = Utils.extract_line_no_comments(self._raw_source[line])
        tokens = Utils.split_tokens(clear_line)
        if KEYWORD_RETURN in tokens or \
           KEYWORD_RETURN_I in tokens:
           has_return = True

      if has_return != True:
         print(f"Warning: {os.path.basename(self._input_file)} line " +
               f"{line + 1}: function '{func.name}' expected to have a return point ('ret'/'reti')")

    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      tokens = Utils.split_tokens(clear_line)
      if KEYWORD_JUMP in tokens or \
         KEYWORD_JUMP_RELATIVE in tokens:
        for func in functions:
          if func.name in tokens:
            print(f"Warning: {os.path.basename(self._input_file)} line " +
                  f"{idx + 1}: branching to function '{func.name}' without using 'call'")

class ConditionPass:
  def __init__(self, input_file: str, source: List[str], raw_source: List[str], blocks: List[Block]):
    self._raw_source = raw_source
    self._processed_source = source
    self._input_file = input_file
    self._blocks = blocks

  def process(self) -> None:
    conditional_blocks = self._find_conditional_blocks()
    self._validate_conditional_blocks(conditional_blocks)
    self._parse_conditions(conditional_blocks)

    return self._processed_source

  def _find_conditional_blocks(self) -> List[Block]:
    return [x for x in self._blocks if x.type == BlockType.IF_BLOCK]

  def _parse_conditions(self, conditional_blocks: List[Block]) -> None:
    for block in conditional_blocks:
      print(f"Condition block at {block.start + 1}")
      self._processed_source[block.end] += "\n<condition_end>:\n"
      for line in range(block.start, block.end):
        clear_line = Utils.extract_line_no_comments(self._processed_source[line])
        if re.match(CONDITION_REGEX, clear_line):
          tokens = Utils.split_tokens(clear_line)
          self._validate_condition(tokens, line)
          converted_condition = self._convert_condition(tokens, clear_line)
          self._processed_source[line] = converted_condition;
          print(converted_condition)

  def _validate_conditional_blocks(self, conditional_blocks: List[Block]) -> None:
    for block in conditional_blocks:
      in_conditions_list = False
      in_condition_body = False
      condition_list_start = 0
      condition_list_end = 0
      skip_inner_block = []
      for line in range(block.start + 1, block.end):
        clear_line = Utils.extract_line_no_comments(self._raw_source[line])
        if len(skip_inner_block) != 0:
          if re.match(BLOCK_REGEX, clear_line):
            skip_inner_block.append(1)
          elif re.match(END_REGEX, clear_line):
            skip_inner_block.pop()
        else:
          if in_conditions_list == False and \
            in_condition_body == False and \
            re.match(CONDITION_REGEX, clear_line):
            in_conditions_list = True
            condition_list_start = line
          elif in_conditions_list == True and \
              in_condition_body == False and \
              not re.match(CONDITION_REGEX, clear_line):
            in_condition_body = True
            in_conditions_list = False
            condition_list_end = line - 1
          elif in_condition_body == True and \
               in_conditions_list == False and \
               re.match(BLOCK_REGEX, clear_line):
            skip_inner_block.append(1)
          elif in_condition_body == True and \
            re.match(CONDITION_REGEX, clear_line):
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: unexpected 'cnd' found")

      if abs(condition_list_end - condition_list_start) >= 2:
        for line in range(condition_list_start, condition_list_end):
          clear_line = Utils.extract_line_no_comments(self._raw_source[line])
          tokens = Utils.split_tokens(clear_line)
          if len(tokens) == 0:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: expected 'cnd'")
          if tokens[-1] not in BOOLEAN_OPERATORS:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: expected 'and' or 'or'")
      # Check last condition
      clear_line = Utils.extract_line_no_comments(self._raw_source[condition_list_end])
      tokens = Utils.split_tokens(clear_line)
      if len(tokens) == 0:
        raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: expected 'cnd'")
      if tokens[-1] in BOOLEAN_OPERATORS:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{condition_list_end + 1}: unexpected '{tokens[-1]}'")

  def _convert_condition(self, tokens: List[str], clear_line: str) -> str:
    # TODO: Conditional Code Emission is not correct
    # Classify conditions
    # Emit code accordingly
    alignment = Utils.get_alignment(clear_line)
    condition = f";{clear_line[:-1]}\n"

    condition_left_side = ConditionalOperand.INVALID
    # Left Side
    if tokens[1] in TOKEN_REGISTER:
      print(f"Condition Left side is a register ('{tokens[1]}')")
      condition_left_side = ConditionalOperand.REGISTER
    elif re.match(NUMBER_REGEX, tokens[1]):
      print(f"Condition Left side is a number ('{tokens[1]}')")
      condition_left_side = ConditionalOperand.NUMBER

    condition_right_side = ConditionalOperand.INVALID
    # Right Side
    if tokens[3] in TOKEN_REGISTER:
      print(f"Condition Right side is a register ('{tokens[3]}')")
      condition_right_side = ConditionalOperand.REGISTER
    elif re.match(NUMBER_REGEX, tokens[3]):
      print(f"Condition Right side is a number ('{tokens[3]}')")
      condition_right_side = ConditionalOperand.NUMBER

    condition += self._emit_condition_code(
            condition_left_side,
            tokens[1],
            condition_right_side,
            tokens[3],
            self._convert_logic_operator_to_jr_condition(
            self._negate_logic_operator(tokens[2])),
            alignment)

    return condition

  def _convert_logic_operator_to_jr_condition(self, operator: str) -> List[str]:
    if operator in TOKEN_EQUAL:
      return ["z"]
    elif operator in TOKEN_NOT_EQUAL:
      return ["nz"]
    elif operator in TOKEN_LESS_THAN:
      return ["c"]
    elif operator in TOKEN_LESS_THAN_EQ_TO:
      return ["c", "z"]
    elif operator in TOKEN_GREATER_THAN:
      return ["nc"]
    elif operator in TOKEN_GREATER_THAN_EQ_TO:
      return ["nc", "z"]

  def _negate_logic_operator(self, operator: str) -> str:
    if operator in TOKEN_EQUAL:
      return TOKEN_NOT_EQUAL[0]
    elif operator in TOKEN_NOT_EQUAL:
      return TOKEN_EQUAL[0]
    elif operator in TOKEN_LESS_THAN:
      return TOKEN_GREATER_THAN_EQ_TO[0]
    elif operator in TOKEN_LESS_THAN:
      return TOKEN_GREATER_THAN[0]
    elif operator in TOKEN_GREATER_THAN:
      return TOKEN_LESS_THAN[0]
    elif operator in TOKEN_GREATER_THAN_EQ_TO:
      return TOKEN_LESS_THAN[0]

  def _emit_condition_code(self,
                           left: ConditionalOperand,
                           left_operand: str,
                           right: ConditionalOperand,
                           right_operand: str,
                           logic_operators: List[str],
                           alignment: str) -> str:
    condition = f"{alignment}ld a, {left_operand}\n"
    condition += f"{alignment}cp {right_operand}\n"

    for idx, operator in enumerate(logic_operators):
      condition += f"{alignment}jr {operator}, <condition_end>\n"

    return condition

  def _validate_condition(self, tokens: List[str], line: int) -> None:
    if tokens[0] != KEYWORD_CND:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: expected 'cnd' found {tokens[0]}")
    if tokens[2] not in CONDITIONAL_OPERATORS:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: unexpected {tokens[2]} found")
    if len(tokens) == 5 and tokens[4] not in BOOLEAN_OPERATORS:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: unexpected {tokens[4]} found")

def main():
  parser = argparse.ArgumentParser(description='rgb pre-processor')
  parser.add_argument('-i', '--input', type=str,
                      help='Input file name', nargs=1)
  parser.add_argument('-o', '--output', type=str,
                      help='Output file name', nargs=1)
  parser.add_argument('-I', '--include', type=str,
                      help='Include directory', nargs="*")
  args = parser.parse_args()

  # Acquire arguments
  input_path = args.input[0]
  output_path = args.output[0]
  include_path = args.include
  if include_path == None:
    include_path = []
  include_path.append(os.getcwd())
  include_path = list(set(include_path))

  # process file
  process_file(input_path, output_path, include_path)


def process_file(input_file: str, output_file: str, include_path: List[str]) -> None:
  file_source = Utils.load_file_source(input_file, include_path)
  raw_source = file_source.copy()
  included_file_list = FindIncludesPass(input_file, file_source, include_path)
  included_files, identifiers = included_file_list.process()
  blocks_detection_pass = BlocksMappingPass(input_file, file_source)
  file_source, blocks = blocks_detection_pass.process()
  functions_pass = FunctionPass(input_file, file_source, blocks)
  function_names, file_source = functions_pass.process()
  reg_alias_pass = RegisterAliasPass(input_file, file_source, blocks, identifiers, function_names)
  file_source = reg_alias_pass.process()
  conditions_pass = ConditionPass(input_file, file_source, raw_source, blocks)
  file_source = conditions_pass.process()

  final_source = file_source
  #save file
  with open(output_file, 'w') as f:
    f.write(Utils.get_flat_text(final_source))

if __name__ == "__main__":
    main()