# Contributing to Log Debugger for Home Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/loryanstrant/HA-Log-Debugger/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Home Assistant version
   - Relevant log snippets
   - Integration configuration (sanitized)

### Suggesting Features

1. Check [Issues](https://github.com/loryanstrant/HA-Log-Debugger/issues) for existing feature requests
2. Create a new issue with:
   - Clear use case description
   - Expected behavior
   - Potential implementation ideas
   - Examples of similar features

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following our coding standards
4. Test your changes thoroughly
5. Commit with clear messages: `git commit -m "Add feature: description"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/loryanstrant/HA-Log-Debugger.git
   cd HA-Log-Debugger
   ```

2. Create a test Home Assistant environment
3. Link the integration:
   ```bash
   ln -s $(pwd)/custom_components/ha_log_debugger /path/to/homeassistant/config/custom_components/
   ```

4. Restart Home Assistant and add the integration

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Add docstrings to all functions and classes
- Keep functions focused and concise

### Home Assistant Specific

- Follow [Home Assistant development guidelines](https://developers.home-assistant.io/)
- Use async/await for I/O operations
- Handle exceptions appropriately
- Log at appropriate levels (debug, info, warning, error)

### Example Code Structure

```python
"""Module description."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_example_function(hass: HomeAssistant, data: dict[str, Any]) -> bool:
    """
    Do something asynchronously.
    
    Args:
        hass: Home Assistant instance
        data: Input data dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Implementation
        return True
    except Exception as e:
        _LOGGER.error("Error in example function: %s", e, exc_info=True)
        return False
```

## Testing

Before submitting a pull request:

1. Test the integration loads correctly
2. Test configuration flow
3. Test all services work as expected
4. Verify sensors update properly
5. Check log parsing accuracy
6. Test AI analysis (if applicable)
7. Ensure no errors in Home Assistant logs

## Documentation

- Update README.md if adding features
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/)
- Add docstrings to new functions/classes
- Update services.yaml for new services
- Update strings.json for UI text

## Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when applicable

Examples:
- `Add support for custom log file paths`
- `Fix entity ID extraction for hyphenated names`
- `Update documentation for AI configuration`
- `Refactor log parsing to improve performance`

## Release Process

1. Update version in `manifest.json`
2. Update CHANGELOG.md
3. Create GitHub release with tag
4. HACS will automatically detect the new release

## Questions?

Feel free to:
- Open a discussion on GitHub
- Comment on relevant issues
- Reach out on the Home Assistant community forum

Thank you for contributing! 🎉
