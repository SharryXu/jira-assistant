import pathlib
import warnings

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from json import dump
from os import environ, remove
from pathlib import Path
from typing import List, Optional, Union

from dotenv import load_dotenv
from urllib3 import disable_warnings

from .excel_definition import ExcelDefinition
from .excel_operation import output_to_excel_file, read_excel_file
from .jira_client import JiraClient
from .sprint_schedule import SprintScheduleStore
from .story import (
    Story,
    sort_stories_by_inline_weights,
    sort_stories_by_property_and_order,
    sort_stories_by_raise_ranking,
)

__all__ = ["run_steps_and_sort_excel_file", "generate_jira_field_mapping_file"]

# Currently, the openpyxl package will report an obsolete warning.
warnings.simplefilter(action="ignore", category=UserWarning)
# Disable the HTTPS certificate verification warning.
disable_warnings()

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE / "assets"


def _get_jira_client() -> Optional[JiraClient]:
    load_dotenv(ASSETS / ".env")

    jira_url: Optional[str] = environ.get("JIRA_URL", default=None)
    if jira_url is None or jira_url.isspace() or len(jira_url) == 0:
        print(
            "The jira url is invalid. Please use the update-jira-info command to add/update url."
        )
        return None

    jira_acccess_token: Optional[str] = environ.get("JIRA_ACCESS_TOKEN", default=None)
    if (
        jira_acccess_token is None
        or jira_acccess_token.isspace()
        or len(jira_acccess_token) == 0
    ):
        print(
            "The jira access token is invalid. Please use the update-jira-info command to add/update token."
        )
        return None

    jira_client = JiraClient(jira_url, jira_acccess_token)

    if not jira_client.health_check():
        print(
            "The jira access token is revoked. Please use the update-jira-info command to add/update token."
        )
        return None

    print(f"Jira info: {jira_url}")

    return jira_client


def _query_jira_information(
    stories: List[Story], excel_definition: ExcelDefinition
) -> bool:
    jira_client = _get_jira_client()

    if jira_client is None:
        return False

    jira_fields = []

    for definition_column in excel_definition.get_columns():
        if (
            definition_column["name"] is None
            or definition_column["jira_field_mapping"] is None
        ):
            continue
        jira_fields.append(
            {
                "name": definition_column["name"],
                "jira_name": definition_column["jira_field_mapping"]["name"],
                "jira_path": definition_column["jira_field_mapping"]["path"],
            }
        )

    jira_query_result = jira_client.get_stories_detail(
        [story["storyId"].strip() for story in stories], jira_fields
    )

    for story in stories:
        story_id: str = story["storyId"].lower().strip()
        if story_id in jira_query_result:
            for jira_field in jira_fields:
                story[jira_field["name"]] = jira_query_result[story_id][
                    jira_field["jira_name"]
                ]
        else:
            # Story ID has been changed because of convertion.
            temp_result = jira_client.get_stories_detail([story_id], jira_fields)
            if len(temp_result) > 0:
                story["storyId"] = list(temp_result.keys())[0].upper()
                for jira_field in jira_fields:
                    story[jira_field["name"]] = list(temp_result.values())[0][
                        jira_field["jira_name"]
                    ].upper()
                print(
                    f"Story id has been changed. Previous: {story_id.upper()}, Current: {story['storyId'].upper()}"
                )
            else:
                print(f"Cannot find related information for story: {story_id}")
                story.need_sort = False
                continue

    return True


def run_steps_and_sort_excel_file(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    excel_definition_file: Optional[Union[str, Path]] = None,
    sprint_schedule_file: Optional[Union[str, Path]] = None,
    over_write: bool = True,
):
    """
    Sort the excel file and output the result

    :parm input_file:
        The excel file need to be sorted. (Absolute path only)

    :parm output_file:
        The sorted excel file location. (Absolute path only)

    :parm sprint_schedule_file:
        The JSON file which contains the priority list to calculate the :py:class:`Milestone`

    :parm excel_definition_file:
        The JSON file which contains the input excel file's structure.

    :parm over_write:
        Whether or not the exist output file will be over-write.
    """
    sprint_schedule = SprintScheduleStore()
    if sprint_schedule_file is None:
        print("Using default sprint schedule...")
        sprint_schedule.load(
            files("jira_assistant.assets")
            .joinpath("sprint_schedule.json")
            .read_text(encoding="utf-8")
        )
    else:
        print("Using custom sprint schedule...")
        sprint_schedule.load_file(sprint_schedule_file)

    excel_definition = ExcelDefinition()
    if excel_definition_file is None:
        print("Using default excel definition...")
        excel_definition.load(
            files("jira_assistant.assets")
            .joinpath("excel_definition.json")
            .read_text(encoding="utf-8")
        )
    else:
        print("Using custom excel definition...")
        excel_definition.load_file(excel_definition_file)

    validation_result = excel_definition.validate()
    if len(validation_result) != 0:
        print(
            "Validating excel definition failed. Please check below information to fix first."
        )
        for item in validation_result:
            print(item)
        return
    print("Validating excel definition success.")

    excel_columns, stories = read_excel_file(
        input_file, excel_definition, sprint_schedule
    )

    if stories is None or len(stories) == 0:
        print("There are no stories inside the excel file.")
        return

    # Execute pre-process steps
    pre_process_steps = excel_definition.get_pre_process_steps()

    for pre_process_step in pre_process_steps:
        print(f"Executing step: {pre_process_step['name']}...")
        if pre_process_step["name"].lower() in "RetrieveJiraInformation".lower():
            need_call_jira_api: bool = False
            for excel_definition_column in excel_definition.get_columns():
                if excel_definition_column["jira_field_mapping"] is not None:
                    need_call_jira_api = True
                    break

            if need_call_jira_api:
                stories_need_call_jira: List[Story] = []
                for story in stories:
                    if story.need_sort:
                        stories_need_call_jira.append(story)
                if not _query_jira_information(
                    stories_need_call_jira, excel_definition
                ):
                    print("Retrieve jira information failed.")
                    return
        elif pre_process_step["name"].lower() in "FilterOutStoryWithoutId".lower():
            for story in stories:
                if story["storyId"] is None:
                    story.need_sort = False
        elif (
            pre_process_step["name"].lower()
            in "FilterOutStoryBasedOnJiraStatus".lower()
        ):
            for story in stories:
                if story["status"] is not None and story[
                    "status"
                ].upper() in pre_process_step["config"].get("JiraStatuses", []):
                    story.need_sort = False
        print("Executing finish.")

    stories_no_need_sort = []
    stories_need_sort = []

    for story in stories:
        if story.need_sort:
            stories_need_sort.append(story)
        else:
            stories_no_need_sort.append(story)

    # Execute sorting logic.
    sort_strategies = excel_definition.get_sort_strategies()

    for sort_strategy in sort_strategies:
        print(f"Executing {sort_strategy['name']} sorting...")
        if sort_strategy["name"] is None:
            continue
        if sort_strategy["name"].lower() in "InlineWeights".lower():
            stories_need_sort = sort_stories_by_inline_weights(stories_need_sort)
        elif sort_strategy["name"].lower() in "SortOrder".lower():
            sort_stories_by_property_and_order(
                stories_need_sort, excel_definition, sort_strategy["config"]
            )
        elif sort_strategy["name"].lower() in "RaiseRanking".lower():
            stories_need_sort = sort_stories_by_raise_ranking(
                stories_need_sort, excel_definition, sort_strategy["config"]
            )
        print("Executing finish.")

    output_to_excel_file(
        output_file,
        stories_need_sort + stories_no_need_sort,  # First output the sorted stories.
        excel_definition,
        excel_columns,
        over_write,
    )

    print(f"{output_file} has been saved.")


def generate_jira_field_mapping_file(
    file: Union[str, Path], over_write: bool = True
) -> bool:
    jira_client = _get_jira_client()

    if jira_client is None:
        return False

    output_file_path: Path = Path(file).absolute()

    if output_file_path.exists():
        if over_write:
            try:
                remove(file)
            except PermissionError as e:
                raise FileExistsError(
                    f"The exist jira field mapping file: {file} cannot be removed. {e.args[0]}"
                ) from e
        else:
            raise FileExistsError(
                f"The jira field mapping file: {file} is already exist."
            )

    with open(output_file_path, mode="x", encoding="utf-8") as output_file:
        dump(jira_client.get_all_fields(), output_file)
        output_file.flush()
        output_file.close()

    return True
