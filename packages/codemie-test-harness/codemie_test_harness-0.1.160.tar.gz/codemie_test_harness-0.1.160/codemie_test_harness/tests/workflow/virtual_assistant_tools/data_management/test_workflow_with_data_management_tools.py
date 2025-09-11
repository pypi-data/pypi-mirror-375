import pytest
from codemie_sdk.models.integration import CredentialTypes

from codemie_test_harness.tests.enums.tools import DataManagementTool
from codemie_test_harness.tests.test_data.data_management_tools_test_data import (
    ELASTIC_TOOL_TASK,
    RESPONSE_FOR_ELASTIC,
    sql_tools_test_data,
    SQL_TOOL_CREATE_TABLE_TASK,
    SQL_TOOL_DELETE_TABLE_TASK,
    SQL_TOOL_INSERT_TABLE_TASK,
    SQL_TOOL_QUERY_TABLE_TASK,
    RESPONSE_FOR_SQL,
)
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil
from codemie_test_harness.tests.utils.env_resolver import EnvironmentResolver
from codemie_test_harness.tests.utils.base_utils import get_random_name

pytestmark = pytest.mark.skipif(
    EnvironmentResolver.is_localhost(),
    reason="Skipping this tests on local environment",
)


@pytest.mark.workflow
@pytest.mark.virtual_workflow
@pytest.mark.elastic
@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6431")
def test_workflow_with_elastic_tools(
    workflow_with_virtual_assistant,
    workflow_utils,
    integration_utils,
    similarity_check,
):
    """Test workflow execution with Elastic tools."""
    assistant_and_state_name = get_random_name()
    credential_values = CredentialsUtil.elastic_credentials()
    integration = integration_utils.create_integration(
        CredentialTypes.ELASTIC, credential_values
    )

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        DataManagementTool.ELASTIC,
        integration=integration,
        task=ELASTIC_TOOL_TASK,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )
    similarity_check.check_similarity(response, RESPONSE_FOR_ELASTIC)


@pytest.mark.workflow
@pytest.mark.virtual_workflow
@pytest.mark.sql
@pytest.mark.regression
@pytest.mark.testcase("EPMCDME-6431")
@pytest.mark.parametrize(
    "db_dialect",
    sql_tools_test_data,
)
def test_workflow_with_sql_tools(
    workflow_with_virtual_assistant,
    workflow_utils,
    integration_utils,
    similarity_check,
    db_dialect,
):
    """Test workflow execution with SQL data management tools (various dialects)."""
    assistant_and_state_name = get_random_name()
    credential_values = CredentialsUtil.sql_credentials(db_dialect)
    integration = integration_utils.create_integration(
        CredentialTypes.SQL, credential_values
    )

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        DataManagementTool.SQL,
        integration=integration,
        task=f"DB dialect is {db_dialect.value}. Run SQL tool and execute SQL queries to perform user requests.",
    )
    workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, SQL_TOOL_CREATE_TABLE_TASK
    )
    workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, SQL_TOOL_INSERT_TABLE_TASK
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, SQL_TOOL_QUERY_TABLE_TASK
    )
    workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name, SQL_TOOL_DELETE_TABLE_TASK
    )

    similarity_check.check_similarity(response, RESPONSE_FOR_SQL)
