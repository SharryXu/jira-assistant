Jira Assistant - userful jira tools
=============================================

|pypi| |python 3.11| |python 3.11 (Mac OS)| |CodeQL| |Documentation|

.. |PyPI| image:: https://img.shields.io/pypi/v/jira-assistant.svg?style=flat-square
    :target https://pypi.org/project/jira-assistant/
    :alt: pypi version

.. |python 3.11| image:: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-11-test.yml/badge.svg
    :target: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-11-test.yml
    :alt: python 3.11

.. |python 3.11 (Mac OS)| image:: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-11-macos-test.yml/badge.svg
    :target: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-11-macos-test.yml
    :alt: python 3.11 (Mac OS)

.. |CodeQL| image:: https://github.com/sharryxu/jira-assistant/workflows/CodeQL/badge.svg
    :target: https://github.com/SharryXu/jira-assistant/actions/workflows/CodeQL.yml
    :alt: CodeQL 

.. |Documentation| image:: https://readthedocs.org/projects/jira-assistant/badge/?version=latest
    :target: https://jira-assistant.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Installation
============
`jira-assistant` can be installed from PyPI using `pip` (note that the package name is different from the importable name)::

    pip install -U jira-assistant

Download
========
jira-assistant is available on PyPI
https://pypi.org/project/jira-assistant

Code
====
The code and issue tracker are hosted on GitHub:
https://github.com/SharryXu/jira-assistant

Features
========

* Parsing the excel file which usually been downloaded from the Jira platform.
* Sorting the excel records using some specific logic.
* Generating the target excel file which contains the result.
* The excel file structure can be customized by JSON file.

A Simple Example
================

You can run below command in the PowerShell (Windows OS) or Shell (UNIX OS) to process the excel files.

.. code-block:: console

    sort-excel-file source.xlsx

After that, you can find the output file in the same folder along with the source file. 
For more details, please check the help message like below:

.. code-block:: console

    sort-excel-file -h

Currently, we are using the `jira access token`__ to do the validation and that means we need you to generate your own access token from the website first.

.. __: https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html

.. code-block:: console

    update-jira-info --token <access_token> --url <jira_url>

If you want to use your own definition files before processing the excel, you can run below command to access some templates which can help you understand the definition file.

.. code-block:: console

    generate-template excel-definition

For more details, please check the help message like below:

.. code-block:: console

    generate-template -h


Code Example For Developer
==========================

Here's a simple program, just to give you an idea about how to use this package.

.. code-block:: python

  import pathlib
  from jira_assistant import process_excel_file
  HERE = pathlib.Path().resolve()
  process_excel_file(HERE / "source.xlsx", HERE / "target.xlsx")

If you want to customize the definition file to adapt the new Excel, you can do below steps.

1. Creating the definition file like below. Inside the :code:`PreProcessSteps` list, you can determine the procedure which will be triggered before sorting and also inside the :code:`SortStrategyPriority` list, you can decide the sort algorithms' order.

.. code-block:: json

  [
      {
          "PreProcessSteps": [
              {
                  "Name": "FilterOutStoryWithoutId",
                  "Enabled": true,
                  "Config": {}
              },
              {
                  "Name": "RetrieveJiraInformation",
                  "Enabled": true,
                  "Config": {}
              },
              {
                  "Name": "FilterOutStoryBasedOnJiraStatus",
                  "Enabled": true,
                  "Config": {
                      "JiraStatuses": [
                          "SPRINT COMPLETE",
                          "PENDING RELEASE",
                          "PRODUCTION TESTING",
                          "CLOSED"
                      ]
                  }
              }
          ],
          "SortStrategies": [
            {
                "Name": "InlineWeights",
                "Priority": 1,
                "Enabled": true,
                "Config": {}
            },
            {
                "Name": "SortOrder",
                "Priority": 2,
                "Enabled": true,
                "Config": {}
            },
            {
                "Name": "SortOrder",
                "Priority": 3,
                "Enabled": true,
                "Config": {
                    "ParentScopeIndexRange": "12-19"
                }
            },
            {
                "Name": "RaiseRanking",
                "Priority": 4,
                "Enabled": true,
                "Config": {
                    "ParentScopeIndexRange": "12-19"
                }
            }
        ]
      },
      {
          "Columns": [
              {
                  "Index": 1,
                  "Name": "entryDate",
                  "Type": "datetime",
                  "RequireSort": false,
                  "SortOrder": false,
                  "ScopeRequireSort": false,
                  "ScopeSortOrder": false,
                  "InlineWeights": 0,
                  "RaiseRanking": 0,
                  "ScopeRaiseRanking": 0
              }
          ]
      }
  ]

2. Indicating the definition file location to the :code:`process_excel_file` method like below.

.. code-block:: python

  process_excel_file(
      HERE / "source.xlsx", 
      HERE / "target.xlsx", 
      excel_definition_file=HERE / "definition_file.json"
  )

Meantime, you can follow the same way to customize the milestone priority file.

1. Configuration file

.. code-block:: json

  [
      {
        "Priority": 1,
        "Sprints": ["R134 S1", "M109"]
      }
  ]

2. Code example

.. code-block:: python

  process_excel_file(
      HERE / "source.xlsx", 
      HERE / "target.xlsx", 
      sprint_schedule_file=HERE / "milestone_priority.json"
  )

Author
======
The jira-assistant was written by Sharry Xu <sharry.xu@outlook.com> in 2022.

Starting with version 0.1.13, the main function of this project has been totally finished.

Contact
=======
Our mailing list is available at `sharry.xu@outlook.com`.

License
=======
All contributions after December 1, 2022 released under MIT license.
