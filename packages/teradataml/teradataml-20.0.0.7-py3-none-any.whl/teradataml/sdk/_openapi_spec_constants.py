# ################################################################################################
# 
# Copyright 2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Adithya Avvaru (adithya.avvaru@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# 
# Version: 1.0
# ModelOps SDK Version: 1.0
#
# This file contains the constants from OpenAPI Specification that are used in the SDK.
# TODO: Not all constants from OpenAPI spec is used in the SDK. Will keep on adding based on the
#       requirements.
# 
# ################################################################################################

from enum import Enum


class DefaultConstants(Enum):
    """
    Constants for default values in OpenAPI Specification.
    """
    DEFAULT_TAG = "DefaultAPI"
    DEFAULT_CLASS = "DefaultApi"
    DEFAULT_TAG_DESC = "APIs without a tag."
    DEFAULT_SCHEMA_TYPE = "object"
    DEFAULT_SCHEMA_VALUE = None
    DEFAULT_DESCRIPTION = "No description available."

class OpenAPIObject(Enum):
    """
    Constants for OpenAPI Specification.
    """
    OPENAPI = "openapi"
    INFO = "info"
    SERVERS = "servers"
    SECURITY = "security"
    TAGS = "tags"
    PATHS = "paths"
    COMPONENTS = "components"
    EXTERNAL_DOCS = "externalDocs"
    JSON_SCHEMA_DIALECT = "jsonSchemaDialect"
    WEBHOOKS = "webhooks"

class InfoObject(Enum):
    """
    Constants for Info Object in OpenAPI Specification.
    """
    TITLE = "title"
    VERSION = "version"
    DESCRIPTION = "description"
    TERMS_OF_SERVICE = "termsOfService"
    CONTACT = "contact"
    LICENSE = "license"
    SUMMARY = "summary"

class ContactObject(Enum):
    """
    Constants for Contact Object in OpenAPI Specification.
    """
    NAME = "name"
    URL = "url"
    EMAIL = "email"

class LicenseObject(Enum):
    """
    Constants for License Object in OpenAPI Specification.
    """
    NAME = "name"
    URL = "url"
    IDENTIFIER = "identifier"

class ServerObject(Enum):
    """
    Constants for Server Object in OpenAPI Specification.
    """
    URL = "url"
    DESCRIPTION = "description"
    VARIABLES = "variables"

class ServerVariableObject(Enum):
    """
    Constants for Server Variable Object in OpenAPI Specification.
    """
    ENUM = "enum"
    DEFAULT = "default"
    DESCRIPTION = "description"

class ComponentsObject(Enum):
    """
    Constants for Components Object in OpenAPI Specification.
    """
    SCHEMAS = "schemas"
    RESPONSES = "responses"
    PARAMETERS = "parameters"
    EXAMPLES = "examples"
    REQUEST_BODIES = "requestBodies"
    HEADERS = "headers"
    SECURITY_SCHEMES = "securitySchemes"
    LINKS = "links"
    CALLBACKS = "callbacks"
    PATH_ITEMS = "pathItems"

class PathsObject(Enum):
    """
    Constants for Paths Object in OpenAPI Specification.
    """
    PATHS = "/{path}"

class PathItemObject(Enum):
    """
    Constants for Path Item Object in OpenAPI Specification.
    """
    REF = "$ref"
    SUMMARY = "summary"
    DESCRIPTION = "description"
    GET = "get"
    PUT = "put"
    POST = "post"
    DELETE = "delete"
    OPTIONS = "options"
    HEAD = "head"
    PATCH = "patch"
    TRACE = "trace"
    SERVERS = "servers"
    PARAMETERS = "parameters"

class OperationObject(Enum):
    """
    Constants for Operation Object in OpenAPI Specification.
    """
    TAGS = "tags"
    SUMMARY = "summary"
    DESCRIPTION = "description"
    EXTERNAL_DOCS = "externalDocs"
    OPERATION_ID = "operationId"
    PARAMETERS = "parameters"
    REQUEST_BODY = "requestBody"
    RESPONSES = "responses"
    CALLBACKS = "callbacks"
    DEPRECATED = "deprecated"
    SECURITY = "security"
    SERVERS = "servers"

class ExternalDocumentationObject(Enum):
    """
    Constants for External Documentation Object in OpenAPI Specification.
    """
    DESCRIPTION = "description"
    URL = "url"

class ParameterObject(Enum):
    """
    Constants for Parameter Object in OpenAPI Specification.
    """
    NAME = "name"
    # If in is "path", the name field MUST correspond to a template expression 
    # occurring within the path field in the Paths Object.
    # If in is "header" and the name field is "Accept", "Content-Type" or
    # "Authorization", the parameter definition SHALL be ignored.
    IN = "in" # Possible values are "query", "header", "path" or "cookie"
    DESCRIPTION = "description"
    REQUIRED = "required"
    DEPRECATED = "deprecated"
    ALLOW_EMPTY_VALUE = "allowEmptyValue"
    # style: Describes how the parameter value will be serialized depending on 
    # the type of the parameter value. Default values (based on value of in): 
    # for "query" - "form"; for "path" - "simple"; for "header" - "simple"; 
    # for "cookie" - "form".
    STYLE = "style"
    EXPLODE = "explode"
    ALLOW_RESERVED = "allowReserved"
    SCHEMA = "schema"
    EXAMPLE = "example"
    EXAMPLES = "examples"
    CONTENT = "content"

class RequestBodyObject(Enum):
    """
    Constants for Request Body Object in OpenAPI Specification.
    """
    CONTENT = "content"
    REQUIRED = "required"
    DESCRIPTION = "description"

class MediaTypeObject(Enum):
    """
    Constants for Media Type Object in OpenAPI Specification.
    """
    SCHEMA = "schema"
    EXAMPLE = "example"
    EXAMPLES = "examples"
    ENCODING = "encoding"

class EncodingObject(Enum):
    """
    Constants for Encoding Object in OpenAPI Specification.
    """
    CONTENT_TYPE = "contentType"
    HEADERS = "headers"
    STYLE = "style"
    EXPLODE = "explode"
    ALLOW_RESERVED = "allowReserved"

class ResponsesObject(Enum):
    """
    Constants for Responses Object in OpenAPI Specification.
    """
    RESPONSES = "responses"
    DEFAULT = "default"
    DESCRIPTION = "description"
    HEADERS = "headers"
    CONTENT = "content"
    LINKS = "links"

class ResponseObject(Enum):
    """
    Constants for Response Object in OpenAPI Specification.
    """
    DESCRIPTION = "description"
    HEADERS = "headers"
    CONTENT = "content"
    LINKS = "links"

class TagObject(Enum):
    """
    Constants for Tag Object in OpenAPI Specification.
    """
    NAME = "name"
    DESCRIPTION = "description"
    EXTERNAL_DOCS = "externalDocs"

class SchemaObject(Enum):
    """
    Constants for Schema Object in OpenAPI Specification.
    """
    TYPE = "type"
    PROPERTIES = "properties"
    ITEMS = "items"
    REQUIRED = "required"
    DESCRIPTION = "description"
    FORMAT = "format"
    EXAMPLE = "example"
    EXAMPLES = "examples"
    ENUM = "enum"
    DEFAULT = "default"
    REF = "$ref"