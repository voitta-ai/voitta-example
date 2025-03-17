# Development Environment Setup

This document outlines different approaches for setting up a development environment for the voitta-example project that allows you to:

1. Use your local voitta implementation (located at `/Users/gregory/g/projects/llm/roma/voitta`) for development
2. Also be able to test with the PyPI version of voitta in a separate environment

## Option 1: Python Virtual Environments with Path Manipulation

This is the simplest approach that uses standard Python tools.

### Development Environment (Local voitta)
- Create a development virtual environment
  ```bash
  python -m venv .venv-dev
  source .venv-dev/bin/activate  # On Unix/macOS
  # or
  .venv-dev\Scripts\activate  # On Windows
  ```
- Install all requirements except voitta from PyPI
  ```bash
  pip install -r requirements.txt
  pip uninstall -y voitta  # Remove voitta if it was installed
  ```
- Use Python's path manipulation to import your local voitta implementation
  ```python
  # At the top of your script
  import sys
  sys.path.insert(0, '/Users/gregory/g/projects/llm/roma/voitta')
  # Now imports will use your local voitta
  from voitta import VoittaRouter
  ```

### Testing Environment (PyPI voitta)
- Create a separate testing virtual environment
  ```bash
  python -m venv .venv-test
  source .venv-test/bin/activate  # On Unix/macOS
  # or
  .venv-test\Scripts\activate  # On Windows
  ```
- Install all requirements including voitta from PyPI
  ```bash
  pip install -r requirements.txt
  ```

### Implementation Details
- Create shell scripts to easily switch between environments:
  - `dev.sh` to activate the development environment and set PYTHONPATH
  - `test.sh` to activate the testing environment
- Update VS Code launch configurations to set the appropriate environment variables

## Option 2: Editable Install with pip

This approach uses pip's editable install feature.

### Development Environment (Local voitta)
- Create a development virtual environment
  ```bash
  python -m venv .venv-dev
  source .venv-dev/bin/activate  # On Unix/macOS
  # or
  .venv-dev\Scripts\activate  # On Windows
  ```
- Install your local voitta in "editable" mode
  ```bash
  pip install -e ../voitta
  ```
- Install other dependencies normally
  ```bash
  pip install -r requirements.txt
  ```

### Testing Environment (PyPI voitta)
- Create a separate testing virtual environment
  ```bash
  python -m venv .venv-test
  source .venv-test/bin/activate  # On Unix/macOS
  # or
  .venv-test\Scripts\activate  # On Windows
  ```
- Install all requirements including voitta from PyPI
  ```bash
  pip install -r requirements.txt
  ```

### Implementation Details
- Editable installs allow you to modify the source code and see changes immediately
- No need for path manipulation in your code
- Create separate launch configurations for each environment

## Option 3: VS Code Workspace with Multiple Projects

This is the most integrated approach that leverages VS Code's workspace features.

### Implementation Details

#### 1. Create a VS Code Workspace

Create a workspace file (e.g., `voitta-workspace.code-workspace`) with the following content:

```json
{
    "folders": [
        {
            "path": ".",
            "name": "voitta-example"
        },
        {
            "path": "../voitta",
            "name": "voitta-local"
        }
    ],
    "settings": {
        "python.defaultInterpreterPath": "${workspaceFolder:voitta-example}/.venv-dev/bin/python",
        "python.analysis.extraPaths": [
            "${workspaceFolder:voitta-local}"
        ],
        "terminal.integrated.env.osx": {
            "PYTHONPATH": "${workspaceFolder:voitta-local}:${env:PYTHONPATH}"
        },
        "terminal.integrated.env.linux": {
            "PYTHONPATH": "${workspaceFolder:voitta-local}:${env:PYTHONPATH}"
        },
        "terminal.integrated.env.windows": {
            "PYTHONPATH": "${workspaceFolder:voitta-local};${env:PYTHONPATH}"
        }
    }
}
```

#### 2. Configure Python Environments

Create two virtual environments:

```bash
# Development environment (using local voitta)
python -m venv .venv-dev
source .venv-dev/bin/activate
pip install -r requirements.txt
pip uninstall -y voitta  # Remove voitta if it was installed

# Testing environment (using PyPI voitta)
python -m venv .venv-test
source .venv-test/bin/activate
pip install -r requirements.txt
```

#### 3. Configure VS Code Launch Configurations

Update the `.vscode/launch.json` file to include configurations for both environments:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Voitta Example (Dev)",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder:voitta-example}/voitta_example.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "python": "${workspaceFolder:voitta-example}/.venv-dev/bin/python",
            "env": {
                "PYTHONPATH": "${workspaceFolder:voitta-local}:${env:PYTHONPATH}"
            }
        },
        {
            "name": "Voitta Example (PyPI)",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder:voitta-example}/voitta_example.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "python": "${workspaceFolder:voitta-example}/.venv-test/bin/python"
        },
        {
            "name": "Filesystem Server",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder:voitta-example}/SERVERS/FILESYSTEM/main.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "env": {
                "PORT": "${env:FILESYSTEM_SERVER_PORT}"
            }
        }
    ],
    "compounds": [
        {
            "name": "Voitta (Dev) + Filesystem Server",
            "configurations": [
                "Filesystem Server",
                "Voitta Example (Dev)"
            ]
        },
        {
            "name": "Voitta (PyPI) + Filesystem Server",
            "configurations": [
                "Filesystem Server",
                "Voitta Example (PyPI)"
            ]
        }
    ]
}
```

#### 4. Create VS Code Tasks

Create a `.vscode/tasks.json` file to easily switch between environments:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Activate Dev Environment",
            "type": "shell",
            "command": "source .venv-dev/bin/activate",
            "windows": {
                "command": ".venv-dev\\Scripts\\activate"
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Activate Test Environment",
            "type": "shell",
            "command": "source .venv-test/bin/activate",
            "windows": {
                "command": ".venv-test\\Scripts\\activate"
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        }
    ]
}
```

#### 5. Update Configuration Files

Ensure that your `voitta.yaml` file is correctly located and referenced in your code. If it's in the `config` directory, update your code to reference it correctly:

```python
# Update this line in your Python files
voittaRouter = VoittaRouter("config/voitta.yaml")
```

#### 6. Using the Workspace

1. Open the workspace file in VS Code: `File > Open Workspace from File...`
2. Use the VS Code Python environment selector to switch between environments
3. Use the Run and Debug panel to launch the application with the appropriate configuration
4. Use the Tasks menu to activate the desired environment in the terminal

### Benefits of the VS Code Workspace Approach

- Seamless navigation between voitta-example and voitta source code
- Integrated debugging across both projects
- Easy switching between development and testing environments
- Consistent environment configuration for all team members
- No need to modify your Python code to handle different import paths

### Additional Considerations

- You may want to add the virtual environment directories to your `.gitignore` file
- Consider using environment variables for configuration that might differ between environments
- Document the setup process for new team members
