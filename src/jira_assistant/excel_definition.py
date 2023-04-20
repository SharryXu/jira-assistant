# -*- coding: utf-8 -*-
"""
This module is used to store excel column definition information.
"""
from __future__ import annotations

import pathlib
import re
from copy import deepcopy
from datetime import datetime
from json import loads
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, List, Optional, Set, TypedDict, Union

from .milestone import Milestone
from .priority import Priority

__all__ = ["ExcelDefinition"]

RaiseRankingLevelScopeIndexValidationRule = re.compile(
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
            if value is None:
                raise ValueError("The pre-process step must have a name.")
            if isinstance(value, str):
                pre_process_step_name = value
            else:
                raise TypeError(
                    "The Name property type in the pre-process step should be string."
                )
        if key.lower() == "enabled".lower():
            if value is None:
                pre_process_step_enabled = False
            elif isinstance(value, bool):
                pre_process_step_enabled = value
            else:
                raise TypeError(
                    "The Enabled property type in the pre-process step should be boolean."
                )
        if key.lower() == "config".lower():
            pre_process_step_config = {}
            if value is not None and isinstance(value, dict):
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
    priority: Optional[int]
    enabled: bool
    config: dict


def parse_json_item_to_sort_strategy(json_item: Any) -> SortStrategy:
    strategy_name = ""
    strategy_priority = 0
    strategy_enabled = False
    strategy_config = {}

    for key, value in json_item.items():
        if key.lower() == "name".lower():
            if value is None:
                raise ValueError("The sort strategy must have a name.")
            if isinstance(value, str):
                strategy_name = value
            else:
                raise TypeError(
                    "The Name property type in the sort strategy should be string."
                )
        if key.lower() == "priority".lower():
            if value is None:
                strategy_priority = 0
            elif isinstance(value, int):
                strategy_priority = value
            else:
                raise TypeError(
                    "The Priority property type in the sort strategy should be integer."
                )
        if key.lower() == "enabled".lower():
            if value is None:
                strategy_enabled = False
            elif isinstance(value, bool):
                strategy_enabled = value
            else:
                raise TypeError(
                    "The Enabled property type in the sort strategy should be boolean."
                )
        if key.lower() == "config".lower():
            strategy_config = {}
            if value is not None and isinstance(value, dict):
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
    name: str
    type: Optional[type]
    require_sort: bool
    sort_order: bool
    scope_require_sort: bool
    scope_sort_order: bool
    inline_weights: int
    raise_ranking: int
    scope_raise_ranking: int
    jira_field_mapping: Optional[dict[str, str]]


def parse_json_item_to_excel_definition_column(json_item: Any) -> ExcelDefinitionColumn:
    column_index = 0
    column_name = ""
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
            if value is None:
                raise ValueError("Column definition must has an index.")
            if isinstance(value, int):
                column_index = value
            else:
                raise TypeError(
                    "The Index property type in the column definition is not integer."
                )
        elif key.lower() == "name".lower():
            if value is None:
                raise ValueError("Column definition must has a name.")
            if isinstance(value, str):
                column_name = value
            else:
                raise TypeError(
                    "The Name property type in the column definition should be string."
                )
        elif key.lower() == "type".lower():
            column_type = ExcelDefinition.convert_str_to_type(value)
        elif key.lower() == "RequireSort".lower():
            column_require_sort = value
        elif key.lower() == "SortOrder".lower():
            column_sort_order = value
        elif key.lower() == "ScopeRequireSort".lower():
            column_scope_require_sort = value
        elif key.lower() == "ScopeSortOrder".lower():
            column_scope_sort_order = value
        elif key.lower() == "InlineWeights".lower():
            column_inline_weights = value
        elif key.lower() == "RaiseRanking".lower():
            column_raise_ranking = value
        elif key.lower() == "ScopeRaiseRanking".lower():
            column_scope_raise_ranking = value
        elif key.lower() == "JiraFieldMapping".lower():
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
            raw_data = loads(content)
        except JSONDecodeError as e:
            raise SyntaxError(
                f"The structure of excel definition file is wrong. Hint: {e.msg} in line {e.lineno}:{e.colno}."
            ) from e

        parse_errors = []

        if len(raw_data) > 0:
            if raw_data[0].get("PreProcessSteps", None) is not None:
                for item in raw_data[0]["PreProcessSteps"]:
                    try:
                        self.pre_process_steps.append(
                            parse_json_item_to_pre_process_step(item)
                        )
                    except (TypeError, ValueError) as e:
                        parse_errors.append(e.args[0])

            if raw_data[0].get("SortStrategies", None) is not None:
                for item in raw_data[0]["SortStrategies"]:
                    try:
                        self.sort_strategies.append(
                            parse_json_item_to_sort_strategy(item)
                        )
                    except (TypeError, ValueError) as e:
                        parse_errors.append(e.args[0])

        if len(raw_data) >= 1:
            for item in raw_data[1]["Columns"]:
                try:
                    self.columns.append(
                        parse_json_item_to_excel_definition_column(item)
                    )
                except (TypeError, ValueError) as e:
                    parse_errors.append(e.args[0])

        if parse_errors:
            # Avoid duplicate error messages.
            parse_error_message = "\n".join(
                [f"{index + 1}. {err}" for index, err in enumerate(set(parse_errors))]
            )
            raise SyntaxError(
                f"The excel definition file has below issues need to be fixed:\n{parse_error_message}"
            )

        return self

    @staticmethod
    def parse_raise_ranking_level_scope_index_expression(
        expression: Union[Any, None],
    ) -> Optional[Set[int]]:
        if expression is None or not isinstance(expression, str):
            return None
        if len(expression) == 0 or expression.isspace():
            return set()
        if (
            RaiseRankingLevelScopeIndexValidationRule.fullmatch(
                "".join(expression.split(" "))
            )
            is None
        ):
            return None  # None means invalid, since we don't have the parse procedure.
        if "-" in expression:
            begin = int(expression.split("-")[0])
            end = int(expression.split("-")[1])
            if begin < end:
                return set(i for i in range(begin, end + 1))
            return set(i for i in range(end, begin + 1))
        return set(int(i) for i in expression.split(","))

    def load_file(self, file: Union[str, Path]) -> "ExcelDefinition":
        """
        Load json file to generate the excel definition

        :param file:
            JSON file location
        """

        if file is None or not pathlib.Path(file).is_absolute():
            raise ValueError("The file is invalid.")

        if not pathlib.Path(file).exists():
            raise ValueError(f"The file is not exist. File: {file}")

        with open(file=file, mode="r", encoding="utf-8") as table_definition_file:
            try:
                self.load(table_definition_file.read())
            finally:
                table_definition_file.close()

        return self

    def validate(self) -> "List":
        return (
            self._validate_pre_process_steps()
            + self._validate_sort_strategies()
            + self._validate_column_definitions()
        )

    def _validate_pre_process_steps(self) -> "List[str]":
        invalid_definitions = []

        # Validate PreProcessSteps
        for pre_process_step in self.pre_process_steps:
            if pre_process_step["name"].isspace() or len(pre_process_step["name"]) == 0:
                invalid_definitions.append("The PreProcessStep name is invalid.")
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

            if "JiraStatuses".lower() in [
                config_name.lower() for config_name in pre_process_step["config"].keys()
            ] and not isinstance(pre_process_step["config"]["JiraStatuses"], list):
                invalid_definitions.append(
                    f"The format of the Jira Statuses is invalid. PreProcessStep: {pre_process_step['name']}. Supported format like: ['CLOSED', 'PENDING RELEASE']."
                )

        return invalid_definitions

    def _validate_sort_strategies(self) -> "List[str]":
        invalid_definitions = []

        # Validate Strategies
        strategy_priorities: list[int] = []
        for strategy in self.sort_strategies:
            if strategy["name"].isspace() or len(strategy["name"]) == 0:
                invalid_definitions.append("The strategy name is invalid.")
                # If strategy name is invalid, no need to check more.
                continue

            if (
                strategy["priority"] is None
                or not isinstance(strategy["priority"], int)
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

            if "ParentScopeIndexRange".lower() in [
                config_name.lower() for config_name in strategy["config"].keys()
            ] and not isinstance(strategy["config"]["ParentScopeIndexRange"], set):
                invalid_definitions.append(
                    f"The format of the Parent Level Index Range is invalid. Strategy: {strategy['name']}. Supported format strings like: 1-20 or 20,30 or empty string."
                )

        if len(strategy_priorities) != len(set(strategy_priorities)):
            invalid_definitions.append(
                "The priority of strategies cannot be duplicate."
            )

        return invalid_definitions

    def _validate_column_definitions(self) -> "List[str]":
        invalid_definitions = []

        # Validate the Columns
        exist_story_id = False
        exist_indexes = []
        exist_inline_weights = []
        for column in self.get_columns():
            column_index: int = column["index"]
            column_name: str = column["name"]
            column_type: Optional[type] = column["type"]
            column_require_sort: bool = column["require_sort"]
            column_sort_order: bool = column["sort_order"]
            column_scope_require_sort: bool = column["scope_require_sort"]
            column_scope_sort_order: bool = column["scope_sort_order"]
            column_inline_weights: int = column["inline_weights"]
            column_raise_ranking: int = column["raise_ranking"]
            column_scope_raise_ranking: int = column["scope_raise_ranking"]
            column_jira_field_mapping: Optional[dict] = column["jira_field_mapping"]

            # Check Name cannot be empty
            if len(column_name) == 0:
                invalid_definitions.append(
                    f"Column name cannot be empty. Index: {column_index}"
                )
                continue

            if column_name.lower() == "StoryId".lower():
                exist_story_id = True

            # Check Missing/Duplicate Index
            if not isinstance(column_index, int):
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
            if not isinstance(column_require_sort, bool):
                invalid_definitions.append(
                    f"Require Sort can only be True/False. Column: {column_name}"
                )

            if not isinstance(column_sort_order, bool):
                invalid_definitions.append(
                    f"Sort Order can only be True(Descending)/False(Ascending). Column: {column_name}"
                )

            # Check Sort
            if not isinstance(column_scope_require_sort, bool):
                invalid_definitions.append(
                    f"Scope Require Sort can only be True/False. Column: {column_name}"
                )

            if not isinstance(column_scope_sort_order, bool):
                invalid_definitions.append(
                    f"Scope Sort Order can only be True(Descending)/False(Ascending). Column: {column_name}"
                )

            # Check InlineWeights
            if not isinstance(column_inline_weights, int):
                invalid_definitions.append(
                    f"Inline Weights can only be number. Column: {column_name}"
                )
            else:
                if (
                    column_inline_weights > 0
                    and column_inline_weights in exist_inline_weights
                ):
                    invalid_definitions.append(
                        f"Duplicate Inline Weights. Currently only support different line weights. Column: {column_name}"
                    )
                exist_inline_weights.append(column_inline_weights)

            # Check RaiseRanking
            if not isinstance(column_raise_ranking, int):
                invalid_definitions.append(
                    f"Raise Ranking can only be number. Column: {column_name}"
                )
            else:
                # Check Support RaiseRanking or not
                if column_type not in (bool,) and column_raise_ranking > 0:
                    invalid_definitions.append(
                        f"Column do not support Raise Ranking feature. Column: {column_name}"
                    )

            if not isinstance(column_scope_raise_ranking, int):
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
            if column_jira_field_mapping is not None and not isinstance(
                column_jira_field_mapping, dict
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
                    "Column Index must be in continuation and starts from 1."
                )

        return invalid_definitions

    @staticmethod
    def convert_str_to_type(type_str: str) -> Optional[type]:
        if type_str is None or not isinstance(type_str, str):
            return None
        type_str = str(type_str).strip().lower()
        if type_str.lower() == "str":
            return str
        if type_str.lower() == "bool":
            return bool
        if type_str.lower() == "datetime":
            return datetime
        if type_str.lower() == "priority":
            return Priority
        if type_str.lower() == "milestone":
            return Milestone
        # Currently, only support float/double
        if type_str.lower() == "number":
            return float
        return None

    def __iter__(self):
        for item in self.columns:
            yield item

    def get_columns(self) -> "List[ExcelDefinitionColumn]":
        return deepcopy(self.columns)

    def get_columns_name(self) -> "List[Optional[str]]":
        return [item["name"] for item in self.columns]

    @property
    def max_column_index(self) -> int:
        return self.columns[len(self.columns) - 1]["index"]

    def get_sort_strategies(self, enabled: bool = True) -> "List[SortStrategy]":
        result: list[SortStrategy] = []
        for sort_strategy in self.sort_strategies:
            if sort_strategy["enabled"] == enabled:
                result.append(deepcopy(sort_strategy))
        result.sort(key=_sort_priority_map, reverse=False)
        return result

    def get_pre_process_steps(self, enabled: bool = True) -> "List[PreProcessStep]":
        result: list[PreProcessStep] = []
        for pre_process_step in self.pre_process_steps:
            if pre_process_step["enabled"] == enabled:
                result.append(deepcopy(pre_process_step))
        return result

    def total_count(self):
        return len(self.columns)


def _sort_priority_map(strategy: SortStrategy) -> int:
    if strategy["priority"] is None or not isinstance(strategy["priority"], int):
        return 0
    return strategy["priority"]
