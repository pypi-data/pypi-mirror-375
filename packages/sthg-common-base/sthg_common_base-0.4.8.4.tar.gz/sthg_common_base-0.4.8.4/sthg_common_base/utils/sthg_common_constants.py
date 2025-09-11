from enum import Enum


class SthgCommonConstants:
    header_x_user_id_key = "x-user-id"
    header_user_id_key = "user_id"
    header_x_request_id_key = "x-request-id"
    header_x_trace_id_key = "x-trace-id"
    header_x_guid_id_key = "x-guid"
    context_trace_id_key = "x_trace_id"
    context_request_id_key = "_x_request_id"
    context_user_id_key = "user_id"
    context_guid_id_key = "x_guid"


class SthgResourceType(Enum):
    # Ontology 类型
    OBJECT_TYPE = "object-type"
    LINK_TYPE = "link-type"
    ACTION_TYPE = "action-type"
    # Function Registry
    CODE_FUNCTION = "function"
    # Foundry
    CODE_PROJECT = "project"
    BRANCH = "branch"
    WORKFLOW = "workflow"
    FLYFLOW = "flyflow"
    PIPELINE = "pipeline"
    DATASET = "dataset"
    # Compass
    DATAEASE = "dataease"
    # 文件夹
    FOLDER = "folder"
    SPACE="space"
    PROJECT="project"