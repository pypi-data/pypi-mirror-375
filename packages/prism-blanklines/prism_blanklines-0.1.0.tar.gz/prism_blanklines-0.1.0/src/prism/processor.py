"""
File processor with change detection.
Copyright (c) 2025-2026 Greg Smethells. All rights reserved.
See the accompanying AUTHORS file for a complete list of authors.
This file is subject to the terms and conditions defined in LICENSE.
"""

from .analyzer import FileAnalyzer
from .config import BlankLineConfig
from .rules import BlankLineRuleEngine
from .types import Statement
from pathlib import Path

class FileProcessor:
  """Handles file processing with change detection"""

  @staticmethod
  def processFile(filepath: Path, config: BlankLineConfig, checkOnly: bool = False) -> bool:
    """Process file and return True if changes were needed
    :param filepath: Path to file to process
    :type filepath: Path
    :param config: Blank line configuration
    :type config: BlankLineConfig
    :param checkOnly: If True, only check if changes needed without writing
    :type checkOnly: bool
    :rtype: bool
    """

    try:
      with open(filepath, encoding='utf-8') as f:
        originalLines = f.readlines()
    except Exception as e:
      print(f'Error reading {filepath}: {e}')
      return False

    # Pass 1: Analyze file structure
    analyzer = FileAnalyzer()
    statements = analyzer.analyzeFile(originalLines)

    # Pass 2: Determine blank line placement
    ruleEngine = BlankLineRuleEngine(config)
    blankLineCounts = ruleEngine.applyRules(statements)

    # Pass 3: Reconstruct file with correct blank line placement
    newLines = FileProcessor._reconstructFile(statements, blankLineCounts)

    # Check if content changed
    if newLines == originalLines:
      return False

    if checkOnly:
      return True

    # Write changes
    try:
      with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(newLines)

      return True
    except Exception as e:
      print(f'Error writing {filepath}: {e}')
      return False

  @staticmethod
  def _reconstructFile(statements: list[Statement], blankLineCounts: list[int]) -> list[str]:
    """Reconstruct file content with correct blank line placement
    :param statements: List of parsed statements
    :type statements: list[Statement]
    :param blankLineCounts: Number of blank lines to add before each statement
    :type blankLineCounts: list[int]
    :rtype: list[str]
    """

    newLines = []

    for i, stmt in enumerate(statements):
      # Skip existing blank lines - we'll add them back where they should be
      if stmt.isBlank:
        continue

      # Add blank lines before this statement if rules specify them
      if i < len(blankLineCounts):
        for _ in range(blankLineCounts[i]):
          newLines.append('\n')

      # Add the statement content
      newLines.extend(stmt.lines)

    return newLines
