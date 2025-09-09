# Azure DevOps Practical Tools

<!-- Basic Python -->
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://pypi.org/project/adopt/)
[![PyPI version](https://badge.fury.io/py/adopt.svg)](https://badge.fury.io/py/adopt)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-green.svg)](https://opensource.org/licenses/BSD-3-Clause)

<!-- Repository -->
[![GitHub](https://img.shields.io/badge/github-azure--devops--tools-blue.svg)](https://github.com/cvandijck/azure-devops-tools)
[![CI](https://github.com/cvandijck/azure-devops-tools/workflows/Build,%20Test%20and%20Install/badge.svg)](https://github.com/cvandijck/azure-devops-tools/actions)

<!-- Tooling -->
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![pytest](https://img.shields.io/badge/pytest-enabled-blue.svg)](https://github.com/pytest-dev/pytest)

<br>

> _To Augustin, a PM with an imperturbable annoyance for all things Azure DevOps.. Without your daily complaints, this project would not exist._

<br>
<br>

**A**zure **D**ev**O**ps **P**ractical **T**ools is a set of tools to automate working with Azure Devops. The tools are developed as a CLI tool `adopt` to easily manage your Azure Devops project. The tool is actively being developed and tools are continuously being added. Suggestions for new tools are always welcome and can be requested via the [GitHub issues](https://github.com/cvandijck/azure-devops-tools/issues) or, even better, by [contributing](#contribute) to the project.

## Installation

The preferred way to install `adopt` to use as a global CLI tool is to install it via `uv` and run it via `uvx`, the `pipx` variant for the `uv` package manager.

If you don't have `uv` and `uvx` installed yet, you can install it by running:

```console
winget install --id=astral-sh.uv
```

or by following the instructions on the [uv website](https://docs.astral.sh/uv/).

After installing `uv`, you can install `adopt` as a uv tool by running:

```console
uv tool install adopt@latest
```

and then run the tool by running:

```console
uvx adopt
```

Alternatively, you can install `adopt` as a CLI tool using pip or globally using pipx:

```console
python -m pip install adopt
```

Or install it as a global CLI tool using pipx:

```console
pipx install adopt
```

## Getting Started

Adopt is developed as a CLI tool to easily manage your Azure Devops project. You can discover which tools are available by displaying the help page of the console script:

```console
adopt --help
```

For each command, you need to provide different arguments to connect to your specific Azure Devops project and team.

Luckily, a lot of these arguments can be stored in a configuration file, so you don't have to provide them each time you run a command. More information on how to configure the tool can be found in the [Configuration](#configuration) section.

### Backlog Print

Get a nicely formatted overview of your backlog in your terminal.

```console
adopt backlog print --url <azure_devops_org_url> --token <azure_devops_personal_token> --project <azure_devops_project> --team <azure_devops_team> --category <azure_devops_backlog_category>
```

### Backlog Sort

Tired of cleaning up your backlog by dragging work items each time you had a backlog refinement or planning session?
With this short command you can automatically sort the backlog following the specific order you like.

```console
adopt backlog print --url <azure_devops_org_url> --token <azure_devops_personal_token> --project <azure_devops_project> --team <azure_devops_team> --category <azure_devops_backlog_category> --sort_key <azure_devops_work_item_field>
```

The `--sort_key` argument determines the order in which the work items will be sorted in the backlog. The value of the `--sort_key` argument should be a string of characters, where each character represents a field of the work item. The order of the characters in the string determines the order in which the work items will be sorted. In lower case, an acending order is used. When capitalized, the item will be sorted in descending order. The following characters are supported:

| Key   | Field                            |
| ----- | -------------------------------- |
| **i** | Iteration path of item           |
| **p** | Priority of item                 |
| **t** | Title of item                    |
| **r** | Rank of parents in their backlog |


For example, the default sorting key `Iprt` command will sort the work items in the backlog first by *iteration path* in descending order (bringing the latest iteration on top), then followed by *priority*, *parent rank* and *title* in ascending order, bringing highest prio work items to the top, with additional sorting by parent item ranking and finally title.

### Backlog Check

Check the backlog for any inconsistencies. The following checks can be performed:

- Check if all work items have a parent
- Check if all work items have are assigned
- Check if all work items have story points assigned

Each check can be enabled separately by using the `--check-{option}` argument, or all at once using the `--check-all` argument.

```console
adopt backlog check --url <azure_devops_org_url> --token <azure_devops_personal_token> --project <azure_devops_project> --team <azure_devops_team> --category <azure_devops_backlog_category> [--check-all] [--check-parent] [--check-assigned] [--check-points]
```

### Backlog Fix

The `backlog fix` command can automatically fix inconsistencies in the backlog. The following fixes can be performed:

- Update the parent work item *State* based on the state of the child work items
- Update the parent work item *Iteration Path* based on the assigned to of the child work items

Each fix can be enabled separately by using the `--fix-{option}` argument, or all at once using the `--fix-all` argument.

```console
adopt backlog fix --url <azure_devops_org_url> --token <azure_devops_personal_token> --project <azure_devops_project> --team <azure_devops_team> --category <azure_devops_backlog_category> [--fix-all] [--fix-state] [--fix-iteration]
```

### Debug logging
Each command has logging functionality built in. The level of logging can be set by using the `--log-level` argument. The default log level is `INFO`.

### Configuration

For each command, you need to provide different arguments to connect to your specific Azure Devops project and team. To make the (re)execution of `adopt` commands easier and facilitates its use in different environments, multiple pathways are provided to configure the tool.

Each configuration option will load predefined values for the required arguments as environment variables, so the first option to provide the required arguments is by setting these variables in the (local) environment.


| Argument    | Environment Variable                  | Description                                               |
| ----------- | ------------------------------------- | --------------------------------------------------------- |
| `--token`   | `ADOPT_AZURE_DEVOPS_PAT`              | A personal access token to authenticate with Azure Devops |
| `--url`     | `ADOPT_AZURE_DEVOPS_ORGANIZATION_URL` | The URL of your Azure Devops organization                 |
| `--project` | `ADOPT_AZURE_DEVOPS_PROJECT_NAME`     | The name of the project you want to work with             |
| `--team`    | `ADOPT_AZURE_DEVOPS_TEAM_NAME`        | The name of the team you want to work with                |

These values can also be loaded, or overwritten, by a local `.env` file in the working directly from which `adopt` is executed.

Alternatively, a TOML-styled configuration file `.adopt` can be used locally in the project directory or globally in the user's home directory to set these required arguments:

```toml
[adopt]
token = "<azure_devops_personal_token>"
url = "<azure_devops_org_url>"
project = "<azure_devops_project>"
team = "<azure_devops_team>"
```

> [!NOTE]
> A combination between the configuration file and an environment variable for your *Azure Personal Access Token* is recommended to safely manage these predefined arguments.

## Nightly Backlog Management
Adopt can be used to automatically manage your backlog on a nightly basis. The easiest way to do this is to add a DevOps pipeline to your project that runs the required `adopt` commands on a nightly basis. An example YAML pipeline to run the `backlog sort` command can be found below:

```yaml
trigger: none

parameters:
- name: logLevel
  displayName: 'Log Level'
  type: string
  default: 'INFO'
  values:
  - DEBUG
  - INFO
  - WARNING
  - ERROR
  - CRITICAL

variables:
  url: "https://dev.azure.com/<your_organization>"
  project: "<your_project>"
  team: "<your_team>"

schedules:
- cron: "0 0 * * *"
  displayName: Nightly run
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

jobs:
- job: ManageBacklog
  displayName: 'Manage Backlog'
  variables:
    ADOPT_AZURE_DEVOPS_ORGANIZATION_URL: $(url)
    ADOPT_AZURE_DEVOPS_PROJECT_NAME: $(project)
    ADOPT_AZURE_DEVOPS_TEAM_NAME: $(team)
  steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.x'
      addToPath: true
    displayName: 'Use Latest Python'

  - script: |
      python -m pip install --upgrade pip
      pip install adopt
    displayName: 'Install latest version of adopt'

  - script: |
      adopt backlog sort --token $(System.AccessToken) --log-level "${{ parameters.logLevel }}" 2>&1 | tee adopt_output.log

      exit_code=${PIPESTATUS[0]}
      if [ $exit_code -ne 0 ]; then
        echo "##vso[task.logissue type=error]adopt backlog sort failed with exit code $exit_code"
        exit $exit_code
      elif grep -q "WARNING" adopt_output.log; then
        echo "##vso[task.logissue type=warning]WARNING detected in adopt backlog sort output"
        echo "##vso[task.complete result=SucceededWithIssues;]WARNING found but continuing pipeline"
        exit 0
      else
        echo "No warnings detected - sort completed successfully"
        exit 0
      fi
    displayName: 'Sort backlog'

  - script: |
      adopt backlog check --token $(System.AccessToken) --log-level "${{ parameters.logLevel }}" 2>&1 | tee adopt_check_output.log

      exit_code=${PIPESTATUS[0]}
      if [ $exit_code -ne 0 ]; then
        echo "##vso[task.logissue type=error]adopt backlog check failed with exit code $exit_code"
        exit $exit_code
      elif grep -q "WARNING" adopt_check_output.log; then
        echo "##vso[task.logissue type=warning]WARNING detected in adopt backlog check output"
        echo "##vso[task.complete result=SucceededWithIssues;]WARNING found but continuing pipeline"
        exit 0
      else
        echo "No warnings detected - check completed successfully"
        exit 0
      fi
    displayName: 'Check backlog'
```

## Contribute

In `adopt`, the incredibly fast package manager `uv` is used to setup and manage the project. To get started with the project, you can install `uv` by running:

```console
winget install --id=astral-sh.uv
```

or by following the instructions on the [uv website](https://docs.astral.sh/uv/).

After installing `uv`, you can setup the project by running:

```console
uv sync
```
For convenience, most operations required to contribute or manage this project are available as `make` commands.
