import sys
import importlib.util

from pathlib import Path

def get_module_from_file(file: Path):
    blocks_file__path = file.absolute()
    # get imports in the blocks file to work
    sys.path.insert(0, str(file.parent))

    spec = importlib.util.spec_from_file_location(
        "automation_module", blocks_file__path
    )
    automation_module = importlib.util.module_from_spec(spec)
    sys.modules["automation_module"] = automation_module
    spec.loader.exec_module(automation_module)

    return automation_module

def get_blocks_state_and_module_from_file(file: Path):    
    automation_module = get_module_from_file(file)
    has_blocks_import = hasattr(automation_module, "blocks")
    has_task_import = hasattr(automation_module, "task")
    has_agent_import = hasattr(automation_module, "agent")

    if not any([has_blocks_import, has_task_import, has_agent_import]):
        raise Exception("No blocks, task, or agent import found in the specified file, likely not an automation file.")
    if has_blocks_import:
        state = automation_module.state.dag
    elif has_task_import:
        state = automation_module.task.blocks_state
    elif has_agent_import:
        state = automation_module.agent.blocks_state
    
    return state, automation_module