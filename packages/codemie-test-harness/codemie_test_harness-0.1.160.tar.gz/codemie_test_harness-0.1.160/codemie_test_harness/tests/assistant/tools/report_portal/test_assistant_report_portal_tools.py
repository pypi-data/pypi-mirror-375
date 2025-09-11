import pytest

from codemie_test_harness.tests.test_data.report_portal_tools_test_data import (
    rp_test_data,
)


@pytest.mark.assistant
@pytest.mark.report_portal
@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    rp_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in rp_test_data],
)
def test_assistant_with_report_portal_tools(
    assistant,
    assistant_utils,
    report_portal_integration,
    similarity_check,
    toolkit,
    tool_name,
    prompt,
    expected_response,
):
    assistant = assistant(
        toolkit,
        tool_name,
        settings=report_portal_integration,
    )
    response = assistant_utils.ask_assistant(assistant, prompt)
    similarity_check.check_similarity(response, expected_response)
