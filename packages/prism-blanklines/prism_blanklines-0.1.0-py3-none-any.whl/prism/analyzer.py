"""
Pass 1: File structure analysis and statement parsing.
Copyright (c) 2025-2026 Greg Smethells. All rights reserved.
See the accompanying AUTHORS file for a complete list of authors.
This file is subject to the terms and conditions defined in LICENSE.
"""

from .classifier import StatementClassifier
from .parser import MultilineParser
from .types import BlockType, Statement

class FileAnalyzer:
  """Pass 1: Parse file into logical statements"""

  def analyzeFile(self, lines: list[str]) -> list[Statement]:
    """Parse file into logical statements"""

    statements = []
    parser = MultilineParser()
    currentStatement = []
    statementStart = 0

    for i, line in enumerate(lines):
      stripped = line.strip()

      # Handle blank lines
      if not stripped:
        if currentStatement:
          # Don't finish current statement if we're expecting a definition (decorator case)
          if not parser.expectingDefinition:
            # Finish current statement
            statements.append(self._createStatement(currentStatement, statementStart, i - 1))

            currentStatement = []

            parser.reset()

        # Add blank line as separate statement (only if not expecting definition)
        if not parser.expectingDefinition:
          statements.append(
            Statement(
              lines=[line],
              startLineIndex=i,
              endLineIndex=i,
              blockType=BlockType.CALL,  # Dummy value
              indentLevel=-1,
              isBlank=True,
            )
          )

        continue

      # Handle comments
      if stripped.startswith('#'):
        if currentStatement:
          # Finish current statement
          statements.append(self._createStatement(currentStatement, statementStart, i - 1))

          currentStatement = []

          parser.reset()

        # Add comment as separate statement
        statements.append(
          Statement(
            lines=[line],
            startLineIndex=i,
            endLineIndex=i,
            blockType=BlockType.CALL,  # Dummy value
            indentLevel=self._getIndentLevel(line),
            isComment=True,
          )
        )
        continue

      # Process code line
      if not currentStatement:
        statementStart = i

      currentStatement.append(line)
      parser.processLine(line)

      # Check if statement is complete
      if parser.isComplete():
        statements.append(self._createStatement(currentStatement, statementStart, i))

        currentStatement = []

        parser.reset()

    # Handle any remaining statement
    if currentStatement:
      statements.append(self._createStatement(currentStatement, statementStart, len(lines) - 1))

    return statements

  def _createStatement(self, lines: list[str], startIdx: int, endIdx: int) -> Statement:
    """Create Statement object from lines"""

    blockType = StatementClassifier.classifyStatement(lines)
    indentLevel = self._getIndentLevel(lines[0])
    isSecondary = StatementClassifier.isSecondaryClause(lines[0])

    return Statement(
      lines=lines,
      startLineIndex=startIdx,
      endLineIndex=endIdx,
      blockType=blockType,
      indentLevel=indentLevel,
      isSecondaryClause=isSecondary,
    )

  def _getIndentLevel(self, line: str) -> int:
    """Calculate indentation level"""

    if not line.strip():
      return -1  # Blank lines have no meaningful indentation

    indent = 0

    for char in line:
      if char == ' ':
        indent += 1
      elif char == '\t':
        indent += 8
      else:
        break

    return indent
