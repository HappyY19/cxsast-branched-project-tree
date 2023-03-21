# cxsast-branched-project-tree
A script to generate the tree view of the branched project, and projects never been branched.


## prerequisites:
1. install python dependency
pip install treelib

2. Run the following SQL query in SQL Server Management Studio, and save the results as 1.csv file.

SELECT [Id]
      ,[OriginalProjectId]
      ,[BranchedOnScanId]
      ,[BranchedProjectId]
      ,[Timestamp]
      ,[Status]
    FROM [CxDB].[dbo].[ProjectBranchTree]

3. Run the following SQL query in SQL Server Management Studio, and save the results as 2.csv file.

    SELECT [Name]
      ,[OpenedAt]
      ,[OpenedBy]
      ,[is_deprecated]
      ,[Owner]
      ,[Owning_Team]
      ,[PresetId]
      ,[ID]
    FROM [CxDB].[dbo].[Projects]

put 1.csv and 2.csv in the same folder as this python script


## Output:
1. branched_projects_tree.txt  (The tree view of project branches, all deleted projects on leave nodes has been removed)
2. project_without_being_branched.csv (The list of projects never been branched)

