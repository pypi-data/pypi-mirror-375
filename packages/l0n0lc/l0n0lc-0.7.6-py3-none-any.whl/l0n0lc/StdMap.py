from .c基础处理 import py类型转c类型, dict初始化列表, c变量, cpp类型
from typing import Tuple, Union, List
from .通用 import toCString


class StdUnorderedMap(c变量):
    def __init__(
            self,
            初始化列表: dict初始化列表,
            名字: str, 是参数: bool) -> None:
        self.初始化列表 = 初始化列表
        super().__init__(
            f'std::unordered_map<{初始化列表.key类型}, {初始化列表.value类型}>', 名字, 是参数)

    def __getitem__(self, key):
        return f'{self}[{toCString(key)}]'

    def __setitem__(self, key, value):
        左 = f'{self}[{toCString(key)}]'
        右 = toCString(value)
        return f'{左} = {右};'
