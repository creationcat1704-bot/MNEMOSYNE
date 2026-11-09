# MNEMOSYNE – Release Notes

**Version:** v0.1.0 Alpha
**Engine:** E-0.1.0-1
**Release Date:** 2026-11-09

## Overview

MNEMOSYNE is a persistence engine designed for the targeted storage and restoration of specific KDE configuration settings on Linux.

## Implemented Features

- `capture` – Captures current KDE configuration values.
- `apply` – Restores individual stored settings.
- `apply-all` – Restores all stored settings.
- `list` – Displays all stored settings and their current values.
- `--version` – Outputs the current version identifier.
- `--help` – Displays available commands and their descriptions.

## Supported Data Types

- string
- int
- double
- bool

## Security and Data Management

- Configuration paths are restricted to `~/.config`.
- Absolute paths and unsafe path-traversal attempts are rejected.
- Manifest write operations are performed atomically.
- Existing settings are updated when a new capture is performed.

## Test Status

- Capture successfully tested.
- Individual apply successfully tested.
- Apply-all successfully tested (8/8 settings).

## Development Status

**Alpha – Early Development Phase**

Further testing regarding persistence across reboots, the inclusion of additional KDE configurations, and engine enhancements are still pending.
