from dataclasses import dataclass
from functools import partial
import re


PATTERN = re.compile(r'\{\{\s*([^}]+)\s*\}\}')


@dataclass
class Template:

    template: str

    def render(self, data: dict = None, expressions: dict = None) -> str:
        """Render the template with the provided data."""
        data = data if data else {}
        expressions = expressions if expressions else {}
        resolver = partial(self._resolve, data=data, expressions=expressions)
        return PATTERN.sub(resolver, self.template)

    def _resolve(self, match, *, data: dict, expressions: dict):
        """Resolve a single name/path from the template."""
        key = match.group(1).strip()
        if key in expressions:
            return expressions[key](data)
        else:
            parts = key.split('.')
            current = data
            for part in parts:
                current = current[part]
            return current
