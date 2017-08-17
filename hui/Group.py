import pulp
from LPHelpers import _boolFromUpperBound

class Group:
    """A representation of a single group
    :param id: a unique identifier to be used in the algorithm
    :param info: a python dictionary/object holding information on the group, including info['size'] and info['minsize']
    """
    def __init__(self, id, info):
        self.id = id
        self.info = info

        # Extract size from info
        if 'size' in info:
            self.size = info['size']
        else:
            self.size = None
        
        # Extract minsize from info
        if 'minsize' in info:
            self.minsize = info['minsize']
        else:
            self.minsize = 0
        
        self.variables = []
        self.notInUse = None
    
    def addVar(self, var):
        """Adds a variable to this group (represents a student that could be in this group)"""
        self.variables.append(var)
    
    def genConstraints(self):
        """Generates constraints for this group that must be part of the LP problem"""
        constraints = []
        
        # Constrain size of group
        if self.size != None:
            constraints.append(sum(self.variables) <= self.size)
        
        # Impose minimum size of group
        if self.minsize != None and self.minsize != 0:
            constraints.append(sum(self.variables) >= self.minsize)
        
        # Add "not in use" variable
        (c,v) = _boolFromUpperBound(sum(self.variables), 0, name=str(self.id) + 'notinuse')
        constraints += c
        self.notInUse = v


        return constraints

    def getNotInUseVar(self):
        return self.notInUse