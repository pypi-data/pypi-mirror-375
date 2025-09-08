from functools import cached_property
from wizlib.app import WizApp
from wizlib.stream_handler import StreamHandler
from wizlib.config_handler import ConfigHandler
from wizlib.ui_handler import UIHandler

from dyngle.command import DyngleCommand
from dyngle.expression import expression


class DyngleApp(WizApp):

    base = DyngleCommand
    name = 'dyngle'
    handlers = [StreamHandler, ConfigHandler, UIHandler]

    @cached_property
    def expressions(self):
        expr_texts = self.config.get('dyngle-expressions')
        if expr_texts:
            return {k: expression(t) for k, t in expr_texts.items()}
        else:
            return {}
