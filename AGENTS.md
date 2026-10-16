# Repository Agent Guide

## Scope

This repository contains both standalone system utilities under `scripts/` and a
packaged application under `apps/webwrap`. Read the nearest project guide before
editing; `apps/webwrap/AGENTS.md` overrides incompatible repository conventions.

## General Rules

- Keep user documentation in Spanish and code, comments, docstrings, and agent
  guidance in English.
- Preserve existing CLI flags, interactive behavior, confirmations, logs, progress
  feedback, and concise actionable errors unless a task explicitly changes them.
- Use `pathlib`, f-strings, specific exceptions, and type hints in changed code.
- Explain destructive effects before execution and retain safe defaults.
- Do not commit credentials, local environments, caches, build output, or generated
  user data.

## Standalone Scripts

- Read a standalone script completely before changing its monolithic workflow.
- Keep scripts directly executable and standard-library-only unless a concrete
  requirement justifies a dependency.
- Preserve both direct CLI automation and the guided interactive menu where present.
- Keep platform-specific commands, privilege checks, feature detection, and graceful
  fallback explicit.
- Place new utilities under the appropriate `scripts/<platform>/<project>/` directory
  with adjacent Spanish documentation.

## Packaged Applications

Packaged applications may use modules, local imports, metadata, dependencies, and
tests. Do not impose the standalone interactive-menu or single-file architecture on
them. For WebWrap, follow `apps/webwrap/AGENTS.md`.

## Validation

- Run focused tests and syntax checks for changed Python code.
- Do not execute Windows maintenance operations from Linux; restrict Linux validation
  to compilation and documentation/path consistency.
- Exercise system-changing utilities only in an appropriate disposable environment.
