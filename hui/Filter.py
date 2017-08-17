import Utils

### Helper Functions

def _intersect(groupA, groupB):
    """Returns the intersection of groupA and groupB"""
    return [item for item in groupA if item in groupB]

def _subtract(groupA, groupB):
    """Returns groupA without elements that are also in groupB"""
    return [item for item in groupA if not item in groupB]

def _union(groupA, groupB):
    """Returns the union of groupA and groupB"""
    elems = set(groupA)
    elems.update(groupB)
    return list(elems)

### Advanced Operations

class ListHolder(object):
    def __init__(self, lst):
        self.lst = lst
    def items(self):
        return self.lst

class ItemHolder(object):
    def __init__(self, item):
        self.it = item
    def item(self):
        return self.it

class IsIn(ListHolder):
    pass

class NotIn(ListHolder):
    pass

class IsNot(ItemHolder):
    pass

class LT(ItemHolder): # Less than
    pass

class GT(ItemHolder): # Greater than
    pass

class LTE(ItemHolder): # Less than or equal to
    pass

class GTE(ItemHolder): # Greater than or equal to
    pass

### Filter Class

class Filter(object):
    """Recursive and operable filter that can be applied to objects
    :param stencil: a dictionary/object that can be applied to other objects (can be a mix of primitives and Item/ListHolders)
    """
    def __init__(self, *args):
        if len(args) == 0:
            self.stencil = None
        elif len(args) == 1:
            self.stencil = args[0]
        else:
            raise TypeError('Filter cannot be created with more than 1 argument')

        self.operation = None
        self.filters = None
        self.isLeaf = True
    
    def _set(self, filters, operation):
        """Sets this filter as a recursively defined filter (thisFilter = (filter1 * filter2) and so on)
        :param filters: child filters tuple (left, right)
        :param operation: string ("and", "or", or "sub") corresponding to the operation to apply to the left and right filter results
        """
        self.filters = filters
        self.operation = operation
        self.isLeaf = False

    def apply(self, propToValToObjects, allEntries):
        """Applies this filter to the entries provided
        :param propToValToObjects: dictionary propToValToObjects[propertyname][value] = [object1, object2, ...] where objects in the list satisfy object1[propertyname] = value
        :param allEntries: a list of all entries, unsorted and uncategorized
        """
        if self.isLeaf:
            # Leaf!
            return self._applyLeaf(propToValToObjects, allEntries)
        else:
            # Node
            (left, right) = self.filters
            leftMatches = left.apply(propToValToObjects, allEntries)
            rightMatches = right.apply(propToValToObjects, allEntries)
            matches = None
            if self.operation == 'and':
                matches = _intersect(leftMatches, rightMatches)
            elif self.operation == 'or':
                matches = _union(leftMatches, rightMatches)
            elif self.operation == 'sub':
                matches = _subtract(leftMatches, rightMatches)
            return matches
            
    
    def _applyLeaf(self, propToValToObjects, allEntries):
        """Apply this leaf using the stencil"""
        if self.stencil == None:
            return allEntries

        matches = None
        for stencilProp in self.stencil:
            stencilVal = self.stencil[stencilProp]

            # Determine the type of filtering
            vals = []
            filterByComparison = False
            invertSelection = False
            if type(stencilVal) is IsIn:
                vals = stencilVal.items()
            elif type(stencilVal) is NotIn:
                vals = stencilVal.items()
                invertSelection = True
            elif type(stencilVal) is IsNot:
                item = stencilVal.item()
                vals = [item]
                invertSelection = True
            elif type(stencilVal) is GT or type(stencilVal) is LT or type(stencilVal) is GTE or type(stencilVal) is LTE:
                filterByComparison = True
            else:
                vals = [stencilVal]

            newCandidates = []

            # FILTER BY COMPARISON
            if filterByComparison:
                # Get all people that match
                newCandidates = []
                for e in allEntries:
                    if not stencilProp in e.info:
                        # Cannot compare if no property defined
                        continue

                    # Now compare
                    val = stencilVal.item()
                    realVal = e.info[stencilProp]

                    success = False
                    if type(stencilVal) is GT:
                        success = (realVal > val)
                    elif type(stencilVal) is GTE:
                        success = (realVal >= val)
                    elif type(stencilVal) is LT:
                        success = (realVal < val)
                    elif type(stencilVal) is LTE:
                        success = (realVal <= val)

                    if success:
                        newCandidates.append(e)

            # FILTER BY VALUE(S)
            else:
                # Gather candidates
                candidates = []
                # > Add candidates that match filter
                for v in vals:
                    if not v in propToValToObjects[stencilProp]:
                        # No objects have this value
                        continue
                    candidates += propToValToObjects[stencilProp][v]
                # > Add candidates that have a wildcard
                if Utils.WILDCARD in propToValToObjects[stencilProp]:
                    candidates += propToValToObjects[stencilProp][Utils.WILDCARD]

                # Invert selection if necessary
                newCandidates = candidates
                if invertSelection:
                    newCandidates = []
                    for entry in allEntries:
                        if entry in candidates:
                            continue
                        # Was not a candidate, make it one
                        newCandidates.append(entry)

            # Merge new candidates with others
            if matches == None:
                # This is the first property
                matches = newCandidates
                continue
            # Use intersection so we can keep only those that maintain all filters
            matches = self._intersect(matches, newCandidates)

            # Stop going if we no longer have any matches
            if len(matches) == 0:
                return []

        return matches

    def __mul__(self, other):
        """Multiplies this filter with the other, returning a new filter that's recursively defined"""
        ret = Filter(None)
        ret._set((self, other), 'and')
        return ret
    
    def __add__(self, other):
        """Adds this filter with the other, returning a new filter that's recursively defined"""
        ret = Filter(None)
        ret._set((self, other), 'or')
        return ret

    def __sub__(self, other):
        """Subtracts the other from this filter, returning a new filter that's recursively defined"""
        ret = Filter(None)
        ret._set((self, other), 'sub')
        return ret
    
    def __str__(self):
        """Returns the string representation of this filter"""
        if (self.filters == None):
            # Leaf
            return str(self.stencil)
        else:
            (left, right) = self.filters
            return '(' + str(left) + ' ' + self.operation + ' ' + str(right) + ')'
            