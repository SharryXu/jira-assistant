# jira-assistant: helps you deal with Jira more efficient

[TOC]

The `jira-assistant` package is a collection of tools which can make easier for you to retrieve information from the Jira platform and doing further processing.

`jira-assistant` requires: Python 3.10+

## A quick example for end user

```powershell
process-excel-file source.xlsx
```

## And here is another quick example for developer

```python
import pathlib
from jira_assistant import run_steps_and_sort_excel_file
HERE = pathlib.Path().resolve()
run_steps_and_sort_excel_file(HERE / "source.xlsx", HERE / "target.xlsx")
```

## Features

* Parsing the excel file which usually been downloaded from the Jira platform.
* Sorting the excel records using some specific logic.
* Generating the target excel file which contains the result.
* The excel file structure can be customized by JSON file.

## Bugs/Requests

Please use the [GitHub issue tracker](https://github.com/SharryXu/jira-assistant/issues) to submit bugs or request features.