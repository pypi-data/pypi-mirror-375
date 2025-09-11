"""
Pass 2: Blank line rule engine.
Copyright (c) 2025-2026 Greg Smethells. All rights reserved.
See the accompanying AUTHORS file for a complete list of authors.
This file is subject to the terms and conditions defined in LICENSE.
"""

from .config import BlankLineConfig
from .types import BlockType, Statement


class BlankLineRuleEngine:
  """Pass 2: Apply blank line rules"""

  def __init__(self, config: BlankLineConfig):
    """Initialize rule engine with configuration
    :param config: Blank line configuration
    :type config: BlankLineConfig
    """

    self.config = config

  def applyRules(self, statements: list[Statement]) -> list[int]:
    """Return list indicating how many blank lines should exist before each statement"""

    if not statements:
      return []

    shouldHaveBlankLine = [False] * len(statements)
    preserveExistingBlank = [False] * len(statements)  # Track blank lines after comments to preserve

    # Track which indices start new scopes (first statement after control/def block)
    startsNewScope = [False] * len(statements)

    for i in range(1, len(statements)):
      # Skip blank lines
      if statements[i].isBlank:
        continue

      # Look backwards to find the most recent non-blank statement
      prev_non_blank_idx = -1

      for j in range(i - 1, -1, -1):
        if not statements[j].isBlank:
          prev_non_blank_idx = j

          break

      if prev_non_blank_idx >= 0:
        prev_stmt = statements[prev_non_blank_idx]

        # If this statement is indented more than the previous one
        if statements[i].indentLevel > prev_stmt.indentLevel:
          # And the previous one was a control/definition statement or secondary clause
          if prev_stmt.blockType in [BlockType.CONTROL, BlockType.DEFINITION] or prev_stmt.isSecondaryClause:
            startsNewScope[i] = True

    # Detect blank lines immediately after comment blocks that should be preserved
    for i in range(len(statements) - 1):
      if statements[i].isComment and statements[i + 1].isBlank:
        # Look ahead to find the next non-blank statement
        for j in range(i + 2, len(statements)):
          if not statements[j].isBlank:
            preserveExistingBlank[j] = True
            break

    # Apply rules at each indentation level independently
    shouldHaveBlankLine = self._applyRulesAtLevel(statements, shouldHaveBlankLine, startsNewScope, 0)

    # Convert boolean list to actual blank line counts
    return self._convertToBlankLineCounts(statements, shouldHaveBlankLine, preserveExistingBlank)

  def _applyRulesAtLevel(
    self,
    statements: list[Statement],
    shouldHaveBlankLine: list[bool],
    startsNewScope: list[bool],
    targetIndent: int,
  ):
    """Apply rules at specific indentation level"""

    prevBlockType = None

    for i, stmt in enumerate(statements):
      # Skip statements at different indentation levels
      if stmt.indentLevel != targetIndent and not stmt.isBlank:
        continue

      # Skip blank lines for rule processing (they will be reconstructed)
      if stmt.isBlank:
        continue

      if stmt.isComment:
        # Comment break rule: blank line before comment (unless following comment)
        # BUT: no blank line at start of new scope has highest precedence
        if prevBlockType is not None and prevBlockType != BlockType.COMMENT and not startsNewScope[i]:
          shouldHaveBlankLine[i] = True

        # Comments cause a break - set prevBlockType to COMMENT so next statement
        # can decide whether it needs a blank line after the comment
        prevBlockType = BlockType.COMMENT

        continue

      # Secondary clause rule: NO blank line before secondary clauses
      if stmt.isSecondaryClause:
        shouldHaveBlankLine[i] = False
        prevBlockType = stmt.blockType

        continue

      # Check if there was a completed control/definition block before this statement
      # by looking for a control/definition at this level whose body has ended
      # OR if we're returning from a deeper indentation level
      completedControlBlock = False
      returningFromNestedLevel = False

      if i > 0:
        # Check if we're returning from a deeper indentation level
        for j in range(i - 1, -1, -1):
          prevStmt = statements[j]

          if prevStmt.isBlank:
            continue

          # If we find a statement at a deeper level, we're returning from nested
          if prevStmt.indentLevel > targetIndent:
            returningFromNestedLevel = True

            break

          # If we find a statement at our level, stop looking
          if prevStmt.indentLevel <= targetIndent:
            break

        # Also check for completed control/definition blocks
        for j in range(i - 1, -1, -1):
          prevStmt = statements[j]

          # Skip blanks and deeper indents
          if prevStmt.isBlank or prevStmt.indentLevel > targetIndent:
            continue

          # If we find a statement at our level
          if prevStmt.indentLevel == targetIndent:
            # Check if it's a control/definition that had a body after it
            if prevStmt.blockType in [BlockType.CONTROL, BlockType.DEFINITION]:
              # Check if there was a deeper indented block after it (its body)
              hasBody = False

              for k in range(j + 1, i):
                if statements[k].indentLevel > targetIndent:
                  hasBody = True

                  break

              if hasBody:
                completedControlBlock = True

                # Don't override prevBlockType - we'll handle this in the main logic

            break

      # Main blank line rules
      # Don't add blank line if this is the first statement in a new scope
      if startsNewScope[i]:
        # Never add blank line at start of new scope, regardless of completed control blocks
        shouldHaveBlankLine[i] = False
      elif prevBlockType is not None:
        # Special case: after comments, don't apply normal block transition rules
        # Comments follow "leave-as-is" behavior - only existing blanks are preserved
        if prevBlockType != BlockType.COMMENT:
          # Special case: after docstrings, don't add blank lines
          if self._isPreviousStatementDocstring(statements, i):
            shouldHaveBlankLine[i] = False
          # Special case: within function/class bodies, be more restrictive
          elif self._isWithinFunctionOrClassBody(statements, i, targetIndent):
            shouldHaveBlankLine[i] = self._needsBlankLineInFunctionBody(prevBlockType, stmt.blockType)
          else:
            shouldHaveBlankLine[i] = self._needsBlankLineBetween(prevBlockType, stmt.blockType) > 0
      elif completedControlBlock:
        # After a completed control block, apply normal rules with CONTROL as prev type
        shouldHaveBlankLine[i] = self._needsBlankLineBetween(BlockType.CONTROL, stmt.blockType) > 0
      elif returningFromNestedLevel:
        # When returning from nested level, add blank line
        shouldHaveBlankLine[i] = True

      prevBlockType = stmt.blockType

    # Recursively process nested indentation levels
    processedIndents = set()

    for stmt in statements:
      if stmt.indentLevel > targetIndent and stmt.indentLevel not in processedIndents:
        processedIndents.add(stmt.indentLevel)
        self._applyRulesAtLevel(statements, shouldHaveBlankLine, startsNewScope, stmt.indentLevel)

    return shouldHaveBlankLine

  def _convertToBlankLineCounts(
    self, statements: list[Statement], shouldHaveBlankLine: list[bool], preserveExistingBlank: list[bool]
  ) -> list[int]:
    """Convert boolean blank line indicators to actual counts
    :param statements: List of statements
    :type statements: list[Statement]
    :param shouldHaveBlankLine: Boolean indicators of where blank lines should exist
    :type shouldHaveBlankLine: list[bool]
    :param preserveExistingBlank: Boolean indicators of existing blank lines to preserve
    :type preserveExistingBlank: list[bool]
    :rtype: list[int]
    """

    blankLineCounts = [0] * len(statements)

    for i, stmt in enumerate(statements):
      if stmt.isBlank:
        continue

      # Preserve existing blank lines after comments (leave-as-is rule)
      if preserveExistingBlank[i]:
        blankLineCounts[i] = 1
        continue

      if not shouldHaveBlankLine[i]:
        continue

      # Find appropriate previous statement for blank line count calculation
      prevNonBlankIdx = -1
      immediatelyPrevIdx = -1

      # First, find the immediately preceding non-blank statement
      for j in range(i - 1, -1, -1):
        if not statements[j].isBlank:
          immediatelyPrevIdx = j

          break

      # For determining blank line count, we need to find the right "previous" statement
      # If we're returning from a nested level, use the last statement at the same level
      if immediatelyPrevIdx >= 0 and statements[immediatelyPrevIdx].indentLevel > stmt.indentLevel:
        # We're returning from nested level - find previous statement at same level
        for j in range(immediatelyPrevIdx - 1, -1, -1):
          if not statements[j].isBlank and statements[j].indentLevel <= stmt.indentLevel:
            prevNonBlankIdx = j

            break
      else:
        # Normal case - use immediately preceding statement
        prevNonBlankIdx = immediatelyPrevIdx

      if prevNonBlankIdx >= 0:
        prevStmt = statements[prevNonBlankIdx]

        # For comments, always use 1 blank line when marked (comment break rule)
        if stmt.isComment:
          blankLineCounts[i] = 1
        else:
          # Use block-to-block configuration
          blankLineCount = self._needsBlankLineBetween(prevStmt.blockType, stmt.blockType)
          blankLineCounts[i] = blankLineCount

    return blankLineCounts

  def _needsBlankLineBetween(self, prevType: BlockType, currentType: BlockType) -> int:
    """Determine number of blank lines needed between block types
    :param prevType: Previous block type
    :type prevType: BlockType
    :param currentType: Current block type
    :type currentType: BlockType
    :rtype: int
    """
    return self.config.getBlankLines(prevType, currentType)

  def _isPreviousStatementDocstring(self, statements: list[Statement], currentIndex: int) -> bool:
    """Check if the previous non-blank statement is a docstring
    :param statements: List of all statements
    :type statements: list[Statement]
    :param currentIndex: Index of current statement
    :type currentIndex: int
    :rtype: bool
    """
    # Find the previous non-blank statement
    prevIndex = -1
    for j in range(currentIndex - 1, -1, -1):
      if not statements[j].isBlank:
        prevIndex = j
        break
    
    if prevIndex == -1:
      return False
    
    prevStmt = statements[prevIndex]
    
    # Must be a CALL block (string literals are classified as CALL)
    if prevStmt.blockType != BlockType.CALL:
      return False
    
    # Must be a single line containing a string literal
    if len(prevStmt.lines) != 1:
      return False
    
    line = prevStmt.lines[0].strip()
    
    # Check if it's a string literal (docstring)
    return (
      (line.startswith('"""') and line.endswith('"""')) or
      (line.startswith("'''") and line.endswith("'''")) or
      (line.startswith('"') and line.endswith('"') and not line.startswith('"""')) or
      (line.startswith("'") and line.endswith("'") and not line.startswith("'''"))
    )

  def _isWithinFunctionOrClassBody(self, statements: list[Statement], currentIndex: int, targetIndent: int) -> bool:
    """Check if current statement is within a function or class body
    :param statements: List of all statements
    :type statements: list[Statement]
    :param currentIndex: Index of current statement
    :type currentIndex: int
    :param targetIndent: Target indentation level being processed
    :type targetIndent: int
    :rtype: bool
    """
    # If we're at indent 0, we're at top level
    if targetIndent == 0:
      return False
    
    # Look backwards for a definition (function or class) at a lower indent level
    for j in range(currentIndex - 1, -1, -1):
      stmt = statements[j]
      if stmt.isBlank:
        continue
      
      # If we find a definition at a lower indent, we're in its body
      if stmt.blockType == BlockType.DEFINITION and stmt.indentLevel < targetIndent:
        return True
      
      # If we find any statement at a lower indent that's not a definition,
      # we're not in a function/class body
      if stmt.indentLevel < targetIndent and stmt.blockType != BlockType.DEFINITION:
        return False
    
    return False

  def _needsBlankLineInFunctionBody(self, prevType: BlockType, currentType: BlockType) -> bool:
    """Determine if blank line is needed between statements within function/class body
    :param prevType: Previous block type
    :type prevType: BlockType
    :param currentType: Current block type
    :type currentType: BlockType
    :rtype: bool
    """
    # Within function bodies, only add blank lines between major blocks:
    # - Before/after control structures (if, for, while, try)
    # - Before/after function/class definitions
    # - Between import blocks and other code (but imports are rare in function bodies)
    
    majorBlocks = {BlockType.CONTROL, BlockType.DEFINITION, BlockType.IMPORT}
    
    # Add blank line before major blocks (but not after)
    if currentType in majorBlocks and prevType not in majorBlocks:
      return True
    
    # Add blank line after major blocks (but not before)  
    if prevType in majorBlocks and currentType not in majorBlocks:
      return True
    
    # No blank lines between regular statements (assignments, calls, declarations)
    return False
