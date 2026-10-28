"""Testdata som delas mellan testerna. Alla konton är påhittade och finns bara i övningsbutiken."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Account:
    email: str
    password: str
    name: str


STANDARD_USER = Account("kund@example.com", "Test1234!", "Kim Kund")
OTHER_USER = Account("kund2@example.com", "Test1234!", "Robin Ring")
NEW_USER = Account("ny@example.com", "Test1234!", "Noa Ny")
LOCKED_USER = Account("last@example.com", "Test1234!", "Lo Låst")
