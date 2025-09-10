from codemie_test_harness.tests.enums.tools import Toolkit, ReportPortalTool

report_portal_tools_test_data = [
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_LAUNCH_DETAILS,
        {"launch_id": "23"},
        """
        {
            "owner": "anton_yeromin",
            "description": "stopped",
            "id": 23,
            "uuid": "05e770ed-4b9d-43c3-acf2-43a50e7875dc",
            "name": "Pytest Regression",
            "number": 2,
            "startTime": "2025-09-08T08:46:01.157Z",
            "endTime": "2025-09-08T09:11:14.987Z",
            "lastModified": "2025-09-08T09:11:15.196270Z",
            "status": "STOPPED",
            "statistics": {
                "executions": {
                    "total": 888,
                    "failed": 4,
                    "passed": 743,
                    "skipped": 141
                },
                "defects": {
                    "to_investigate": {
                        "total": 145,
                        "ti001": 145
                    }
                }
            },
            "attributes": [
                {
                    "key": "status",
                    "value": "stopped"
                },
                {
                    "key": "env",
                    "value": "azure"
                }
            ],
            "mode": "DEFAULT",
            "analysing": [],
            "approximateDuration": 0.0,
            "hasRetries": false,
            "rerun": false,
            "metadata": {
                "rp.cluster.lastRun": "1757322678794"
            },
            "retentionPolicy": "REGULAR"
        },
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_ALL_LAUNCHES,
        {"page_number": 1},
        """
        {
            "content": [
                {
                    "owner": "anton_yeromin",
                    "description": "stopped",
                    "id": 22,
                    "uuid": "038c493c-b9bf-405f-b1b1-7842ffe5de9a",
                    "name": "Pytest Regression",
                    "number": 1,
                    "startTime": "2025-09-08T08:17:26.906Z",
                    "endTime": "2025-09-08T08:46:23.541Z",
                    "lastModified": "2025-09-08T08:46:23.826436Z",
                    "status": "STOPPED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "failed": 19,
                            "passed": 728,
                            "skipped": 141
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 160,
                                "ti001": 160
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "status",
                            "value": "stopped"
                        },
                        {
                            "key": "env",
                            "value": "azure"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 0.0,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757321194743"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "description": "stopped",
                    "id": 23,
                    "uuid": "05e770ed-4b9d-43c3-acf2-43a50e7875dc",
                    "name": "Pytest Regression",
                    "number": 2,
                    "startTime": "2025-09-08T08:46:01.157Z",
                    "endTime": "2025-09-08T09:11:14.987Z",
                    "lastModified": "2025-09-08T09:11:15.196270Z",
                    "status": "STOPPED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "failed": 4,
                            "passed": 743,
                            "skipped": 141
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 145,
                                "ti001": 145
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "status",
                            "value": "stopped"
                        },
                        {
                            "key": "env",
                            "value": "azure"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 0.0,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757322678794"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 25,
                    "uuid": "b1580190-ddd7-4496-9904-61f140665a65",
                    "name": "Pytest Regression",
                    "number": 4,
                    "startTime": "2025-09-08T11:49:50.308Z",
                    "endTime": "2025-09-08T12:06:25.438Z",
                    "lastModified": "2025-09-08T12:06:25.540618Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "passed": 846,
                            "skipped": 42
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 42,
                                "ti001": 42
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "preview"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 3202.146,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757333186074"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "description": "stopped",
                    "id": 26,
                    "uuid": "4b9b9d74-dd07-4ddf-a6cb-f1450bfacd9e",
                    "name": "Pytest Regression",
                    "number": 5,
                    "startTime": "2025-09-08T12:43:08.988Z",
                    "endTime": "2025-09-08T13:16:11.869Z",
                    "lastModified": "2025-09-08T13:16:12.022623Z",
                    "status": "STOPPED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "failed": 3,
                            "passed": 744,
                            "skipped": 141
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 144,
                                "ti001": 144
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "status",
                            "value": "stopped"
                        },
                        {
                            "key": "env",
                            "value": "azure"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 995.13,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757337373405"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "description": "stopped",
                    "id": 27,
                    "uuid": "22d20d4a-004f-4286-a630-5baa59a4aeff",
                    "name": "Pytest Regression",
                    "number": 6,
                    "startTime": "2025-09-08T13:50:57.368Z",
                    "endTime": "2025-09-08T13:52:37.258Z",
                    "lastModified": "2025-09-08T13:52:39.860832Z",
                    "status": "STOPPED",
                    "statistics": {
                        "executions": {
                            "total": 15,
                            "passed": 1,
                            "failed": 14
                        },
                        "defects": {}
                    },
                    "attributes": [
                        {
                            "key": "status",
                            "value": "stopped"
                        },
                        {
                            "key": "env",
                            "value": "preview"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 995.13,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757339559884"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 28,
                    "uuid": "95ec670d-2252-42a3-8250-a028dcce8176",
                    "name": "Pytest Regression",
                    "number": 7,
                    "startTime": "2025-09-08T13:58:52.195Z",
                    "endTime": "2025-09-08T14:16:33.106Z",
                    "lastModified": "2025-09-08T14:16:33.172673Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "failed": 3,
                            "passed": 843,
                            "skipped": 42
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 45,
                                "ti001": 45
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "preview"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 995.13,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757340994692"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 30,
                    "uuid": "f8cc3f1a-7582-46c2-b12e-0c20a3dbb9c5",
                    "name": "Pytest Regression",
                    "number": 8,
                    "startTime": "2025-09-08T15:00:41.161Z",
                    "endTime": "2025-09-08T15:17:26.672Z",
                    "lastModified": "2025-09-08T15:17:26.725642Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "failed": 1,
                            "passed": 845,
                            "skipped": 42
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 43,
                                "ti001": 43
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "preview"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1028.0205,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757344647421"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 31,
                    "uuid": "e441203d-40a6-4718-b365-67fbd6bf8b7c",
                    "name": "Pytest Regression",
                    "number": 9,
                    "startTime": "2025-09-09T06:36:31.663Z",
                    "endTime": "2025-09-09T09:55:07.390391Z",
                    "lastModified": "2025-09-09T09:55:07.396057Z",
                    "status": "INTERRUPTED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "passed": 770,
                            "failed": 8,
                            "skipped": 110
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 118,
                                "ti001": 118
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "aws"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1020.517333,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757411732542"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 32,
                    "uuid": "dc344b53-b929-4b75-ab82-6cb61f04040d",
                    "name": "Pytest Regression",
                    "number": 10,
                    "startTime": "2025-09-09T06:38:19.683Z",
                    "endTime": "2025-09-09T09:55:07.395393Z",
                    "lastModified": "2025-09-09T09:55:07.396166Z",
                    "status": "INTERRUPTED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "passed": 300,
                            "failed": 447,
                            "skipped": 141
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 588,
                                "ti001": 588
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "azure"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1020.517333,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757411824642"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 33,
                    "uuid": "a4052bd7-42f9-4486-86a6-fa662a8618b1",
                    "name": "Pytest Regression",
                    "number": 11,
                    "startTime": "2025-09-09T07:00:31.710Z",
                    "endTime": "2025-09-09T10:55:07.405340Z",
                    "lastModified": "2025-09-09T10:55:07.409351Z",
                    "status": "INTERRUPTED",
                    "statistics": {
                        "executions": {
                            "total": 79,
                            "passed": 5,
                            "failed": 55,
                            "skipped": 19
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 66,
                                "ti001": 66
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "azure"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1020.517333,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757415316362"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 34,
                    "uuid": "4c967328-1dd3-4405-a117-dd5c66ad53a5",
                    "name": "Pytest Regression",
                    "number": 12,
                    "startTime": "2025-09-09T07:21:28.293Z",
                    "endTime": "2025-09-09T10:55:07.408322Z",
                    "lastModified": "2025-09-09T10:55:07.409535Z",
                    "status": "INTERRUPTED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "passed": 732,
                            "failed": 9,
                            "skipped": 147
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 156,
                                "ti001": 156
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "gcp"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1020.517333,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757415319529"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 35,
                    "uuid": "56dd60de-0271-43b2-81be-5c0cfe3d847f",
                    "name": "Pytest Regression",
                    "number": 13,
                    "startTime": "2025-09-09T10:00:22.942Z",
                    "endTime": "2025-09-09T13:55:07.376388Z",
                    "lastModified": "2025-09-09T13:55:07.377003Z",
                    "status": "INTERRUPTED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "passed": 309,
                            "failed": 438,
                            "skipped": 141
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 579,
                                "ti001": 579
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "azure"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1020.517333,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757426192463"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 36,
                    "uuid": "41420ab8-6039-452a-b408-c5f9299a43f1",
                    "name": "Pytest Regression",
                    "number": 14,
                    "startTime": "2025-09-09T10:01:06.439Z",
                    "endTime": "2025-09-09T10:40:03.279Z",
                    "lastModified": "2025-09-09T10:40:03.436937Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "passed": 811,
                            "failed": 35,
                            "skipped": 42
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 77,
                                "ti001": 77
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "preview"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1020.517333,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757414409362"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 38,
                    "uuid": "5c046800-d746-4b08-a8da-7e24f40d0048",
                    "name": "Pytest Regression",
                    "number": 15,
                    "startTime": "2025-09-09T15:00:20.775Z",
                    "endTime": "2025-09-09T18:55:07.379965Z",
                    "lastModified": "2025-09-09T18:55:07.380779Z",
                    "status": "INTERRUPTED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "passed": 730,
                            "failed": 17,
                            "skipped": 141
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 158,
                                "ti001": 158
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "azure"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1349.598,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757444112042"
                    },
                    "retentionPolicy": "REGULAR"
                },
                {
                    "owner": "anton_yeromin",
                    "id": 39,
                    "uuid": "08368b09-5bf1-4c0f-bffa-189e316fca63",
                    "name": "Pytest Regression",
                    "number": 16,
                    "startTime": "2025-09-09T15:00:49.573Z",
                    "endTime": "2025-09-09T17:32:16.900Z",
                    "lastModified": "2025-09-09T17:32:17.018510Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 888,
                            "passed": 828,
                            "failed": 18,
                            "skipped": 42
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 60,
                                "ti001": 60
                            }
                        }
                    },
                    "attributes": [
                        {
                            "key": "env",
                            "value": "preview"
                        }
                    ],
                    "mode": "DEFAULT",
                    "analysing": [],
                    "approximateDuration": 1349.598,
                    "hasRetries": false,
                    "rerun": false,
                    "metadata": {
                        "rp.cluster.lastRun": "1757439142457"
                    },
                    "retentionPolicy": "REGULAR"
                }
            ],
            "page": {
                "number": 1,
                "size": 20,
                "totalElements": 15,
                "totalPages": 1
            }
        },
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.FIND_TEST_ITEM_BY_ID,
        {"item_id": "2884"},
        """
        {
            "id": 2884,
            "uuid": "16617c14-babf-4c30-be17-30510d8d5073",
            "name": "codemie_test_harness/tests/workflow/assistant_tools/ado/test_workflow_with_assistant_with_ado_test_plan_tools.py::test_workflow_with_assistant_with_ado_test_plan_tools",
            "codeRef": "codemie_test_harness/tests/workflow/assistant_tools/ado/test_workflow_with_assistant_with_ado_test_plan_tools.py:test_workflow_with_assistant_with_ado_test_plan_tools",
            "parameters": [],
            "attributes": [
                {
                    "key": null,
                    "value": "regression"
                }
            ],
            "type": "STEP",
            "startTime": "2025-09-08T08:51:45.158Z",
            "endTime": "2025-09-08T08:52:54.202Z",
            "status": "FAILED",
            "statistics": {
                "executions": {
                    "total": 1,
                    "failed": 1
                },
                "defects": {
                    "to_investigate": {
                        "total": 1,
                        "ti001": 1
                    }
                }
            },
            "pathNames": {
                "launchPathName": {
                    "name": "Pytest Regression",
                    "number": 2
                }
            },
            "issue": {
                "issueType": "ti001",
                "autoAnalyzed": false,
                "ignoreAnalyzer": false,
                "externalSystemIssues": []
            },
            "hasChildren": false,
            "hasStats": true,
            "launchId": 23,
            "uniqueId": "auto:87331521821410ba6c28c2a3a9643eb7",
            "testCaseId": "codemie_test_harness/tests/workflow/assistant_tools/ado/test_workflow_with_assistant_with_ado_test_plan_tools.py:test_workflow_with_assistant_with_ado_test_plan_tools",
            "testCaseHash": -800162226,
            "patternTemplates": [],
            "path": "2884"
        },
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_TEST_ITEMS_FOR_LAUNCH,
        {"launch_id": "23", "page_number": 1, "status": "FAILED"},
        """
        {
            "content": [
                {
                    "id": 2884,
                    "uuid": "16617c14-babf-4c30-be17-30510d8d5073",
                    "name": "codemie_test_harness/tests/workflow/assistant_tools/ado/test_workflow_with_assistant_with_ado_test_plan_tools.py::test_workflow_with_assistant_with_ado_test_plan_tools",
                    "codeRef": "codemie_test_harness/tests/workflow/assistant_tools/ado/test_workflow_with_assistant_with_ado_test_plan_tools.py:test_workflow_with_assistant_with_ado_test_plan_tools",
                    "parameters": [],
                    "attributes": [
                        {
                            "key": "",
                            "value": "regression"
                        }
                    ],
                    "type": "STEP",
                    "startTime": "2025-09-08T08:51:45.158Z",
                    "endTime": "2025-09-08T08:52:54.202Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 1,
                            "failed": 1
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 1,
                                "ti001": 1
                            }
                        }
                    },
                    "pathNames": {
                        "launchPathName": {
                            "name": "Pytest Regression",
                            "number": 2
                        }
                    },
                    "issue": {
                        "issueType": "ti001",
                        "autoAnalyzed": false,
                        "ignoreAnalyzer": false,
                        "externalSystemIssues": []
                    },
                    "hasChildren": false,
                    "hasStats": true,
                    "launchId": 23,
                    "uniqueId": "auto:87331521821410ba6c28c2a3a9643eb7",
                    "testCaseId": "codemie_test_harness/tests/workflow/assistant_tools/ado/test_workflow_with_assistant_with_ado_test_plan_tools.py:test_workflow_with_assistant_with_ado_test_plan_tools",
                    "testCaseHash": -800162226,
                    "patternTemplates": [],
                    "path": "2884"
                },
                {
                    "id": 3105,
                    "uuid": "df7e2a49-ed1c-458e-aac0-5dfaab1e2943",
                    "name": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py::test_workflow_with_sql_tools_with_hardcoded_args[DataBaseDialect.MS_SQL]",
                    "codeRef": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py:test_workflow_with_sql_tools_with_hardcoded_args",
                    "parameters": [
                        {
                            "key": "prompt",
                            "value": "{'sql_query': \"SELECT table_name\\n                            FROM\\n                            information_schema.tables\\n                            WHERE\\n                            table_type = 'BASE TABLE'\\n                            AND\\n                            table_catalog = 'autotests'\\n                            AND\\n                            table_schema = 'dbo';\\n                            \"}"
                        },
                        {
                            "key": "toolkit",
                            "value": "Data Management"
                        },
                        {
                            "key": "db_dialect",
                            "value": "mssql"
                        },
                        {
                            "key": "expected_response",
                            "value": "[{'table_name': 'Users'}, {'table_name': 'Products'}]"
                        },
                        {
                            "key": "tool_name",
                            "value": "sql"
                        }
                    ],
                    "attributes": [
                        {
                            "key": "skipif",
                            "value": "False"
                        },
                        {
                            "key": "",
                            "value": "regression"
                        }
                    ],
                    "type": "STEP",
                    "startTime": "2025-09-08T08:57:10.737Z",
                    "endTime": "2025-09-08T08:57:32.809Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 1,
                            "failed": 1
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 1,
                                "ti001": 1
                            }
                        }
                    },
                    "pathNames": {
                        "launchPathName": {
                            "name": "Pytest Regression",
                            "number": 2
                        }
                    },
                    "issue": {
                        "issueType": "ti001",
                        "autoAnalyzed": false,
                        "ignoreAnalyzer": false,
                        "externalSystemIssues": []
                    },
                    "hasChildren": false,
                    "hasStats": true,
                    "launchId": 23,
                    "uniqueId": "auto:7d6e822c868f455cc026c303af84a8ce",
                    "testCaseId": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py:test_workflow_with_sql_tools_with_hardcoded_args[Data Management,[{'table_name': 'Users'}, {'table_name': 'Products'}],mssql,sql,{'sql_query': \"SELECT table_name\\n                            FROM\\n                            information_schema.tables\\n                            WHERE\\n                            table_type = 'BASE TABLE'\\n                            AND\\n                            table_catalog = 'autotests'\\n                            AND\\n                            table_schema = 'dbo';\\n                            \"}]",
                    "testCaseHash": 847364112,
                    "patternTemplates": [],
                    "path": "3105"
                },
                {
                    "id": 3133,
                    "uuid": "54788617-b214-4057-9a20-3c4d34ee9432",
                    "name": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py::test_workflow_with_sql_tools_with_overriding_args[DataBaseDialect.MS_SQL]",
                    "codeRef": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py:test_workflow_with_sql_tools_with_overriding_args",
                    "parameters": [
                        {
                            "key": "prompt",
                            "value": "{'sql_query': \"SELECT table_name\\n                            FROM\\n                            information_schema.tables\\n                            WHERE\\n                            table_type = 'BASE TABLE'\\n                            AND\\n                            table_catalog = 'autotests'\\n                            AND\\n                            table_schema = 'dbo';\\n                            \"}"
                        },
                        {
                            "key": "toolkit",
                            "value": "Data Management"
                        },
                        {
                            "key": "db_dialect",
                            "value": "mssql"
                        },
                        {
                            "key": "expected_response",
                            "value": "[{'table_name': 'Users'}, {'table_name': 'Products'}]"
                        },
                        {
                            "key": "tool_name",
                            "value": "sql"
                        }
                    ],
                    "attributes": [
                        {
                            "key": "skipif",
                            "value": "False"
                        },
                        {
                            "key": "",
                            "value": "regression"
                        }
                    ],
                    "type": "STEP",
                    "startTime": "2025-09-08T08:57:42.220Z",
                    "endTime": "2025-09-08T08:58:04.877Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 1,
                            "failed": 1
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 1,
                                "ti001": 1
                            }
                        }
                    },
                    "pathNames": {
                        "launchPathName": {
                            "name": "Pytest Regression",
                            "number": 2
                        }
                    },
                    "issue": {
                        "issueType": "ti001",
                        "autoAnalyzed": false,
                        "ignoreAnalyzer": false,
                        "externalSystemIssues": []
                    },
                    "hasChildren": false,
                    "hasStats": true,
                    "launchId": 23,
                    "uniqueId": "auto:4ccd523db59b8f0aae122708ec054430",
                    "testCaseId": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py:test_workflow_with_sql_tools_with_overriding_args[Data Management,[{'table_name': 'Users'}, {'table_name': 'Products'}],mssql,sql,{'sql_query': \"SELECT table_name\\n                            FROM\\n                            information_schema.tables\\n                            WHERE\\n                            table_type = 'BASE TABLE'\\n                            AND\\n                            table_catalog = 'autotests'\\n                            AND\\n                            table_schema = 'dbo';\\n                            \"}]",
                    "testCaseHash": -266643613,
                    "patternTemplates": [],
                    "path": "3133"
                },
                {
                    "id": 3154,
                    "uuid": "0a2d317f-5e4f-4ac3-a5d0-c0c8368357d0",
                    "name": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py::test_workflow_with_sql_tools_direct[DataBaseDialect.MS_SQL]",
                    "codeRef": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py:test_workflow_with_sql_tools_direct",
                    "parameters": [
                        {
                            "key": "prompt",
                            "value": "{'sql_query': \"SELECT table_name\\n                            FROM\\n                            information_schema.tables\\n                            WHERE\\n                            table_type = 'BASE TABLE'\\n                            AND\\n                            table_catalog = 'autotests'\\n                            AND\\n                            table_schema = 'dbo';\\n                            \"}"
                        },
                        {
                            "key": "toolkit",
                            "value": "Data Management"
                        },
                        {
                            "key": "db_dialect",
                            "value": "mssql"
                        },
                        {
                            "key": "expected_response",
                            "value": "[{'table_name': 'Users'}, {'table_name': 'Products'}]"
                        },
                        {
                            "key": "tool_name",
                            "value": "sql"
                        }
                    ],
                    "attributes": [
                        {
                            "key": "skipif",
                            "value": "False"
                        },
                        {
                            "key": "",
                            "value": "regression"
                        }
                    ],
                    "type": "STEP",
                    "startTime": "2025-09-08T08:58:09.114Z",
                    "endTime": "2025-09-08T08:58:29.596Z",
                    "status": "FAILED",
                    "statistics": {
                        "executions": {
                            "total": 1,
                            "failed": 1
                        },
                        "defects": {
                            "to_investigate": {
                                "total": 1,
                                "ti001": 1
                            }
                        }
                    },
                    "pathNames": {
                        "launchPathName": {
                            "name": "Pytest Regression",
                            "number": 2
                        }
                    },
                    "issue": {
                        "issueType": "ti001",
                        "autoAnalyzed": false,
                        "ignoreAnalyzer": false,
                        "externalSystemIssues": []
                    },
                    "hasChildren": false,
                    "hasStats": true,
                    "launchId": 23,
                    "uniqueId": "auto:d28f8ed5670ce281b4e111a58251504d",
                    "testCaseId": "codemie_test_harness/tests/workflow/direct_tools_calling/test_workflow_with_data_management_tools.py:test_workflow_with_sql_tools_direct[Data Management,[{'table_name': 'Users'}, {'table_name': 'Products'}],mssql,sql,{'sql_query': \"SELECT table_name\\n                            FROM\\n                            information_schema.tables\\n                            WHERE\\n                            table_type = 'BASE TABLE'\\n                            AND\\n                            table_catalog = 'autotests'\\n                            AND\\n                            table_schema = 'dbo';\\n                            \"}]",
                    "testCaseHash": 1554145012,
                    "patternTemplates": [],
                    "path": "3154"
                }
            ],
            "page": {
                "number": 1,
                "size": 20,
                "totalElements": 4,
                "totalPages": 1
            }
        },
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_LOGS_FOR_TEST_ITEM,
        {"item_id": "2884", "page_number": 1},
        """
        {
            "content": [
                {
                    "id": 105239,
                    "time": "2025-09-08T08:51:45.164Z",
                    "message": "Making /v1/assistants request to https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com/code-assistant-api<class 'dict'>",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105240,
                    "time": "2025-09-08T08:51:45.164Z",
                    "message": "Request body: {'name': 'sdp_xjwyipzcypfocwq', 'description': 'Integration test assistant', 'system_prompt': 'You are a helpful integration test assistant', 'project': 'codemie', 'context': [], 'llm_model_type': 'gpt-4o-2024-08-06', 'toolkits': [{'toolkit': 'Azure DevOps Test Plan', 'tools': [{'name': 'create_test_plan', 'settings_config': False, 'settings': {'id': 'cfe4c992-6338-42ed-ab44-807bdaa1cefa', 'date': '2025-09-08T08:51:03.438066', 'update_date': '2025-09-08T08:51:03.438066', 'user_id': '4c80b5ea-fae8-4c72-b09e-339909b84537', 'project_name': 'codemie', 'alias': 'sdp_ifyrslqqplcxyhx', 'default': False, 'is_global': False, 'credential_type': <CredentialTypes.AZURE_DEVOPS: 'AzureDevOps'>, 'credential_values': [{'key': 'url', 'value': 'https://dev.azure.com'}, {'key': 'token', 'value': '**********'}, {'key': 'project', 'value': 'CodemieAnton'}, {'key': 'organization', 'value': 'AntonYeromin'}], 'setting_type': <IntegrationType.PROJECT: 'project'>}}, {'name': 'create_test_suite', 'settings_config': False, 'settings': {'id': 'cfe4c992-6338-42ed-ab44-807bdaa1cefa', 'date': '2025-09-08T08:51:03.438066', 'update_date': '2025-09-08T08:51:03.438066', 'user_id': '4c80b5ea-fae8-4c72-b09e-339909b84537', 'project_name': 'codemie', 'alias': 'sdp_ifyrslqqplcxyhx', 'default': False, 'is_global': False, 'credential_type': <CredentialTypes.AZURE_DEVOPS: 'AzureDevOps'>, 'credential_values': [{'key': 'url', 'value': 'https://dev.azure.com'}, {'key': 'token', 'value': '**********'}, {'key': 'project', 'value': 'CodemieAnton'}, {'key': 'organization', 'value': 'AntonYeromin'}], 'setting_type': <IntegrationType.PROJECT: 'project'>}}, {'name': 'add_test_case', 'settings_config': False, 'settings': {'id': 'cfe4c992-6338-42ed-ab44-807bdaa1cefa', 'date': '2025-09-08T08:51:03.438066', 'update_date': '2025-09-08T08:51:03.438066', 'user_id': '4c80b5ea-fae8-4c72-b09e-339909b84537', 'project_name': 'codemie', 'alias': 'sdp_ifyrslqqplcxyhx', 'default': False, 'is_global': False, 'credential_type': <CredentialTypes.AZURE_DEVOPS: 'AzureDevOps'>, 'credential_values': [{'key': 'url', 'value': 'https://dev.azure.com'}, {'key': 'token', 'value': '**********'}, {'key': 'project', 'value': 'CodemieAnton'}, {'key': 'organization', 'value': 'AntonYeromin'}], 'setting_type': <IntegrationType.PROJECT: 'project'>}}, {'name': 'delete_test_suite', 'settings_config': False, 'settings': {'id': 'cfe4c992-6338-42ed-ab44-807bdaa1cefa', 'date': '2025-09-08T08:51:03.438066', 'update_date': '2025-09-08T08:51:03.438066', 'user_id': '4c80b5ea-fae8-4c72-b09e-339909b84537', 'project_name': 'codemie', 'alias': 'sdp_ifyrslqqplcxyhx', 'default': False, 'is_global': False, 'credential_type': <CredentialTypes.AZURE_DEVOPS: 'AzureDevOps'>, 'credential_values': [{'key': 'url', 'value': 'https://dev.azure.com'}, {'key': 'token', 'value': '**********'}, {'key': 'project', 'value': 'CodemieAnton'}, {'key': 'organization', 'value': 'AntonYeromin'}], 'setting_type': <IntegrationType.PROJECT: 'project'>}}, {'name': 'delete_test_plan', 'settings_config': False, 'settings': {'id': 'cfe4c992-6338-42ed-ab44-807bdaa1cefa', 'date': '2025-09-08T08:51:03.438066', 'update_date': '2025-09-08T08:51:03.438066', 'user_id': '4c80b5ea-fae8-4c72-b09e-339909b84537', 'project_name': 'codemie', 'alias': 'sdp_ifyrslqqplcxyhx', 'default': False, 'is_global': False, 'credential_type': <CredentialTypes.AZURE_DEVOPS: 'AzureDevOps'>, 'credential_values': [{'key': 'url', 'value': 'https://dev.azure.com'}, {'key': 'token', 'value': '**********'}, {'key': 'project', 'value': 'CodemieAnton'}, {'key': 'organization', 'value': 'AntonYeromin'}], 'setting_type': <IntegrationType.PROJECT: 'project'>}}], 'label': '', 'settings_config': False, 'is_external': False, 'settings': {'id': 'cfe4c992-6338-42ed-ab44-807bdaa1cefa', 'date': '2025-09-08T08:51:03.438066', 'update_date': '2025-09-08T08:51:03.438066', 'user_id': '4c80b5ea-fae8-4c72-b09e-339909b84537', 'project_name': 'codemie', 'alias': 'sdp_ifyrslqqplcxyhx', 'default': False, 'is_global': False, 'credential_type': <CredentialTypes.AZURE_DEVOPS: 'AzureDevOps'>, 'credential_values': [{'key': 'url', 'value': 'https://dev.azure.com'}, {'key': 'token', 'value': '**********'}, {'key': 'project', 'value': 'CodemieAnton'}, {'key': 'organization', 'value': 'AntonYeromin'}], 'setting_type': <IntegrationType.PROJECT: 'project'>}}], 'user_prompts': [], 'shared': False, 'is_react': False, 'is_global': False, 'slug': 'sdp_xjwyipzcypfocwq', 'mcp_servers': [], 'assistant_ids': []}",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105241,
                    "time": "2025-09-08T08:51:45.165Z",
                    "message": "Starting new HTTPS connection (1): codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105242,
                    "time": "2025-09-08T08:51:45.226Z",
                    "message": "https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443 \"POST /code-assistant-api/v1/assistants HTTP/1.1\" 200 39",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105243,
                    "time": "2025-09-08T08:51:45.226Z",
                    "message": "Received response with status 200",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105244,
                    "time": "2025-09-08T08:51:45.226Z",
                    "message": "Response datasource_type: <class 'dict'>",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105245,
                    "time": "2025-09-08T08:51:45.228Z",
                    "message": "Successfully processed /v1/assistants request to <class 'dict'>",
                    "level": "INFO",
                    "itemId": 2884
                },
                {
                    "id": 105246,
                    "time": "2025-09-08T08:51:45.228Z",
                    "message": "Making /v1/assistants request to https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com/code-assistant-apityping.List[codemie_sdk.models.assistant.AssistantBase]",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105247,
                    "time": "2025-09-08T08:51:45.228Z",
                    "message": "Request params: {'page': 0, 'per_page': 200, 'scope': 'visible_to_user', 'minimal_response': True}",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105248,
                    "time": "2025-09-08T08:51:45.229Z",
                    "message": "Starting new HTTPS connection (1): codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105249,
                    "time": "2025-09-08T08:51:45.299Z",
                    "message": "https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443 \"GET /code-assistant-api/v1/assistants?page=0&per_page=200&scope=visible_to_user&minimal_response=True HTTP/1.1\" 200 69989",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105290,
                    "time": "2025-09-08T08:51:45.310Z",
                    "message": "Received response with status 200",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105291,
                    "time": "2025-09-08T08:51:45.311Z",
                    "message": "Response datasource_type: <class 'dict'>",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105292,
                    "time": "2025-09-08T08:51:45.312Z",
                    "message": "Successfully processed /v1/assistants request to typing.List[codemie_sdk.models.assistant.AssistantBase]",
                    "level": "INFO",
                    "itemId": 2884
                },
                {
                    "id": 105293,
                    "time": "2025-09-08T08:51:45.314Z",
                    "message": "Making /v1/workflows request to https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com/code-assistant-api<class 'dict'>",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105294,
                    "time": "2025-09-08T08:51:45.314Z",
                    "message": "Request body: {'project': 'codemie', 'name': 'sdp_xpgivblpavtdeza', 'description': 'Test Workflow', 'yaml_config': 'enable_summarization_node: false\\ntools: []\\nassistants:\\n- id: sdp_xjwyipzcypfocwq\\n  model: gpt-4o-2024-08-06\\n  assistant_id: 6ef6a01d-70ef-4211-a385-8c99b87eee72\\nstates:\\n- id: sdp_xjwyipzcypfocwq\\n  assistant_id: sdp_xjwyipzcypfocwq\\n  task: Run\\n  next:\\n    state_id: end\\n', 'mode': <WorkflowMode.SEQUENTIAL: 'Sequential'>, 'shared': True, 'icon_url': None}",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105295,
                    "time": "2025-09-08T08:51:45.315Z",
                    "message": "Starting new HTTPS connection (1): codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105296,
                    "time": "2025-09-08T08:51:45.394Z",
                    "message": "https://codemie-azure.eks-sandbox.aws.main.edp.projects.epam.com:443 \"POST /code-assistant-api/v1/workflows HTTP/1.1\" 200 2119",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105297,
                    "time": "2025-09-08T08:51:45.394Z",
                    "message": "Received response with status 200",
                    "level": "DEBUG",
                    "itemId": 2884
                },
                {
                    "id": 105298,
                    "time": "2025-09-08T08:51:45.394Z",
                    "message": "Response datasource_type: <class 'dict'>",
                    "level": "DEBUG",
                    "itemId": 2884
                }
            ],
            "page": {
                "number": 1,
                "size": 20,
                "totalElements": 903,
                "totalPages": 46
            }
        },
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_USER_INFORMATION,
        {"username": "anton_yeromin"},
        """
        {
            "uuid": "de49a61f-1100-4de6-be8e-4ed7d62f5f27",
            "active": true,
            "id": 4,
            "userId": "anton_yeromin",
            "email": "anton_yeromin@epam.com",
            "fullName": "Anton Yeromin",
            "accountType": "SAML",
            "userRole": "USER",
            "photoLoaded": true,
            "metadata": {
                "last_login": 1757403246837,
                "synchronizationDate": 1757314564405
            },
            "assignedProjects": {
                "epm-cdme": {
                    "projectId": 4,
                    "projectRole": "PROJECT_MANAGER",
                    "entryType": "INTERNAL"
                },
                "anton_yeromin_personal": {
                    "projectId": 6,
                    "projectRole": "PROJECT_MANAGER",
                    "entryType": "PERSONAL"
                }
            }
        },
        """,
    ),
    (
        Toolkit.REPORT_PORTAL,
        ReportPortalTool.GET_DASHBOARD_DATA,
        {"dashboard_id": "2"},
        """
        {
            "description": "dashboard for testing purposes",
            "owner": "dmytro_adamtsev",
            "id": 2,
            "name": "test-dashboard",
            "widgets": []
        },
        """,
    ),
]
