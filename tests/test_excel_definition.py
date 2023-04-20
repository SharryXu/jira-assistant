import pathlib

from pytest import raises

from jira_assistant.excel_definition import ExcelDefinition

HERE = pathlib.Path(__file__).resolve().parent
SRC_ASSETS = HERE.parent / "src/jira_assistant/assets"
TEST_ASSETS = HERE / "files"


class TestExcelDefinition:
    def test_load_happy_path(self):
        excel_definition_filename = SRC_ASSETS / "excel_definition.json"

        store = ExcelDefinition()
        with open(excel_definition_filename, encoding="utf-8") as file:
            store.load(file.read())
        assert store.total_count() > 0

    def test_load_using_none_input(self):
        store = ExcelDefinition()
        content: str = None  # type: ignore
        with raises(ValueError) as err:
            store.load(content)
        assert "There is no content in the excel definition file." in str(err.value)

    def test_load_file(self):
        excel_definition_filename = SRC_ASSETS / "excel_definition.json"
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)
        assert store.total_count() > 0

    def test_load_file_none(self):
        store = ExcelDefinition()
        file: str = None  # type: ignore
        with raises(ValueError) as err:
            store.load_file(file)
        assert "invalid" in str(err.value)

    def test_iter(self):
        excel_definition_filename = SRC_ASSETS / "excel_definition.json"
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)
        items = []
        for item in store:
            items.append(item)
        assert len(items) > 0

    def test_validate(self):
        excel_definition_filename = SRC_ASSETS / "excel_definition.json"
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 0

    def test_validate_missing_story_id(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_missing_story_id.json"
        )
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 1

    def test_validate_duplicate_index(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_duplicate_index.json"
        )
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 1

    def test_validate_duplicate_inline_weights(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_duplicate_inline_weights.json"
        )
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 1

    def test_validate_invalid_name(self):
        excel_definition_filename = TEST_ASSETS / "excel_definition_invalid_name.json"
        store = ExcelDefinition()
        with raises(SyntaxError) as err:
            store.load_file(excel_definition_filename)

        assert (
            "The excel definition file has below issues need to be fixed"
            in err.value.args[0]
        )
        assert (
            "The Name property type in the column definition should be string."
            in err.value.args[0]
        )

    def test_validate_invalid_raise_ranking(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_invalid_raise_ranking.json"
        )
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 1

    def test_validate_invalid_require_sort(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_invalid_require_sort.json"
        )
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 2

    def test_validate_invalid_type(self):
        excel_definition_filename = TEST_ASSETS / "excel_definition_invalid_type.json"
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 2

    def test_validate_invalid_index(self):
        excel_definition_filename = TEST_ASSETS / "excel_definition_invalid_index.json"
        store = ExcelDefinition()
        with raises(SyntaxError) as err:
            store.load_file(excel_definition_filename)

        assert (
            "The excel definition file has below issues need to be fixed"
            in err.value.args[0]
        )
        assert (
            "The Index property type in the column definition is not integer."
            in err.value.args[0]
        )

    def test_validate_index_not_continuation(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_index_not_continuation.json"
        )
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 1

    def test_validate_strategy_duplicate_priority(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_strategy_duplicate_priority.json"
        )
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 1

    def test_validate_strategy_invalid_name(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_strategy_invalid_name.json"
        )
        store = ExcelDefinition()
        store.load_file(excel_definition_filename)

        validation_result = store.validate()

        assert len(validation_result) == 1

    def test_validate_invalid_structure(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_invalid_structure.txt"
        )
        store = ExcelDefinition()

        with raises(Exception) as err:
            store.load_file(excel_definition_filename)

        assert (
            "The structure of excel definition file is wrong. Hint: Expecting ',' delimiter in line 49:1"
            in err.value.args[0]
        )

    def test_validate_invalid_pre_process_step_name(self):
        excel_definition_filename = (
            TEST_ASSETS / "excel_definition_invalid_pre_process_step_name.json"
        )
        store = ExcelDefinition()

        with raises(SyntaxError) as err:
            store.load_file(excel_definition_filename)

        assert (
            "The excel definition file has below issues need to be fixed"
            in err.value.args[0]
        )
        assert "The pre-process step must have a name." in err.value.args[0]
