# -*- coding: utf-8 -*-
"""
This module is used to store excel column definition information.
"""
import json
import pathlib
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from re import compile
from types import NoneType
from typing import Any, TypedDict

from .milestone import Milestone
from .priority import Priority

__all__ = ["ExcelDefinition"]

RaiseRankingLevelScopeIndexValidationRule = compile(
    r"(^(\d{1,},){0,}\d{1,}$)|^\d{1,}-\d{1,}$"
)

# Load -> Parse -> Validate?


class PreProcessStep(TypedDict):
    name: str
    enabled: bool
    config: dict


def parse_json_item_to_pre_process_step(json_item: Any) -> PreProcessStep:
    pre_process_step_name = ""
    pre_process_step_enabled = False
    pre_process_step_config = {}

    for key, value in json_item.items():
        if key.lower() == "name".lower():
            if type(value) is str:
                pre_process_step_name = value
            else:
                raise TypeError("The Name property type should be string.")
        if key.lower() == "enabled".lower():
            if type(value) is bool:
                pre_process_step_enabled = value
            else:
                raise TypeError("The Enabled property type should be boolean.")
        if key.lower() == "config".lower():
            pre_process_step_config = {}
            if value is not None and type(value) is dict:
                for name in value:
                    # More config support.
                    if name.lower() == "JiraStatuses".lower():
                        pre_process_step_config["JiraStatuses"] = value.get(name, None)

    return PreProcessStep(
        name=pre_process_step_name,
        enabled=pre_process_step_enabled,
        config=pre_process_step_config,
    )


class SortStrategy(TypedDict):
    name: str
    priority: int | NoneType
    enabled: bool
    config: dict


def parse_json_item_to_sort_strategy(json_item: Any) -> SortStrategy:
    strategy_name = ""
    strategy_priority = 0
    strategy_enabled = False
    strategy_config = {}

    for key, value in json_item.items():
        if key.lower() == "name".lower():
            if type(value) is str:
                strategy_name = value
            else:
                raise TypeError("The Name property type should be string.")
        if key.lower() == "priority".lower():
            if type(value) is int:
                strategy_priority = value
            else:
                raise TypeError("The Priority property type should be integer.")
        if key.lower() == "enabled".lower():
            # TODO: Some basic error should be through now???
            if type(value) is bool:
                strategy_enabled = value
            else:
                raise TypeError("The Enabled property type should be boolean.")
        if key.lower() == "config".lower():
            strategy_config = {}
            if value is not None and type(value) is dict:
                for name in value:
                    # More config support.
                    if name.lower() == "ParentScopeIndexRange".lower():
                        strategy_config[
                            name
                        ] = ExcelDefinition.parse_raise_ranking_level_scope_index_expression(
                            value.get(name, None)
                        )

    return SortStrategy(
        name=strategy_name,
        priority=strategy_priority,
        enabled=strategy_enabled,
        config=strategy_config,
    )


class ExcelDefinitionColumn(TypedDict):
    index: int
    name: str | NoneType
    type: type | NoneType
    require_sort: bool
    sort_order: bool
    scope_require_sort: bool
    scope_sort_order: bool
    inline_weights: int
    raise_ranking: int
    scope_raise_ranking: int
    jira_field_mapping: dict[str, str] | NoneType


def parse_json_item_to_excel_definition_column(json_item: Any) -> ExcelDefinitionColumn:
    column_index = 0
    column_name = None
    column_type = None
    column_require_sort = False
    column_sort_order = False
    column_scope_require_sort = False
    column_scope_sort_order = False
    column_inline_weights = -1
    column_raise_ranking = -1
    column_scope_raise_ranking = -1
    column_jira_field_mapping = None

    for key, value in json_item.items():
        if key.lower() == "index".lower():
            column_index = value
        if key.lower() == "name".lower():
            column_name = value
        if key.lower() == "type".lower():
            column_type = ExcelDefinition.convert_str_to_type(value)
        if key.lower() == "RequireSort".lower():
            column_require_sort = value
        if key.lower() == "SortOrder".lower():
            column_sort_order = value
        if key.lower() == "ScopeRequireSort".lower():
            column_scope_require_sort = value
        if key.lower() == "ScopeSortOrder".lower():
            column_scope_sort_order = value
        if key.lower() == "InlineWeights".lower():
            column_inline_weights = value
        if key.lower() == "RaiseRanking".lower():
            column_raise_ranking = value
        if key.lower() == "ScopeRaiseRanking".lower():
            column_scope_raise_ranking = value
        if key.lower() == "JiraFieldMapping".lower():
            column_jira_field_mapping = value

    return ExcelDefinitionColumn(
        index=column_index,
        name=column_name,
        type=column_type,
        require_sort=column_require_sort,
        sort_order=column_sort_order,
        scope_require_sort=column_scope_require_sort,
        scope_sort_order=column_scope_sort_order,
        inline_weights=column_inline_weights,
        raise_ranking=column_raise_ranking,
        scope_raise_ranking=column_scope_raise_ranking,
        jira_field_mapping=column_jira_field_mapping,
    )


class ExcelDefinition:
    def __init__(self) -> None:
        self.columns: list[ExcelDefinitionColumn] = []
        self.sort_strategies: list[SortStrategy] = []
        self.pre_process_steps: list[PreProcessStep] = []

    def load(self, content: str) -> "ExcelDefinition":
        """
        Load json string to generate the excel definition

        :param content:
            JSON string content
        """

        if content is None:
            raise ValueError("There is no content in the excel definition file.")

        try:
            raw_data = json.loads(content)

            if len(raw_data) > 0:
                if raw_data[0].get("PreProcessSteps", None) is not None:
                    for item in raw_data[0]["PreProcessSteps"]:
                        self.pre_process_steps.append(
                            parse_json_item_to_pre_process_step(item)
                        )

                if raw_data[0].get("SortStrategies", None) is not None:
                    for item in raw_data[0]["SortStrategies"]:
                        self.sort_strategies.append(
                            parse_json_item_to_sort_strategy(item)
                        )

            if len(raw_data) >= 1:
                for item in raw_data[1]["Columns"]:
                    self.columns.append(
                        parse_json_item_to_excel_definition_column(item)
                    )
        except Exception:
            raise ValueError(
                "The JSON structure of the excel definition file is wrong. Please check the documentation: https://github.com/SharryXu/jira-assistant"
            )

        return self

    @staticmethod
    def parse_raise_ranking_level_scope_index_expression(
        expression: "Any | None",
    ) -> "set[int] | None":
        if expression is None or type(expression) is not str:
            return None
        elif len(expression) == 0 or expression.isspace():
            return set()
        elif (
            RaiseRankingLevelScopeIndexValidationRule.fullmatch(
                "".join(expression.split(" "))
            )
            is None
        ):
            return None  # None means invalid, since we don't have the parse procedure.
        elif "-" in expression:
            begin = int(expression.split("-")[0])
            end = int(expression.split("-")[1])
            if begin < end:
                return set(i for i in range(begin, end + 1))
            else:
                return set(i for i in range(end, begin + 1))
        else:
            return set(int(i) for i in expression.split(","))

    def load_file(self, file: "str | Path") -> "ExcelDefinition":
        """
        Load json file to generate the excel definition

        :param file:
            JSON file location
        """

        if file is None or not pathlib.Path(file).is_absolute():
            raise ValueError("The file is invalid.")

        if not pathlib.Path(file).exists():
            raise ValueError(f"The file is not exist. File: {file}")

        with open(file=file, mode="r") as table_definition_file:
            try:
                self.load(table_definition_file.read())
            finally:
                table_definition_file.close()

        return self

    def validate(self) -> "list":
        invalid_definitions = []

        # Validate PreProcessSteps
        for pre_process_step in self.pre_process_steps:
            if (
                pre_process_step["name"] is None
                or type(pre_process_step["name"]) is not str
                or pre_process_step["name"].isspace()
                or len(pre_process_step["name"]) == 0
            ):
                invalid_definitions.append(f"The PreProcessStep name is invalid.")
                # If strategy name is invalid, no need to check more.
                continue

            if "JiraStatuses".lower() in [
                config_name.lower() for config_name in pre_process_step["config"].keys()
            ] and (
                pre_process_step["name"].lower()
                != "FilterOutStoryBasedOnJiraStatus".lower()
            ):
                invalid_definitions.append(
                    f"Only FilterOutStoryBasedOnJiraStatus step support JiraStatuses config. PreProcessStep: {pre_process_step['name']}."
                )

            if (
                "JiraStatuses".lower()
                in [
                    config_name.lower()
                    for config_name in pre_process_step["config"].keys()
                ]
                and type(pre_process_step["config"]["JiraStatuses"]) is not list
            ):
                invalid_definitions.append(
                    f"The format of the Jira Statuses is invalid. PreProcessStep: {pre_process_step['name']}. Supported format like: ['CLOSED', 'PENDING RELEASE']."
                )

        # Validate Strategies
        strategy_priorities: list[int] = []
        for strategy in self.sort_strategies:
            if (
                strategy["name"] is None
                or type(strategy["name"]) is not str
                or strategy["name"].isspace()
                or len(strategy["name"]) == 0
            ):
                invalid_definitions.append(f"The strategy name is invalid.")
                # If strategy name is invalid, no need to check more.
                continue

            if (
                strategy["priority"] is None
                or type(strategy["priority"]) is not int
                or strategy["priority"] < 0
            ):
                invalid_definitions.append(
                    f"The strategy priority is invalid. Strategy: {strategy['name']}"
                )
            else:
                strategy_priorities.append(strategy["priority"])

            if "ParentScopeIndexRange".lower() in [
                config_name.lower() for config_name in strategy["config"].keys()
            ] and (
                strategy["name"].lower() != "SortOrder".lower()
                and strategy["name"].lower() != "RaiseRanking".lower()
            ):
                invalid_definitions.append(
                    f"Only RaiseRanking and SortOrder strategy support ParentScopeIndexRange config. Strategy: {strategy['name']}."
                )

            if (
                "ParentScopeIndexRange".lower()
                in [config_name.lower() for config_name in strategy["config"].keys()]
                and type(strategy["config"]["ParentScopeIndexRange"]) is not set
            ):
                invalid_definitions.append(
                    f"The format of the Parent Level Index Range is invalid. Strategy: {strategy['name']}. Supported format strings like: 1-20 or 20,30 or empty string."
                )

        if len(strategy_priorities) != len(set(strategy_priorities)):
            invalid_definitions.append(
                f"The priority of strategies cannot be duplicate."
            )

        # Validate the Columns
        exist_story_id = False
        exist_indexes = []
        exist_inline_weights = []
        for column in self.get_columns():
            column_index: int = column["index"]
            column_name: str | None = column["name"]
            column_type: type | None = column["type"]
            column_require_sort: bool = column["require_sort"]
            column_sort_order: bool = column["sort_order"]
            column_scope_require_sort: bool = column["scope_require_sort"]
            column_scope_sort_order: bool = column["scope_sort_order"]
            column_inline_weights: int = column["inline_weights"]
            column_raise_ranking: int = column["raise_ranking"]
            column_scope_raise_ranking: int = column["scope_raise_ranking"]
            column_jira_field_mapping: dict | None = column["jira_field_mapping"]

            # Check Name cannot be empty
            if type(column_name) is not str or len(column_name) == 0:
                invalid_definitions.append(
                    f"Column name cannot be empty. Index: {column_index}"
                )
                continue

            if column_name.lower() == "StoryId".lower():
                exist_story_id = True

            # Check Missing/Duplicate Index
            if type(column_index) is not int:
                invalid_definitions.append(
                    f"Column Index can only be number. Column: {column_name}"
                )
            elif column_index is None:
                invalid_definitions.append(f"Missing Index. Column: {column_name}")
            elif column_index in exist_indexes:
                invalid_definitions.append(f"Duplicate Index. Column: {column_name}")
            else:
                exist_indexes.append(column_index)
            # Check Property Type
            if column_type not in (
                str,
                bool,
                datetime,
                Priority,
                Milestone,
                float,
            ):
                invalid_definitions.append(
                    f"Invalid Column Type. Column: {column_name}"
                )

            # Check Sort
            if type(column_require_sort) is not bool:
                invalid_definitions.append(
                    f"Require Sort can only be True/False. Column: {column_name}"
                )

            if type(column_sort_order) is not bool:
                invalid_definitions.append(
                    f"Sort Order can only be True(Descending)/False(Ascending). Column: {column_name}"
                )

            # Check Sort
            if type(column_scope_require_sort) is not bool:
                invalid_definitions.append(
                    f"Scope Require Sort can only be True/False. Column: {column_name}"
                )

            if type(column_scope_sort_order) is not bool:
                invalid_definitions.append(
                    f"Scope Sort Order can only be True(Descending)/False(Ascending). Column: {column_name}"
                )

            # Check InlineWeights
            # TODO: Currently only support different line weights.
            if type(column_inline_weights) is not int:
                invalid_definitions.append(
                    f"Inline Weights can only be number. Column: {column_name}"
                )
            else:
                if (
                    column_inline_weights > 0
                    and column_inline_weights in exist_inline_weights
                ):
                    invalid_definitions.append(
                        f"Duplicate Inline Weights. Column: {column_name}"
                    )
                exist_inline_weights.append(column_inline_weights)

            # Check RaiseRanking
            if type(column_raise_ranking) is not int:
                invalid_definitions.append(
                    f"Raise Ranking can only be number. Column: {column_name}"
                )
            else:
                # Check Support RaiseRanking or not
                if column_type not in (bool,) and column_raise_ranking > 0:
                    invalid_definitions.append(
                        f"Column do not support Raise Ranking feature. Column: {column_name}"
                    )

            if type(column_scope_raise_ranking) is not int:
                invalid_definitions.append(
                    f"Scope Raise Ranking can only be number. Column: {column_name}"
                )
            else:
                # Check Support RaiseRanking or not
                if column_type not in (bool,) and column_scope_raise_ranking > 0:
                    invalid_definitions.append(
                        f"Column do not support Scope Raise Ranking feature. Column: {column_name}"
                    )

            if column_jira_field_mapping is None:
                continue
            elif (
                column_jira_field_mapping is not None
                and type(column_jira_field_mapping) is not dict
            ):
                invalid_definitions.append(
                    f"Jira Field Mapping can only be dictionary. Column: {column_name}"
                )
            else:
                jira_field_name = column_jira_field_mapping.get("name", None)
                if jira_field_name is None or jira_field_name.isspace():
                    invalid_definitions.append(
                        f"Jira Field Mapping has the invalid name. Column: {column_name}"
                    )
                jira_field_path = column_jira_field_mapping.get("path", None)
                if jira_field_path is None or jira_field_path.isspace():
                    invalid_definitions.append(
                        f"Jira Field Mapping has the invalid path. Column: {column_name}"
                    )

        if len(self.columns) > 0 and exist_story_id is False:
            invalid_definitions.append(
                "Must have a column named StoryId so that program can identify the record."
            )

        if len(invalid_definitions) == 0:
            self.columns.sort(key=lambda c: c["index"], reverse=False)

            if len(self.columns) > 0 and (
                self.columns[0]["index"] != 1
                or self.columns[len(self.columns) - 1]["index"] != len(self.columns)
            ):
                invalid_definitions.append(
                    f"Column Index must be in continuation and starts from 1."
                )

        return invalid_definitions

    @staticmethod
    def convert_str_to_type(type_str: str) -> "type | None":
        if type_str is None or type(type_str) is not str:
            return None
        type_str = str(type_str).strip().lower()
        if type_str.lower() == "str":
            return str
        elif type_str.lower() == "bool":
            return bool
        elif type_str.lower() == "datetime":
            return datetime
        elif type_str.lower() == "priority":
            return Priority
        elif type_str.lower() == "milestone":
            return Milestone
        # Currently, only support float/double
        elif type_str.lower() == "number":
            return float
        else:
            return None

    def __iter__(self):
        for item in self.columns:
            yield item

    def get_columns(self) -> "list[ExcelDefinitionColumn]":
        return deepcopy(self.columns)

    def get_columns_name(self) -> "list[str | None]":
        return [item["name"] for item in self.columns]

    @property
    def max_column_index(self) -> int:
        return self.columns[len(self.columns) - 1]["index"]

    def get_sort_strategies(self, enabled: bool = True) -> "list[SortStrategy]":
        result: list[SortStrategy] = []
        for sort_strategy in self.sort_strategies:
            if sort_strategy["enabled"] == enabled:
                result.append(deepcopy(sort_strategy))
        result.sort(key=_sort_priority_map, reverse=False)
        return result

    def get_pre_process_steps(self, enabled: bool = True) -> "list[PreProcessStep]":
        result: list[PreProcessStep] = []
        for pre_process_step in self.pre_process_steps:
            if pre_process_step["enabled"] == enabled:
                result.append(deepcopy(pre_process_step))
        return result

    def total_count(self):
        return len(self.columns)


def _sort_priority_map(strategy: SortStrategy) -> int:
    if strategy["priority"] is None or type(strategy["priority"]) is not int:
        return 0
    else:
        return strategy["priority"]
