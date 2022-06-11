import os
import re
from typing import List, Tuple

from enums import BlockType
from constants import *
from support.block import Block
from support.program import Program
from utils import Utils

class ProgramPass:
  def  __init__(self,
                input_file: str,
                source: List[str],
                blocks: List[Block]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks

  def process(self) -> Tuple[Program, List[str]]:
    prog_blocks = [x for x in self._blocks if x.type == BlockType.PRG_BLOCK]
    self._validate_blocks(prog_blocks)
    self._program = self._process_prog_block(prog_blocks[0])
    return self._program, self._raw_source

  def _process_prog_block(self, prog_block:Block) -> Program:
    program = None
    for line in range(prog_block.start, prog_block.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line])
      if re.match(NAME_REGEX, clear_line):
        tokens = Utils.split_tokens(clear_line)

        if Utils.is_valid_identifier(tokens[1]) == False:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{line + 1}: invalid program identifier '{tokens[1]}'")

        program = Program(tokens[1], self._input_file)
        self._raw_source[line] = f'{program.name}: ;{self._raw_source[line]}'
        return program

    raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                       f"{prog_block.start + 1}: program name expected")


  def _validate_blocks(self, prog_blocks: List[Block]) -> None:
    if len(prog_blocks) == 0:
      raise RuntimeError(f"{os.path.basename(self._input_file)}: " +
                         f"entry point 'prg' program blocks required.")
    if len(prog_blocks) > 1:
      raise RuntimeError(f"{os.path.basename(self._input_file)}: " +
                         f"multiple entry point 'prg' program blocks detected.")
