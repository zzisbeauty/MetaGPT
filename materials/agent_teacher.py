from typing import Dict
from datetime import datetime


from metagpt.roles.role import Role, RoleReactMode
from metagpt.actions.write_tutorial import WriteContent, WriteDirectory

from metagpt.logs import logger
from metagpt.const import TUTORIAL_PATH
from metagpt.schema import Message
from metagpt.utils.file import File


# 定义角色类
# TutorialAssistant 角色助手，输入一句话生成一个markdown格式的教程文档
class TutorialAssistant(Role):
    ...
    """Tutorial assistant, input one sentence to generate a tutorial document in markup format.
    Args:
        name: The name of the role.
        profile: The role profile description.
        goal: The goal of the role.
        constraints: Constraints or requirements for the role.
    """

    def __init__(self, 
                 name: str = "Stitch",
                 profile: str = "Tutorial Assistant",
                 goal: str = "Generate tutorial documents",
                 constraints: str = "Strictly follow Markdown's syntax, with neat and standardized layout",
                 language: str = "Chinese",):
        super().__init__(name=name, profile=profile, goal=goal, constraints=constraints, language=language)
        self.set_actions([WriteDirectory(language=self.language)]) # 动作
        self.topic: str = "" # 主题
        self.main_title: str = ""
        self.total_content: str = ""
        self.language: str = language
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)