# MobileFlowsCalls
This is a set of tools to help automate the population of the ServiceNow tenant with the appropriate users for use with the Workspace ONE UEM Mobile Flow process.  The tool takes as input a CSV file described below and builds ServiceNow users.

## CSV Layout
1. First Name
2. Last Name
3. Department
4. Mobile Phone - This will **usually** be the number of the SE or the EBC employee.  It is use for Windows Hello for Business setup so for testing purposes this is a requirement.
5. Title
6. Manager Last Name - This last name must appear in the Last Name field listed above.
