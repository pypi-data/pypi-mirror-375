"""
Command line interface for prism.
Copyright (c) 2025-2026 Greg Smethells. All rights reserved.
See the accompanying AUTHORS file for a complete list of authors.
This file is subject to the terms and conditions defined in LICENSE.
"""

import argparse
import sys
from .config import BlankLineConfig
from .processor import FileProcessor
from .types import BlockType
from pathlib import Path

def main():
  """CLI entry point"""

  parser = argparse.ArgumentParser(description='Enforce blank line rules from CLAUDE.md')

  parser.add_argument('paths', nargs='+', help='Files or directories to process')
  parser.add_argument(
    '--check', action='store_true', help='Check if files need formatting (exit code 1 if changes needed)'
  )

  # Configuration options
  parser.add_argument('--config', type=Path, help='Path to configuration file (default: ./prism.toml)')
  parser.add_argument('--no-config', action='store_true', help='Ignore configuration file')
  parser.add_argument(
    '--blank-lines-default', type=int, metavar='N', help='Default blank lines between different block types (0-3)'
  )
  parser.add_argument(
    '--blank-lines',
    action='append',
    metavar='FROM_TO=N',
    help='Override blank lines for specific transition (e.g., assignment_to_call=2)',
  )
  parser.add_argument(
    '--blank-lines-consecutive-control',
    type=int,
    metavar='N',
    help='Blank lines between consecutive control blocks (0-3)',
  )
  parser.add_argument(
    '--blank-lines-consecutive-definition',
    type=int,
    metavar='N',
    help='Blank lines between consecutive definition blocks (0-3)',
  )

  args = parser.parse_args()

  # Load configuration
  try:
    config = loadConfiguration(args)
  except (ValueError, FileNotFoundError) as e:
    print(f'Configuration error: {e}', file=sys.stderr)
    sys.exit(1)

  exitCode = 0
  processedCount = 0
  changedCount = 0

  for pathStr in args.paths:
    path = Path(pathStr)

    if path.is_file() and path.suffix == '.py':
      processedCount += 1

      changed = FileProcessor.processFile(path, config, checkOnly=args.check)

      if changed:
        changedCount += 1

        if args.check:
          print(f'would reformat {path}')

          exitCode = 1
        else:
          print(f'reformatted {path}')
    elif path.is_dir():
      for pyFile in path.rglob('*.py'):
        processedCount += 1

        changed = FileProcessor.processFile(pyFile, config, checkOnly=args.check)

        if changed:
          changedCount += 1

          if args.check:
            print(f'would reformat {pyFile}')

            exitCode = 1
          else:
            print(f'reformatted {pyFile}')

  if args.check and exitCode == 0:
    print(f'All {processedCount} files already formatted correctly.')
  elif not args.check:
    print(f'Processed {processedCount} files, reformatted {changedCount}.')

  sys.exit(exitCode)

def loadConfiguration(args) -> BlankLineConfig:
  """Load configuration from file and CLI overrides
  :param args: Parsed command line arguments
  :rtype: BlankLineConfig
  :raises: ValueError for invalid configuration
  :raises: FileNotFoundError if specified config file not found
  """

  # Start with defaults
  config = BlankLineConfig.fromDefaults()

  # Load from config file unless --no-config is specified
  if not args.no_config:
    configPath = args.config or Path('./prism.toml')

    if configPath.exists():
      try:
        config = BlankLineConfig.fromToml(configPath)
      except (ValueError, FileNotFoundError):
        if args.config:  # Only error if user explicitly specified config
          raise

        # If default config file has issues, just use defaults
        pass

  # Apply CLI overrides
  if args.blank_lines_default is not None:
    validateBlankLineCount(args.blank_lines_default, '--blank-lines-default')

    config.defaultBetweenDifferent = args.blank_lines_default

  if args.blank_lines_consecutive_control is not None:
    validateBlankLineCount(args.blank_lines_consecutive_control, '--blank-lines-consecutive-control')

    config.consecutiveControl = args.blank_lines_consecutive_control

  if args.blank_lines_consecutive_definition is not None:
    validateBlankLineCount(args.blank_lines_consecutive_definition, '--blank-lines-consecutive-definition')

    config.consecutiveDefinition = args.blank_lines_consecutive_definition

  # Parse --blank-lines overrides
  if args.blank_lines:
    for override in args.blank_lines:
      try:
        transitionKey, valueStr = override.split('=', 1)

        value = int(valueStr)

        validateBlankLineCount(value, f'--blank-lines {override}')

        # Parse transition (e.g., "assignment_to_call")
        parts = transitionKey.split('_to_')

        if len(parts) != 2:
          raise ValueError(f'Invalid transition format in --blank-lines {override}. Expected: blocktype_to_blocktype=N')

        fromBlockName, toBlockName = parts

        fromBlock = parseBlockTypeName(fromBlockName)
        toBlock = parseBlockTypeName(toBlockName)

        config.transitions[(fromBlock, toBlock)] = value
      except ValueError as e:
        if '=' not in override:
          raise ValueError(f'Invalid format for --blank-lines: {override}. Expected: blocktype_to_blocktype=N')
        else:
          raise ValueError(f'Invalid --blank-lines override: {e}')

  return config

def validateBlankLineCount(value: int, option: str):
  """Validate blank line count for CLI options
  :param value: Value to validate
  :type value: int
  :param option: Option name for error messages
  :type option: str
  :raises: ValueError if invalid
  """

  if value < 0 or value > 3:
    raise ValueError(f'{option} must be between 0 and 3, got: {value}')

def parseBlockTypeName(name: str) -> BlockType:
  """Parse block type name for CLI
  :param name: Block type name
  :type name: str
  :rtype: BlockType
  :raises: ValueError if invalid
  """

  blockTypeMap = {
    'assignment': BlockType.ASSIGNMENT,
    'call': BlockType.CALL,
    'import': BlockType.IMPORT,
    'control': BlockType.CONTROL,
    'definition': BlockType.DEFINITION,
    'declaration': BlockType.DECLARATION,
    'comment': BlockType.COMMENT,
  }

  if name not in blockTypeMap:
    validNames = ', '.join(blockTypeMap.keys())

    raise ValueError(f'Unknown block type: {name}. Valid types: {validNames}')

  return blockTypeMap[name]

if __name__ == '__main__':
  main()
