import pytest

from codemie_test_harness.tests.enums.tools import ProjectManagementTool
from codemie_test_harness.tests.test_data.pm_tools_test_data import (
    JIRA_TOOL_PROMPT,
    RESPONSE_FOR_JIRA_TOOL,
    CONFLUENCE_TOOL_PROMPT,
    RESPONSE_FOR_CONFLUENCE_TOOL,
    JIRA_CLOUD_TOOL_PROMPT,
    RESPONSE_FOR_JIRA_CLOUD_TOOL,
    CONFLUENCE_CLOUD_TOOL_PROMPT,
    RESPONSE_FOR_CONFLUENCE_CLOUD_TOOL,
)
from codemie_test_harness.tests.utils.constants import ProjectManagementIntegrationType

pm_tools_test_data = [
    pytest.param(
        ProjectManagementTool.JIRA,
        ProjectManagementIntegrationType.JIRA,
        JIRA_TOOL_PROMPT,
        RESPONSE_FOR_JIRA_TOOL,
        marks=pytest.mark.jira,
    ),
    pytest.param(
        ProjectManagementTool.CONFLUENCE,
        ProjectManagementIntegrationType.CONFLUENCE,
        CONFLUENCE_TOOL_PROMPT,
        RESPONSE_FOR_CONFLUENCE_TOOL,
        marks=pytest.mark.confluence,
    ),
    pytest.param(
        ProjectManagementTool.JIRA,
        ProjectManagementIntegrationType.JIRA_CLOUD,
        JIRA_CLOUD_TOOL_PROMPT,
        RESPONSE_FOR_JIRA_CLOUD_TOOL,
        marks=[pytest.mark.jira, pytest.mark.jira_cloud],
    ),
    pytest.param(
        ProjectManagementTool.CONFLUENCE,
        ProjectManagementIntegrationType.CONFLUENCE_CLOUD,
        CONFLUENCE_CLOUD_TOOL_PROMPT,
        RESPONSE_FOR_CONFLUENCE_CLOUD_TOOL,
        marks=[pytest.mark.confluence, pytest.mark.confluence_cloud],
    ),
]
