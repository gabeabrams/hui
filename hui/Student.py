import pulp
import Utils

class Student:
    """A representation of a single student
    :param id: a unique identifier for use in the algrotihm
    :param info: a python object holding student information
    :param groups: a list of all groups (see Group.py) that are being considered by the algorithm
    """
    def __init__(self, id, info, groups):
        self.id = id
        self.info = info
    
        self.allVariables = []
        self.groupIDToVariable = {}
        
        for group in groups:
            var = pulp.LpVariable(Utils.encodeVarName(id, group.id), lowBound=0, cat='Integer')
            self.allVariables.append(var)
            self.groupIDToVariable[group.id] = var
            group.addVar(var)
        
    def getVar(self, gid):
        """Get the LP variable associated with group with id: gid"""
        var = self.groupIDToVariable[gid]
        return var
    
    def genConstraints(self):
        """Returns constraints that are required in the LP problem"""
        constraints = []
        
        # Must be in exactly one group
        constraints.append(sum(self.allVariables) == 1)
        
        return constraints