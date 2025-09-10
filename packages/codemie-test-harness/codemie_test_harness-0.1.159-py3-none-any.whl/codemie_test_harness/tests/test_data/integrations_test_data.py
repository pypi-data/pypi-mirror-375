import os

import pytest

from codemie_sdk.models.integration import CredentialTypes
from codemie_test_harness.tests.enums.integrations import DataBaseDialect
from codemie_test_harness.tests.utils.aws_parameters_store import CredentialsUtil

valid_integrations = [
    pytest.param(
        CredentialTypes.AWS,
        CredentialsUtil.aws_credentials(),
        marks=[
            pytest.mark.aws,
            pytest.mark.cloud,
        ],
    ),
    pytest.param(
        CredentialTypes.AZURE,
        CredentialsUtil.azure_credentials(),
        marks=[
            pytest.mark.azure,
            pytest.mark.cloud,
        ],
    ),
    pytest.param(
        CredentialTypes.GCP,
        CredentialsUtil.gcp_credentials(),
        marks=[
            pytest.mark.gcp,
            pytest.mark.cloud,
            pytest.mark.skipif(
                os.getenv("ENV") == "azure",
                reason="Still have an issue with encoding long strings",
            ),
        ],
    ),
    pytest.param(
        CredentialTypes.SONAR,
        CredentialsUtil.sonar_credentials(),
        marks=pytest.mark.sonar,
    ),
    pytest.param(
        CredentialTypes.SONAR,
        CredentialsUtil.sonar_cloud_credentials(),
        marks=pytest.mark.sonar,
    ),
    pytest.param(
        CredentialTypes.GIT,
        CredentialsUtil.gitlab_credentials(),
        marks=pytest.mark.gitlab,
    ),
    pytest.param(
        CredentialTypes.GIT,
        CredentialsUtil.github_credentials(),
        marks=pytest.mark.github,
    ),
    pytest.param(
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.confluence_credentials(),
        marks=[
            pytest.mark.confluence,
            pytest.mark.project_management,
        ],
    ),
    pytest.param(
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.confluence_cloud_credentials(),
        marks=[
            pytest.mark.confluence,
            pytest.mark.confluence_cloud,
            pytest.mark.project_management,
        ],
    ),
    pytest.param(
        CredentialTypes.JIRA,
        CredentialsUtil.jira_credentials(),
        marks=[
            pytest.mark.jira,
            pytest.mark.project_management,
        ],
    ),
    pytest.param(
        CredentialTypes.JIRA,
        CredentialsUtil.jira_cloud_credentials(),
        marks=[
            pytest.mark.jira,
            pytest.mark.jira_cloud,
            pytest.mark.project_management,
        ],
    ),
    pytest.param(
        CredentialTypes.SQL,
        CredentialsUtil.sql_credentials(DataBaseDialect.POSTGRES),
        marks=pytest.mark.sql,
    ),
    pytest.param(
        CredentialTypes.SQL,
        CredentialsUtil.sql_credentials(DataBaseDialect.MY_SQL),
        marks=pytest.mark.sql,
    ),
    pytest.param(
        CredentialTypes.ELASTIC,
        CredentialsUtil.elastic_credentials(),
        marks=pytest.mark.elastic,
    ),
    pytest.param(
        CredentialTypes.MCP,
        CredentialsUtil.mcp_credentials(),
        marks=pytest.mark.mcp,
    ),
    pytest.param(
        CredentialTypes.AZURE_DEVOPS,
        CredentialsUtil.azure_devops_credentials(),
        marks=pytest.mark.azure,
    ),
    pytest.param(
        CredentialTypes.FILESYSTEM,
        CredentialsUtil.file_system_credentials(),
        marks=pytest.mark.file_system,
    ),
    pytest.param(
        CredentialTypes.EMAIL,
        CredentialsUtil.gmail_credentials(),
        marks=[
            pytest.mark.notification,
            pytest.mark.email,
        ],
    ),
    pytest.param(
        CredentialTypes.TELEGRAM,
        CredentialsUtil.telegram_credentials(),
        marks=[
            pytest.mark.notification,
            pytest.mark.telegram,
        ],
    ),
    pytest.param(
        CredentialTypes.SERVICE_NOW,
        CredentialsUtil.servicenow_credentials(),
        marks=pytest.mark.servicenow,
    ),
    pytest.param(
        CredentialTypes.KEYCLOAK,
        CredentialsUtil.keycloak_credentials(),
        marks=pytest.mark.keycloak,
    ),
    pytest.param(
        CredentialTypes.KUBERNETES,
        CredentialsUtil.kubernetes_credentials(),
        marks=[
            pytest.mark.kubernetes,
            pytest.mark.cloud,
            pytest.mark.skipif(
                os.getenv("ENV") == "azure",
                reason="Still have an issue with encoding long strings",
            ),
        ],
    ),
    pytest.param(
        CredentialTypes.REPORT_PORTAL,
        CredentialsUtil.report_portal_credentials(),
        marks=pytest.mark.report_portal,
    ),
]

testable_integrations = [
    pytest.param(
        CredentialTypes.AWS,
        CredentialsUtil.aws_credentials(),
        marks=[
            pytest.mark.aws,
            pytest.mark.cloud,
        ],
    ),
    pytest.param(
        CredentialTypes.AZURE,
        CredentialsUtil.azure_credentials(),
        marks=[
            pytest.mark.azure,
            pytest.mark.cloud,
        ],
    ),
    pytest.param(
        CredentialTypes.GCP,
        CredentialsUtil.gcp_credentials(),
        marks=[
            pytest.mark.gcp,
            pytest.mark.cloud,
            pytest.mark.skipif(
                os.getenv("ENV") == "azure",
                reason="Still have an issue with encoding long strings",
            ),
        ],
    ),
    pytest.param(
        CredentialTypes.SONAR,
        CredentialsUtil.sonar_credentials(),
        marks=pytest.mark.sonar,
    ),
    pytest.param(
        CredentialTypes.SONAR,
        CredentialsUtil.sonar_cloud_credentials(),
        marks=pytest.mark.sonar,
    ),
    pytest.param(
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.confluence_credentials(),
        marks=[
            pytest.mark.confluence,
            pytest.mark.project_management,
        ],
    ),
    pytest.param(
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.confluence_cloud_credentials(),
        marks=[
            pytest.mark.confluence,
            pytest.mark.confluence_cloud,
            pytest.mark.project_management,
        ],
    ),
    pytest.param(
        CredentialTypes.JIRA,
        CredentialsUtil.jira_credentials(),
        marks=[
            pytest.mark.jira,
            pytest.mark.project_management,
        ],
    ),
    pytest.param(
        CredentialTypes.JIRA,
        CredentialsUtil.jira_cloud_credentials(),
        marks=[
            pytest.mark.jira,
            pytest.mark.jira_cloud,
            pytest.mark.project_management,
        ],
    ),
    pytest.param(
        CredentialTypes.EMAIL,
        CredentialsUtil.gmail_credentials(),
        marks=[
            pytest.mark.email,
            pytest.mark.notification,
            pytest.mark.skipif(
                os.getenv("ENV") == "local",
                reason="Skipping this test on local environment",
            ),
        ],
    ),
    pytest.param(
        CredentialTypes.SERVICE_NOW,
        CredentialsUtil.servicenow_credentials(),
        marks=pytest.mark.servicenow,
    ),
    pytest.param(
        CredentialTypes.KUBERNETES,
        CredentialsUtil.kubernetes_credentials(),
        marks=[
            pytest.mark.kubernetes,
            pytest.mark.cloud,
            pytest.mark.skipif(
                os.getenv("ENV") == "azure",
                reason="Still have an issue with encoding long strings",
            ),
        ],
    ),
    pytest.param(
        CredentialTypes.REPORT_PORTAL,
        CredentialsUtil.report_portal_credentials(),
        marks=pytest.mark.report_portal,
    ),
]

invalid_integrations = [
    pytest.param(
        CredentialTypes.AWS,
        CredentialsUtil.invalid_aws_credentials(),
        "An error occurred (SignatureDoesNotMatch) when calling the GetUser operation: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details.",
        marks=[
            pytest.mark.aws,
            pytest.mark.cloud,
        ],
    ),
    pytest.param(
        CredentialTypes.AZURE,
        CredentialsUtil.invalid_azure_credentials(),
        "Invalid client secret provided. Ensure the secret being sent in the request is the client secret value, not the client secret ID, for a secret added to app",
        marks=[
            pytest.mark.azure,
            pytest.mark.cloud,
        ],
    ),
    pytest.param(
        CredentialTypes.GCP,
        CredentialsUtil.invalid_gcp_credentials(),
        "Error: ('Could not deserialize key data. The data may be in an incorrect format, "
        + "the provided password may be incorrect, it may be encrypted with an unsupported algorithm, "
        + "or it may be an unsupported key type",
        marks=[
            pytest.mark.gcp,
            pytest.mark.cloud,
            pytest.mark.skipif(
                os.getenv("ENV") == "azure",
                reason="Still have an issue with encoding long strings",
            ),
        ],
    ),
    pytest.param(
        CredentialTypes.SONAR,
        CredentialsUtil.invalid_sonar_credentials(),
        "Invalid token",
        marks=pytest.mark.sonar,
    ),
    pytest.param(
        CredentialTypes.SONAR,
        CredentialsUtil.invalid_sonar_cloud_credentials(),
        "Invalid token",
        marks=pytest.mark.sonar,
    ),
    pytest.param(
        CredentialTypes.EMAIL,
        CredentialsUtil.invalid_gmail_credentials(),
        "SMTP Code: 535. SMTP error",
        marks=[
            pytest.mark.email,
            pytest.mark.notification,
            pytest.mark.skipif(
                os.getenv("ENV") == "local",
                reason="Skipping this test on local environment",
            ),
        ],
    ),
    pytest.param(
        CredentialTypes.JIRA,
        CredentialsUtil.invalid_jira_credentials(),
        "Unauthorized (401)",
        marks=pytest.mark.jira,
    ),
    pytest.param(
        CredentialTypes.CONFLUENCE,
        CredentialsUtil.invalid_confluence_credentials(),
        "Access denied",
        marks=pytest.mark.confluence,
    ),
    pytest.param(
        CredentialTypes.SERVICE_NOW,
        CredentialsUtil.invalid_servicenow_credentials(),
        'ServiceNow tool exception. Status: 401. Response: {"error":{"message":"User Not Authenticated","detail":"Required to provide Auth information"}',
        marks=pytest.mark.servicenow,
    ),
    pytest.param(
        CredentialTypes.KUBERNETES,
        CredentialsUtil.invalid_kubernetes_credentials(),
        "Error: (401)\nReason: Unauthorized",
        marks=[
            pytest.mark.kubernetes,
            pytest.mark.cloud,
        ],
    ),
    pytest.param(
        CredentialTypes.REPORT_PORTAL,
        CredentialsUtil.invalid_report_portal_credentials(),
        "401 Client Error:  for url: https://report-portal.core.kuberocketci.io/api/v1/epm-cdme/launch?page.page=1",
        marks=pytest.mark.report_portal,
    ),
]
