import pulp
import LPHelpers as lph
import Utils

##### Goal Interface #####
class Goal(object):
    def __init__(self, required, netReward, partialReward):
        self.required = required
        self.netReward = netReward
        self.partialReward = partialReward

    def genConstraintsAndRewards(self, dataBox):
        return ([], []) # (constraints, rewards)

##### Goal Classes #####
# For a given studentFilter and groupFilter, goal is to put all students into one of the groups (students and groups defined by filter)



class GroupFilterGoal(Goal):
    """Goal is to put all relevant students into preferable groups.
    :param studentFilter: a filter that gives the list of relevant students
    :param groupFilter: a filter that gives the list of preferable groups
    :param required: if true, this goal must be fully completed
    :param netReward: amount to be awarded if all students are placed into preferable groups
    :param partialReward: amount to be awarded for each student that is placed into a preferable group
    """
    def __init__(self, studentFilter=None, groupFilter=None, required=True, netReward=0, partialReward=0):
        Goal.__init__(self, required, netReward, partialReward)

        self.studentFilter = studentFilter
        self.groupFilter = groupFilter

    def genConstraintsAndRewards(self, dataBox):
        constraints = []
        rewards = []

        students = dataBox.filterStudents(self.studentFilter)
        groups = dataBox.filterGroups(self.groupFilter)

        if len(students) > 0:
            if len(groups) == 0:
                print "Could not find groups that match filter: " + str(groupFilter) + ". Impossible to create groups."
                return None

            allSatVars = []
            for student in students:
                variables = []
                for group in groups:
                    variables.append(student.getVar(group.id))
                # Create variable v which is 1 only if student is in one of the groups
                (c,v) = lph._boolFromLowerBound(sum(variables), 1)
                constraints += c
                # Save this variable
                allSatVars.append(v)

                # If this is required, add constraint
                if self.required:
                    constraints.append(lph._requireTrue(v))

                # Add partial reward
                (c,rvar) = lph._createRewardVar(v, self.partialReward)
                constraints += c
                rewards.append(rvar)

                
            # Create variable satistifed which is 1 only if all required students are in appropriate groups
            (c,satisfied) = lph._boolFromLowerBound(sum(allSatVars), len(students))
            constraints += c

            # Add a reward
            (c,v) = lph._createRewardVar(satisfied, self.netReward)
            constraints += c
            rewards.append(v)

        return (constraints, rewards)

# For a groupFilter, propertyName, and minSimilar, goal is for all groups to have at least minSimilar students that share the same value for propertyName. All groups means those groups matching the groupFilter
class MinSimilarGoal(Goal):
    """Goal is to get at least minSimilar similar people into each relevant group (exception: empty groups also satisfy this goal)
    :param groupFilter: filter that gives the list of relevant groups
    :param propertyName: the property name that will be used for testing comparison (for objectA and objectB, they are similar if objectA[propertyName] == objectB[propertyName])
    :param minSimilar: the minimum number of people that need to be similar in each group
    :param required: if true, this goal must be fully completed
    :param netReward: amount to be awarded if all relevant groups satisfy this goal
    :param partialReward: amount to be awarded for each relevant group that satisfies this goal
    """
    def __init__(self, groupFilter=None, propertyName=None, minSimilar=-1, required=True, netReward=0, partialReward=0):
        Goal.__init__(self, required, netReward, partialReward)

        if propertyName == None:
            raise TypeError('propertyName is required')

        self.groupFilter = groupFilter
        self.propertyName = propertyName
        self.minSimilar = minSimilar

    def genConstraintsAndRewards(self, dataBox):
        constraints = []
        rewards = []

        PLACEHOLDER = -1
        
        # Function to get self.minSimilar for specific group size
        def _getCutoff(groupSize):
            ret = PLACEHOLDER
            
            if self.minSimilar != PLACEHOLDER:
                # Look for value for this group size
                
                # If self.minSimilar is dictionary, look up group size
                if type(self.minSimilar) is dict:
                    if groupSize in self.minSimilar:
                        ret = self.minSimilar[groupSize]
                    else:
                        # group size not in dictionary
                        return None # caller should interpret this as "no restriction
                # If self.minSimilar is same for all groups (not dict), just return that
                else:
                    ret = self.minSimilar
            if ret == PLACEHOLDER:
                return groupSize
            else:
                return ret
        
        # Grab clicks (groups of students that are similar based on propertyname)
        clicks = dataBox.getStudentsWhoShareProperty(self.propertyName)
        
        # Filter groups
        groupsOfInterest = dataBox.filterGroups(self.groupFilter)

        satVariables = []
        for group in groupsOfInterest:
            groupMin = _getCutoff(group.size)
            if groupMin == None:
                # No restriction, don't continue, don't add constraints
                continue
            
            if groupMin == 0:
                print "Cannot apply min similarity constraint when minimum similar is " + str(groupMin) + ". Constraint on property " + self.propertyName
                continue

            groupVariables = []
            for i in range(len(clicks)):
                click = clicks[i]
                # Create click count var
                variables = []
                for student in click:
                    var = student.getVar(group.id)
                    variables.append(var)
                # Create variable v thats 1 only if click satisfies goal
                (c,v) = lph._boolFromLowerBound(sum(variables), groupMin)
                constraints += c
                groupVariables.append(v)

            # Get sat variable
            (c,v) = lph._boolFromLowerBound(sum(groupVariables), 1)
            constraints += c
            # Also satisfied if nobody is in the group
            (c,vsat) = lph._boolOr(v, group.getNotInUseVar())
            constraints += c
            satVariables.append(vsat)
            
            # Add partial reward
            (c,rvar) = lph._createRewardVar(vsat, self.partialReward)
            constraints += c
            rewards.append(rvar)

        # Done going through groups. Now, add sat and reward
        
        # Create variable satisfied thats 1 only if at least one sat var is true
        (c,satisfied) = lph._boolFromLowerBound(sum(satVariables), len(groupsOfInterest))
        constraints += c

        # Add constraint if required
        if self.required:
            constraints.append(lph._requireTrue(satisfied))

        # Add reward
        (c,v) = lph._createRewardVar(satisfied, self.netReward)
        constraints += c
        rewards.append(v)

        return (constraints, rewards)

# For a groupFilter, propertyName, and maxSimilar, goal is for all groups to have at most maxSimilar students that share the same value for propertyName. All groups means those groups matching the groupFilter
class MaxSimilarGoal(Goal):
    # Partial reward:
    # awarded for each group that satisfies this goal

    # Net reward:
    # awarded if all groups satisfy this goal
    """Goal is for all relevant groups to have at most maxSimilar similar people
    :param groupFilter: a filter that gives the list of relevant groups
    :param propertyName: the property name that will be used for testing comparison (for objectA and objectB, they are similar if objectA[propertyName] == objectB[propertyName])
    :param maxSimilar: the maximum number of similar people allowed in each relevant group
    :param required: if true, this goal must be fully completed
    :param netReward: amount to be awarded if all relevant groups satisfy this goal
    :param partialReward: amount to be awarded for each relevant group that satisfies this goal
    """
    def __init__(self, groupFilter=None, propertyName=None, maxSimilar=-1, required=True, netReward=0, partialReward=0):
        Goal.__init__(self, required, netReward, partialReward)

        if propertyName == None:
            raise TypeError('propertyName is required')
        if maxSimilar < 0:
            raise TypeError('maxSimilar is required and must be positive')

        self.groupFilter = groupFilter
        self.propertyName = propertyName
        self.maxSimilar = maxSimilar

    def genConstraintsAndRewards(self, dataBox):
        constraints = []
        rewards = []

        PLACEHOLDER = -1
        
        # Function to get self.maxSimilar for sepecific group size
        def _getCutoff(groupSize):
            ret = PLACEHOLDER
            
            if self.maxSimilar != PLACEHOLDER:
                # Look for value for this group size
                
                # If self.maxSimilar is dictionary, look up group size
                if type(self.maxSimilar) is dict:
                    if groupSize in self.maxSimilar:
                        ret = self.maxSimilar[groupSize]
                    else:
                        # group size not in dictionary
                        return None # caller should interpret this as "no restriction
                # If self.maxSimilar is same for all groups (not dict), just return that
                else:
                    ret = self.maxSimilar
                    
            if ret == PLACEHOLDER:
                # Replace placeholder with 1 (nobody should be similar)
                return 1
            else:
                return ret
        
        # Grab clicks (groups of students that are similar based on propertyname)
        clicks = dataBox.getStudentsWhoShareProperty(self.propertyName)
        
        # Filter groups
        groupsOfInterest = dataBox.filterGroups(self.groupFilter)

        satVariables = []
        violateVariables = []
        for group in groupsOfInterest:
            
            groupMax = _getCutoff(group.size)
            if groupMax == None:
                # No restriction, don't continue, don't add constraints
                continue
            
            if group.size != None and (groupMax > group.size or groupMax == 0):
                print "Cannot apply max similarity constraint when maximum similar is " + str(groupMax) + ". Constraint on property " + self.propertyName
                continue

            groupViolateVars = []
            for i in range(len(clicks)):
                click = clicks[i]
                # Create click count variable
                variables = []
                for student in click:
                    var = student.getVar(group.id)
                    variables.append(var)

                # Create variable v thats 1 only if click violates goal
                (c,v) = lph._boolFromLowerBound(sum(variables), groupMax + 1)
                constraints += c
                violateVariables.append(v)
                groupViolateVars.append(v)

            # Add partial reward only if none of this group violate
            (c,v) = lph._boolFromUpperBound(sum(groupViolateVars), 0)
            constraints += c
            (c,rvar) = lph._createRewardVar(v, self.partialReward)
            constraints += c
            rewards.append(rvar)

        # Done going through groups. Now, add sat and reward

        # Create variable satisfied thats 1 only if none of the violateVariables is true
        (c,satisfied) = lph._boolFromUpperBound(sum(violateVariables), 0)
        constraints += c

        # Add constraint if required
        if self.required:
            constraints.append(lph._requireTrue(satisfied))

        # Add reward
        (c,v) = lph._createRewardVar(satisfied, self.netReward)
        constraints += c
        rewards.append(v)

        return (constraints, rewards)

# For a groupFilter, groupProperty, studentFilter, and studentProperty, goal is for all students to be assigned to groups where student[studentProperty] = group[groupProperty]
class MustMatchGoal(Goal):
    """Goal where all relevant students must be placed in a relevant group where student[studentProperty] == group[groupProperty]
    :param groupFilter: a filter that gives the list of relevant groups
    :param studentFilter: a filter that gives the list of relevant students
    :param groupProperty: a property name to be used in testing match (group and student match if student[studentProperty] == group[groupProperty])
    :param studentProperty: a property name to be used in testing match (group and student match if student[studentProperty] == group[groupProperty])
    :param required: if true, this goal must be fully completed
    :param netReward: amount to be awarded if all relevant students satisfy this goal
    :param partialReward: amount to be awarded for each relevant student that satisfies this goal
    """
    def __init__(self, groupFilter=None, groupProperty=None, studentFilter=None, studentProperty=None, required=True, netReward=0, partialReward=0):
        Goal.__init__(self, required, netReward, partialReward)

        if groupProperty == None:
            raise TypeError('groupProperty must be defined')
        if studentProperty == None:
            raise TypeError('studentProperty must be defined')

        self.groupFilter = groupFilter
        self.groupProperty = groupProperty
        self.studentFilter = studentFilter
        self.studentProperty = studentProperty

    def genConstraintsAndRewards(self, dataBox):
        constraints = []
        rewards = []

        allSatVars = []
        students = dataBox.filterStudents(self.studentFilter)
        for student in students:
            if not self.studentProperty in student.info:
                continue
            groupVariables = []
            groups = dataBox.filterGroups(self.groupFilter)
            for group in groups:
                if not self.groupProperty in group.info:
                    continue

                # Skip if they don't match
                paramsMatch = (group.info[self.groupProperty] == student.info[self.studentProperty])
                wildcardIncluded = (group.info[self.groupProperty] == Utils.WILDCARD or student.info[self.studentProperty] == Utils.WILDCARD)
                if not paramsMatch and not wildcardIncluded:
                    continue

                # Yes, this is a match
                variable = student.getVar(group.id)
                groupVariables.append(variable)
            if len(groupVariables) == 0:
                continue

            # Create variable v thats true if this student satisfied match goal
            (c,v) = lph._boolFromLowerBound(sum(groupVariables), 1)
            constraints += c
            # Keep track of sat vars
            allSatVars.append(v)

            # Add constraint if required
            if self.required:
                constraints.append(lph._requireTrue(v))

            # Add partial reward
            (c,rvar) = lph._createRewardVar(v, self.partialReward)
            constraints += c
            rewards.append(rvar)

        # Create variable satisfied which is 1 only if all students satisfy the goal
        (c,satisfied) = lph._boolFromLowerBound(sum(allSatVars), len(students))
        constraints += c

        # Add a reward
        (c,v) = lph._createRewardVar(satisfied, self.netReward)
        constraints += c
        rewards.append(v)

        return (constraints, rewards)

class PodGoal(Goal):
    """Goal where each "pod" of students must be in a group together
    :param studentFilter: a filter that gives a list of students to be together in a group
    :param studentFilters: a list of filters, each of which gives a list of students to be placed together in a group
    :param required: if true, this goal must be fully completed
    :param netReward: amount to be awarded if all relevant "pods" are satisfied
    :param partialReward: amount to be awarded for each "pod" that satisfies this goal
    """
    def __init__(self, studentFilter=None, studentFilters=None, required=True, netReward=0, partialReward=0):
        Goal.__init__(self, required, netReward, partialReward)

        if studentFilter != None and studentFilters != None:
            # Both are defined
            raise TypeError('studentFilter and studentFilters can\'t both be defined')
        if studentFilter == None and studentFilters == None:
            raise TypeError('either studentFilter or studentFilters must be defined')

        if studentFilters != None:
            self.studentFilters = studentFilters
        else:
            self.studentFilters = [studentFilter]

    def genConstraintsAndRewards(self, dataBox):
        constraints = []
        rewards = []

        groups = dataBox.getGroups()

        allSatVars = []
        for studentFilter in self.studentFilters:
            students = dataBox.filterStudents(studentFilter)

            groupSatVariables = []
            for group in groups:
                groupVariables = []
                for student in students:
                    groupVariables.append(student.getVar(group.id))
                # Create variable v that is 1 only if the group of students are in this group
                (c,v) = lph._boolFromLowerBound(sum(groupVariables), len(students))
                constraints += c
                groupSatVariables.append(v)
            # groupSatVariables is a list of booleans: if one is true, the students are in the same group
            (c,v) = lph._boolFromLowerBound(sum(groupSatVariables), 1)
            constraints += c
            allSatVars.append(v)

            # Partial reward
            (c,rvar) = lph._createRewardVar(v, self.partialReward)
            constraints += c
            rewards.append(rvar)

        # Create variable that's 1 only if all selections of students are grouped together
        (c,satisfied) = lph._boolFromLowerBound(sum(allSatVars), len(self.studentFilters))
        constraints += c

        # Add constraint if required
        if self.required:
            constraints.append(lph._requireTrue(satisfied))

        # Add net reward
        (c,vreward) = lph._createRewardVar(satisfied, self.netReward)
        constraints += c
        rewards.append(vreward)

        return (constraints, rewards)