import re

class JavaCobolField:
    def __init__(self, level, name, pic=None, length=0, decimal=False, comp3=False,
                 default=None, comment="", occurs_count=0, redefines=None):
        self.level = level
        self.name = name
        self.pic = pic
        self.length = length
        self.decimal = decimal
        self.comp3 = comp3
        self.default = default
        self.comment = comment
        self.occurs_count = occurs_count
        self.redefines = redefines
        self.children = []
        self.offset_in_parent = 0

    def __repr__(self):
        return (f'CobolField(level={self.level}, name="{self.name}", pic="{self.pic}", length={self.length}, default="{self.default}"'
                f'occurs_count={self.occurs_count}, redefines={self.redefines}, children={len(self.children)}, '
                f'offset={self.offset_in_parent})')


