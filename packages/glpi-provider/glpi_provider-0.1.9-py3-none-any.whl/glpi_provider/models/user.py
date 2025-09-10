from dataclasses import dataclass


@dataclass
class User:
    id: int
    last_name: str
    first_name: str
    mobile: str

    @property
    def name(self) -> str:
        return f'{self.first_name} {self.last_name}'