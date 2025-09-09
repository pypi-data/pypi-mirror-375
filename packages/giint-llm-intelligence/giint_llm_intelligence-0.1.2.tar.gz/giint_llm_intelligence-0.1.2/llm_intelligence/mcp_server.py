#!/usr/bin/env python3
"""
LLM Intelligence MCP Server

Thin wrapper that imports business logic from core module.
MCP servers should only contain wrapper functions.
"""

import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

from .core import (
    respond as core_respond,
    report_tool_usage as core_report_tool_usage,
    get_qa_context as core_get_qa_context,
    list_qa_sessions as core_list_qa_sessions,
    llms_must_use_this_to_be_intelligent as core_llms_guide,
    remind_me_what_giint_is as core_giint_reminder
)

from .projects import (
    create_project as core_create_project,
    get_project as core_get_project,
    update_project as core_update_project,
    list_projects as core_list_projects,
    delete_project as core_delete_project,
    add_feature_to_project as core_add_feature_to_project,
    add_component_to_feature as core_add_component_to_feature,
    add_task_to_component as core_add_task_to_component,
    update_task_status as core_update_task_status
)

# Setup logging
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("llm-intelligence")


@mcp.tool()
async def respond(
    qa_id: str,
    user_prompt_description: str,
    one_liner: str,
    key_tags: List[str],
    involved_files: List[str],
    project_id: str,
    feature: str,
    component: str,
    deliverable: str,
    subtask: str,
    task: str,
    workflow_id: str,
    response_file_path: Optional[str] = None,
    simple_response_string: Optional[str] = None,
    is_from_waypoint: bool = False
) -> Dict[str, Any]:
    """
    Harvest response into QA conversation with unified simple/complex interface.
    
    This is a thin wrapper around the core business logic.
    """
    mode = "simple" if simple_response_string else "complex"
    logger.info(f"Processing respond() for qa_id: {qa_id} in {mode} mode")
    return core_respond(
        qa_id=qa_id,
        user_prompt_description=user_prompt_description,
        one_liner=one_liner,
        key_tags=key_tags,
        involved_files=involved_files,
        project_id=project_id,
        feature=feature,
        component=component,
        deliverable=deliverable,
        subtask=subtask,
        task=task,
        workflow_id=workflow_id,
        response_file_path=response_file_path,
        simple_response_string=simple_response_string,
        is_from_waypoint=is_from_waypoint
    )


@mcp.tool()
async def report_tool_usage(
    tools_used: List[str],
    response_file_path: str,
    involved_files: List[str]
) -> Dict[str, Any]:
    """
    Archive tool usage details during work.
    
    This is a thin wrapper around the core business logic.
    """
    logger.info(f"Processing report_tool_usage() for {len(tools_used)} tools")
    return core_report_tool_usage(
        tools_used=tools_used,
        response_file_path=response_file_path,
        involved_files=involved_files
    )


@mcp.tool()
async def get_qa_context(
    qa_id: str,
    last_n: int = 3
) -> Dict[str, Any]:
    """
    Get context from QA file.
    
    This is a thin wrapper around the core business logic.
    """
    logger.info(f"Processing get_qa_context() for qa_id: {qa_id}")
    return core_get_qa_context(qa_id=qa_id, last_n=last_n)


@mcp.tool()
async def list_qa_sessions(
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all QA sessions.
    
    This is a thin wrapper around the core business logic.
    """
    logger.info(f"Processing list_qa_sessions() for project_id: {project_id}")
    return core_list_qa_sessions(project_id=project_id)


@mcp.tool()
async def llms_must_use_this_to_be_intelligent() -> str:
    """
    LLMs must always use this first while responding through normal channels.
    
    LLM Intelligence exposes a new final output channel (response files), and the 
    conversation channel of normal channels becomes a way to think and do work.
    This achieves multi-fire intelligence through cognitive separation.
    
    Returns concise instructions for using the LLM Intelligence system properly.
    """
    logger.info("Providing LLM Intelligence usage guide")
    return core_llms_guide()


@mcp.tool()
async def remind_me_what_giint_is() -> str:
    """
    Reminds what GIINT stands for and its purpose.
    
    GIINT is what you think it is. General Intuitive Intelligence for Neural Transformers.
    Welcome to GIINT - the cognitive architecture for true AI intelligence.
    
    Returns GIINT definition and welcome message.
    """
    logger.info("Providing GIINT definition")
    return core_giint_reminder()


# Project Management Tools

@mcp.tool()
async def create_project(
    project_id: str,
    project_dir: str,
    starlog_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new project with validation.
    
    Args:
        project_id: Unique project identifier
        project_dir: Path to project directory
        starlog_path: Optional path to STARLOG project
        
    Returns:
        Project creation result
    """
    logger.info(f"Creating project: {project_id}")
    return core_create_project(project_id, project_dir, starlog_path)


@mcp.tool()
async def get_project(project_id: str) -> Dict[str, Any]:
    """
    Get project by ID.
    
    Args:
        project_id: Project identifier
        
    Returns:
        Project data
    """
    logger.info(f"Getting project: {project_id}")
    return core_get_project(project_id)


@mcp.tool()
async def list_projects() -> Dict[str, Any]:
    """
    List all projects.
    
    Returns:
        List of all projects
    """
    logger.info("Listing all projects")
    return core_list_projects()


@mcp.tool()
async def update_project(
    project_id: str,
    project_dir: Optional[str] = None,
    starlog_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update existing project.
    
    Args:
        project_id: Project identifier
        project_dir: Optional new project directory
        starlog_path: Optional new STARLOG path
        
    Returns:
        Update result
    """
    logger.info(f"Updating project: {project_id}")
    return core_update_project(project_id, project_dir, starlog_path)


@mcp.tool()
async def delete_project(project_id: str) -> Dict[str, Any]:
    """
    Delete project by ID.
    
    Args:
        project_id: Project identifier
        
    Returns:
        Deletion result
    """
    logger.info(f"Deleting project: {project_id}")
    return core_delete_project(project_id)


@mcp.tool()
async def add_feature_to_project(
    project_id: str,
    feature_name: str
) -> Dict[str, Any]:
    """
    Add feature to project.
    
    Args:
        project_id: Project identifier
        feature_name: Name of feature to add
        
    Returns:
        Feature addition result
    """
    logger.info(f"Adding feature {feature_name} to project {project_id}")
    return core_add_feature_to_project(project_id, feature_name)


@mcp.tool()
async def add_component_to_feature(
    project_id: str,
    feature_name: str,
    component_name: str
) -> Dict[str, Any]:
    """
    Add component to feature.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name to add
        
    Returns:
        Component addition result
    """
    logger.info(f"Adding component {component_name} to feature {feature_name}")
    return core_add_component_to_feature(project_id, feature_name, component_name)


@mcp.tool()
async def add_task_to_component(
    project_id: str,
    feature_name: str,
    component_name: str,
    task_id: str,
    is_human_only_task: bool,
    agent_id: Optional[str] = None,
    human_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add task to component.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name
        task_id: Task identifier
        is_human_only_task: Whether task requires human
        agent_id: Agent ID if AI task
        human_name: Human name if human task
        
    Returns:
        Task addition result
    """
    logger.info(f"Adding task {task_id} to component {component_name}")
    return core_add_task_to_component(
        project_id, feature_name, component_name, task_id,
        is_human_only_task, agent_id, human_name
    )


@mcp.tool()
async def update_task_status(
    project_id: str,
    feature_name: str,
    component_name: str,
    task_id: str,
    is_done: bool,
    is_blocked: bool,
    blocked_description: Optional[str],
    is_ready: bool
) -> Dict[str, Any]:
    """
    Update task status.
    
    Args:
        project_id: Project identifier
        feature_name: Feature name
        component_name: Component name  
        task_id: Task identifier
        is_done: Whether task is done
        is_blocked: Whether task is blocked
        blocked_description: Why task is blocked
        is_ready: Whether task is ready
        
    Returns:
        Task status update result
    """
    logger.info(f"Updating status for task {task_id}")
    return core_update_task_status(
        project_id, feature_name, component_name, task_id,
        is_done, is_blocked, blocked_description, is_ready
    )


def main():
    """Entry point for console script."""
    mcp.run()


if __name__ == "__main__":
    main()