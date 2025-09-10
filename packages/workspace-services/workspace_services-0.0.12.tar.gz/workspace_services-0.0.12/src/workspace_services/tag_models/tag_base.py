from pydantic import BaseModel


class TagBase(BaseModel):
    tagging_difficulty: int = 0  # TODO: 添加难度系数机制, 获取标注员反馈
    abandon: bool = False  # TODO: 添加废弃标记机制, 获取标注员反馈
