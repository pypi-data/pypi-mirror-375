from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    last_name: str
    first_name: str
    mobile: Optional[str] = None
    username: Optional[str] = None

    @property
    def name(self) -> str:
        return f'{self.first_name} {self.last_name}'