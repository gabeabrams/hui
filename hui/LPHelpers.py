import pulp

# LINEAR OPTIMIZATION HELPERS
# All return (c,v) LPConstraint[] c and LPVariable v (constraints required to maintain state of variable)
# M should be a large number (>= max value of variable)

M = 19999.0

# From http://cs.stackexchange.com/questions/71091/express-a-complex-if-statement-to-linear-programming?rq=1
global nextVarID
nextVarID = 1

def _boolFromLowerBound(variable, lowBound, name=None):
    """Creates a variable: v is 1 if variable >= lowBound
    :return: (c,v) where c is a list of constraints required to maintain the state of the variable, and v is the variable of interest
    """
    constraints = []

    global nextVarID
    if name == None:
        name = 'low' + str(nextVarID)
        nextVarID += 1
    
    # variable 1 if lowBound <= variable holds
    boolVar = pulp.LpVariable(name, lowBound=0, cat='Integer')

    constraints.append(boolVar * M <= variable - lowBound + M)
    constraints.append(boolVar * M >= variable - lowBound + 1)
    constraints.append(boolVar <= 1)

    return (constraints, boolVar)

def _boolFromUpperBound(variable, upperBound, name=None):
    """Creates a variable: v is 1 if variable <= lowBound
    :return: (c,v) where c is a list of constraints required to maintain the state of the variable, and v is the variable of interest
    """
    constraints = []

    global nextVarID
    if name == None:
        name = 'name' + str(nextVarID)
        nextVarID += 1

    # variable 1 if upperBound >= variable holds
    boolVar = pulp.LpVariable(name, lowBound=0, cat='Integer')

    constraints.append(boolVar * M <= upperBound + M - variable)
    constraints.append(boolVar * M >= upperBound - variable + 1)
    constraints.append(boolVar <= 1)

    return (constraints, boolVar)

def _boolAnd(varA, varB, name=None):
    """Creates a variable: v is 1 if varA == varB == 1
    :return: (c,v) where c is a list of constraints required to maintain the state of the variable, and v is the variable of interest
    """
    constraints = []

    global nextVarID
    if name == None:
        name = 'and' + str(nextVarID)
        nextVarID += 1

    # variable 1 if varA == 1 and varB == 1
    boolVar = pulp.LpVariable(name, lowBound=0, cat='Integer')

    constraints.append(0 <= varA + varB - 2 * boolVar)
    constraints.append(varA + varB - 2 * boolVar <= 1)

    return (constraints, boolVar)

def _boolOr(varA, varB, name=None):
    """Creates a variable: v is 1 if varA == 1or varB == 1
    :return: (c,v) where c is a list of constraints required to maintain the state of the variable, and v is the variable of interest
    """
    constraints = []

    global nextVarID
    if name == None:
        name = 'or' + str(nextVarID)
        nextVarID += 1

    # variable 1 if varA == 1 and varB == 1
    boolVar = pulp.LpVariable(name, lowBound=0, cat='Integer')
    constraints.append(boolVar <= varA + varB)
    constraints.append(boolVar * 2 >= varA + varB)

    return (constraints, boolVar)



def _requireTrue(variable):
    """Creates a constraint that requires that variable == True
    :return: constraint
    """
    return variable >= 1

def _requireFalse(variable):
    """Creates a constraint that requires that variable == False
    :return: constraint
    """
    return variable <= 0

def _createRewardVar(boolean, reward, name=None):
    """Creates a new variable that should be added to the rewards function
    :return: (c,v) where c is a list of constraints and v = boolean ? reward : 0
    """
    global nextVarID
    if name == None:
        name = 'reward' + str(nextVarID)
        nextVarID += 1

    rewardVar = pulp.LpVariable(name, lowBound=0, cat='Integer')

    constraints = [rewardVar == reward * boolean]
    return (constraints, rewardVar)