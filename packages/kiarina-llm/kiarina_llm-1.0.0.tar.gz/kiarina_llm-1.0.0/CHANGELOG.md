# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-09-09

### Added
- Initial release of kiarina-llm
- RunContext management for LLM pipeline processing
- Type-safe FSName validation for filesystem-safe names
- Type-safe IDStr validation for identifiers
- Configuration management using pydantic-settings-manager
- Environment variable configuration support
- Runtime configuration overrides
- Cross-platform compatibility with Windows reserved name validation
- Full type hints and Pydantic validation
- Comprehensive test suite

### Features
- **RunContext**: Structured context information holder
  - Application author and name (filesystem safe)
  - Tenant, user, agent, and runner identifiers
  - Time zone and language settings
  - Extensible metadata support
- **Type Safety**: Custom Pydantic types for validation
  - FSName: Filesystem-safe names with cross-platform validation
  - IDStr: Identifier strings with pattern validation
- **Configuration**: Flexible settings management
  - Environment variable support with KIARINA_LLM_RUN_CONTEXT_ prefix
  - Runtime configuration overrides
  - Default value management

### Dependencies
- pydantic>=2.10.1
- pydantic-settings>=2.10.1
- pydantic-settings-manager>=2.1.0
