from abc import ABC, abstractmethod


class Node(ABC):
    ''' Base class for the nodes of the parse tree. '''
    _type = None

    @abstractmethod
    def validate(self, scope):
        pass

    @abstractmethod
    def generate(self, builder, scope):
        pass

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, typ):
        self._type = typ
