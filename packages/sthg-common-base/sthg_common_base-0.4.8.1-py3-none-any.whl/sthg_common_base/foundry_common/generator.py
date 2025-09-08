"""
@Author  ：duomei
@File    ：generator.py
@Time    ：2025/9/8 16:46
"""
import uuid
from enum import Enum

from sthg_common_base.utils.sthg_common_constants import SthgResourceType


# ===== 定义 ResourcePool 枚举，每个值是 (scope, resource_type 枚举列表) =====
class ResourcePool(Enum):
    ONTOLOGY = ("ontology", [SthgResourceType.OBJECT_TYPE, SthgResourceType.LINK_TYPE, SthgResourceType.ACTION_TYPE])
    FUNCTION = ("function-registry", [SthgResourceType.CODE_FUNCTION])
    FOUNDRY = ("foundry", [
        SthgResourceType.CODE_PROJECT, SthgResourceType.BRANCH, SthgResourceType.WORKFLOW,
        SthgResourceType.FLYFLOW, SthgResourceType.PIPELINE, SthgResourceType.DATASET
    ])
    COMPASS = ("compass", [SthgResourceType.DATAEASE, SthgResourceType.FOLDER])

# ===== 通用 RID 生成函数 =====
def GenerateRid(resource_type: SthgResourceType, namespace: str = "main") -> str:
    """
    根据 SthgResourceType 枚举生成 RID，scope 根据 ResourcePool 自动匹配
    """
    found_scope = None
    for pool in ResourcePool:
        scope, types = pool.value
        if resource_type in types:
            found_scope = scope
            break

    if not found_scope:
        valid_types = [t.value for pool in ResourcePool for t in pool.value[1]]
        raise ValueError(f"未知 resource_type '{resource_type}'，可选类型: {valid_types}")

    rid_uuid = str(uuid.uuid4())
    return f"ri.{found_scope}.{namespace}.{resource_type.value}.{rid_uuid}"


