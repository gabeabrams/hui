import pulp
from random import shuffle
from Group import Group
from Student import Student
from DataBox import DataBox
import Utils


class GroupCreator(object):
    def __init__(self, students=None, groups=None, goalGroups=None, determinateSolution=False):
        self.students = students
        self.groups = groups
        self.goalGroups = goalGroups
        self.determinateSolution = determinateSolution

    def addStudent(self, student):
        if self.students == None:
            self.students = []
        self.students.append(student)

    def addStudents(self, students):
        """Adds students to the problem. Students should be dictionaries."""
        for s in students:
            self.addStudent(s)

    def addEmptyGroup(self, group):
        if self.groups == None:
            self.groups = []
        self.groups.append(group)

    def addEmptyGroups(self, groups):
        """Adds groups to the problem. Groups should be dictionaries. To set max size, let group['size'] = upperBound. To set min size, let group['minsize'] = lowerBound"""
        for g in groups:
            self.addEmptyGroup(g)

    def addGoalGroup(self, goalGroup):
        if self.goalGroups == None:
            self.goalGroups = []
        self.goalGroups.append(goalGroup)

    def addGoalGroups(self, goalGroups):
        for goalGroup in goalGroups:
            self.addGoalGroup(goalGroup)

    def setDeterminateSolution(self, isDeterminate):
        self.determinateSolution = isDeterminate

    def createGroups(self):
        algoResults = self._runAlgorithm(self.students, self.groups)
        return algoResults

    def _runAlgorithm(self, students, groups):
        """Puts students into groups based on sets of goals given to the algorithm.
        :param students: a list of students that will be placed into groups
        :param groups: a list of possible groups that students can be placed into
        :param goalGroups: a list of goal lists. The algorithm attempts to solve based on the first list of goals. If a set of goals cannot be achieved (they must be set to required=True), then the algorithm moves on to the next goal group.
        :param determinateSolution: boolean. If True, a random solution will be chosen from the set of optimal solutions.
        :return: solInfo or None if all goal groups were too strict. solInfo['goalGroup'] = index of goal group used. solInfo['reward'] = total reward given. solInfo['groups'] = {'info': group info, 'students': list of student infos}
        """

        # Prepare to collect logs
        logs = []

        goalGroups = self.goalGroups
        if goalGroups is None:
            goalGroups = [[]]
        determinateSolution = self.determinateSolution

        # Make sure we have enough information
        if students == None:
            raise TypeError('students must be included')
        if groups == None:
            raise TypeError('groups must be included')

        # Shuffle students and groups if randomizing the solution
        if not determinateSolution:
            shuffle(students)
            shuffle(groups)
        studentInfos = students
        groupInfos = groups

        # Make sure M is large enough
        if (len(students) > Utils.M or len(groups) > Utils.M):
            raise ValueError('You cannot have ' + str(Utils.M) + ' or more students/groups.')


        # Set up groups
        groups = []
        gidToGroupInfo = {}
        nextGID = 1
        for group in groupInfos:
            groupObj = Group(nextGID, group)
            if groupObj.size != None and groupObj.size == 0:
                # Skip groups with no room
                continue
            groups.append(groupObj)
            gidToGroupInfo[groupObj.id] = group
            nextGID += 1
            
        # Set up students
        students = []
        sidToStudentInfo = {}
        nextSID = 1
        for student in studentInfos:
            studentObj = Student(nextSID, student, groups)
            students.append(studentObj)
            sidToStudentInfo[studentObj.id] = student
            nextSID += 1
        
        # Set up data box
        dataBox = DataBox(students, groups)
        
        # Run for each set of goals until 'Optimal' is found, or return None    
        for i in range(len(goalGroups)):
            goals = goalGroups[i]
            problem = pulp.LpProblem("Group Membership Problem", pulp.LpMaximize)
            
            # Add student constraints
            failedAddingConstraints = False
            for student in students:
                constraints = student.genConstraints()
                if constraints == None:
                    failedAddingConstraints = True
                    break
                for constraint in constraints:
                    problem += constraint
            
            # Add group constraints
            for group in groups:
                constraints = group.genConstraints()
                if constraints == None:
                    failedAddingConstraints = True
                    break
                for constraint in constraints:
                    problem += constraint

            # Add goal constraints
            rewards = []
            for goal in goals:
                ret = goal.genConstraintsAndRewards(dataBox)
                if ret == None:
                    failedAddingConstraints = True
                    break
                (constraints, theseRewards) = ret
                # Add constraints to problem
                for constraint in constraints:
                    problem += constraint
                # Accumulate rewards 
                rewards += theseRewards
                    
            if failedAddingConstraints:
                logs.append("Goal group " + str(i) + " failed because constraints couldn't be interpreted. Trying next goal group...")
                continue

            
            # Objective function
            problem += sum(rewards), 'reward'
            
            # Attempt to solve
            # print problem
            problem.solve()
            
            solved = pulp.LpStatus[problem.status] == 'Optimal'
            if solved:
                logs.append("Goal group " + str(i) + " was successful.")
                output = {}
                output['groups'] = [None for _ in range(len(groups))]
                output['reward'] = pulp.value(problem.objective)
                output['goalGroup'] = i
                output['logs'] = logs
                #output = [{"students": [students], "group": groupinfo}, ...]
                for variable in problem.variables():
                    # print variable.name + ' = ' + str(variable.varValue)
                    if variable.name == '__dummy':
                        continue
                    if variable.varValue == 0:
                        continue
                    ret = Utils.decodeVarName(variable.name)
                    if ret == None:
                        continue
                    (sid,gid) = ret
                    student = sidToStudentInfo[sid]
                    group = gidToGroupInfo[gid]
                    
                    index = gid - 1
                    if output['groups'][index] == None:
                        output['groups'][index] = {}
                        output['groups'][index]['students'] = []
                        output['groups'][index]['info'] = group
                    output['groups'][index]['students'].append(student)
                # put in info for empty groups
                for group in groups:
                    gid = group.id
                    index = gid - 1
                    if output['groups'][index] == None:
                        output['groups'][index] = {'students':[],'info':group.info}
                
                return output
            else:
                logs.append("> Goal group " + str(i) + " was too strict. Trying next goal group...")
        logs.append("All goal groups were too strict. No groups could be created")

        output = {}
        output['groups'] = None
        output['Reward'] = None
        output['goalGroup'] = None
        output['logs'] = logs
        return output
