import typer
from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich import box
from rich.markdown import Markdown
from rich.progress import Progress, TextColumn, BarColumn, MofNCompleteColumn
from td.utils.tasks import Task
from td.utils.lists import List
from td.utils.workspaces import Workspace
from td.utils.config import get_config
from td.utils.checks import Checks
from td.utils.fileutils import Fileutils
from shutil import get_terminal_size

# TODO: Make the changes happen by default
PATH = "td.txt" # Change this to testtd.txt when testing
CONFIGPATH = "config.txt" # Change this to testconfig.txt when testing
checks = Checks(PATH, CONFIGPATH)
fileutils = Fileutils(PATH, CONFIGPATH)

console = Console()

class CenteredProgress(Progress):
    """
    same as rich's progress bar but centered
    """
    def get_renderable(self):
        return Align.center(super().get_renderable())

def get_terminal_width():
    terminal_width, _ = get_terminal_size()

    return terminal_width

def center_print(text: str, style: str = ""):
    width = get_terminal_width()
    console.print(Align.center(text, width=width), style=style)

def get_checklist_item(rank: int, object_id: int) -> str:
    """
    Returns the name of the item
    """
    all_tasks = fileutils.get_tasks()

    for task in all_tasks:
        if object_id == task.id:
            break

    task.checklist.sort(key = lambda item: item[-1])
    return task.checklist[int(rank)-1][:-1]

def get_parent_list(task: Task) -> List:
    all_lists = fileutils.get_lists()

    for ls in all_lists:
        if task.id in ls.task_ids:
            return ls

def get_parent_workspace(ls: List) -> Workspace:
    all_workspaces = fileutils.get_workspaces()

    for ws in all_workspaces:
        if ls.id in ws.list_ids:
            return ws    

def adjust_ranks(object_ranks: list):
    object_ranks.sort()

    if len(object_ranks) > 1:
        decrement_value = 0

        for index, _ in enumerate(object_ranks):

            object_ranks[index] -= decrement_value

            decrement_value += 1

def adjust_checklist_ranks(object_ranks: list, marking_as_done: bool = False):
    
    object_ranks.sort(key=lambda rank: int(rank))

    if len(object_ranks) > 1:
        decrement_value = 0

        for index, _ in enumerate(object_ranks):
            if not marking_as_done:
                try:
                    object_ranks[index + 1]

                except IndexError:
                    return
                
            object_ranks[index] = int(object_ranks[index])

            if marking_as_done:
                object_ranks[index] -= decrement_value
                decrement_value += 1

            # converting back to a string to make it usable by the rest of the program
            # TODO: make it so that int is accepted everywhere instead of strings
            object_ranks[index] = str(object_ranks[index])

def print_task(task: Task):
    
    CONFIGS = get_config(CONFIGPATH)

    task.name = format_task_name(task)
    ls = get_parent_list(task)

    title = f"[italic {CONFIGS['LIST_NAME_COLOR']}]in list '{ls.name}'[/italic {CONFIGS['LIST_NAME_COLOR']}]\n"
    
    table = Table(show_header=True, show_edge=False, show_footer=False, show_lines=False, box=box.SIMPLE_HEAD)
    
    table.add_column('ID', header_style=CONFIGS['TASK_ID_COLOR'], style=CONFIGS['TASK_ID_COLOR'], justify='center')
    table.add_column('Name', header_style=CONFIGS['TASK_NAME_COLOR'], style=CONFIGS['TASK_NAME_COLOR'], justify='center')
    table.add_column('Imp', header_style=CONFIGS['IMPORTANCE_HEADER_COLOR'], justify='center')
    table.add_column('Status', justify='center')

    rank = str(get_rank_of_task(task)[1])

    if task.completed:
        table.add_row(rank, task.name, str(task.importance), 'Completed')
    else:
        table.add_row(rank, task.name, str(task.importance), 'Not completed')

    checklist_table = Table(show_header=True, show_edge=False, show_footer=False, show_lines=False, box=box.SIMPLE_HEAD)

    checklist_table.add_column('Rank', style=CONFIGS['TASK_ID_COLOR'], justify='center')
    checklist_table.add_column('Name', style=CONFIGS['TASK_NAME_COLOR'], justify='center')
    checklist_table.add_column('Status', style='#25E44B', justify='center')

    # if description is empty
    if task.description == "":
        task.description = 'N\A'

    # If checklist is empty
    if task.checklist == [] or task.checklist == ['']:
        checklist_table.add_row('N\A', 'N\A', 'N\A')

    else:
        counter = 1
        
        # Sort checklist items based on whether or not they're completed
        task.checklist.sort(key=lambda item: item[-1])
        
        for item in task.checklist:
            if checks.check_checklist_completion(item):
                name = f"[s]{item[:-1]}[/]"
                status = 'Completed'

            else:
                name = item[:-1]
                status = 'Not completed'

            checklist_table.add_row(str(counter), name, status)
            counter += 1

    task_heading = Markdown('# Task')
    description_heading = Markdown("## Description")
    checklist_heading = Markdown('## Checklist')

    center_print(task_heading)
    print()
    center_print(title)
    center_print(table)

    print('\n')

    center_print(description_heading)
    print()
    center_print(task.description, style=CONFIGS['TASK_DESCRIPTION_COLOR'])

    print('\n')

    center_print(checklist_heading)
    print()
    center_print(checklist_table)
    print()

    # Printing the progress bar for the checklist
    total = task.num_done + task.num_undone
    print_progress_bar(total=total, num_completed=task.num_done)

    print('\n')

def add_tasks_to_table(ls: List, table: Table, with_description: bool, ranks_of_tasks: list, show_completed_only: bool, show_undone_only: bool):
    CONFIGS = get_config(CONFIGPATH)
    all_tasks = fileutils.get_tasks()

    # Sort tasks based on importance
    all_tasks.sort(key=lambda task: task.importance, reverse=True)

    if with_description:

        table.add_column('Description', header_style=CONFIGS['TASK_DESCRIPTION_COLOR'], style=CONFIGS['TASK_DESCRIPTION_COLOR'], justify='center')
        
        for task in all_tasks:

            if task.id in ls.task_ids:
                
                rank = str(ranks_of_tasks.pop(0)[1])

                # This condition basically just checks if the task can be printed or not
                # if show_completed_only is true only print completed tasks
                # if show_undone_only is true only print non completed tasks
                # if none are true then just print the task
                if ((show_completed_only and task.completed) or (show_undone_only and not task.completed)) or (not show_completed_only and not show_undone_only):

                    name = format_task_name(task)

                    # If description is empty
                    if task.description == "":
                        task.description = 'N\A'

                    if task.completed:
                        status = 'Completed'
                        style = CONFIGS['TASK_DONE_COLOR']
                    else:
                        status = 'Not completed'
                        style = CONFIGS[f'TASK_IMPORTANCE_{task.importance}_COLOR']

                    table.add_row(
                        rank,
                        name,
                        str(task.importance),
                        status,
                        task.description,
                        style=style
                    )

    else:
        for task in all_tasks:

            if task.id in ls.task_ids:

                rank = str(ranks_of_tasks.pop(0)[1])
                
                if ((show_completed_only and task.completed) or (show_undone_only and not task.completed)) or (not show_completed_only and not show_undone_only):
                    name = format_task_name(task)
                        
                    if task.completed:
                        status = 'Completed'
                        style = CONFIGS['TASK_DONE_COLOR']
                    else:
                        status = 'Not completed'
                        style = CONFIGS[f'TASK_IMPORTANCE_{task.importance}_COLOR']

                    table.add_row(
                        rank,
                        name,
                        str(task.importance),
                        status,
                        style=style
                    )

    return table

def count_completed_tasks(ls: List):
    """
    Counts completed tasks in a list
    """
    all_tasks = fileutils.get_tasks()
    count = 0

    # TODO: change this to use get_parent_list
    for task in all_tasks:
        if task.id in ls.task_ids:
            if task.completed:
                count += 1

    return count

def print_progress_bar(total: int, num_completed: int) -> None:
    with CenteredProgress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn()
    ) as progress:
        progress.add_task(description="[italic #96FF4B]Progress[/italic #96FF4B]", total=total, completed=num_completed)

def print_list(ls: List, ls_rank: int, ranks_of_tasks: list, show_completed_only: bool, show_undone_only: bool, with_description: bool = False):

    CONFIGS = get_config(CONFIGPATH)

    title = f"\n[bold {CONFIGS['LIST_ID_COLOR']}]ID: {ls_rank}[/] |[bold {CONFIGS['LIST_NAME_COLOR']}] {ls.name}[/]\n"
    
    table = Table(show_header=True, show_edge=False, show_footer=False, show_lines=False, box=box.SIMPLE_HEAD)

    table.add_column('ID', header_style=CONFIGS['TASK_ID_COLOR'], style=CONFIGS['TASK_ID_COLOR'], justify='center')
    table.add_column('Name', header_style=CONFIGS['TASK_NAME_COLOR'], style=CONFIGS['TASK_NAME_COLOR'], justify='center')
    table.add_column('Imp', header_style=CONFIGS['IMPORTANCE_HEADER_COLOR'], justify='center')
    table.add_column('Status', justify='center')
    
    if ls.task_ids == []:
        # If the list is empty
        table.add_row('N\A', 'N\A', 'N\A', 'N\A')
    else:
        table = add_tasks_to_table(ls, table, with_description, ranks_of_tasks, show_completed_only, show_undone_only)

    center_print(title)
    center_print(table)
    
    print()

    print_progress_bar(total=len(ls.task_ids), num_completed=count_completed_tasks(ls))

    print()

def print_workspace(ws: Workspace, rank: int):
    CONFIGS = get_config(CONFIGPATH)
    
    # TODO: change this to use ranks later
    title_id = f"[bold {CONFIGS['WORKSPACE_ID_COLOR']}]ID: {rank}[/]"
    title_name = f"[italic {CONFIGS['WORKSPACE_NAME_COLOR']}]in workspace '{ws.name}'[/]"
    
    center_print(title_id)
    center_print(title_name)

def print_all_workspaces(ws_ranks: list):
    all_workspaces = fileutils.get_workspaces()
    CONFIGS = get_config(CONFIGPATH)
    
    for ws in all_workspaces:
        # TODO: change this to use ranks later
        rank = ws_ranks.pop(0)[1]
        text = f"[bold {CONFIGS['WORKSPACE_ID_COLOR']}]ID: {rank}[/] | [bold {CONFIGS['WORKSPACE_NAME_COLOR']}]{ws.name}[/]"
        
        print()
        center_print(text)
        print()
        
    print()

def get_tasks_in_list(ls: List):
    """
    Gets all the tasks that belong to a list
    """
    all_tasks = fileutils.get_tasks()

    tasks_in_list = []

    for task_id in ls.task_ids:
        for task in all_tasks:
            if task.id == int(task_id):
                tasks_in_list.append(task)
                all_tasks.remove(task)

    # Sort based on importance
    tasks_in_list.sort(key=lambda task: task.importance, reverse=True)

    return tasks_in_list

def get_lists_in_workspace(ws: Workspace) -> list:
    all_lists = fileutils.get_lists()

    lists_in_workspace = []

    for list_id in ws.list_ids:
        for ls in all_lists:
            if ls.id == list_id:
                lists_in_workspace.append(ls)
                all_lists.remove(ls)

    return lists_in_workspace

# TODO: remove this when I add ranks to workspaces
def get_workspace_from_id(ws_id: int):
    all_workspaces = fileutils.get_workspaces()

    for ws in all_workspaces:
        if ws.id == ws_id:
            return ws
    return None

def generate_ranks(objects: list, unused_ranks: list) -> list:
    """
    objects is a list of either lists or tasks to get ranks of.
    objects is expected to be sorted.
    returns a list of tuples -> [(object_id, object_rank)]

    unused_ranks is the list of ranks which are going to be assigned to 
    the objects in order
    """
    ranks = []
    for obj in objects:
        ranks.append((obj.id, unused_ranks.pop(0)))
    
    return ranks

def get_object_from_rank(rank: int):
    rank = int(rank)

    c_ws_id = fileutils.get_current_workspace_id()
    c_ws = get_workspace_from_id(c_ws_id)

    if c_ws is None:
        all_workspaces = fileutils.get_workspaces()
        
        unused_ranks = list(range(1, len(all_workspaces)+1))
        ws_ranks = generate_ranks(all_workspaces, unused_ranks)

        for ws_rank in ws_ranks:
            if rank == ws_rank[1]:
                for ws in all_workspaces:
                    if ws.id == ws_rank[0]:
                        return ws
        
        raise typer.BadParameter(f"The ID '{rank}' doesn't exist!")

    if rank == 1:
        return c_ws

    all_tasks = fileutils.get_tasks()
    all_tasks.sort(key=lambda task: task.importance, reverse=True)

    ws_list_ranks = get_ranks_of_lists_in_workspace(c_ws)
    lists = get_lists_in_workspace(c_ws)

    # Check to see if the rank is a list
    for list_rank in ws_list_ranks[1:]:
        if list_rank[1] == rank:
            for ls in lists:
                if ls.id == list_rank[0]:
                    return ls

    # Holds the ranks of all tasks
    all_task_ranks = []

    for ls in lists:
        used_ranks = ws_list_ranks + all_task_ranks
        task_ranks = get_ranks_of_tasks_in_list(c_ws, ls, used_ranks)

        all_task_ranks += task_ranks

    for task_rank in all_task_ranks:
        if task_rank[1] == rank:
            for task in all_tasks:
                if task.id == task_rank[0]:
                    return task

    raise typer.BadParameter(f"The ID '{rank}' doesn't exist!")

def generate_id():
    all_ids = fileutils.get_all_ids()
    try:
        for num in range(1,int(all_ids[-1])+1):
            if num not in all_ids:
                return num
            
    except IndexError:
        return 1
    
    return int(all_ids[-1])+1

def format_task_name(task: Task):
        if task.completed:
            return f"[s]{task.name[:-1]}[/]"
        
        return task.name[:-1]

def get_ranks_of_lists_in_workspace(ws: Workspace) -> list:
    """
    Takes in a workspace and returns the ranks of every list in that workspace.
    rank 1 is always assigned to the workspace given and the list that this function
    returns includes that rank

    """

    lists = get_lists_in_workspace(ws)

    # The objects to be given to generate_ranks
    objects = [ws]

    for ls in lists:
        objects.append(ls)

    unused_ranks = list(range(1, len(objects)+1))
    
    checks.check_unused_ranks(unused_ranks, len(objects))
    
    return generate_ranks(objects, unused_ranks) # list_ranks

def get_rank_of_list(ws: Workspace, ls: List) -> tuple:
    """
    Takes in a workspace and a list which is inside that workspace.
    Returns the rank of that list
    """
    list_ranks = get_ranks_of_lists_in_workspace(ws)

    for list_rank in list_ranks:
        if list_rank[0] == ls.id:
            return list_ranks

def get_ranks_of_tasks_in_list(ws: Workspace, ls: List, used_ranks: list) -> list:
    """
    Takes in a workspace and a list.
    Generates ranks of only the tasks in a list.
    used_ranks is a list of ranks that have already been used. 
    This function starts off at the end of used_ranks. 
    used_ranks is expected to be sorted.
    """
    tasks = get_tasks_in_list(ls)
    unused_ranks = list(range((used_ranks[-1][1])+1, ((used_ranks[-1][1])+len(tasks))+1))

    return generate_ranks(tasks, unused_ranks)

def get_rank_of_task(task: Task):
    c_ws_id = fileutils.get_current_workspace_id()
    c_ws = get_workspace_from_id(c_ws_id)

    # TODO: Maybe update this later to be faster
    task_ranks = get_ranks_of_tasks_in_workspace(c_ws)
            
    for task_rank in task_ranks:
        if task.id == task_rank[0]:
            return task_rank

def get_tasks_in_workspace(ws:Workspace) -> list:
    lists = get_lists_in_workspace(ws)

    tasks_in_workspace = []

    for ls in lists:
        tasks = get_tasks_in_list(ls)

        tasks_in_workspace += tasks

    return tasks_in_workspace

def get_rank_from_task_id(task_id: int, c_ws: Workspace) -> int:
    """
    Returns only the rank
    """
    task_ranks = get_ranks_of_tasks_in_workspace(c_ws)

    for task_rank in task_ranks:
        if task_rank[0] == task_id:
            return task_rank[1]
        
def get_rank_from_list_id(ls_id: int, c_ws: Workspace) -> int:
    """
    Returns only the rank
    """

    list_ranks = get_ranks_of_lists_in_workspace(c_ws)

    for ls_rank in list_ranks:
        if ls_rank[0] == ls_id:
            return ls_rank[1]
            
def get_ranks_of_tasks_in_workspace(ws: Workspace) -> list:
    """
    Gets ranks of all tasks in a workspace in a tuple
    """

    tasks = get_tasks_in_workspace(ws)

    list_ranks = get_ranks_of_lists_in_workspace(ws)
    
    formatted_list_ranks = [list_rank[1] for list_rank in list_ranks]
    formatted_list_ranks.sort()

    first_rank = formatted_list_ranks[-1]+1 # Add one to the greatest rank
    last_rank = formatted_list_ranks[-1] + len(tasks) + 1

    unused_ranks = list(range(first_rank, last_rank))

    task_ranks = generate_ranks(tasks, unused_ranks)

    return task_ranks

def get_rank_of_workspace_from_id(ws_id: int) -> int:
    objects = fileutils.get_workspaces()

    unused_ranks = list(range(1, len(objects)+1))

    ws_ranks = generate_ranks(objects, unused_ranks)

    for ws_rank in ws_ranks:
        if ws_rank[0] == ws_id:
            return ws_rank[1]
