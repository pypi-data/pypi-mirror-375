from pilot.control.impl.base_controller import BaseController

from unit import Unit


class Controller(BaseController):
    # __init__ を省略し親クラスのまま利用

    def _init_unit(self):
        # input_path は BaseController から引き継ぐ
        return Unit()
