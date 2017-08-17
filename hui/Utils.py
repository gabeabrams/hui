import sys

# Constants
M = 500

# Wildcard for filters
WILDCARD = '*'

# Helpers

## Encode/decode variable names 
# sid and gid are stored in variable names then are decoded after pulp solves the problem
NAME_PREPEND = 'membership_'
def encodeVarName(sid, gid):
    """Takes an sid and gid and creates an LP variable name"""
    return NAME_PREPEND + str(sid) + '_' + str(gid)

def decodeVarName(varName):
    """Given an LP variable name, extracts the sid and gid"""
    try:
        parts = varName.split('_')
        return (int(parts[1]), int(parts[2]))
    except IndexError:
        return None

def multAll(lst):
    """Multiplies a list of variables together"""
    if len(lst) == 0:
        return 0
    
    out = lst[0]
    for i in range(1,len(lst)):
        out *= lst[i]
    return out