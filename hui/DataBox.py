class DataBox:
    """An object that intelligently holds all students and groups is a queryable fashion"""
    def __init__(self, students, groups):
        self.allStudents = students
        self.allGroups = groups
        
        self.groupsByProp = {}
        for group in groups:
            for prop in group.info:
                val = group.info[prop]
                
                if not prop in self.groupsByProp:
                    self.groupsByProp[prop] = {}
                if not val in self.groupsByProp[prop]:
                    self.groupsByProp[prop][val] = []
                self.groupsByProp[prop][val].append(group)
        
        self.studentsByProp = {}
        for student in students:
            info = student.info

            for prop in info:
                val = info[prop]
                
                if not prop in self.studentsByProp:
                    self.studentsByProp[prop] = {}
                if not val in self.studentsByProp[prop]:
                    self.studentsByProp[prop][val] = []
                self.studentsByProp[prop][val].append(student)
        
        
    def getStudents(self):
        """Get all students"""
        return self.allStudents

    def getGroups(self):
        """Get all groups"""
        return self.allGroups
    
    def _filter(self, filter, mapping, allEntries):
        if (filter == None):
            return allEntries

        return filter.apply(mapping, allEntries)

    def filterStudents(self, filter):
        """Apply a filter to all students"""
        return self._filter(filter, self.studentsByProp, self.allStudents)

    def filterGroups(self, filter):
        """Apply a filter to all groups"""
        return self._filter(filter, self.groupsByProp, self.allGroups)
    
    def getStudentsWhoShareProperty(self, propertyname):
        """Returns a list of arrays where each array contains students that have the same value for that property"""
        
        out = []
        
        for val in self.studentsByProp[propertyname]:    
            out.append(self.studentsByProp[propertyname][val])
            
        return out