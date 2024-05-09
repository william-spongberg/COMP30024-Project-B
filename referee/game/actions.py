# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from dataclasses import dataclass

from .coord import Coord


@dataclass(frozen=True, slots=True)
class PlaceAction():
    """
    A dataclass representing a "place action", where four board coordinates
    denote the placement of a tetromino piece.
    """
    c1: Coord
    c2: Coord
    c3: Coord
    c4: Coord

    @property
    def coords(self) -> list[Coord]:
        try:
            return list([self.c1, self.c2, self.c3, self.c4])
        except:
            raise AttributeError("Invalid coords")

    def __str__(self) -> str:
        try:
            return f"PLACE({self.c1}, {self.c2}, {self.c3}, {self.c4})"
        except:
            return f"PLACE(<invalid coords>)"
        
    def __eq__(self, value: 'PlaceAction') -> bool:
        return set(self.coords) == set(value.coords)


Action = PlaceAction
