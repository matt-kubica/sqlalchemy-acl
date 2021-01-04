from abc import ABC, abstractmethod
from .models import AccessLevelModel



class Iterator(ABC):

    @abstractmethod
    def get_next(self) -> AccessLevelModel:
        pass

    @abstractmethod
    def has_more(self) -> bool:
        pass


# iterator start at some node and iterate through all sub-nodes
# implements breadth-first-search algorithm
class TreeIterator(Iterator):

    def __init__(self, starting):
        self.queue = [starting]

    def get_next(self) -> AccessLevelModel:
        if self.has_more():
            current = self.queue.pop(0)
            self.queue.extend(current.children)
            return current

    def has_more(self) -> bool:
        if self.queue:
            return True
        return False




class IterableCollection(ABC):

    @abstractmethod
    def create_iterator(self) -> Iterator:
        pass


class AccessLevelsTree(IterableCollection):

    def __init__(self, starting_level):
        self.starting_level = starting_level

    def create_iterator(self) -> TreeIterator:
        return TreeIterator(self.starting_level)

    def subnodes_list(self) -> [AccessLevelModel]:
        subnodes, iterator = [], TreeIterator(self.starting_level)
        while True:
            current = iterator.get_next()
            if current: subnodes.append(current)
            else: break

        return subnodes
