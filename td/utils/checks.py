import typer
import os
from rich import print as rprint
from rich.prompt import Confirm
from td.utils.fileutils import Fileutils
from td.utils.tasks import Task
from td.utils.lists import List
from td.utils.workspaces import Workspace

class Checks:
    
    def __init__(self, PATH: str, CONFIGPATH: str):
        self.PATH = PATH
        self.CONFIGPATH = CONFIGPATH
        self.fileutils = Fileutils(self.PATH, self.CONFIGPATH)

    def check_type(self, typ: str):
        if typ.lower() not in ['workspace', 'list', 'task', 'checklist', 'ws', 'ls', 't', 'cs']:
            raise typer.BadParameter(f"Type '{typ}' doesn't exist! Try (workspace, list or task)")
        return typ.lower()

    def check_id(self, object_id: int):
        all_ids = self.fileutils.get_all_ids()
        
        if object_id != None:
            if object_id not in all_ids: # Change this later
                raise typer.BadParameter(f"The ID '{object_id}' doesn't exist!")
        return object_id

    def check_item(self, item: str):
        if item.lower() not in ['description', 'importance', 'checklist', 'cs', 'd', 'im']:
            raise typer.BadParameter(f"Item type '{item}' doesn't exist! Try (description, checklist, importance)")
        return item.lower()

    def check_importance(self, importance: int):
        if importance not in [1, 2, 3]:
            raise typer.BadParameter("Importance should be between (1-3)!")
        return importance
    
    def check_string_arg(self, name: str):
        """
        Removes any newline character from a string
        """

        return name.strip('\n')

    def check_checklist(self, task_id: int, item_name: str):
        #TODO: try changing this to get_tasks_in_current_workspace
        all_tasks = self.fileutils.get_tasks()
        for task in all_tasks:
            if task_id == task.id:
                task.name = task.name[:-1]

                if item_name.isdigit():
                    if len(task.checklist) == 1 and '' in task.checklist:
                        raise typer.BadParameter(f"An item of rank {item_name} is not a part of the checklist in {task.name}")
                    elif int(item_name) not in range(1, len(task.checklist)+1):
                        raise typer.BadParameter(f"An item of rank {item_name} is not a part of the checklist in {task.name}")
                else:
                    if item_name not in self._remove_last_char_in_item(task.checklist):
                        raise typer.BadParameter(f"The item '{item_name}' is not a part of the checklist in {task.name}")
                
                break

    def check_checklist_completion(self, item: str) -> bool:
        if item[-1] == '0':
            return False
        return True
    
    def check_count_type(self, typ: str) -> bool:
        if typ not in ['done', 'undone', 'd', 'u', 'completed', 'uncompleted']:
            raise typer.BadParameter(f'Invalid type - Use either done or undone')
    
        return typ
        
    def check_list_available(self, c_ws: Workspace):
        """
        If no list is available add a default list
        """
        
        if c_ws.list_ids == []:

            new_id = self._generate_id()
            default_list = List(new_id, 'To Do')
            self.fileutils.add_list_to_file(default_list)

            # Add the newly created list to the workspace which was created first
            self.fileutils.add_list_to_workspace(c_ws.id, new_id)
    
    def check_workspace_available(self):
        """
        If no workspace is available - add a default workspace
        """
        all_workspaces = self.fileutils.get_workspaces()

        if all_workspaces == []:
            new_id = self._generate_id()
            default_ws = Workspace(workspace_id=new_id, name='Workspace 1')
            self.fileutils.add_workspace_to_file(default_ws)
            self.check_list_available(default_ws)

    def check_current_workspace(self, ws_id: int):
        """
        A check to see if a deleted workspace is the current workspace.
        If it is then go to the main menu.
        """
        c_ws_id = self.fileutils.get_current_workspace_id()

        if c_ws_id == ws_id:
            self.fileutils.set_current_workspace(0) # Main menu

    def check_task_id(self, object_id: int):
        """
        Checks if an id belongs to a task
        """
        task_ids = self.fileutils.get_task_ids()

        if object_id not in task_ids:
            raise typer.BadParameter("ID given doesn't belong to a task!")

    def check_list_id(self, object_id: int):
        """
        Check if the id given belongs to a list
        """
        list_ids = self.fileutils.get_list_ids()

        if object_id not in list_ids:
            raise typer.BadParameter("ID given doesn't belong to a list!")
        
    def check_workspace_id(self, object_id: int):
        """
        Check if the given id belongs to a workspace
        """
        ws_ids = self.fileutils.get_workspace_ids()

        if object_id not in ws_ids:
            raise typer.BadParameter("ID given doesn't belong to a workspace!")
    
        return object_id
        
    def check_unused_ranks(self, unused_ranks: list, len_of_objects: int):
        if len(unused_ranks) > len_of_objects:
            unused_ranks.pop(-1)
        
        # Why is this here???
        return unused_ranks
    
    def check_color_value(self, color_value: str):
        try:
            if color_value[0] == "#":
                if len(color_value[1:]) == 6:
                    if self._check_hex(color_value[1:]):
                        return
            
            else:
                if len(color_value) == 6:
                    if self._check_hex(color_value):
                        return
        
        except:
            pass

        raise typer.BadParameter(f"'{color_value}' is not a valid color value. Try something like '#FFAABB'")

    def check_if_in_main_menu(self):
        """
        Checks if the user is in the main menu.
        Mainly to be used to disable commands such as add and delete in
        the main menu.
        """
        c_ws_id = self.fileutils.get_current_workspace_id()

        if c_ws_id is None:
            raise typer.BadParameter("You can't use that command since you're in the main menu!")
    
    def check_file(self):
        with open(self.PATH) as f:
            lines = f.readlines()

            if ('[TASKS]\n' not in lines or '[LISTS]\n' not in lines) or '[WORKSPACES]\n' not in lines:
                rprint(f"[bold red]{self.PATH} has been modified![/bold red]")
                
                if Confirm.ask(f"Do you want to create a new instance of {self.PATH}? [bold red]This will result in all your workspaces being deleted[/bold red]"):
                    # PATH is deleted so that the program can have a fresh start and be usable
                    os.remove(self.PATH)
                    
                    quit()

                else:
                    print("Exiting program")
                    quit()
    
    def _generate_id(self) -> int:
        all_ids = self.fileutils.get_all_ids()
        try:
            for num in range(1,int(all_ids[-1])+1):
                if num not in all_ids:
                    return num
                
        except IndexError:
            return 1
        
        return int(all_ids[-1])+1

    def _remove_last_char_in_item(self, checklist: list) -> list:
        new_list = []
        for item in checklist:
            new_list.append(item[:-1])


        return new_list
    
    def _check_hex(self, value: str) -> bool:
        
        for char in value:
            char = char.upper()

            if ((char < '0' or char > '9') and (char < 'A' or char > 'F')):
                return False
            
        return True
