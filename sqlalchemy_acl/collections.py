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


# parse yaml and traverse access-levels tree with DFS algorithm
class AccessLevelsParser():

    def __init__(self, path):
        self.access_levels = []
        self.config = None
        try:
            with open(path) as fp:
                import yaml
                self.config = yaml.load(fp, Loader=yaml.FullLoader)
        except FileNotFoundError:
            # TODO: change to logging
            print('ACL config file ({0}) not found, exiting...'.format(path))
            exit(1)

    def traverse(self, current, parent=None):
        current_object = AccessLevelModel(role_description=current['description'], parent=parent)
        self.access_levels.append(current_object)

        if current['children']:
            [self.traverse(child, current_object) for child in current['children']]

        return

    def get_access_levels(self):
        self.traverse(self.config['root'])
        return self.access_levels