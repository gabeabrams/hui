#hui – Heuristic Unification Instrument
If you're curious, "hui" means "to unite" in Hawaiian.


## Guide

### 1. Set Up the Problem

You can either set up the problem in the constructor...

```py
from hui import *
gc = GroupCreator(students=[...], groups=[...], goalGroups=[...], determinateSolution=True)
```

...or individually define parts of the problem as follows:


#### a. Make a Group Creator

```py
from hui import *
gc = GroupCreator()
```

#### b. Add Students

```py
gc.addStudent({"name":"ben", "gender": "M", "loc": "campus", "failing": True})
gc.addStudents([{"name":"lisa", "loc": "offcampus"}, ...])
```

Student objects can be anything you want.

#### c. Add Empty Groups

```py
gc.addEmptyGroup({"size": 4, "name": "sharks"})
gc.addEmptyGroups({"size": 4, "minsize": 2, "name": "turtles"})
```

Define a group's maximum size by adding a property: group['size']. Default: unlimited.<br>
Define a group's minimum size by adding a property: group['minsize']. Default: 0.

#### d. Turn On/Off Randomization

By default, solutions are randomized if possible. To turn this off, do this:

```py
gc.setDeterminateSolution(True)
```

#### e. Add Groups of Goals (problem constraints)

```py
gc.addGoalGroup(goalgroup0)
gc.addGoalGroups([goalgroup1, goalgroup2, ...])
```

The algorithm takes a list of goal groups `[goalgroup0, goalgroup1, ...]`. Each goal group is a set of constraints (e.g., everyone should have the same age). The algorithm will attempt to create groups with the constraints in `goalgroup0`. If groups cannot be created, the algorithm will try goalgroup1, then goalgroup2, etc.

_Note: you can also assign rewards to each goal. However, keep in mind that rewards greatly complicate the problem and might make computation time prohibitive. If you have complex constraints, we recommend creating many goal groups with no rewards._

See below for a list of types of constraints that can be applied.

#### GroupFilterGoal
Applies a Filter on all students to get the list of students affected by this goal. Then applies another Filter on all groups to get a list of acceptable groups. This goal aims to put filtered students into one of the groups that match the group filter. Filters are defined in the following section.

Example use case: all students with `diet="vegetarian"` should go into groups with `meal="lasagna"`.

```py
GroupFilterGoal(studentFilter=Filter({"diet": "vegetarian"}), groupFilter=Filter({"meal": "lasagna"})
```

###### Parameters:
*studentFilter* (niu.Filter) – Filter that's applied to find the students affected by this goal. Optional: if not included, all students will be included in this goal.

*groupFilter* (niu.Filter) – Filter that's applied to find the list of preferred groups. Optional: if not included, all groups will be included in this goal.

*netReward* (number) – Awarded if all filtered students are placed into preferred groups. Default: 0.

*partialReward* (number) – Awarded for each filtered student that's placed into a preferred group. Default: 0.

*required* (boolean) – Requires that this goal be completely met, otherwise algorithm will fail and move to the next goal group. Default: True.

#### MinSimilarGoal
For a given `groupFilter`, `propertyName`, and `minSimilar`: applies `groupFilter` to get the list of groups affected by this goal. For affected groups, requires that at least `minSimilar` students share the same value for `propertyName`.

Example use case: for groups where `type="studytogether"`, at least 3 of the students should have the same value for property `location`.

```python
MinSimilarGoal(groupFilter=Filter({"type": "studytogether"}), propertyName="location", minSimilar=3)
```

###### Parameters:
*groupFilter* (niu.Filter) – Filter that's applied to find the list of groups affected by this goal. Optional: if not included, all groups will be included in this goal.

*propertyName* (string) – The property name that will be used to define similarity.

*minSimilar* (number or dict) – If number, this value applies to all groups in groupFilter. If dict (group size ==> minSimilar), uses group size to look up the minSimilar value. If the resulting value of this process is -1, the group size will be used instead of -1 (the entire group must be similar).

*netReward* (number) – awarded if all groups fit this goal. Default: 0.

*partialReward* (number) – awarded for each group that fits this goal. Default: 0.

*required* (boolean) – requires that this goal be completely met, otherwise algorithm will fail and move to the next goal group. Default: True.

#### MaxSimilarGoal
For a given `groupFilter`, `propertyName`, and `maxSimilar`: applies `groupFilter` to get the list of groups affected by this goal. For affected groups, requires that at most `maxSimilar` students share the same value for `propertyName`.

Example use case: for groups where `type="diversitymeeting"`, at most 2 students can have the same value for property `firstlanguage`.

```python
MaxSimilarGoal(groupFilter=Filter({"type": "diversitymeeting"}), propertyName="firstlanguage", maxSimilar=2)
```

###### Parameters:
*groupFilter* (niu.Filter) – Filter that's applied to find the list of groups affected by this goal. Optional: if not included, all groups will be included in this goal.

*propertyName* (string) – The property name that will be used to define similarity.

*maxSimilar* (number or dict) – If number, this value applies to all groups in groupFilter. If dict (group size ==> minSimilar), uses group size to look up the maxSimilar value. If the resulting value of this process is -1, then 1 will be used instead (the entire group must be diverse).

*netReward* (number) – Awarded if all groups fit this goal. Default: 0.

*partialReward* (number) – Awarded for each group that fits this goal. Default: 0.

*required* (boolean) – Requires that this goal be completely met, otherwise algorithm will fail and move to the next goal group. Default: True.

#### MustMatchGoal
For a given `groupFilter`, `groupProperty`, `studentFilter`, and `studentProperty`, for students and groups that match those filters, the goal is for all students to be assigned to groups where student[studentProperty] = group[groupProperty]. If the student does not have a value for studentProperty, it is unaffected by this goal. If a group does not have a value for groupProperty, the equality above will evaluate to False (no students with studentProperty defined will match with this group).

Example use case: students should be placed into a group that matches their favorite topic (`student["favoriteTopic"] = group["topic"]`).

```python
MinSimilarGoal(groupProperty="topic", studentProperty="favoritetopic")
```

###### Parameters:

*groupFilter* (niu.Filter) – Filter that's applied to find the list of groups affected by this goal. Optional: if not included, all groups will be included in this goal.

*groupProperty* (string) – Property that's used to extract the comparable value from groups.

*studentFilter* (niu.Filter) – Filter that's applied to find the list of students affected by this goal. Optional: if not included, all students will be included in this goal.

*studentProperty* (string) – Property that's used to extract the comparable value from students.

*netReward* (number) – Awarded if all students are placed into matching groups. Default: 0.

*partialReward* (number) – Awarded for each student that is placed into a matching goal. Default: 0.

*required* (boolean) – Requires that this goal be completely met, otherwise algorithm will fail and move to the next goal group. Default: True.

#### PodGoal
For a given `studentFilter` or `studentFilters`, the goal is to place all students matched by (each) filter into the same group.

Example use case 1: graduate students should be placed together: all students that match Filter({"status": "graduate-student"}) are placed together.

```python
PodGoal(studentFilter=Filter({"status": "graduate-student"}))
```

###### Parameters:

*studentFilter* (niu.Filter) – Filter that's applied to all students. The goal is to put all matching students into the same group.

*studentFilters* (niu.Filter) – Filters that are applied to all students. For each filter, the goal is to put all matching students into the same group.

**Note:** Either `studentFilter` or `studentFilters` must be included.

*netReward* (number) – Awarded if all filters satisfy the goal (for each filter, those matching students are in the same group). Default: 0.

*partialReward* (number) – Awarded for each filter that satisfies the goal (for each filter, if those matching students are in the same group, award partialReward). Default: 0.

*required* (boolean) – Requires that this goal be completely met, otherwise algorithm will fail and move to the next goal group. Default: True.

### 2. Run algorithm

```py
groupData = gc.createGroups()
```

### 3. Interpret results

An object will be returned:

```py
{
	goalGroup: <goal group index used to create the groups>,
	reward: <total reward for this solution>,
	logs: [<log string>, ...],
	groups: [
		{
			info: <group info object>,
			students: [<student>, ...]
		}, ...
	]
}
```

If `goalGroup=None`, no groups could be formed given the goalGroups.

<hr>

## Filter Class

### Creating a filter

`Filter(filterDef)`

Where `filterDef` is a dictionary. When applied, the filter only allows objects that match filterDef. This is much like a JSON query in a NoSQL database like Mongo.

Example:

```py
filterDef = {"age": 10, "year": "freshman"}
```

when applied to:

```py
students = [
  {"name": "Bob", "age": 52}
  {"name": "Lelani", "age": 10, "year": "freshman"},
  {"name": "Kekoa", "age": 10, "year": "sophomore"}
 ]
```

would produce:  

```py
childProdigies = [{"name": "Lelani", "age": 10, "year": "freshman"}]
```

### Combining filters

You can combine filters using two operations: "or", "and" that are defined using simple mathematical operations. There is no limit to the recursive complexity of the operations you perform. However, + and * are defined only on Filters (no division, powers, constant multipliers, etc).

Use **Add (+)** to perform the "or" operation.

Use **Multiply (*)** to perform the "and" operation.

Use **Subtract (-)** to perform the "subtract" operation where FilterA - FilterB means: find elements that match FilterA but don't match FilterB.

Example:<br>
You have four filters that we need to combine in order to find only people who are allowed to view a restricted movie:

```py
isAdult = Filter({"type": "adult"})
isTeen = Filter({"type": "teen"})
hasPermission = Filter({"permissionGranted": True})
inBanned = Filter({"banned": True})
```

We can construct:

```py
canViewMovieFilter = isAdult + (isTeen * hasPermission) - isBanned
```

...which can be interpreted as: each person can be an adult **or** can be a teen **and** have permission, with the exception of banned people who cannot attend no matter what.

### Special Comparisons

You can create complex filters with a few extra types of comparisons:

**IsIn(list)** – filter keeps entries where `entry[prop] in list`  
Example: keep those studying sciences. `Filter({"field": IsIn(["physics", "chemistry", ...
)})`

**NotIn(list)** – filter keeps entries where `not entry[prop] in list`  
Example: keep those not studying physics or chemistry. `Filter({"field": NotIn(["physics", "chemistry"])})`

**IsNot(value)** – filter keeps entries where `entry[prop] != value`  
Example: keep those who aren't 48in tall. `Filter({"height": IsNot(48)})`

**GT(value)** – filter keeps entries where `entry[prop] > value`  
Example: keep those who are taller than 48in. `Filter({"height": GT(48)})`

**GTE(value)** – filter keeps entries where `entry[prop] >= value`  
Example: keep those who are at least 48in tall. `Filter({"height": GTE(48)})`

**LT(value)** – filter keeps entries where `entry[prop] < value`  
Example: keep those who are shorter than 48in. `Filter({"height": LT(48)})`

**LTE(value)** – filter keeps entries where `entry[prop] <= value`  
Example: keep those who are 48in or shorter. `Filter({"height": LTE(48)})`

Examples use case: we need a filter that will only keep students who are teens. Here are a few ways of doing this (age is an integer, agegroup is in ["kid", "teen", "adult"]):

```py
teens = Filter({"age": IsIn([13,14,15,16,17,18,19])})
teens = Filter({"agegroup": NotIn(["kid", "adult"])})
teens = Filter({"agegroup": IsNot("kid")}) * Filter({"agegroup": IsNot("adult")})
teens = Filter({"age": GT(12)}) * Filter({"age": LT(20)})
teens = Filter({"age": GTE(13)}) * Filter({"age": LTE(19)})
```
### Wildcards
To include a wildcard value in an object, set a value to `"*"`.

Example: a student likes all topics of study

```
student = Student({"name": "Jan", "topic": "*"})
```

