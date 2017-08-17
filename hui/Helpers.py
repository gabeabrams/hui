import csv as csvOperator
import re
import sys
import traceback
import string

# All these functions will become public via __init__.py

def _keepOnlyLetters(str):
  regex = re.compile('[^a-zA-Z]', re.UNICODE)
  return regex.sub('', str)
  

def _readCSV(filename):
  try:
    with open(filename) as file:
      # Read file
      csvfile = csvOperator.reader(file, delimiter=',')
      
      # Create CSV Object
      csv = {}
      csv['data'] = []
      csv['headers'] = None
      for row in csvfile:
        if (csv['headers'] == None):
          csv['headers'] = row
        else:
          csv['data'].append(row)

      return csv

  except:
    print "Couldn't read the file: " + filename + "\nError: ", sys.exc_info()[0]
    traceback.print_exc(file=sys.stdout)
    sys.exit(0)

def readCSVRoster(filename):
  csv = _readCSV(filename)

  properties = []
  for header in csv['headers']:
    header = _keepOnlyLetters(header).lower()
    properties.append(header)

  students = []
  for row in csv['data']:
    student = {}
    for i in range(len(row)):
      student[properties[i]] = row[i]
    students.append(student)

  return students

def readCSVPremadeGroups(filename, studentProperties=None):
  """studentProperties is a list of student properties in the order they appear in the CSV.
  For example, if a CSV row (each group is a row) is as follows: "Rowan Wilson, rowan@harvard.edu, 1579348, Bob Tilano, bob@harvard.edu, 57387294"
  Then the format is: fullname, email, huid, fullname, email, huid, ...
  Thus, studentProperties = ['fullname', 'email', 'huid']
  """

  csv = _readCSV(filename)
    
  # Create studentProperties if needed
  if studentProperties == None:
    studentProperties = []
    firstHeader = None
    for header in csv['headers']:
      header = _keepOnlyLetters(header).lower()
      if firstHeader == header:
        # Found beginning of repeating sequence
        break
      if firstHeader == None:
        firstHeader = header

      studentProperties.append(header)


  # Pull groups from CSV data
  groups = []
  for row in csv['data']:
    students = []

    currStudent = None
    for i in range(len(row)):
      if len(row[i].strip()) == 0:
        break
      propIndex = i % len(studentProperties)
      if propIndex == 0:
        # Just starting a new student
        currStudent = {}
      else:
        currStudent[studentProperties[propIndex]] = row[i]

      if propIndex == len(studentProperties) - 1:
        # Just finished adding properties to a student
        students.append(currStudent)

    if len(students) > 0:
      groups.append(students)

  return groups
    

