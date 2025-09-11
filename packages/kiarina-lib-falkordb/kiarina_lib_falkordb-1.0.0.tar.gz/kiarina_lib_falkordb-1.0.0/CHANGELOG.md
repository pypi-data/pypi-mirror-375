# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-09-09

### Added
- Initial release of kiarina-lib-falkordb
- FalkorDB client with configuration management using pydantic-settings-manager
- Connection pooling and caching
- Retry mechanism for connection failures
- Support for both sync and async operations (async prepared for future FalkorDB support)
- Type safety with full type hints and Pydantic validation
- Environment variable configuration support
- Runtime configuration overrides
- Multiple named configurations support

### Dependencies
- falkordb (from kiarina/falkordb-py fork with redis6 support)
- pydantic-settings>=2.10.1
- pydantic-settings-manager>=2.1.0
- redis>=6.4.0
