#!/usr/bin/env python3

import os
import re
import argparse
import sys

from enum import Enum
from typing import List

sys.tracebacklimit = 0

DEF_STRUCTURE_REGEX = r"^(\s)*def(\s)*(\w)+,(\s)*(\w)+(\s)*$"
UNDEF_STRUCTURE_REGEX = r"^(\s)*undef(\s)*(\w)+(\s)*$"

class Utils:
  @staticmethod
  def extract_line_no_comments(line: str) -> str:
    index = line.find(';')
    return line if index == -1 else line[:index]

class LabelOperation(Enum):
  DEF_LABEL = "DEF_LABEL"
  UNDEF_LABEL = "UNDEF_LABEL"

class RegisterLabelOperation:
  def __init__(self, position: int, label: str, register: str,
                 op: LabelOperation):
    self._position = position
    self._label = label
    self._register = register
    self._op = op

  @property
  def position(self) -> int:
    return self._position

  @property
  def label(self) -> str:
    return self._label

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

  def process(self) -> None:
    def_labels = self._locate_defs()
    undef_labels = self._locate_undefs()

    self._process_source(def_labels, undef_labels)

  def _locate_defs(self) -> List[RegisterLabelOperation]:
    def_labels = []
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(DEF_STRUCTURE_REGEX, clear_line):
        self._raw_source[idx] = f"; {line}"

        proper_command = re.split('def', clear_line)[1]
        target_label = re.split(',', proper_command)[1].strip()
        target_register = re.split(',', proper_command)[0].strip()

        def_labels.append(RegisterLabelOperation(idx, target_label,
                                                 target_register,
                                                 LabelOperation.DEF_LABEL))

    return def_labels

  def _locate_undefs(self) -> List[RegisterLabelOperation]:
    undef_labels = []
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(UNDEF_STRUCTURE_REGEX, clear_line):
        self._raw_source[idx] = f"; {line}"
        register_label = re.split('undef', clear_line)[1].strip()
        undef_labels.append(RegisterLabelOperation(idx, register_label,
                                                 "", LabelOperation.DEF_LABEL))

    return undef_labels

  def _process_source(self, defs: List[RegisterLabelOperation],
                      undefs: List[RegisterLabelOperation]) -> None:
    for idx, line in enumerate(self._raw_source):
      active_defs = self._locate_active_defs(defs, undefs, idx)

      if len(active_defs) != 0:
        label_list = ""
        for label in active_defs:
          label_list += f"{label.label}, "

        print(label_list)


  def _locate_active_defs(self, defs: List[RegisterLabelOperation],
                          undefs: List[RegisterLabelOperation],
                          index: int):
    active_labels = []

    for idx in range(0, index):
      for label in defs:
        if label.position == idx:
          if len(active_labels) != 0 and \
             len([x for x in active_labels if x.label == label.label]) != 0:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: label '{label.label}' has already been defined")
          active_labels.append(label)
      for label in undefs:
        if label.position == idx:
          if len(active_labels) == 0 or \
             len([x for x in active_labels if x.label == label.label]) == 0:
            raise RuntimeError(f"{idx + 1}: label '{label.label}' has not been defined")
          active_labels = [x for x in active_labels if x.label != label.label]

    return active_labels

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

  reg_label_pass = RegisterLabelPass(input_file, file_source)
  reg_label_pass.process()

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