"""
Unit tests for blank line rule engine.
Copyright (c) 2025-2026 Greg Smethells. All rights reserved.
See the accompanying AUTHORS file for a complete list of authors.
This file is subject to the terms and conditions defined in LICENSE.
"""

from prism.rules import BlankLineRuleEngine
from prism.config import BlankLineConfig
from prism.types import BlockType, Statement

class TestBlankLineRuleEngine:
  def createStatement(self, blockType, indentLevel=0, isComment=False, isBlank=False, isSecondaryClause=False):
    """Helper to create test statements"""
    return Statement(
      lines=['dummy'],
      startLineIndex=0,
      endLineIndex=0,
      blockType=blockType,
      indentLevel=indentLevel,
      isComment=isComment,
      isBlank=isBlank,
      isSecondaryClause=isSecondaryClause,
    )

  def testSameBlockType(self):
    """Test no blank line between same block types (except Control/Definition)"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.ASSIGNMENT),
      self.createStatement(BlockType.ASSIGNMENT),
    ]
    result = engine.applyRules(statements)

    assert result == [0, 0]

  def testDifferentBlockTypes(self):
    """Test blank line between different block types"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.IMPORT),
      self.createStatement(BlockType.ASSIGNMENT),
    ]
    result = engine.applyRules(statements)

    assert result == [0, 1]  # Blank line before second statement

  def testConsecutiveControlBlocks(self):
    """Test consecutive Control blocks need separation"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.CONTROL),
      self.createStatement(BlockType.CONTROL),
    ]
    result = engine.applyRules(statements)

    assert result == [0, 1]  # Blank line before second control block

  def testConsecutiveDefinitionBlocks(self):
    """Test consecutive Definition blocks need separation"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.DEFINITION),
      self.createStatement(BlockType.DEFINITION),
    ]
    result = engine.applyRules(statements)

    assert result == [0, 1]  # Blank line before second definition block

  def testSecondaryClauseRule(self):
    """Test no blank line before secondary clauses"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.CONTROL),  # if
      self.createStatement(BlockType.CONTROL, isSecondaryClause=True),  # else
    ]
    result = engine.applyRules(statements)

    assert result == [0, 0]  # No blank line before else

  def testCommentBreakRule(self):
    """Test blank line before comments (comment break rule)"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.ASSIGNMENT),
      self.createStatement(BlockType.ASSIGNMENT, isComment=True),
    ]
    result = engine.applyRules(statements)

    assert result == [0, 1]  # Blank line before comment

  def testBlankLinesIgnored(self):
    """Test blank lines are ignored in rule processing"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.ASSIGNMENT),
      self.createStatement(BlockType.ASSIGNMENT, isBlank=True),
      self.createStatement(BlockType.CALL),
    ]
    result = engine.applyRules(statements)

    assert result == [0, 0, 1]  # Blank line before CALL (different from ASSIGNMENT)

  def testIndentationLevelProcessing(self):
    """Test rules applied independently at each indentation level"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.ASSIGNMENT, indentLevel=0),
      self.createStatement(BlockType.ASSIGNMENT, indentLevel=2),  # Nested
      self.createStatement(BlockType.CALL, indentLevel=2),  # Nested different type
      self.createStatement(BlockType.CALL, indentLevel=0),  # Back to level 0
    ]
    result = engine.applyRules(statements)

    # Level 0: ASSIGNMENT -> CALL (different types, need blank line)
    # Level 2: ASSIGNMENT -> CALL (different types, need blank line)
    assert result == [0, 0, 1, 1]

  def testNeedsBlankLineBetweenMethod(self):
    """Test private _needsBlankLineBetween method"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())

    # Same types (except Control/Definition)
    assert not engine._needsBlankLineBetween(BlockType.ASSIGNMENT, BlockType.ASSIGNMENT)
    assert not engine._needsBlankLineBetween(BlockType.CALL, BlockType.CALL)
    assert not engine._needsBlankLineBetween(BlockType.IMPORT, BlockType.IMPORT)

    # Same Control/Definition types (special rule)
    assert engine._needsBlankLineBetween(BlockType.CONTROL, BlockType.CONTROL)
    assert engine._needsBlankLineBetween(BlockType.DEFINITION, BlockType.DEFINITION)

    # Different types
    assert engine._needsBlankLineBetween(BlockType.IMPORT, BlockType.ASSIGNMENT)
    assert engine._needsBlankLineBetween(BlockType.ASSIGNMENT, BlockType.CALL)

  def testEmptyStatements(self):
    """Test handling of empty statement list"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    result = engine.applyRules([])

    assert result == []

  def testComplexScenario(self):
    """Test complex scenario with multiple rules"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.IMPORT),  # 0: import
      self.createStatement(BlockType.IMPORT),  # 1: import (same type)
      self.createStatement(BlockType.ASSIGNMENT),  # 2: assignment (different type)
      self.createStatement(BlockType.ASSIGNMENT, isComment=True),  # 3: comment (comment break)
      self.createStatement(BlockType.CALL),  # 4: call (after comment)
      self.createStatement(BlockType.CONTROL),  # 5: if (different type)
      self.createStatement(BlockType.CONTROL, isSecondaryClause=True),  # 6: else (secondary clause)
      self.createStatement(BlockType.CONTROL),  # 7: another if (consecutive control)
    ]
    result = engine.applyRules(statements)
    expected = [
      0,  # 0: first statement
      0,  # 1: same type as previous (import)
      1,  # 2: different type (assignment after import)
      1,  # 3: comment break rule
      0,  # 4: after comment reset
      1,  # 5: different type (control after call)
      0,  # 6: secondary clause rule (no blank before else)
      1,  # 7: consecutive control blocks rule
    ]

    assert result == expected

  def testCommentBreakRuleRegression(self):
    """Regression test for comment break rule bug (original issue)"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.ASSIGNMENT),
      self.createStatement(BlockType.ASSIGNMENT, isComment=True),
    ]
    result = engine.applyRules(statements)

    # Comment should get blank line despite same block type
    assert result == [0, 1]

  def testIndentationProcessingRegression(self):
    """Regression test for indentation level processing bug (original issue)"""

    engine = BlankLineRuleEngine(BlankLineConfig.fromDefaults())
    statements = [
      self.createStatement(BlockType.ASSIGNMENT, indentLevel=0),
      self.createStatement(BlockType.ASSIGNMENT, indentLevel=2),  # Nested
      self.createStatement(BlockType.CALL, indentLevel=2),  # Nested different type
      self.createStatement(BlockType.CALL, indentLevel=0),  # Back to level 0
    ]
    result = engine.applyRules(statements)

    # Should get blank lines: none, none, different types at level 2, returning from nested
    assert result == [0, 0, 1, 1]
