#!/usr/bin/env python3

import os
import re
import argparse
import sys

from enum import Enum
from typing import List

sys.tracebacklimit = 0

DEF_STRUCTURE_REGEX = r"^(\s)*!alias(\s)*(\w)+,(\s)*(\w)+(\s)*$"
UNDEF_STRUCTURE_REGEX = r"^(\s)*!unalias(\s)*(\w)+(\s)*$"

class Utils:
  @staticmethod
  def extract_line_no_comments(line: str) -> str:
    index = line.find(';')
    return line if index == -1 else line[:index]

  @staticmethod
  def get_flat_text(text: List[str]) -> str:
    flat_text = ""
    for line in text:
      flat_text += line

    return flat_text

class LabelOperation(Enum):
  DEF_LABEL = "DEF_LABEL"
  UNDEF_LABEL = "UNDEF_LABEL"

class RegisterLabelOperation:
  def __init__(self, position: int, alias: str, register: str,
                 op: LabelOperation):
    self._position = position
    self._alias = alias
    self._register = register
    self._op = op

  @property
  def position(self) -> int:
    return self._position

  @property
  def alias(self) -> str:
    return self._alias

  @property
  def register(self) -> str:
    return self._register

  @property
  def operation(self) -> LabelOperation:
    return self._op


class RegisterLabelPass:
  def __init__(self, input_file: str, source: List[str]):
    self._raw_source = source
    self._input_file = input_file

  @property
  def processed_source(self) -> List[str]:
    return self._processed_source

  def process(self) -> None:
    def_alias = self._locate_defs()
    undef_alias = self._locate_undefs()

    self._process_source(def_alias, undef_alias)

  def _locate_defs(self) -> List[RegisterLabelOperation]:
    def_alias = []
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(DEF_STRUCTURE_REGEX, clear_line):
        self._raw_source[idx] = f"; {line}"

        proper_command = re.split('!alias', clear_line)[1]
        target_alias = re.split(',', proper_command)[1].strip()
        target_register = re.split(',', proper_command)[0].strip()

        def_alias.append(RegisterLabelOperation(idx, target_alias,
                                                 target_register,
                                                 LabelOperation.DEF_LABEL))
    return def_alias

  def _locate_undefs(self) -> List[RegisterLabelOperation]:
    undef_alias = []
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(UNDEF_STRUCTURE_REGEX, clear_line):
        self._raw_source[idx] = f"; {line}"
        register_alias = re.split('!unalias', clear_line)[1].strip()
        undef_alias.append(RegisterLabelOperation(idx, register_alias,
                                                 "", LabelOperation.DEF_LABEL))
    return undef_alias

  def _process_source(self, defs: List[RegisterLabelOperation],
                      undefs: List[RegisterLabelOperation]) -> None:
    self._processed_source = []
    for idx, line in enumerate(self._raw_source):
      active_defs = self._locate_active_defs(defs, undefs, idx)
      clear_line = Utils.extract_line_no_comments(line)
      split_line = re.split('\s+', clear_line)

      line_text = line
      for line_token in split_line:
        for def_target in active_defs:
          if def_target.alias in line_token:
            line_text = line.replace(def_target.alias, def_target.register)

      self._processed_source.append(line_text)

  def _locate_active_defs(self, defs: List[RegisterLabelOperation],
                          undefs: List[RegisterLabelOperation],
                          index: int):
    active_alias = []

    for idx in range(0, index):
      for alias in defs:
        if alias.position == idx:
          if len(active_alias) != 0 and \
             len([x for x in active_alias if x.alias == alias.alias]) != 0:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: alias '{alias.alias}' has already been defined")
          if len(active_alias) != 0 and \
             len([x for x in active_alias if x.register == alias.register]) != 0:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: register '{alias.register}' has already been aliased")
          active_alias.append(alias)
      for alias in undefs:
        if alias.position == idx:
          if len(active_alias) == 0 or \
             len([x for x in active_alias if x.alias == alias.alias]) == 0:
            raise RuntimeError(f"{idx + 1}: alias '{alias.alias}' has not been defined")
          active_alias = [x for x in active_alias if x.alias != alias.alias]

    return active_alias

def main():
  parser = argparse.ArgumentParser(description='rgb pre-processor')
  parser.add_argument('Input', metavar='input', type=str,
                      help='Input file name')
  parser.add_argument('Output', metavar='output', type=str,
                      help='Output file name')
  args = parser.parse_args()

  # Acquire arguments
  input_path = args.Input
  output_path = args.Output

  # process file
  process_file(input_path, output_path)


def process_file(input_file: str, output_file: str) -> None:
  file_source = load_file_source(input_file)

  reg_alias_pass = RegisterLabelPass(input_file, file_source)
  reg_alias_pass.process()


  final_source = reg_alias_pass.processed_source
  #save file
  with open(output_file, 'w') as f:
    f.write(Utils.get_flat_text(final_source))

def load_file_source(file_path: str) -> List[str]:
  contents = []
  try:
    with open(file_path) as f:
      contents = f.readlines()
  except:
    raise RuntimeError(f"Unable to open file {file_path}")

  return contents

if __name__ == "__main__":
    main()