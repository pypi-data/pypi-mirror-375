# Prudentia CLI (pevx)

A development CLI tool for Prudentia internal developers.

## Installation

### From PyPI (when published)

```bash
pip install pevx
```

### Development Mode

Clone the repository and install in development mode using Poetry:

```bash
git clone https://github.com/Prudentia-Sciences/pevx
cd pevx
poetry install
```

## Usage

After installation, you can use the CLI with the `pevx` command:

```bash
# Show help
pevx --help

# Authenticate poetry with AWS CodeArtifact
pevx poetry add-codeartifact
```

## Available Commands

- `poetry add-codeartifact`: Authenticate poetry with AWS CodeArtifact
  - Configures poetry to use Prudentia's private Python package repository
  - Uses AWS credentials to obtain authentication token
- `uv add [package]`: Install Prudentia's private packages using `uv`

## Command Options

### _poetry add-codeartifact_

```bash
pevx poetry add-codeartifact --domain custom-domain --domain-owner 123456789 --repo custom-repo --region us-west-2
```

Default values:
- Domain: prudentia-sciences
- Domain Owner: 728222516696
- Repository: pypi-store
- Region: us-east-1

### _uv add [package]_

```bash
pevx uv add [package] --domain custom-domain --domain-owner 123456789 --repo custom-repo --region us-west-2
```

Default values:
- Domain: prudentia-sciences
- Domain Owner: 728222516696
- Repository: pypi-store
- Region: us-east-1

## Development

### Adding New Commands

1. Create a new file in the `pevx/commands/` directory for your command group
2. Implement your command using Click
3. Import and register your command in `pevx/cli.py`

Example:

```python
# In pevx/commands/my_command.py
import click

@click.command()
def my_command():
    """Command description."""
    click.echo("Running my command")

# In pevx/cli.py, add:
from pevx.commands.my_command import my_command
cli.add_command(my_command)
```

### CI/CD and Versioning

This project uses a comprehensive CI/CD pipeline with semantic-release:

1. **Automated Testing**
   - Runs tests on multiple Python versions (3.9, 3.10, 3.11, 3.12)
   - Generates code coverage reports

2. **Semantic Versioning**
   - Automatically determines the next version number based on commit messages
   - Creates GitHub releases with generated changelogs

3. **Automated Publishing to PyPI**
   - When a new version is detected, automatically builds and publishes to PyPI

#### Required Secrets

To use the CI/CD pipeline, add this secret to your GitHub repository:

- `PYPI_API_TOKEN`: API token for PyPI

#### Commit Message Format

For semantic-release to work properly, use conventional commit messages:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Common types:
- `fix`: Bug fixes (triggers PATCH version bump)
- `feat`: New features (triggers MINOR version bump)
- `feat!`, `fix!`, `refactor!`, etc.: Breaking changes (triggers MAJOR version bump)

Once published to PyPI, team members can install the CLI tool with:

```bash
pip install pevx
```