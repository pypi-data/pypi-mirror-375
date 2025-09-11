## How to create Software Development Kit (SDK) using OpenAPI spec

All SDKs should be in module `teradataml.sdk`. If a module name `<module_name>` is to be created with OpenAPI JSON file, 
- The json file (say `openapi_spec.json`) should be placed in the directory `teradataml/data/sdk/<module_name>"` after creating required folders to maintain the folder structure.
- Create a folder `<module_name>` in `teradataml/sdk/` and place `__init__.py` file.
- Copy and paste the code from `teradataml/sdk/modelops/__init__.py` to newly created `__init__.py` file.
- Update the constants `SdkNames` and `SdkPackagePaths` in `teradataml/sdk/constants.py` to name the module and locate to appropriate location of OpenAPI JSON spec.
- Update the values to the constants `SdkNames` and `SdkPackagePaths` in `__init__.py`.
- Create `teradataml/sdk/<module_name>/_constants.py`.
- Copy and paste the code from `teradataml/sdk/modelops/_constants.py`. Keep empty dictionaries if no change in class names and function names is required. Fill in the dictionary similar to `teradataml/sdk/modelops/_constants.py` with intended class and function names.
- If customization is needed in client object, copy and paste the file `teradataml/sdk/modelops/_client.py` to `teradataml/sdk/<module_name>/_client.py` and update corresponding imports (for new client) in `teradataml/sdk/<module_name>/__init__.py`. Otherwise, user can use `BaseClient` from `teradataml/sdk/api_client.py`.
- Generate Pydantic models for OpenAPI schema using below commands which will create `teradataml/sdk/<module_name>/models.py`. Add unit test cases similar to `teradataml/tests/unit/sdk/test_modelops_schema.py` which import models and use helper class to bulk test the classes.
```shell
pip install datamodel-code-generator==0.27.3
# Run below command from pyTeradata directory.
datamodel-codegen --input teradataml/data/sdk/<module_name>/openapi_spec.json --input-file-type openapi --output teradataml/sdk/<module_name>/models.py --output-model-type pydantic_v2.BaseModel --use-field-description --keep-model-order --target-python-version=3.8 --use-schema-description  --field-constraints --allow-population-by-field-name --strict-types bool int float # From windows use datamodel-codegen.exe
```
- If there are not schema in OpenAPI spec, create empty file `teradataml/sdk/<module_name>/models.py`.


## What is created dynamically

When the user runs `from teradataml.sdk.<module_name> import *` or `from teradataml.sdk.<module_name> import AnyClass`, it creates classes and class methods dynamically.

How are these classes created?
- Tags from OpenAPI spec are converted to Camel case and used as classes.
- If any of the API endpoint methods does not have tags associated with them, such functions are kept in class name `DefaultApi`.

How are class methods created?
- All the API endpoint methods form each function of the class.
- The function names are taken from `OperationId` field of function in OpenAPI JSON spec. The value of `OperationId` is converted to Snake case along with replacing hyphens (`-`) with underscores (`_`). This new value is used as API function name for the user to call by passing parameters.


## Example - Vantage ModelOps SDK

Couple of the tags in ModelOps OpenAPI spec is `Alert rules`, `Models`. These tags are converted to classes `AlertRules` and `Models` respectively.

The API end point `/api/models` contains `get` method with `operationId` as `getCollectionResource-model-get`. The framework creates `get_collection_resource_model_get(...)` function in `Models` class. 

Similarly, the API end point `/api/models/{id}/alertRules` contains `get` method with `operationId` as `getAlertRules`. The framework creates `get_alert_rules(...)` functions in `AlertRules` class.

So, these API endpoints can be accessed through SDK as follows:
```python
# Authenticate and connect to client.
from teradataml.sdk.modelops import ModelOpsClient
from teradataml.sdk import ClientCredentialsAuth # Three different authentication mechanisms are supported.
auth_obj = ClientCredentialsAuth(
    auth_client_id="<client_id>",
    auth_client_secret="<client_secret>",
    auth_token_url="https://10.27.117.175/sso/realms/teradata/protocol/openid-connect/token"
)
client = ModelOpsCleint(
    base_url="https://10.27.117.175/core",
    auth=auth_obj,
    ssl_verify=False
)

# Import required classes.
from teradataml.sdk.modelops import AlertRules, Models

# Some APIs are tied with Project ID which needs to be set to the client.
client.set_project_id("<uuid_project_id>")

# Create Models object and get all the models.
mod = Models(client=client)
models = mod.get_collection_resource_model_get()

# Get alert rules for any one of the model.
ar = AlertRules(client=client)
ar.get_alert_rules(id="<uuid_model_id>")
```

## Note:
- All the argument to the API functions are read as `**kwargs`. So, the user has to pass keyword arguments i.e., positional argument usage is not supported yet.
- The following validations are done for arguments which accepts basic data types:
  - Missing required arguments.
  - Invalid type passed to arguments.
  - Invalid (non-permitted) value passed to arguments.
- Validations for dict type objects (like input for `requestBody`) are yet to be added.