from abc import ABC, abstractmethod
from .models import AccessLevelModel

class Iterator(ABC):

    @abstractmethod
    def get_next(self) -> AccessLevelModel:
        pass

    @abstractmethod
    def has_more(self) -> bool:
        pass


class TreeIterator(Iterator):

    def __init__(self, tree, starting):
        self.current = starting
        self.tree = tree

    def get_next(self) -> AccessLevelModel:
        pass

    def has_more(self) -> bool:
        pass



class IterableCollection(ABC):

    @abstractmethod
    def create_iterator(self) -> Iterator:
        pass


class AccessLevelsTree(IterableCollection):

    def __init__(self, root_level):
        self.root_level = root_level

    def create_iterator(self) -> Iterator:
        pass

