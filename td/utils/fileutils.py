from td.utils.tasks import Task
from td.utils.lists import List
from td.utils.workspaces import Workspace
from td.utils.config import set_default_config
import os

class Fileutils:

    def __init__(self, PATH: str, CONFIGPATH: str):
        self.ID_INDEX = 0
        self.NAME_INDEX = 1
        self.IMPORTANCE_INDEX = 2
        self.DESCRIPTION_INDEX = 3
        self.CHECKLIST_INDEX = 4
        self.TASKS_INDEX = 2
        self.LISTS_INDEX = 2
        self.CURRENT_WORKSPACE_VAR_INDEX = 0

        # Change this to something else later
        # What separates different elements in an object in td.txt
        self.SEPARATOR = ",._=+*&(,../){./;'"

        self.PATH = PATH
        self.CONFIGPATH = CONFIGPATH
        
    def create_file(self):
        with open(self.PATH, mode='w') as f:
            f.write('CURRENT_WORKSPACE=0\n')
            f.write('[TASKS]\n')
            f.write('[LISTS]\n')
            f.write('[WORKSPACES]\n')

    def check_existance(self):

        if not os.path.exists(self.PATH):
            self.create_file()

        if not os.path.exists(self.CONFIGPATH):
            set_default_config(self.CONFIGPATH)

    def check_blank_lines(self):
        with open(self.PATH, mode='r') as f:
            lines = f.readlines()

            while "\n" in lines:
                lines.remove("\n")

        with open(self.PATH, mode='w') as f:
            for line in lines:
                f.write(line)

    def get_checklist_item_index(self, item_name: str, line: list) -> int:
        for index, name in enumerate(line):
            if name[:-1] == item_name:
                if index >= self.CHECKLIST_INDEX:
                    break

        return index

    def get_lines_and_item_index(self, object_id: int) -> tuple:
        INDEX = None

        with open(self.PATH, mode='r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                line = line.split(self.SEPARATOR)

                if line[self.ID_INDEX] == str(object_id):
                    INDEX = i
                    break

        if INDEX is None:
            raise Exception("ID not found in file")
        
        return lines, INDEX

    def get_tasks(self):
        all_tasks = []

        with open(self.PATH, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                if line[self.ID_INDEX].isdigit():
                    line = line.split(self.SEPARATOR)
                    
                    task = Task(task_id=line[self.ID_INDEX],
                                name=line[self.NAME_INDEX],
                                importance=line[self.IMPORTANCE_INDEX],
                                description=line[self.DESCRIPTION_INDEX])
                    
                    for checklist_item in line[self.CHECKLIST_INDEX:]:
                        if checklist_item == '\n':
                            break
                        elif checklist_item == '':
                            continue

                        task.add_item(checklist_item)

                    all_tasks.append(task)

                elif line == '[LISTS]\n':
                    break

        return all_tasks

    def get_task_ids(self):
        task_ids = []

        with open(self.PATH, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                if line == '[LISTS]\n':
                    break
                
                line = line.split(self.SEPARATOR)

                if line[self.ID_INDEX].isdigit():
                    task_ids.append(int(line[self.ID_INDEX]))

        return task_ids
    
    def get_lists(self):
        all_lists = []
        start_adding = False

        with open(self.PATH, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:

                if line == '[LISTS]\n':
                    start_adding = True
                    continue

                if line == '[WORKSPACES]\n':
                    break

                if start_adding:
                    line = line.split(self.SEPARATOR)
                    
                    if line[self.ID_INDEX].isdigit():
                        
                        ls = List(
                            list_id=line[self.ID_INDEX],
                            name=line[self.NAME_INDEX]
                        )

                        for task_id in line[self.TASKS_INDEX:]:
                            if task_id.isdigit():
                                ls.task_ids.append(int(task_id))

                            else:
                                break
                        all_lists.append(ls)

        return all_lists
    
    def get_list_ids(self):
        list_ids = []
        start_adding = False

        with open(self.PATH) as f:
            lines = f.readlines()
            
            for line in lines[1:]:
                if line == '[LISTS]\n':
                    start_adding = True
                    continue

                if line == '[WORKSPACES]\n':
                    break
                
                if start_adding:
                    line = line.split(self.SEPARATOR)
                    
                    if line[self.ID_INDEX].isdigit():
                        list_ids.append(int(line[self.ID_INDEX]))

            return list_ids
        
    def get_workspaces(self) -> list:
        all_workspaces = []
        start_adding = False

        with open(self.PATH, 'r') as f:
            lines = f.readlines()

            for line in lines[1:]:
                
                if line == '[WORKSPACES]\n':
                    start_adding = True
                    continue

                if start_adding:
                    line = line.split(self.SEPARATOR)

                    if line[self.ID_INDEX].isdigit():

                        ws = Workspace(
                            workspace_id=line[self.ID_INDEX],
                            name=line[self.NAME_INDEX]
                        )
                    
                    for list_id in line[self.LISTS_INDEX:]:
                        if list_id.isdigit():
                            ws.list_ids.append(int(list_id))
                        
                        else:
                            break
                    
                    all_workspaces.append(ws)

            return all_workspaces
        
    def get_workspace_ids(self) -> list:
        workspace_ids = []
        start_adding = False

        with open(self.PATH) as f:
            lines = f.readlines()

            for line in lines[1:]:
                if line == '[WORKSPACES]\n':
                    start_adding = True
                    continue

                if start_adding:
                    line = line.split(self.SEPARATOR)

                    if line[self.ID_INDEX].isdigit():
                        workspace_ids.append(int(line[self.ID_INDEX]))
        
        return workspace_ids
        
    def get_all_ids(self):

        all_ids = self.get_task_ids() + self.get_list_ids() + self.get_workspace_ids()
        all_ids.sort()

        return all_ids

    def mark_checklist_item_as_done(self, object_id: int, item_name: str = ""):
        lines, INDEX = self.get_lines_and_item_index(object_id)
        line = lines[INDEX].split(self.SEPARATOR)
        
        # index = self.get_checklist_item_index(item_name, line)
        for index, item in enumerate(line[self.CHECKLIST_INDEX:]):
            if item[:-1] == item_name:
                if item[-1] == '0':
                    line[index+self.CHECKLIST_INDEX] = line[index+self.CHECKLIST_INDEX][:-1] + '1'
                    break

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def mark_checklist_item_as_undone(self, object_id: int, item_name: str = ""):
        lines, INDEX = self.get_lines_and_item_index(object_id)
        line = lines[INDEX].split(self.SEPARATOR)

        # index = self.get_checklist_item_index(rank, line)

        for index, item in enumerate(line[self.CHECKLIST_INDEX:]):
            if item[:-1] == item_name:
                if item[-1] == '1':
                    line[index+self.CHECKLIST_INDEX] = line[index+self.CHECKLIST_INDEX][:-1] + '0'

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def mark_task_as_done(self, object_id: int):
        lines, INDEX = self.get_lines_and_item_index(object_id)
        line = lines[INDEX].split(self.SEPARATOR)
        
        line[self.NAME_INDEX] = line[self.NAME_INDEX][:-1] + '1'

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def mark_task_as_undone(self, object_id: int):
        lines, INDEX = self.get_lines_and_item_index(object_id)
        line = lines[INDEX].split(self.SEPARATOR)
        
        line[self.NAME_INDEX] = line[self.NAME_INDEX][:-1] + '0'

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def add_task_to_file(self, task: Task):

        with open(self.PATH, mode='r') as f:
            lines = f.readlines()

            for index, line in enumerate(lines):
                if line == '[LISTS]\n':
                    # The zero after id represents whether the task is completed or not
                    lines.insert(index, f"{task.id}{self.SEPARATOR}{task.name}{self.SEPARATOR}{task.importance}{self.SEPARATOR}{task.description}{self.SEPARATOR}\n")
                    break

        self.update_file(lines)

    def add_list_to_file(self, ls: List):
        
        with open(self.PATH, mode='r') as f:
            lines = f.readlines()

            for index, line in enumerate(lines):
                if line == '[WORKSPACES]\n':
                    lines.insert(index, f"{ls.id}{self.SEPARATOR}{ls.name}{self.SEPARATOR}\n")
                    break

        self.update_file(lines)

    def add_workspace_to_file(self, ws: Workspace):
        with open(self.PATH, mode='a') as f:
            f.write(f"{ws.id}{self.SEPARATOR}{ws.name}{self.SEPARATOR}\n")

    def _find_list_with_task_id(self, task_id: int) -> int:
        """
        Finds a list given a task id
        returns the id of the list
        """
        task_id = int(task_id)

        lists = self.get_lists()

        for ls in lists:
            if task_id in ls.task_ids:
                return ls.id
        
    def _find_workspace_with_list_id(self, list_id: int) -> int:

        all_workspaces = self.get_workspaces()

        for ws in all_workspaces:
            if list_id in ws.list_ids:
                return ws.id

    def delete_task(self, task_id: int, task_only: bool = False):
        """
        If task only is true
        only a task is deleted and its id is not deleted from a list
        """
        lines, INDEX = self.get_lines_and_item_index(task_id)

        lines.remove(lines[INDEX])

        if not task_only:
            list_id = self._find_list_with_task_id(task_id)
            # Updating index to the index of the list
            _, INDEX = self.get_lines_and_item_index(int(list_id))
            INDEX -= 1 # This is done because a task has been deleted

            for line in lines:
                line = line.split(self.SEPARATOR)
                
                if str(list_id) == line[self.ID_INDEX]:
                    line.remove(str(task_id))
                    break
        
            lines[INDEX] = self.SEPARATOR.join(line)

        self.update_file(lines)

    def delete_list(self, list_id: int, list_only: bool = False):
        lines, INDEX = self.get_lines_and_item_index(list_id)

        line = lines[INDEX].split(self.SEPARATOR)
        
        for task_id in line[self.TASKS_INDEX:]:
            if task_id.isdigit():
                self.delete_task(int(task_id), task_only=True)

        # Redoing this to update lines after deletion of tasks
        lines, INDEX = self.get_lines_and_item_index(list_id)
        lines.remove(lines[INDEX])

        if not list_only:
            ws_id = self._find_workspace_with_list_id(list_id)
            
            _, INDEX = self.get_lines_and_item_index(int(ws_id))
            INDEX -= 1 # This is done because a list has been deleted

            for line in lines:
                line = line.split(self.SEPARATOR)
                
                if str(ws_id) == line[self.ID_INDEX]:
                    line.remove(str(list_id))
                    break

            lines[INDEX] = self.SEPARATOR.join(line)

        self.update_file(lines)

    def delete_workspace(self, ws_id: int):
        lines, INDEX = self.get_lines_and_item_index(ws_id)

        line = lines[INDEX].split(self.SEPARATOR)

        for list_id in line[self.LISTS_INDEX:]:
            if list_id.isdigit():
                self.delete_list(int(list_id), list_only=True)

        # Redoing this to update lines after deletion of lists
        lines, INDEX = self.get_lines_and_item_index(ws_id)
        lines.remove(lines[INDEX])

        self.update_file(lines)

    def delete_item(self, item_type: str, object_id: int, item_name: str = ""):
        lines, INDEX = self.get_lines_and_item_index(object_id)
        line = lines[INDEX].split(self.SEPARATOR)

        if item_type == 'checklist' and item_name != "":
            # This deletes the first occurence of the item
            index = self.get_checklist_item_index(item_name, line)
            del line[index]

            # TODO: Remove this when workspaces are implemented
            # Check to see if a comma get deleted in the last line 
            if line[-1] != '\n':
                # If this is the last line
                if len(line[self.CHECKLIST_INDEX:]) == 0:
                    line.append('')
            
        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def delete_task_description(self, task_id: int):
        lines, INDEX = self.get_lines_and_item_index(task_id)
        line = lines[INDEX].split(self.SEPARATOR)

        line[self.DESCRIPTION_INDEX] = ''

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def add_task_to_list(self, list_id: int, task_id: int):
        lines, INDEX = self.get_lines_and_item_index(list_id)
        line = lines[INDEX].split(self.SEPARATOR)

        if line[self.TASKS_INDEX][-2:] == '\n' or line[-1] == '\n':
            line.remove('\n')
            line.append(str(task_id))
            line.append('\n')

        else:
            # TODO: Remove this once workspaces are added
            # line[self.TASKS_INDEX] = line[self.TASKS_INDEX] + str(task_id) + self.SEPARATOR
            if '' in line:
                line.remove('')
                
            line.append(str(task_id))

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def add_list_to_workspace(self, workspace_id: int, list_id: int):
        lines, INDEX = self.get_lines_and_item_index(workspace_id)
        line = lines[INDEX].split(self.SEPARATOR)
        
        if line[self.LISTS_INDEX][-2:] == '\n' or line[-1] == '\n':
            line.remove('\n')
            line.append(str(list_id))
            line.append('\n')
        
        else:
            if '' in line:
                line.remove('')

            line.append(str(list_id))

        lines[INDEX] = self.SEPARATOR.join(line)
        
        self.update_file(lines)

    def add_item(self, item_type: str, item_name: str, object_id: int):
        lines, INDEX = self.get_lines_and_item_index(object_id)
        line = lines[INDEX].split(self.SEPARATOR)

        if item_type == 'checklist':
            item_name = item_name + '0' # 0 is meant to represent if the item is completed or not
            if line[self.CHECKLIST_INDEX][-1:] == '\n':
                line[self.CHECKLIST_INDEX] = line[self.CHECKLIST_INDEX][:-2] + item_name + self.SEPARATOR + '\n'
            else:
                if line[-1] == '\n':
                    line[self.CHECKLIST_INDEX] = line[self.CHECKLIST_INDEX] + self.SEPARATOR + item_name
                else:
                    if line[self.CHECKLIST_INDEX] == '':
                        line[self.CHECKLIST_INDEX] = line[self.CHECKLIST_INDEX] + item_name
                    else:
                        line[self.CHECKLIST_INDEX] = line[self.CHECKLIST_INDEX] + self.SEPARATOR + item_name

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def edit_task(self, item_type: str, object_id: int, new_item: str, item_name: str = ""):
        lines, INDEX = self.get_lines_and_item_index(object_id)
        line = lines[INDEX].split(self.SEPARATOR)

        if item_type == 'name':

            # If the task is not completed
            if line[self.NAME_INDEX][-1] == '0':
                line[self.NAME_INDEX] = new_item + '0'
            else:
                line[self.NAME_INDEX] = new_item + '1'

        elif item_type == 'id':
            line[self.ID_INDEX] = new_item

        elif item_type == 'importance':
            if line[self.IMPORTANCE_INDEX][1:] == '\n':
                line[self.IMPORTANCE_INDEX] = new_item + '\n'

            else:
                line[self.IMPORTANCE_INDEX] = new_item

        elif item_type == "description":
            line[self.DESCRIPTION_INDEX] = new_item
        
        else:
            # item_type == checklist
            index = self.get_checklist_item_index(item_name, line)
            line[index] = new_item + '0'

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def rename_list(self, ls_id: int, new_name: str) -> None:
        lines, INDEX = self.get_lines_and_item_index(ls_id)
        line = lines[INDEX].split(self.SEPARATOR)

        line[self.NAME_INDEX] = new_name

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def rename_workspace(self, ws_id: int, new_name: str) -> None:
        lines, INDEX = self.get_lines_and_item_index(ws_id)
        line = lines[INDEX].split(self.SEPARATOR)

        line[self.NAME_INDEX] = new_name

        lines[INDEX] = self.SEPARATOR.join(line)
        self.update_file(lines)

    def get_current_workspace_id(self) -> int:
        """
        Returns None if no workspace yet exists or if in the main menu
        """
        with open(self.PATH) as f:
            line = f.readlines()[self.CURRENT_WORKSPACE_VAR_INDEX]
            line = line.split('=')

            line[1] = line[1][:-1]

        # This check is for first run
        # TODO: Add defualt workspace on startup
        if int(line[1]) != 0:
            return int(line[1])
        
        # If no workspace yet exists or in the main menu
        else:
            return None

    def set_current_workspace(self, ws_id: int):
        with open(self.PATH) as f:
            lines = f.readlines()
            line = lines[self.CURRENT_WORKSPACE_VAR_INDEX]

            line = line.split('=')

            line[1] = str(ws_id) + '\n'

        lines[self.CURRENT_WORKSPACE_VAR_INDEX] = '='.join(line)

        self.update_file(lines)

    def update_file(self, lines: list) -> None:
        with open(self.PATH, mode='w') as f:
            for line in lines:
                f.write(line)
