# PyPI Publishing Instructions

## Setup (One-time)
```bash
# Set environment variables
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJDg4MDRkZGFjLTNmN2EtNGI3ZS05Y2EzLTM2MmIyNTk2NTJlNwACKlszLCIzMjAxZTI0OS01Yzk2LTQwNmEtOGQ3Yi0zNDM3MjEzZDkyNGIiXQAABiA5oBdgIQ3bdlUPCmJdTTyovKGzTeZYdILgM0DnxN2-eA
export TWINE_USERNAME=__token__

# Or create ~/.pypirc file:
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJDg4MDRkZGFjLTNmN2EtNGI3ZS05Y2EzLTM2MmIyNTk2NTJlNwACKlszLCIzMjAxZTI0OS01Yzk2LTQwNmEtOGQ3Yi0zNDM3MjEzZDkyNGIiXQAABiA5oBdgIQ3bdlUPCmJdTTyovKGzTeZYdILgM0DnxN2-eA
EOF
```

## Publish
```bash
# Upload to PyPI
python -m twine upload dist/*

# Or test first
python -m twine upload --repository testpypi dist/*
```

## Verify
```bash
# Install from PyPI
pip install jira-mcp-server

# Test command
jira-mcp-server --help
```

Package files ready in `dist/`:
- `jira_mcp_server-1.0.0-py3-none-any.whl`
- `jira_mcp_server-1.0.0.tar.gz`