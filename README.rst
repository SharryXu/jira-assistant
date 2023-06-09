Jira Assistant - userful jira tools
=============================================

|pypi| |Download| |Package Size| |CodeFactor| |GithubIssues| |Linux| |Windows| |Mac OS| |Pylint| |CodeQL| |Documentation| |Codecov| |CodeClimate| |License|

.. |PyPI| image:: https://img.shields.io/pypi/v/jira-assistant.svg?style=flat-square
    :target https://pypi.org/project/jira-assistant/
    :alt: pypi version

.. |Download| image:: https://static.pepy.tech/personalized-badge/jira-assistant?period=month&units=international_system&left_color=black&right_color=blue&left_text=downloads/month
    :target: https://pepy.tech/project/jira-assistant
    :alt: download

.. |Package Size| image:: https://img.shields.io/github/repo-size/sharryxu/jira-assistant
    :target: https://img.shields.io/github/repo-size/sharryxu/jira-assistant
    :alt: Package Size

.. |GitHubIssues| image:: https://img.shields.io/github/issues/sharryxu/jira-assistant
   :target: https://img.shields.io/github/issues/sharryxu/jira-assistant
   :alt: GitHub issues

.. |Linux| image:: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-linux-test.yml/badge.svg
    :target: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-linux-test.yml
    :alt: python 3.11 (Linux)

.. |Mac OS| image:: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-macos-test.yml/badge.svg
    :target: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-macos-test.yml
    :alt: python 3.11 (Mac OS)

.. |Windows| image:: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-windows-test.yml/badge.svg
    :target: https://github.com/SharryXu/jira-assistant/actions/workflows/python-3-windows-test.yml
    :alt: python 3.11 (Windows)

.. |Pylint| image:: https://github.com/sharryxu/jira-assistant/actions/workflows/pylint.yml/badge.svg
    :target: https://github.com/SharryXu/jira-assistant/actions/workflows/pylint.yml
    :alt: Pylint 

.. |CodeQL| image:: https://github.com/sharryxu/jira-assistant/workflows/CodeQL/badge.svg
    :target: https://github.com/SharryXu/jira-assistant/actions/workflows/CodeQL.yml
    :alt: CodeQL 

.. |Documentation| image:: https://readthedocs.org/projects/jira-assistant/badge/?version=latest
    :target: https://jira-assistant.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |Codecov| image:: https://codecov.io/gh/SharryXu/jira-assistant/branch/main/graph/badge.svg?token=BLI8NMS6S6 
    :target: https://codecov.io/gh/SharryXu/jira-assistant
    :alt: Codecov

.. |CodeClimate| image:: https://api.codeclimate.com/v1/badges/aeae36dcbb250784672b/maintainability
   :target: https://codeclimate.com/github/SharryXu/jira-assistant/maintainability
   :alt: Maintainability

.. |CodeFactor| image:: https://www.codefactor.io/repository/github/sharryxu/jira-assistant/badge
   :target: https://www.codefactor.io/repository/github/sharryxu/jira-assistant
   :alt: CodeFactor

.. |License| image:: https://img.shields.io/github/license/sharryxu/jira-assistant
   :target: https://img.shields.io/github/license/sharryxu/jira-assistant
   :alt: License

Collecting Ideas!!!
===================
If you have any ideas or good requirements related to this package, please let us know and we will do our best to fulfill! Please send emails to <sharry.xu@outlook.com>.

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

Documentation
=============

For full documentation, including installation, tutorials and PDF documents, please see https://jira-assistant.readthedocs.io/en/stable/

A Simple Example
================
You can run below command in the PowerShell (Windows OS) or Shell (UNIX OS) to process the excel files.

.. code-block:: console

    process-excel-file source.xlsx

After that, you can find the output file in the same folder along with the source file. 
For more details, please check the help message like below:

.. code-block:: console

    process-excel-file -h

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
  from jira_assistant import run_steps_and_sort_excel_file
  HERE = pathlib.Path().resolve()
  run_steps_and_sort_excel_file(HERE / "source.xlsx", HERE / "target.xlsx")

If you want to customize the definition file to adapt the new Excel, you can do below steps.

1. Creating the definition file like below. Inside the :code:`PreProcessSteps` list, you can determine the procedure which will be triggered before sorting and also inside the :code:`SortStrategyPriority` list, you can decide the sort algorithms' order. Note: We need to make sure there is one column named ``StoryId`` and only one.

.. code-block:: json

  [
      {
          "PreProcessSteps": [
              {
                  "Name": "FilterOutStoryWithoutId",
                  "Enabled": true,
                  "Priority": 1,
                  "Config": {}
              },
              {
                  "Name": "RetrieveJiraInformation",
                  "Enabled": true,
                  "Priority": 2,
                  "Config": {}
              },
              {
                  "Name": "FilterOutStoryBasedOnJiraStatus",
                  "Enabled": true,
                  "Priority": 3,
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

2. Indicating the definition file location to the :code:`run_steps_and_sort_excel_file` method like below.

.. code-block:: python

  run_steps_and_sort_excel_file(
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

  run_steps_and_sort_excel_file(
      HERE / "source.xlsx", 
      HERE / "target.xlsx", 
      sprint_schedule_file=HERE / "milestone_priority.json"
  )

Author
======
The jira-assistant was written by Sharry Xu <sharry.xu@outlook.com> in 2022.

Starting with version 0.1.5, the main function of this project has been totally finished.

License
=======
All contributions after December 1, 2022 released under MIT license.
