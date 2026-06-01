# Nutanix Permission Tester

Test Nutanix Prism Central and Prism Element API reachability and read permissions.

## Features

- Python standard library only
- JSON output support
- Safe, audit-oriented behavior
- Placeholder configuration for Nutanix environments

## Configuration

Edit `nutanix_permission_tester.py` and configure the placeholder values. Do not commit real API tokens, passwords, UUIDs, IP addresses, or internal infrastructure details to a public repository.

## Usage

```bash
python nutanix_permission_tester.py --json-file permission-report.json
```

## Security Notes

The script currently disables SSL certificate verification by using `ssl._create_unverified_context()`. This may be useful in lab environments, but it is not recommended for production. For production use, configure proper certificate validation.

## Disclaimer

This script is provided as an example. Test it in a safe environment before using it against production Nutanix infrastructure.
