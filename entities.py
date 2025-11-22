"""
作者：yanhuang2486
entities.py
-----------
实体定义模块。

该模块定义了应用中使用的核心数据实体：`User`、`Item`、`ItemType`、`Demand`、`Application`。
每个实体提供 `to_dict()` 和 `from_dict()` 方法用于在内存对象与磁盘 JSON 之间序列化/反序列化。

模块级说明（全局/输入/输出）：
- 输入数据来源：上层控制器或 GUI 将以基本 Python 类型（例如字符串、列表等）构造这些实体。
- 输出数据：实体的 `to_dict()` 返回可序列化的字典，可写入 JSON；`from_dict()` 接受字典并返回实体对象。
- 入口参数：每个类的构造函数参数即为创建实体所需的入口参数，均在类 docstring 中注明含义和类型。

注：本文件不直接操作文件系统，文件读写由 `controllers.DataManager` 负责调用这些实体的序列化方法。
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any

class User:
    """用户实体。

    构造参数（入口参数）：
    - user_id: 唯一标识字符串（通常使用 UUID）
    - username: 登录名/显示名
    - password: 密码（明文存储，注意安全性；如需生产应加密）
    - contact_info: 联系方式（电话或微信等）
    - role: 角色字符串（例如 '普通用户' 或 '管理员'），默认 '普通用户'

    to_dict() 输出：返回包含上述字段的字典，适合写入 JSON。
    from_dict() 输入：接受字典并返回 `User` 实例（用于读取 JSON 后恢复对象）。
    """
    def __init__(self, user_id: str, username: str, password: str, contact_info: str, role: str = "普通用户"):
        # 唯一标识
        self.user_id = user_id
        # 登录名/用户名
        self.username = username
        # 密码（当前实现为明文字段）
        self.password = password
        # 联系方式
        self.contact_info = contact_info
        # 用户角色
        self.role = role

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。

        返回: dict 包含 user_id, username, password, contact_info, role
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password": self.password,
            "contact_info": self.contact_info,
            "role": self.role
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典反序列化为 User 对象。

        参数: data - 包含用户字段的字典（通常来自 JSON 解析）
        返回: User 实例
        """
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            password=data["password"],
            contact_info=data["contact_info"],
            role=data.get("role", "普通用户")
        )

class Item:
    """物品实体。

    构造参数（入口参数）：
    - item_id: 物品唯一 id（UUID）
    - item_name: 物品名称
    - description: 物品描述（当前实现中用于存放属性前缀 + 详细描述）
    - item_type: 物品类型名称（例如 '书籍'）
    - contact_info: 发布者联系方式
    - owner_id: 发布者 user_id
    - image: 可选图片路径或标识
    - status: 状态字符串，例如 '已发布'、'已下架'

    to_dict(): 返回可序列化字典，包含 create_time 字段（字符串）。
    from_dict(): 接受字典并返回 Item 实例，会恢复 create_time（若缺失则使用当前时间）。
    """
    def __init__(self, item_id: str, item_name: str, description: str, item_type: str, 
                 contact_info: str, owner_id: str, image: str = "", status: str = "已发布"):
        self.item_id = item_id
        self.item_name = item_name
        # description 字段可能包含属性序列化前缀（例如 '属性: 作者=张三; 出版社=xx'）
        self.description = description
        self.item_type = item_type
        self.image = image
        self.contact_info = contact_info
        self.status = status
        self.owner_id = owner_id
        # create_time 记录为字符串，格式 "%Y-%m-%d %H:%M:%S"
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典，供写入 JSON 使用。

        返回字典包含 item_id, item_name, description, item_type, image, contact_info, status, owner_id, create_time
        """
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "description": self.description,
            "item_type": self.item_type,
            "image": self.image,
            "contact_info": self.contact_info,
            "status": self.status,
            "owner_id": self.owner_id,
            "create_time": self.create_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """从字典恢复 Item 实例。

        参数: data（通常从 JSON 解析得到的字典）
        返回: Item 实例（create_time 若存在则恢复，否则设置为当前时间）
        """
        item = cls(
            item_id=data["item_id"],
            item_name=data["item_name"],
            description=data["description"],
            item_type=data["item_type"],
            contact_info=data["contact_info"],
            owner_id=data["owner_id"],
            image=data.get("image", ""),
            status=data.get("status", "已发布")
        )
        item.create_time = data.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return item

class ItemType:
    """物品类型实体。

    表示一个可选的物品类型及其属性名列表，例如类型 '书籍' 的 attributes 可能为 ['作者', '出版社', 'ISBN']。

    构造参数：type_id（类型 id）、type_name（类型名称）、attributes（属性名列表）。
    to_dict()/from_dict() 用于在磁盘 JSON 与内存对象之间转换。
    """
    def __init__(self, type_id: str, type_name: str, attributes: List[str]):
        self.type_id = type_id
        self.type_name = type_name
        # 属性名列表，按顺序显示输入框或拼接到 description 中
        self.attributes = attributes

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典：包含 type_id、type_name、attributes"""
        return {
            "type_id": self.type_id,
            "type_name": self.type_name,
            "attributes": self.attributes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemType':
        """从字典恢复 ItemType 实例。"""
        return cls(
            type_id=data["type_id"],
            type_name=data["type_name"],
            attributes=data["attributes"]
        )

class Demand:
    """需求实体。

    构造参数：demand_id（id）、demand_type（需求类型）、description（描述）、publisher_id（发布者 id）。
    create_time 在构造时生成或从字典恢复。
    """
    def __init__(self, demand_id: str, demand_type: str, description: str, publisher_id: str):
        self.demand_id = demand_id
        self.demand_type = demand_type
        self.description = description
        self.publisher_id = publisher_id
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典，包含 create_time。"""
        return {
            "demand_id": self.demand_id,
            "demand_type": self.demand_type,
            "description": self.description,
            "publisher_id": self.publisher_id,
            "create_time": self.create_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Demand':
        """从字典恢复 Demand 实例。"""
        demand = cls(
            demand_id=data["demand_id"],
            demand_type=data["demand_type"],
            description=data["description"],
            publisher_id=data["publisher_id"]
        )
        demand.create_time = data.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return demand

class Application:
    """申请记录实体（用户向管理员提交的申请）。

    构造参数：application_id, app_type（例如 '成为管理员'）、content（申请内容）、applicant_id（申请人 id）、app_status（默认 '待处理'）。
    to_dict()/from_dict() 用于持久化与恢复。
    """
    def __init__(self, application_id: str, app_type: str, content: str, applicant_id: str, app_status: str = "待处理"):
        self.application_id = application_id
        self.app_type = app_type
        self.content = content
        self.app_status = app_status
        self.applicant_id = applicant_id
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典，包含 create_time 和当前状态。"""
        return {
            "application_id": self.application_id,
            "app_type": self.app_type,
            "content": self.content,
            "app_status": self.app_status,
            "applicant_id": self.applicant_id,
            "create_time": self.create_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Application':
        """从字典恢复 Application 实例（用于从 JSON 恢复）。"""
        application = cls(
            application_id=data["application_id"],
            app_type=data["app_type"],
            content=data["content"],
            applicant_id=data["applicant_id"],
            app_status=data.get("app_status", "待处理")
        )
        application.create_time = data.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return application