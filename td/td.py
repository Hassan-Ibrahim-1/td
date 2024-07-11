import typer
import inquirer
from typing_extensions import Annotated
from typing import List as typing_List
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich import box
from td.utils import apputils
from td.utils.tasks import Task
from td.utils.lists import List
from td.utils.workspaces import Workspace
from td.utils.checks import Checks
from td.utils.config import get_config, edit_config_value
from td.utils.fileutils import Fileutils

# TODO: Make the changes happen by default
PATH = "td.txt"  # Change this to testtd.txt when testing
CONFIGPATH = "config.txt"  # Change this to testconfig.txt when testing

checks = Checks(PATH, CONFIGPATH)
fileutils = Fileutils(PATH, CONFIGPATH)

app = typer.Typer(rich_markup_mode='rich')
console = Console()

@app.command(rich_help_panel="Utilities")
def add(
    typ: Annotated[str, typer.Argument(callback=checks.check_type, rich_help_panel="Task config", help="Specify the type you want to add: [bold green]workspace, list task, or task checklist[/bold green]")],
    name: Annotated[str, typer.Argument(rich_help_panel="Config", help="Specify the name/content", callback=checks.check_string_arg)],
    description: Annotated[str, typer.Option('--description', '-d', rich_help_panel="Task config", help="Set the description for a task")]="",
    importance: Annotated[int, typer.Option('--importance', '-im', min=1, max=3, clamp=True, rich_help_panel="Task config", help="Add a level of importance to your task (1 - 3)")]=1,
    object_rank: Annotated[int, typer.Option('--id', '-i', rich_help_panel="Task config", help="Specify this when adding a checklist for a task.")]=None
):
    """
    [bold yellow]Adds a task, a task checklist, list or workspace[/bold yellow]
    """
    fileutils.check_existance()
    checks.check_file()

    if typ in ['task', 't']:
        checks.check_workspace_available()
        checks.check_if_in_main_menu()

        c_ws_id = fileutils.get_current_workspace_id()
        c_ws = apputils.get_workspace_from_id(c_ws_id)

        new_id = apputils.generate_id()
        name = name + '0'
        new_task = Task(name=name, task_id=new_id, description=description, importance=importance)
        fileutils.add_task_to_file(task=new_task)

        checks.check_list_available(c_ws)

        # TODO: Make this better
        # Get c_ws again if a defualt list has been created
        c_ws = apputils.get_workspace_from_id(c_ws_id)

        if object_rank == None:
            # If no id is provided - add the task to the list with the smallest id
            lists = apputils.get_lists_in_workspace(c_ws)

            fileutils.add_task_to_list(list_id=lists[0].id, task_id=new_id)

            rank = apputils.get_rank_from_task_id(new_id, c_ws)

            show(object_rank=rank)
            
        else:
            # If an id is provided
            obj = apputils.get_object_from_rank(object_rank)
            try:
                checks.check_list_id(obj.id)
                
                fileutils.add_task_to_list(list_id=obj.id, task_id=new_id)

                show(object_rank=object_rank)

            except typer.BadParameter:
                lists = apputils.get_lists_in_workspace(c_ws)

                fileutils.add_task_to_list(list_id=lists[0].id, task_id=new_id)
                
                rank = apputils.get_rank_from_task_id(new_id, c_ws)
                show(object_rank=rank)
            

    elif typ in ['checklist', 'cs']:
        checks.check_workspace_available()
        checks.check_if_in_main_menu()

        if object_rank == None:
            raise typer.BadParameter("You didn't specify an id!")
        else:
            obj = apputils.get_object_from_rank(object_rank)
            
            if isinstance(obj, Task):
                fileutils.add_item(item_type='checklist', object_id=obj.id, item_name=name)
                
                show(object_rank=object_rank)
            
            else:
                raise typer.BadParameter(f"The ID '{obj.id}' doesn't belong to a task")

    elif typ in ['list', 'ls']:
        checks.check_workspace_available()
        checks.check_if_in_main_menu()

        new_id = apputils.generate_id()
        new_list = List(list_id=new_id, name=name)
        fileutils.add_list_to_file(new_list)

        if object_rank is None:
            c_ws_id = fileutils.get_current_workspace_id()

            fileutils.add_list_to_workspace(workspace_id=c_ws_id, list_id=new_id)

            # Get the workspace after adding the list
            c_ws = apputils.get_workspace_from_id(c_ws_id)

            rank = apputils.get_rank_from_list_id(new_id, c_ws)

            show(object_rank=rank)

        else:
            # TODO: get rid of this

            checks.check_workspace_id(object_rank)
            fileutils.add_list_to_workspace(workspace_id=object_rank, list_id=new_id)

    elif typ in ['workspace', 'ws']:
        new_id = apputils.generate_id()
        new_workspace = Workspace(name, new_id)
        fileutils.add_workspace_to_file(new_workspace)
        checks.check_list_available(new_workspace)

        rank = apputils.get_rank_of_workspace_from_id(new_id)
        
        c_ws_id = fileutils.get_current_workspace_id()
        
        # This is run to go to the main menu so that the new workspace can be displayed
        exit()
        show(object_rank=rank)

        if c_ws_id is None:
            fileutils.set_current_workspace(0)

        else:
            fileutils.set_current_workspace(c_ws_id)

    fileutils.check_blank_lines()

@app.command("del", rich_help_panel="Utilities")
def delete(
    object_ranks: Annotated[typing_List[int], typer.Argument(help="The ID of the thing you want to delete")],
    checklist_ranks: Annotated[typing_List[int], typer.Option("--rank", "-r", help="The name of the element in the object or its rank (The number the checklist item appears in show -i (id)).")] = [],
    delete_description: Annotated[bool, typer.Option("--description", "-d", help="Delete the description of a task.")] = False
):
    """
    [bold yellow]Delete a task, list or workspace[/bold yellow]
    """
    fileutils.check_existance()
    checks.check_file()


    for object_rank in object_ranks:
        obj = apputils.get_object_from_rank(object_rank)

        if isinstance(obj, Task):
            checks.check_if_in_main_menu()

            if delete_description:
                fileutils.delete_task_description(obj.id)
                
                c_ws_id = fileutils.get_current_workspace_id()
                c_ws = apputils.get_workspace_from_id(c_ws_id)
                
                ls = apputils.get_parent_list(obj)

                show(object_rank=apputils.get_rank_from_list_id(ls.id, c_ws))

                continue

            if checklist_ranks == []:
                # If a checklist rank isn't given
                # This means we're deleting the task itself

                checks.check_task_id(obj.id)
                ls = apputils.get_parent_list(obj)
                fileutils.delete_task(obj.id)

                c_ws_id = fileutils.get_current_workspace_id()
                c_ws = apputils.get_workspace_from_id(c_ws_id)

                ls_rank = apputils.get_rank_from_list_id(ls.id, c_ws)

                show(object_rank=ls_rank)

            else:
                # If deleting a checklist item

                apputils.adjust_ranks(checklist_ranks)

                for checklist_rank in checklist_ranks:
                    checklist_rank = str(checklist_rank)
                    
                    checks.check_task_id(obj.id)
                    checks.check_checklist(obj.id, checklist_rank)

                    if checklist_rank.isdigit():
                        item_name = apputils.get_checklist_item(checklist_rank, obj.id)
                        fileutils.delete_item(item_type='checklist', object_id=obj.id, item_name=item_name)
                    else:
                        fileutils.delete_item(item_type='checklist', object_id=obj.id, item_name=checklist_rank)
                
                show(object_rank=object_rank)

        elif isinstance(obj, List):
            checks.check_if_in_main_menu()
            checks.check_list_id(obj.id)
            fileutils.delete_list(obj.id)

            show()

        elif isinstance(obj, Workspace):
            checks.check_workspace_id(obj.id)
            delete = typer.confirm(f"Are you sure you want to delete the workspace '{obj.name}'")

            if delete:
                fileutils.delete_workspace(obj.id)
                checks.check_current_workspace(obj.id)
                show()
                
            else:
                rprint('[bold red]Aborted.[/]')
                
@app.command(rich_help_panel="Utilities")
def show(
    show_all: Annotated[bool, typer.Option('--all', '-a', help="Show task including descriptions and checklists")] = False,
    show_workspaces: Annotated[bool, typer.Option('--workspaces', '-w', help="Show all workspaces")] = False,
    object_rank: Annotated[int, typer.Option('--id', '-i', help="If specified, show detailed information about the object")]=None,
    show_completed_only: Annotated[bool, typer.Option('--completed', '-c', help='Show only completed tasks')] = False,
    show_undone_only: Annotated[bool, typer.Option('--undone', '-u', help='Show undone tasks only')] = False
):
    """
    [bold yellow]Shows all tasks[/bold yellow]
    """
    fileutils.check_existance()
    checks.check_file()

    all_tasks = fileutils.get_tasks()
    all_lists = fileutils.get_lists()

    # Reset them if both are enabled
    if show_completed_only and show_undone_only:
        show_undone_only = False
        show_completed_only = False

    elif fileutils.get_current_workspace_id() is None:

        # Creates a default workspace
        checks.check_workspace_available()

        if object_rank is None:
            show_workspaces = True

    if show_workspaces:
        # TODO: generate ranks here
        objects = fileutils.get_workspaces()
        unused_ranks = list(range(1, len(objects)+1))
        ws_ranks = apputils.generate_ranks(objects, unused_ranks)

        apputils.print_all_workspaces(ws_ranks)
    
    else:
        if object_rank == None:
            # If printing all lists
            c_ws_id = fileutils.get_current_workspace_id()
            c_ws = apputils.get_workspace_from_id(c_ws_id)

            ws_list_ranks = apputils.get_ranks_of_lists_in_workspace(c_ws)

            apputils.print_workspace(c_ws, ws_list_ranks[0][1])

            lists = apputils.get_lists_in_workspace(c_ws)
            
            all_task_ranks = []

            for ls in lists:
                used_ranks = ws_list_ranks + all_task_ranks
                used_ranks.sort(key= lambda rank: rank[1])
                ranks_of_tasks_in_list = apputils.get_ranks_of_tasks_in_list(c_ws, ls, used_ranks)
                all_task_ranks += ranks_of_tasks_in_list

                apputils.print_list(ls, ws_list_ranks.pop(1)[1], ranks_of_tasks_in_list, show_completed_only, show_undone_only, with_description=show_all)
        
        else:
            # If printing a specific object
            obj = apputils.get_object_from_rank(object_rank)
            
            # If the object is a task
            if isinstance(obj, Task):

                for task in all_tasks:
                    if task.id == obj.id:
                        apputils.print_task(task)
                        break

            elif isinstance(obj, List):
                # If the object is a list
                for ls in all_lists:
                    if ls.id == obj.id:
                        c_ws_id = fileutils.get_current_workspace_id()
                        c_ws = apputils.get_workspace_from_id(c_ws_id)
                        
                        ws_list_ranks = apputils.get_ranks_of_lists_in_workspace(c_ws)
                        
                        # Getting the ranks of the tasks in a list
                        ranks_of_tasks_in_workspace = apputils.get_ranks_of_tasks_in_workspace(c_ws)

                        ranks_of_tasks_in_list = []

                        for rank in ranks_of_tasks_in_workspace:
                            if rank[0] in ls.task_ids:
                                ranks_of_tasks_in_list.append(rank)

                        apputils.print_list(ls, object_rank, ranks_of_tasks_in_list, show_completed_only, show_undone_only, with_description=True)
                        break

            elif isinstance(obj, Workspace):
                ws_list_ranks = apputils.get_ranks_of_lists_in_workspace(obj)

                apputils.print_workspace(obj, ws_list_ranks[0][1])

                lists = apputils.get_lists_in_workspace(obj)
                
                all_task_ranks = []

                for ls in lists:
                    used_ranks = ws_list_ranks + all_task_ranks
                    used_ranks.sort(key= lambda rank: rank[1])
                    ranks_of_tasks_in_list = apputils.get_ranks_of_tasks_in_list(obj, ls, used_ranks)
                    
                    all_task_ranks += ranks_of_tasks_in_list

                    apputils.print_list(ls, ws_list_ranks.pop(1)[1], ranks_of_tasks_in_list, show_completed_only, show_undone_only)

@app.command(rich_help_panel="Utilities")
def rename(
    object_rank: Annotated[int, typer.Argument(help="The id of the thing you want to change")],
    new_name: Annotated[str, typer.Argument(help="What you want the new name to be")]
):
    """
    [bold yellow]Renames a task, list or workspace[/bold yellow]
    """
    fileutils.check_existance()
    checks.check_file()

    obj = apputils.get_object_from_rank(object_rank)

    if isinstance(obj, Task):
        checks.check_task_id(obj.id)
        fileutils.edit_task(item_type='name', new_item=new_name, object_id=obj.id)

    elif isinstance(obj, List):
        checks.check_list_id(obj.id)
        fileutils.rename_list(obj.id, new_name)

    elif isinstance(obj, Workspace):
        checks.check_workspace_id(obj.id)
        fileutils.rename_workspace(obj.id, new_name)
    
    show(object_rank=object_rank)

@app.command(rich_help_panel='Utilities')
def edit(
    item_type: Annotated[str, typer.Argument(callback=checks.check_item, help="The type of item you want to edit (description, importance, checklist)")],
    object_rank: Annotated[int, typer.Argument(help='Specify the ID of the object you want to edit')],
    new_item: Annotated[str, typer.Argument(help="The new item that you want to replace the previous with")],
    checklist_rank: Annotated[str, typer.Option('--rank', '-r', help="The rank of the list item you want to edit.")] = ""
):
    """
    [bold yellow]Edits the importance, checklist or description[/bold yellow]
    """
    fileutils.check_existance()
    checks.check_file()

    checks.check_if_in_main_menu()

    all_tasks = fileutils.get_tasks()

    obj = apputils.get_object_from_rank(object_rank)
    checks.check_task_id(obj.id)

    for task in all_tasks:
        if task.id == obj.id:

            if item_type in ['checklist', 'cs']:
                if checklist_rank == "":
                    raise typer.BadParameter(f"Name/rank not provided. Use the -r option to provide a rank.")  
                checks.check_checklist(obj.id, checklist_rank)
                item_name = apputils.get_checklist_item(checklist_rank, obj.id)
                fileutils.edit_task(item_type='checklist', new_item=new_item, object_id=obj.id, item_name=item_name)
                show(object_rank=object_rank)
            else:
                if item_type == 'importance':
                    checks.check_importance(int(new_item))
                
                # This does both importance and description
                fileutils.edit_task(item_type=item_type, new_item=new_item, object_id=obj.id)
                
                show(object_rank=object_rank)
            
            break

@app.command(rich_help_panel="Utilities")
def done(
    object_ranks: Annotated[typing_List[int], typer.Argument(help="The ID of the thing you want to marke as completed or the ID of the thing to which the checklist item belongs")],
    checklist_ranks: Annotated[typing_List[str], typer.Option('--rank', '-r', help="The rank or the name of the checklist item you want to edit")] = [],
):
    fileutils.check_existance()
    checks.check_file()

    checks.check_if_in_main_menu()

    for object_rank in object_ranks:

        obj = apputils.get_object_from_rank(object_rank)

        try:
            checks.check_task_id(obj.id)

            if checklist_ranks == []:
                # Task is being marked as completed
                # Checks for if the id belongs to a task or not
                fileutils.mark_task_as_done(obj.id)

                c_ws_id = fileutils.get_current_workspace_id()
                c_ws = apputils.get_workspace_from_id(c_ws_id)

                parent_ls = apputils.get_parent_list(obj)
                ls_rank = apputils.get_rank_from_list_id(parent_ls.id, c_ws)
                
                show(object_rank=ls_rank)
            
            else:
                # Checklist item being marked as completed
                
                if 'all' in checklist_ranks:

                    for checklist_item in obj.checklist:
                        if checklist_item != '':
                            fileutils.mark_checklist_item_as_done(obj.id, checklist_item[:-1])

                else:
                    apputils.adjust_checklist_ranks(checklist_ranks, marking_as_done=True)

                    for checklist_rank in checklist_ranks:

                        checks.check_checklist(obj.id, checklist_rank)
                        item_name = apputils.get_checklist_item(checklist_rank, obj.id)
                        fileutils.mark_checklist_item_as_done(obj.id, item_name)

                    c_ws_id = fileutils.get_current_workspace_id()
                    c_ws = apputils.get_workspace_from_id(c_ws_id)

                    task_rank = apputils.get_rank_from_task_id(obj.id, c_ws)

                    show(object_rank=task_rank)

        except typer.BadParameter:
            pass

        try:
            checks.check_list_id(obj.id)

            for task_id in obj.task_ids:
                fileutils.mark_task_as_done(task_id)

            show(object_rank)

        except typer.BadParameter:
            pass

@app.command(rich_help_panel="Utilities")
def undone(
    object_ranks: Annotated[typing_List[int], typer.Argument(help="The ID of the thing you want to marke as completed or the ID of the thing to which the checklist item belongs")],
    checklist_ranks: Annotated[typing_List[str], typer.Option('--rank', '-r', help="The rank or the name of the checklist item you want to edit")] = []
):
    
    fileutils.check_existance()
    checks.check_file()

    checks.check_if_in_main_menu()
    
    for object_rank in object_ranks:

        obj = apputils.get_object_from_rank(object_rank)

        try:
            checks.check_task_id(obj.id)
            if checklist_ranks == []:
                # Task being marked as undone
                fileutils.mark_task_as_undone(obj.id)

                c_ws_id = fileutils.get_current_workspace_id()
                c_ws = apputils.get_workspace_from_id(c_ws_id)

                parent_ls = apputils.get_parent_list(obj)
                ls_rank = apputils.get_rank_from_list_id(parent_ls.id, c_ws)
                
                show(object_rank=ls_rank)

            else:
                # Checklist item being marked as undone
                if 'all' in checklist_ranks:

                    for checklist_item in obj.checklist:
                        if checklist_item != '':
                            fileutils.mark_checklist_item_as_undone(obj.id, checklist_item[:-1])
                
                else:    
                    apputils.adjust_checklist_ranks(checklist_ranks)

                    for checklist_rank in checklist_ranks:

                        checks.check_checklist(obj.id, checklist_rank)
                        item_name = apputils.get_checklist_item(checklist_rank, obj.id)
                        fileutils.mark_checklist_item_as_undone(obj.id, item_name)
                
                c_ws_id = fileutils.get_current_workspace_id()
                c_ws = apputils.get_workspace_from_id(c_ws_id)

                task_rank = apputils.get_rank_from_task_id(obj.id, c_ws)
                show(object_rank=task_rank)

        except typer.BadParameter:
            pass

        try:
            checks.check_list_id(obj.id)

            for task_id in obj.task_ids:
                fileutils.mark_task_as_undone(task_id)

            show()

        except typer.BadParameter:
            pass

@app.command()
def count(
    typ: Annotated[str, typer.Argument(callback=checks.check_count_type, help='Count the number of completed or uncompleted tasks.')],
    object_id: Annotated[int, typer.Option('--id', '-i', help='The id of the task or list in which you want to count the number of completed items')] = None
):
    fileutils.check_existance()
    checks.check_file()

    # Variables used to print the progres bar
    num_to_be_counted = 0

    # The variable that determines whether or not to count completed or uncompleted tasks
    count_completed = False

    total = 0

    table = Table(show_header=True, show_edge=False, show_footer=False, show_lines=False, box=box.SIMPLE_HEAD)

    if typ in ['done', 'd', 'completed']:
        count_completed = True
        table.add_column('Number of completed objects', justify='center', header_style='#E9F93D', style='#20E2AA')

    else:
        table.add_column('Number of uncompleted objects', justify='center', style='#20E2AA', header_style='#E9F93D')

    if object_id is None:
        checks.check_if_in_main_menu()

        c_ws_id = fileutils.get_current_workspace_id()
        c_ws = apputils.get_workspace_from_id(c_ws_id)
        
        all_lists = apputils.get_lists_in_workspace(c_ws)

        for ls in all_lists:
            total += len(ls.task_ids)

            tasks_in_list = apputils.get_tasks_in_list(ls)

            for task in tasks_in_list:

                if count_completed:
                    if task.completed:
                        num_to_be_counted += 1
                
                else:
                    if not task.completed:
                        num_to_be_counted += 1
    
    else:
        obj = apputils.get_object_from_rank(object_id)

        if isinstance(obj, List):
            checks.check_if_in_main_menu()


            tasks_in_list = apputils.get_tasks_in_list(obj)

            total = len(tasks_in_list)

            for task in tasks_in_list:
                if count_completed:
                    if task.completed:
                        num_to_be_counted += 1
                
                else:
                    if not task.completed:
                        num_to_be_counted += 1
        
            text = f"[italic #4BFFF6] in list '{obj.name}' [/italic #4BFFF6]"

            print()
            apputils.center_print(text)

        elif isinstance(obj, Task):
            checks.check_if_in_main_menu()


            total = len(obj.checklist)

            if count_completed:
                num_to_be_counted = obj.num_done
            
            else:
                num_to_be_counted = obj.num_undone
            
            text = f"[italic #4BFFF6] in task '{obj.name}' [/italic #4BFFF6]"

            print()
            apputils.center_print(text)

        elif isinstance(obj, Workspace):
            all_lists = apputils.get_lists_in_workspace(obj)

            for ls in all_lists:
                total += len(ls.task_ids)

                tasks_in_list = apputils.get_tasks_in_list(ls)

                for task in tasks_in_list:

                    if count_completed:
                        if task.completed:
                            num_to_be_counted += 1
                    
                    else:
                        if not task.completed:
                            num_to_be_counted += 1

    table.add_row(f"{num_to_be_counted} out of {total}")
    
    print()

    apputils.center_print(table)

    print('\n')

@app.command()
def config():
    
    fileutils.check_existance()
    checks.check_file()

    CONFIGS = get_config(CONFIGPATH)

    ls_configs = [config.lower() for config in CONFIGS.keys()]

    questions = [
        inquirer.List(
            'config',
            message="What config do you want to edit?",
            choices=ls_configs
        )
    ]

    config_to_edit = inquirer.prompt(questions, raise_keyboard_interrupt=True)
    

    questions = [
        inquirer.Text(
            'color',
            message=f"old config: {CONFIGS[config_to_edit['config'].upper()]}. What is the new value you want to set?"
        )
    ]

    new_value = inquirer.prompt(questions, raise_keyboard_interrupt=True)    

    checks.check_color_value(new_value['color'])

    if new_value['color'][0] != '#':
        new_value['color'] = '#' + new_value['color']

    edit_config_value(CONFIGPATH, config_to_edit['config'].upper(), new_value['color'].upper())    


@app.command()
def move(
    object_rank: Annotated[int, typer.Argument()] = None,
    location_rank: Annotated[int, typer.Option('--location', '-l', help="Where you want to move the task to.")] = None,
    move_completed: Annotated[bool, typer.Option('--completed', '-c', help="Move all completed tasks")] = False
):
    
    if not move_completed and object_rank is None:
        raise typer.BadParameter("Please specify an ID!")
    
    if move_completed:

        if location_rank is None:
            raise typer.BadParameter("Please specify a location when moving a task!")
        
        ls = apputils.get_object_from_rank(location_rank)

        if not isinstance(ls, List):
            raise typer.BadParameter("Location specified isn't a list!")
        
        c_ws_id = fileutils.get_current_workspace_id()
        c_ws = apputils.get_workspace_from_id(c_ws_id)

        tasks = apputils.get_tasks_in_workspace(c_ws)

        for task in tasks:
            if task.completed:
                fileutils.delete_task(task.id)
                fileutils.add_task_to_file(task)
                fileutils.add_task_to_list(ls.id, task.id)
        
        show(object_rank=location_rank)

    else:
        obj = apputils.get_object_from_rank(object_rank)

        # TODO: make this work with every other object
        if isinstance(obj, Workspace):
            fileutils.set_current_workspace(obj.id)

            show()

        elif isinstance(obj, Task):
            
            if location_rank is None:
                raise typer.BadParameter("Please specify a location when moving a task!")
            
            ls = apputils.get_object_from_rank(location_rank)

            if not isinstance(ls, List):
                raise typer.BadParameter("Location specified isn't a list!")
            
            fileutils.delete_task(obj.id)
            fileutils.add_task_to_file(obj)
            fileutils.add_task_to_list(ls.id, obj.id)

            show(object_rank=location_rank)

@app.command()
def clear(
    object_ranks: Annotated[typing_List[int], typer.Argument(help="IDs of lists or tasks you want to clear")] = None
):
    checks.check_if_in_main_menu()

    if object_ranks == []:
        c_ws_id = fileutils.get_current_workspace_id()
        c_ws = apputils.get_workspace_from_id(c_ws_id)

        lists = apputils.get_lists_in_workspace(c_ws)

        for ls in lists:
            tasks = apputils.get_tasks_in_list(ls)
            
            if tasks is not None:
                
                for task in tasks:
                    if task.completed:
                        fileutils.delete_task(task.id)
        
    else:
        for object_rank in object_ranks:
            obj = apputils.get_object_from_rank(object_rank)
            
            if isinstance(obj, List):
                tasks = apputils.get_tasks_in_list(obj)

                if tasks is not None:
                    for task in tasks:
                        if task.completed:
                            fileutils.delete_task(task.id)

            elif isinstance(obj, Task):
                for item in obj.checklist:
                    if item[-1] == '1':
                        fileutils.delete_item("checklist", obj.id, item[:-1])
            
            else:
                raise typer.BadParameter(f"The id '{object_rank}' doesn't belong to a list or task")
        
    show()

@app.command()
def exit():
    # Set the current workspace to an id no object can have
    # When the id is 0 - the user is in the main menu
    fileutils.set_current_workspace(0)

    show()

if __name__ == "__main__":
    app()

