import pytest

from codemie_test_harness.tests.test_data.report_portal_tools_test_data import (
    rp_test_data,
)


@pytest.mark.workflow
@pytest.mark.workflow_with_assistant
@pytest.mark.report_portal
@pytest.mark.regression
@pytest.mark.parametrize(
    "toolkit,tool_name,prompt,expected_response",
    rp_test_data,
    ids=[f"{row[0]}_{row[1]}" for row in rp_test_data],
)
def test_workflow_with_assistant_with_report_portal_tools(
    assistant,
    workflow_with_assistant,
    workflow_utils,
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

    workflow_with_assistant = workflow_with_assistant(assistant, prompt)
    response = workflow_utils.execute_workflow(
        workflow_with_assistant.id, assistant.name
    )
    similarity_check.check_similarity(response, expected_response)
