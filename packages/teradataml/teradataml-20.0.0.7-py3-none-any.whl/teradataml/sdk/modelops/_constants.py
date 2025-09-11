# The below dictionary can be used by developers to map the tags to class names
# if developer want to use different class names for the tags in the OpenAPI spec.
_DEV_DEFINED_TAG_TO_CLASS_NAME_MAPPER = {}

# The below dictionary can be used by developers to map the old class methods
# to the new class methods if developer want to use different method names if
# operationID in the OpenAPI spec, is not correct and doesn't behave as per
# description/summary.
_DEV_DEFINED_CLASS_FUNCTIONS_MAPPER = {
    "/api/projects/{id}": {
        "get": {
            "operationID": "getItemResource-project-get",
            "function_name": "find_by_id"
        },
        "put": {
            "operationID": "putItemResource-project-put",
            "function_name": "replace_by_id"
        },
        "patch": {
            "operationID": "patchItemResource-project-patch",
            "function_name": "update_by_id"
        }
    },
    "/api/projects": {
        "post": {
            "operationID": "postCollectionResource-project-post",
            "function_name": "create_project"
        },
        "get": {
            "operationID": "getCollectionResource-project-get",
            "function_name": "find_all"
        }
    },
    "/api/projects/{id}/batchImportAI": {
        "post": {
            "operationID": "batchImportAI",
            "function_name": "import_models"
        }
    },
    "/api/deployments/search/findActiveByTrainedModelIdAndEngineType": {
        "get": {
            "operationID": "executeSearch-deployment-get_6",
            "function_name": "find_active_by_trained_model_and_engine_type"
        }
    },
    "/api/deployments/search/findActive": {
        "get": {
            "operationID": "executeSearch-deployment-get_1",
            "function_name": "find_active"
        }
    },
    "/api/datasetConnections/search/findByArchived": {
        "get": {
            "operationID": "executeSearch-datasetconnection-get_4",
            "function_name": "find_by_archived"
        }
    },
    "/api/datasetTemplates/search/findByArchived": {
        "get": {
            "operationID": "executeSearch-datasettemplate-get_3",
            "function_name": "find_by_archived"
        }
    },
    "/api/datasets/search/findByArchived": {
        "get": {
            "operationID": "executeSearch-dataset-get_4",
            "function_name": "find_by_archived"
        }
    },
    "/api/featureEngineeringTasks/search/findByArchived": {
        "get": {
            "operationID": "executeSearch-featureengineeringtask-get_3",
            "function_name": "find_by_archived"
        }
    },
    "/api/models/search/findByArchived": {
        "get": {
            "operationID": "executeSearch-model-get_4",
            "function_name": "find_by_archived"
        }
    },
    "/api/projects/search/findByArchived": {
        "get": {
            "operationID": "executeSearch-project-get_2",
            "function_name": "find_by_archived"
        }
    },
    "/api/trainedModels/search/findByArchived": {
        "get": {
            "operationID": "executeSearch-trainedmodel-get_3",
            "function_name": "find_by_archived"
        }
    },
    "/api/datasetConnections/{id}": {
        "get": {
            "operationID": "getItemResource-datasetconnection-get",
            "function_name": "find_by_id"
        }
    },
    "/api/datasetTemplates/{id}": {
        "get": {
            "operationID": "getItemResource-datasettemplate-get",
            "function_name": "find_by_id"
        }
    },
    "/api/datasets/{id}": {
        "get": {
            "operationID": "getItemResource-dataset-get",
            "function_name": "find_by_id"
        }
    },
    "/api/deployments/{id}": {
        "get": {
            "operationID": "getItemResource-deployment-get",
            "function_name": "find_by_id"
        }
    },
    "/api/featureEngineeringEvents/{id}": {
        "get": {
            "operationID": "getItemResource-featureengineeringevent-get",
            "function_name": "find_by_id"
        }
    },
    "/api/featureEngineeringTasks/{id}": {
        "get": {
            "operationID": "getItemResource-featureengineeringtask-get",
            "function_name": "find_by_id"
        }
    },
    "/api/jobEvents/{id}": {
        "get": {
            "operationID": "getItemResource-jobevent-get",
            "function_name": "find_by_id"
        }
    },
    "/api/jobs/{id}": {
        "get": {
            "operationID": "getItemResource-job-get",
            "function_name": "find_by_id"
        }
    },
    "/api/modelAttributes/{id}": {
        "get": {
            "operationID": "getItemResource-modelattribute-get",
            "function_name": "find_by_id"
        }
    },
    "/api/models/{id}": {
        "get": {
            "operationID": "getItemResource-model-get",
            "function_name": "find_by_id"
        }
    },
    "/api/projectAttributes/{id}": {
        "get": {
            "operationID": "getItemResource-projectattribute-get",
            "function_name": "find_by_id"
        }
    },
    "/api/tags/{id}": {
        "get": {
            "operationID": "getItemResource-tag-get",
            "function_name": "find_by_id"
        }
    },
    "/api/trainedModelEvents/{id}": {
        "get": {
            "operationID": "getItemResource-trainedmodelevent-get",
            "function_name": "find_by_id"
        }
    },
    "/api/trainedModels/{id}": {
        "get": {
            "operationID": "getItemResource-trainedmodel-get",
            "function_name": "find_by_id"
        }
    },
    "/api/userAttributes/{id}": {
        "get": {
            "operationID": "getItemResource-userattribute-get",
            "function_name": "find_by_id"
        }
    },
    "/api/archives/{entityType}/{entityId}": {
        "delete": {
            "operationID": "unArchive",
            "function_name": "unarchive"
        }
    },
    "/api/alerts": {
        "get": {
            "operationID": "getAlerts",
            "function_name": "find_all"
        }
    },
    "/api/datasetConnections": {
        "get": {
            "operationID": "getCollectionResource-datasetconnection-get",
            "function_name": "find_all"
        }
    },
    "/api/datasetTemplates": {
        "get": {
            "operationID": "getCollectionResource-datasettemplate-get",
            "function_name": "find_all"
        }
    },
    "/api/datasets": {
        "get": {
            "operationID": "getCollectionResource-dataset-get",
            "function_name": "find_all"
        }
    },
    "/api/deployments": {
        "get": {
            "operationID": "getCollectionResource-deployment-get",
            "function_name": "find_all"
        }
    },
    "/api/engineTypes": {
        "get": {
            "operationID": "getEngineTypes",
            "function_name": "find_all"
        }
    },
    "/api/featureEngineeringEvents": {
        "get": {
            "operationID": "getCollectionResource-featureengineeringevent-get",
            "function_name": "find_all"
        }
    },
    "/api/featureEngineeringTasks": {
        "get": {
            "operationID": "getCollectionResource-featureengineeringtask-get",
            "function_name": "find_all"
        }
    },
    "/api/jobEvents": {
        "get": {
            "operationID": "getCollectionResource-jobevent-get",
            "function_name": "find_all"
        }
    },
    "/api/jobs": {
        "get": {
            "operationID": "getCollectionResource-job-get",
            "function_name": "find_all"
        }
    },
    "/api/modelAttributes": {
        "get": {
            "operationID": "getCollectionResource-modelattribute-get",
            "function_name": "find_all"
        }
    },
    "/api/models": {
        "get": {
            "operationID": "getCollectionResource-model-get",
            "function_name": "find_all"
        }
    },
    "/api/projectAttributes": {
        "get": {
            "operationID": "getCollectionResource-projectattribute-get",
            "function_name": "find_all"
        }
    },
    "/api/services": {
        "get": {
            "operationID": "getServices",
            "function_name": "find_all"
        }
    },
    "/api/tags": {
        "get": {
            "operationID": "getCollectionResource-tag-get",
            "function_name": "find_all"
        }
    },
    "/api/trainedModelEvents": {
        "get": {
            "operationID": "getCollectionResource-trainedmodelevent-get",
            "function_name": "find_all"
        }
    },
    "/api/trainedModels": {
        "get": {
            "operationID": "getCollectionResource-trainedmodel-get",
            "function_name": "find_all"
        }
    },
    "/api/userAttributes": {
        "get": {
            "operationID": "getCollectionResource-userattribute-get",
            "function_name": "find_all"
        }
    },
    "/api/userInfo": {
        "get": {
            "operationID": "getUserInfo",
            "function_name": "find_all"
        }
    }
}