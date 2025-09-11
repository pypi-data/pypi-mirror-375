# Sherlock 🔍

A powerful CLI tool for analyzing AWS CloudWatch Logs with ease.

## Description

Sherlock is a Python-based command-line tool that helps you filter, analyze, and export AWS CloudWatch Logs. It provides an intuitive interface to search through your logs with custom filters and export them to readable formats with human-readable timestamps.

## Features

- 🔍 Filter CloudWatch Logs by time range and custom patterns
- 📅 Convert timestamps to human-readable date formats
- 📝 Export logs to text files with structured formatting
- ⚡ Fast and efficient log processing
- 🛡️ Built-in AWS authentication support

## Installation

### From PyPI
```bash
pip install sherlock
```

## Configuration

Make sure you have AWS credentials configured.

Required permissions:
- `logs:FilterLogEvents`
- `logs:DescribeLogGroups`

## Usage
```bash
sherlock --log-group "my-log-group" --start "2025-09-10T12:00:00Z" --end "2025-09-10T12:15:00Z" --region "eu-central-1" --filter-pattern "UnwantedException"
```

### Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--log-group` | CloudWatch Log Group name | Yes | - |
| `--start-time` | Start time for filtering (ISO8601 format) | Yes | - |
| `--end-time` | End time for filtering (ISO8601 format) | Yes | - |
| `--region` | End time for filtering (ISO8601 format) | Yes | - |
| `--filter-pattern` | CloudWatch filter pattern | No | "" |
| `--output` | Output file name | No | `logs.txt` |

### Time Format

Time parameters (`--start-time` and `--end-time`) must be in ISO8601 format:

- `2025-09-10T14:30:00Z` (UTC timezone)
- `2025-09-10T14:30:00+02:00` (with timezone offset)
- `2025-09-10T14:30:00.123Z` (with milliseconds)

## Output Format

The exported logs include the following columns:
1. **Timestamp** - Original timestamp in milliseconds
2. **Date** - Human-readable date (YYYY-MM-DD HH:MM:SS)
3. **Log Stream** - CloudWatch log stream name
4. **Message** - The actual log message

Example output:
```
1757506004044	2025-09-10 14:06:44	my-log-group/3cb6c84259584af3be92688fc6f809eb	ERROR: Application failure occurred
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Eric Villa** - [eric@besharp.it](mailto:eric.villa91@gmail.com)