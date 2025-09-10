from codemie_test_harness.tests.enums.tools import Toolkit, ReportPortalTool

rp_test_data = [
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_EXTENDED_LAUNCH_DATA_AS_RAW,
        "Get details for the launch with ID 23 in a raw HTML format",
        """
        The launch with ID 23 has been successfully retrieved in HTML format. Here is the raw HTML content for your reference:
       
       ```html
       <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
       <html>
       <head>
         <title></title>
         <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
         <style type="text/css">
           a {text-decoration: none}
         </style>
       </head>
       <body text="#000000" link="#000000" alink="#000000" vlink="#000000">
       <table role="none" width="100%" cellpadding="0" cellspacing="0" border="0">
       <tr>
           <td width="50%">&nbsp;</td><td align="center">
           <table id="JR_PAGE_ANCHOR_0_1" role="none" class="jrPage" data-jr-height="57605" cellpadding="0" cellspacing="0" border="0" style="empty-cells: show; width: 842px; border-collapse: collapse;">
             <style type="text/css">
             #JR_PAGE_ANCHOR_0_1 th {font-weight: normal;}
             #JR_PAGE_ANCHOR_0_1 ul {list-style-type: disc; padding-inline-start: 40px; margin: 0px;}
             #JR_PAGE_ANCHOR_0_1 ol {list-style-type: decimal; padding-inline-start: 40px; margin: 0px;}
           </style>
           <tr role="none" valign="top" style="height:0">
           <td style="width:20px"></td>
           <!-- Additional table cells with widths defined -->
           </tr>
           <tr valign="top" style="height:20px">
           <td colspan="26">
           <!-- Detailed information about the launch -->
           </td>
           </tr>
           <!-- Additional rows containing more detailed information about steps, types, and statistics -->
           </table>
       </td>
       </tr>
       <tr>
           <td width="50%">&nbsp;</td>
       </tr>
       </table>
       </body>
       </html>
       ```
       This HTML document contains structured details about the launch, including metadata, statistics, and step-by-step information.
        If you need to reformat the data or extract specific information, please let me know how I can assist further!, 
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_LAUNCH_DETAILS,
        "Get details about launch with ID 23",
        """
        Launch Details: Pytest Regression (Launch 2)
        Overview
        ID: 23
        Name: Pytest Regression
        Number: 2
        Status: STOPPED
        Owner: anton_yeromin
        Environment: azure
        Timing Information
        Start Time: September 8, 2025, 08:46:01
        End Time: September 8, 2025, 09:11:14
        Duration: ~25 minutes
        Test Execution Statistics
        Total Tests: 888
        Passed: 743 (83.7%)
        Failed: 4 (0.5%)
        Skipped: 141 (15.9%)
        Defect Information
        To Investigate: 145 issues
        This launch appears to have been manually stopped, as indicated by its status and description.
        Despite being stopped, it shows a good pass rate of 83.7%, with only 4 failed tests.
        However, there are 145 items marked as "to investigate" which might require attention.
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_ALL_LAUNCHES,
        "Get all Report Portal launches",
        """
        ReportPortal Launches Summary
        Here are all the recent launches in ReportPortal:
        1. Pytest Regression - Launch 1
        Status: STOPPED
        Owner: anton_yeromin
        Environment: azure
        Duration: September 8, 2025, 08:17 - 08:46 (29 minutes)
        Test Results: 888 total tests (728 passed, 19 failed, 141 skipped)
        Issues: 160 marked "to investigate"
        2. Pytest Regression - Launch 2
        Status: STOPPED
        Owner: anton_yeromin
        Environment: azure
        Duration: September 8, 2025, 08:46 - 09:11 (25 minutes)
        Test Results: 888 total tests (743 passed, 4 failed, 141 skipped)
        Issues: 145 marked "to investigate"
        3. Pytest Regression - Launch 4
        Status: FAILED
        Owner: anton_yeromin
        Environment: preview
        Duration: September 8, 2025, 11:49 - 12:06 (17 minutes)
        Test Results: 888 total tests (846 passed, 0 failed, 42 skipped)
        Issues: 42 marked "to investigate"
        4. Pytest Regression - Launch 5
        Status: STOPPED
        Owner: anton_yeromin
        Environment: azure
        Duration: September 8, 2025, 12:43 - 13:16 (33 minutes)
        Test Results: 888 total tests (744 passed, 3 failed, 141 skipped)
        Issues: 144 marked "to investigate"
        5. Pytest Regression - Launch 6
        Status: STOPPED
        Owner: anton_yeromin
        Environment: preview
        Duration: September 8, 2025, 13:50 - 13:52 (2 minutes)
        Test Results: 15 total tests (1 passed, 14 failed, 0 skipped)
        Issues: None reported
        6. Pytest Regression - Launch 7
        Status: FAILED
        Owner: anton_yeromin
        Environment: preview
        Duration: September 8, 2025, 13:58 - 14:16 (18 minutes)
        Test Results: 888 total tests (843 passed, 3 failed, 42 skipped)
        Issues: 45 marked "to investigate"
        7. Pytest Regression - Launch 8
        Status: FAILED
        Owner: anton_yeromin
        Environment: preview
        Duration: September 8, 2025, 15:00 - 15:17 (17 minutes)
        Test Results: 888 total tests (845 passed, 1 failed, 42 skipped)
        Issues: 43 marked "to investigate"
        8. Pytest Regression - Launch 9
        Status: INTERRUPTED
        Owner: anton_yeromin
        Environment: aws
        Duration: September 9, 2025, 06:36 - 09:55 (3 hours, 19 minutes)
        Test Results: 888 total tests (770 passed, 8 failed, 110 skipped)
        Issues: 118 marked "to investigate"
        9. Pytest Regression - Launch 10
        Status: INTERRUPTED
        Owner: anton_yeromin
        Environment: azure
        Duration: September 9, 2025, 06:38 - 09:55 (3 hours, 17 minutes)
        Test Results: 888 tReportPortal Launches Summary
        Here are all the recent launches in ReportPortal:
        1. Pytest Regression - Launch 1
        Status: STOPPED
        Owner: anton_yeromin
        Environment: azure
        Duration: September 8, 2025, 08:17 - 08:46 (29 minutes)
        Test Results: 888 total tests (728 passed, 19 failed, 141 skipped)
        Issues: 160 marked "to investigate"
        2. Pytest Regression - Launch 2
        Status: STOPPED
        Owner: anton_yeromin
        Environment: azure
        Duration: September 8, 2025, 08:46 - 09:11 (25 minutes)
        Test Results: 888 total tests (743 passed, 4 failed, 141 skipped)
        Issues: 145 marked "to investigate"
        3. Pytest Regression - Launch 4
        Status: FAILED
        Owner: anton_yeromin
        Environment: preview
        Duration: September 8, 2025, 11:49 - 12:06 (17 minutes)
        Test Results: 888 total tests (846 passed, 0 failed, 42 skipped)
        Issues: 42 marked "to investigate"
        4. Pytest Regression - Launch 5
        Status: STOPPED
        
        Owner: anton_yeromin
        
        Environment: azure
        
        Duration: September 8, 2025, 12:43 - 13:16 (33 minutes)
        
        Test Results: 888 total tests (744 passed, 3 failed, 141 skipped)
        
        Issues: 144 marked "to investigate"
        
        5. Pytest Regression - Launch 6
        Status: STOPPED
        
        Owner: anton_yeromin
        
        Environment: preview
        
        Duration: September 8, 2025, 13:50 - 13:52 (2 minutes)
        
        Test Results: 15 total tests (1 passed, 14 failed, 0 skipped)
        
        Issues: None reported
        
        6. Pytest Regression - Launch 7
        Status: FAILED
        
        Owner: anton_yeromin
        
        Environment: preview
        
        Duration: September 8, 2025, 13:58 - 14:16 (18 minutes)
        
        Test Results: 888 total tests (843 passed, 3 failed, 42 skipped)
        
        Issues: 45 marked "to investigate"
        
        7. Pytest Regression - Launch 8
        Status: FAILED
        
        Owner: anton_yeromin
        
        Environment: preview
        
        Duration: September 8, 2025, 15:00 - 15:17 (17 minutes)
        
        Test Results: 888 total tests (845 passed, 1 failed, 42 skipped)
        
        Issues: 43 marked "to investigate"
        
        8. Pytest Regression - Launch 9
        Status: INTERRUPTED
        
        Owner: anton_yeromin
        
        Environment: aws
        
        Duration: September 9, 2025, 06:36 - 09:55 (3 hours, 19 minutes)
        
        Test Results: 888 total tests (770 passed, 8 failed, 110 skipped)
        
        Issues: 118 marked "to investigate"
        
        9. Pytest Regression - Launch 10
        Status: INTERRUPTED
        
        Owner: anton_yeromin
        
        Environment: azure
        
        Duration: September 9, 2025, 06:38 - 09:55 (3 hours, 17 minutes)
        
        Test Results: 888 total tests (300 passed, 447 failed, 141 skipped)
        
        Issues: 588 marked "to investigate"
        
        10. Pytest Regression - Launch 11
        Status: INTERRUPTED
        
        Owner: anton_yeromin
        
        Environment: azure
        
        Duration: September 9, 2025, 07:00 - 10:55 (3 hours, 55 minutes)
        
        Test Results: 79 total tests (5 passed, 55 failed, 19 skipped)
        
        Issues: 66 marked "to investigate"
        
        11. Pytest Regression - Launch 12
        Status: INTERRUPTED
        
        Owner: anton_yeromin
        
        Environment: gcp
        
        Duration: September 9, 2025, 07:21 - 10:55 (3 hours, 34 minutes)
        
        Test Results: 888 total tests (732 passed, 9 failed, 147 skipped)
        
        Issues: 156 marked "to investigate"
        
        12. Pytest Regression - Launch 13
        Status: IN_PROGRESS
        
        Owner: anton_yeromin
        
        Environment: azure
        
        Start Time: September 9, 2025, 10:00
        
        Test Results (so far): 888 total tests (309 passed, 438 failed, 141 skipped)
        
        Issues: 579 marked "to investigate"
        
        13. Pytest Regression - Launch 14
        Status: FAILED
        
        Owner: anton_yeromin
        
        Environment: preview
        
        Duration: September 9, 2025, 10:01 - 10:40 (39 minutes)
        
        Test Results: 888 total tests (811 passed, 35 failed, 42 skipped)
        
        Issues: 77 marked "to investigate"
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.FIND_TEST_ITEM_BY_ID,
        "Get test item by ID 2884",
        """
        Test Item Details: ID 2884
        Test Information
        Name: test_workflow_with_assistant_with_ado_test_plan_tools
        Status: FAILED
        Type: STEP
        Path: workflow/assistant_tools/ado
        Launch ID: 23
        Launch Number: 2
        Location
        File: codemie_test_harness/tests/workflow/assistant_tools/ado/test_workflow_with_assistant_with_ado_test_plan_tools.py
        Timing
        Start Time: September 8, 2025, 08:51:45
        End Time: September 8, 2025, 08:52:54
        Duration: 1 minute, 9 seconds
        Test Statistics
        Executions: Failed: 1
        Defects: To Investigate: 1 (ti001)
        Attributes
        Type: Regression
        Issue Analysis
        This test attempts to create an assistant with Azure DevOps Test Plan tools and create a test plan in the "CodemieAnton" project.
        The test appears to have failed, though the logs show that the assistant was created successfully and the test plan was created with ID 3.
        Without seeing explicit error messages in the logs, the failure might be related to:
        Assertion failures that weren't logged
        Issues during test teardown
        Expected vs. actual state differences
        Timeout issues
        Would you like me to retrieve the logs for this test item to investigate the failure further?
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_TEST_ITEMS_FOR_LAUNCH,
        "Get test items for launch ID 23",
        """
        Here are some test items for launch ID 23:
       
       1. **Test Item:** `test_cli_mcp_server[cat file.txt]`
          - **File:** `codemie_test_harness/tests/assistant/tools/mcp/test_cli_mcp_server.py`
         - **Status:** PASSED
          - **Attributes:** Regression, MCP
          - **Start Time:** 2025-09-08T08:46:34.564Z
          - **End Time:** 2025-09-08T08:46:41.799Z
       
       2. **Test Item:** `test_create_assistant_and_prompt_with_file[test.csv]`
          - **File:** `codemie_test_harness/tests/assistant/test_assistants.py`
          - **Status:** PASSED
          - **Attributes:** Regression, Smoke, Testcase EPMCDME-4001, EPMCDME-4002, EPMCDME-2527
          - **Start Time:** 2025-09-08T08:46:34.565Z
         - **End Time:** 2025-09-08T08:46:50.522Z
       
       3. **Test Item:** `test_assistant_with_codebase_tools[Toolkit.CODEBASE_TOOLS_CodeBaseTool.SEARCH_CODE_REPO_V2]`
          - **File:** `codemie_test_harness/tests/assistant/tools/codebase/test_codebase_tools.py`
          - **Status:** PASSED
          - **Attributes:** Regression
          - **Start Time:** 2025-09-08T08:46:34.566Z
          - **End Time:** 2025-09-08T08:47:21.503Z
       
       4. **Test Item:** `test_edit_description_for_file_datasource`
          - **File:** `codemie_test_harness/tests/assistant/datasource/test_file_indexing.py`
          - **Status:** PASSED
          - **Attributes:** Regression, Smoke
          - **Start Time:** 2025-09-08T08:46:34.606Z
          - **End Time:** 2025-09-08T08:46:41.655Z
       
       5. **Test Item:** `test_create_assistant_with_file_datasource[gecko-test.ini]`
          - **File:** `codemie_test_harness/tests/assistant/datasource/test_file_indexing.py`
          - **Status:** SKIPPED
          - **Attributes:** Regression, Smoke
          - **Start Time:** 2025-09-08T08:46:34.564Z
          - **End Time:** 2025-09-08T08:46:34.627Z
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_LOGS_FOR_TEST_ITEM,
        "Get logs for test item ID 2884",
        """
        Here are the logs for test item ID 2884:
       
       1. **Time:** 2025-09-08T08:51:45.164Z  
          **Level:** DEBUG  
          **Message:** Making /v1/assistants request to https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com/code-assistant-api<class 'dict'>
          
       2. **Time:** 2025-09-08T08:51:45.164Z  
          **Level:** DEBUG  
          **Message:** Request body: {'name': 'sdp_xjwyipzcypfocwq', 'description': 'Integration test assistant', 'system_prompt': 'You are a helpful integration test assistant', 'project': 'codemie', 'context': [], 'llm_model_type': 'gpt-4o-2024-08-06', 'toolkits': [{'toolkit': 'Azure DevOps Test Plan', 'tools': [{'name': 'create_test_plan', ...}]  
       
       3. **Time:** 2025-09-08T08:51:45.165Z  
          **Level:** DEBUG  
          **Message:** Starting new HTTPS connection (1): codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443
          
       4. **Time:** 2025-09-08T08:51:45.226Z  
          **Level:** DEBUG  
          **Message:** https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443 "POST /code-assistant-api/v1/assistants HTTP/1.1" 200 39
          
       5. **Time:** 2025-09-08T08:51:45.226Z  
          **Level:** DEBUG  
          **Message:** Received response with status 200
          
       6. **Time:** 2025-09-08T08:51:45.226Z  
          **Level:** DEBUG  
          **Message:** Response datasource_type: <class 'dict'>
          
       7. **Time:** 2025-09-08T08:51:45.228Z  
          **Level:** INFO  
          **Message:** Successfully processed /v1/assistants request to <class 'dict'>
          
       8. **Time:** 2025-09-08T08:51:45.228Z  
          **Level:** DEBUG  
          **Message:** Making /v1/assistants request to https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com/code-assistant-apityping.List[codemie_sdk.models.assistant.AssistantBase]
          
       9. **Time:** 2025-09-08T08:51:45.228Z  
          **Level:** DEBUG  
          **Message:** Request params: {'page': 0, 'per_page': 200, 'scope': 'visible_to_user', 'minimal_response': True}
          
       10. **Time:** 2025-09-08T08:51:45.229Z  
           **Level:** DEBUG  
           **Message:** Starting new HTTPS connection (1): codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443
          
       11. **Time:** 2025-09-08T08:51:45.299Z  
           **Level:** DEBUG  
           **Message:** https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443 "GET /code-assistant-api/v1/assistants?page=0&per_page=200&scope=visible_to_user&minimal_response=True HTTP/1.1" 200 69989
          
       12. **Time:** 2025-09-08T08:51:45.310Z  
           **Level:** DEBUG  
           **Message:** Received response with status 200
          
       13. **Time:** 2025-09-08T08:51:45.311Z  
           **Level:** DEBUG  
           **Message:** Response datasource_type: <class 'dict'>
          
       14. **Time:** 2025-09-08T08:51:45.312Z  
           **Level:** INFO  
           **Message:** Successfully processed /v1/assistants request to typing.List[codemie_sdk.models.assistant.AssistantBase]
          
       15. **Time:** 2025-09-08T08:51:45.314Z  
           **Level:** DEBUG  
           **Message:** Making /v1/workflows request to https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com/code-assistant-api<class 'dict'>
          
       16. **Time:** 2025-09-08T08:51:45.314Z  
           **Level:** DEBUG  
           **Message:** Request body: {'project': 'codemie', 'name': 'sdp_xpgivblpavtdeza', 'description': 'Test Workflow', 'yaml_config': 'enable_summarization_node: false\\ntools: []\\nassistants:\\n- id: sdp_xjwyipzcypfocwq\\n  model: gpt-4o-2024-08-06\\n  assistant_id: 6ef6a01d-70ef-4211-a385-8c99b87eee72\\nstates:\\n- id: ...
          
       17. **Time:** 2025-09-08T08:51:45.315Z  
           **Level:** DEBUG  
           **Message:** Starting new HTTPS connection (1): codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443
          
       18. **Time:** 2025-09-08T08:51:45.394Z  
           **Level:** DEBUG  
           **Message:** https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443 "POST /code-assistant-api/v1/workflows HTTP/1.1" 200 2119
          
       19. **Time:** 2025-09-08T08:51:45.394Z  
           **Level:** DEBUG  
           **Message:** Received response with status 200
          
       20. **Time:** 2025-09-08T08:51:45.394Z  
           **Level:** DEBUG  
           **Message:** Response datasource_type: <class 'dict'>
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_USER_INFORMATION,
        "Get user information from reportal with username anton_yeromin",
        """
        User Information: Anton Yeromin
        Personal Details
        Full Name: Anton Yeromin
        Email: anton_yeromin@epam.com
        Username: anton_yeromin
        User ID: 4
        Account Type: SAML
        Role: USER
        Status: Active
        Photo: Loaded
        Login Information
        Last Login: September 9, 2025
        Synchronization Date: September 8, 2025
        Project Assignments
        EPM-CDME Project
        Project ID: 4
        Role: PROJECT_MANAGER
        Entry Type: INTERNAL
        Personal Project
        Project ID: 6
        Name: anton_yeromin_personal
        Role: PROJECT_MANAGER
        Entry Type: PERSONAL
        This user has project management responsibilities in both an internal project (EPM-CDME) and their personal project space.
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_DASHBOARD_DATA,
        "Get dashboard data from report portal where ID = 2",
        """
        Dashboard Details: test-dashboard
        I was able to retrieve the dashboard data for ID 2:
        Dashboard Information
        ID: 2
        Name: test-dashboard
        Owner: dmytro_adamtsev
        Description: dashboard for testing purposes
        Dashboard Content
        This dashboard does not contain any widgets. 
        It appears to be an empty dashboard that was likely created for testing purposes, as suggested by its name and description.
        """,
    ),
]
