"""
This script provides functions that get the set configuration and it also sets default configurations
"""
from rich import print as rprint
from rich.prompt import Confirm

DEFAULT_CONFIGS = {
    "TASK_ID_COLOR": "#EEFF54",
    "TASK_NAME_COLOR": "#00FFBE",
    "TASK_IMPORTANCE_1_COLOR": "#D6FF00",
    "TASK_IMPORTANCE_2_COLOR": "#FF9900",
    "TASK_IMPORTANCE_3_COLOR": "#FF2900",
    "TASK_DESCRIPTION_COLOR" : "#FDE088",
    "TASK_DONE_COLOR": "#40E82A",
    "IMPORTANCE_HEADER_COLOR": "#A66DC3",
    "LIST_ID_COLOR": "#FF6262",
    "LIST_NAME_COLOR": "#4BFFF6",
    "WORKSPACE_ID_COLOR": "#B7F868",
    "WORKSPACE_NAME_COLOR": "#6876F8"
}

def set_default_config(CONFIGPATH):
    with open(CONFIGPATH, mode='w') as f:
        f.write(f"TASK_ID_COLOR={DEFAULT_CONFIGS['TASK_ID_COLOR']}\n")
        f.write(f"TASK_NAME_COLOR={DEFAULT_CONFIGS['TASK_NAME_COLOR']}\n")
        
        f.write(f"IMPORTANCE_HEADER_COLOR={DEFAULT_CONFIGS['IMPORTANCE_HEADER_COLOR']}\n")
        f.write(f"TASK_IMPORTANCE_1_COLOR={DEFAULT_CONFIGS['TASK_IMPORTANCE_1_COLOR']}\n")
        f.write(f"TASK_IMPORTANCE_2_COLOR={DEFAULT_CONFIGS['TASK_IMPORTANCE_2_COLOR']}\n")
        f.write(f"TASK_IMPORTANCE_3_COLOR={DEFAULT_CONFIGS['TASK_IMPORTANCE_3_COLOR']}\n")

        f.write(f"TASK_DONE_COLOR={DEFAULT_CONFIGS['TASK_DONE_COLOR']}\n")        
        f.write(f"TASK_DESCRIPTION_COLOR={DEFAULT_CONFIGS['TASK_DESCRIPTION_COLOR']}\n")
        
        f.write(f"LIST_ID_COLOR={DEFAULT_CONFIGS['LIST_ID_COLOR']}\n")
        f.write(f"LIST_NAME_COLOR={DEFAULT_CONFIGS['LIST_NAME_COLOR']}\n")

        f.write(f"WORKSPACE_ID_COLOR={DEFAULT_CONFIGS['WORKSPACE_ID_COLOR']}\n")
        f.write(f"WORKSPACE_NAME_COLOR={DEFAULT_CONFIGS['WORKSPACE_NAME_COLOR']}\n")

def get_config(CONFIGPATH: str):
    configs = []
    with open(CONFIGPATH, mode='r') as f:
        lines = f.readlines()
        formatted_lines = []

        for line in lines:
            try:
                formatted_lines.append(line[:line.index('=')])
            except ValueError:
                break

        for config_name in DEFAULT_CONFIGS.keys():

            if config_name in formatted_lines:
                line = lines[formatted_lines.index(config_name)]
                line = line.split('=')
                configs.append((config_name, line[1][:-1]))

            else:
                rprint(f"[bold red]Configuration for {config_name} missing![/bold red]")

                if Confirm.ask("Do you want to go back to default configurations?\n[bold red]This will reset all your configurations[/bold red]"):
                    set_default_config(CONFIGPATH)
                    return get_config(CONFIGPATH)

                else:
                    print("Exiting program")
                    quit()
    formatted_configs = {}

    for config_name, value in configs:
        formatted_configs[config_name] = value

    return formatted_configs

def edit_config_value(CONFIGPATH:str, config_to_edit: str, new_value: str):
    
    with open(CONFIGPATH, mode='r') as f:
        lines = f.readlines()

        for index, line in enumerate(lines):
            if config_to_edit in line:
                line = line.split('=')        
                line[1] = new_value + '\n'
                break
        
    lines[index] = "=".join(line)

    with open(CONFIGPATH, mode='w') as f:
        for line in lines:
            f.write(line)
            