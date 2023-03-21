"""
prerequisites:
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


Output:
1. branched_projects_tree.txt  (The tree view of project branches, all deleted projects on leave nodes has been removed)
2. project_without_being_branched.csv (The list of projects never been branched)

"""
import os
import csv
from treelib import Tree


def get_branch_project_from_csv(file_name):
    """
    read from CSV file, get branched projects information
    :param file_name:
    :return:
    """
    with open(file_name, encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        return [{
            "Id": int(row[0]),
            "OriginalProjectId": int(row[1]),
            "BranchedOnScanId": int(row[2]),
            "BranchedProjectId": int(row[3]),
            "Timestamp": row[4],
            "Status": row[5]
        } for row in reader]


def get_projects_from_csv(file_name):
    """
    read from CSV file, get all projects information
    :param file_name:
    :return:
    """
    with open(file_name, encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        projects = {}
        for row in reader:
            projects[int(row[7])] = {
                "Name": row[0],
                "OpenedAt": row[1],
                "OpenedBy": row[2],
                "is_deprecated": row[3],
                "Owner": row[4],
                "Owning_Team": row[5],
                "PresetId": int(row[6]),
                "ID": int(row[7]),
            }
        return projects


def convert_project_dict_to_tag(project):
    """

    :param project: dict
    :return:
    """
    return ", ".join([f"{key}: {value}" for key, value in project.items()])


def get_project_without_being_branched(branch_list, projects_dict):
    """

    :param branch_list: a list, which has all the projects being branched
    :param projects_dict: a dict, which has all original projects information
    :return:
    """
    # collect all the project id from branch project table
    project_branch_id_list = []
    for item in branch_list:
        project_branch_id_list.append(item.get("OriginalProjectId"))
        project_branch_id_list.append(item.get("BranchedProjectId"))
    unique_ids_in_branch_project_table = set(project_branch_id_list)
    # collect all the project id from projects table
    unique_ids_in_projects_table = set([item for item in projects_dict.keys()])
    # use set diff to find out the projects not being branched
    project_id_without_being_branched = unique_ids_in_projects_table.difference(unique_ids_in_branch_project_table)
    # sort the projects by project id
    projects_without_being_branched = sorted([int(item) for item in project_id_without_being_branched])
    with open("project_without_being_branched.csv", "w", newline='') as a_file:
        fieldnames = ["Name", "OpenedAt", "OpenedBy", "is_deprecated", "Owner", "Owning_Team", "PresetId", "ID"]
        csv_writer = csv.DictWriter(a_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for project_id in projects_without_being_branched:
            project = projects_dict.get(project_id)
            is_deprecated = project.get("is_deprecated")
            # ignore the projects that been deleted
            if is_deprecated == '1':
                continue
            csv_writer.writerow(project)


def get_tree(branch_list, projects_dict):
    """

   :param branch_list: a list, which has all the projects being branched
   :param projects_dict: a dict, which has all the original projects
   :return:
   """
    tree = Tree()
    tree.create_node(tag="Root", identifier="root")
    new_leave_nodes = set()
    for branched_project in branch_list:
        original_project_id = branched_project.get("OriginalProjectId")
        branched_project_id = branched_project.get("BranchedProjectId")
        if original_project_id not in new_leave_nodes:
            tree.create_node(
                tag=convert_project_dict_to_tag(projects_dict.get(original_project_id)),
                identifier=original_project_id,
                parent='root',
            )
            tree.create_node(
                tag=convert_project_dict_to_tag(projects_dict.get(branched_project_id)),
                identifier=branched_project_id,
                parent=original_project_id,
            )
            new_leave_nodes.add(original_project_id)
            new_leave_nodes.add(branched_project_id)
        else:
            tree.create_node(
                tag=convert_project_dict_to_tag(projects_dict.get(branched_project_id)),
                identifier=branched_project_id,
                parent=original_project_id,
            )
            new_leave_nodes.add(branched_project_id)
    tree_depth = tree.depth()

    # traverse the tree, to remove all leave node that is_deprecated is marked as 1
    # which means, the project has been deleted
    while tree_depth > 0:
        leaves = tree.leaves()
        for leave in leaves:
            project = projects_dict.get(leave.identifier)
            is_deprecated = project.get("is_deprecated")
            if is_deprecated == '1':
                tree.remove_node(leave.identifier)
        tree_depth -= 1
    return tree


if __name__ == '__main__':
    projects_being_branched_list = get_branch_project_from_csv(file_name="1.csv")
    original_project_dict = get_projects_from_csv(file_name="2.csv")
    tree = get_tree(branch_list=projects_being_branched_list, projects_dict=original_project_dict)
    tree.show()
    filePath = "branched_projects_tree.txt"
    if os.path.exists(filePath):
        os.remove(filePath)
    tree.save2file(filename=filePath)
    get_project_without_being_branched(branch_list=projects_being_branched_list, projects_dict=original_project_dict)

