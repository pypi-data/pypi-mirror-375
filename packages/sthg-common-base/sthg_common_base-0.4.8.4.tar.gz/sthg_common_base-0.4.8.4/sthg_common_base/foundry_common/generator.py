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

class GeneratorBase:
    # ===== 通用 RID 生成函数 =====
    def generate_rid(
        self,
        resource_type: str,  # 支持SthgResourceType和str类型
        namespace: str = None,
        scope: str = None  # 新增参数，允许外部传入 scope
    ) -> str:
        """
        根据资源类型生成 RID，兼容SthgResourceType枚举和字符串

        :param resource_type: 资源类型，可以是SthgResourceType枚举或对应的字符串值
        :param namespace: 可选命名空间，默认 main
        :param scope: 可选 scope，如果传入则使用，否则自动匹配 ResourcePool
        :return: ri.xxx.main.xxx.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        """
        # 处理资源类型，将字符串转换为对应的枚举
        if isinstance(resource_type, str):
            try:
                resource_type = SthgResourceType(resource_type)
                resource_type = resource_type.value
            except ValueError:
                if scope is None:
                    raise ValueError(f"自定义类型必须指定scope")
        elif not isinstance(resource_type, SthgResourceType):
            raise TypeError("resource_type 必须是 SthgResourceType 枚举或字符串")

        found_scope = scope
        if not found_scope:
            for pool in ResourcePool:
                pool_scope, types = pool.value
                if resource_type in [t.value for t in types]:
                    found_scope = pool_scope
                    break

        if not found_scope:
            valid_types = [t.value for pool in ResourcePool for t in pool.value[1]]
            raise ValueError(
                f"未知 resource_type '{resource_type}'，可选类型: {valid_types}"
            )
        if not namespace:
            namespace = "main"
        rid_uuid = str(uuid.uuid4())
        return f"ri.{found_scope.lower()}.{namespace.lower()}.{resource_type.lower()}.{rid_uuid}"
