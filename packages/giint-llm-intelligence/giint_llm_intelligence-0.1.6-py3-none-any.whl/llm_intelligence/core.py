#!/usr/bin/env python3
"""
LLM Intelligence Core Module

Business logic for the LLM Intelligence system.
MCP server imports and wraps these functions.
"""

import os
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .projects import get_project, update_project_mode

# Setup logging
logger = logging.getLogger(__name__)


def respond(
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
    
    Args:
        qa_id: QA session identifier
        user_prompt_description: LLM's interpretation of user request
        one_liner: Brief summary of what was accomplished
        key_tags: Tags for categorization
        involved_files: Files that were created/modified
        project_id: Project identifier (free-form string)
        feature: Feature being worked on (free-form string)
        component: Component being worked on (free-form string)
        deliverable: Deliverable being created (free-form string)
        subtask: Subtask being handled (free-form string)
        task: Specific task (free-form string)
        workflow_id: Workflow identifier (free-form string)
        response_file_path: Path to response file (complex workflow)
        simple_response_string: Direct response content (simple workflow)
        is_from_waypoint: Whether this is from a STARLOG waypoint
        
    Returns:
        Success confirmation with details
    """
    try:
        # 1. Validate project exists
        project_result = get_project(project_id)
        if "error" in project_result:
            logger.error(f"Project validation failed: {project_result['error']}")
            return {"error": f"Project validation failed: {project_result['error']}"}
        
        # 2. Handle both simple and complex response modes
        if simple_response_string and response_file_path:
            return {"error": "Cannot specify both simple_response_string and response_file_path"}
        
        if not simple_response_string and not response_file_path:
            return {"error": "Must specify either simple_response_string or response_file_path"}
        
        # Configuration
        base_dir = Path(os.environ.get("LLM_INTELLIGENCE_DIR", "/tmp/llm_intelligence_responses"))
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Get response content based on mode
        if simple_response_string:
            response_content = simple_response_string
            response_path = None
        else:
            # Complex mode - read from file
            response_path = Path(response_file_path)
            if not response_path.exists():
                logger.error(f"Response file not found: {response_file_path}")
                return {"error": f"Response file not found: {response_file_path}"}
            
            try:
                with open(response_path, 'r', encoding='utf-8') as f:
                    response_content = f.read()
            except Exception as e:
                logger.error(f"Failed to read response file: {e}", exc_info=True)
                return {"error": f"Failed to read response file: {e}"}
        
        # 2. Set up organized structure
        qa_dir = base_dir / "qa_sets" / qa_id
        qa_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create QA file
        qa_file_path = qa_dir / "qa.json"
        qa_data = _load_qa_file(qa_file_path)
        
        if not qa_data:
            qa_data = {
                "qa_id": qa_id,
                "created_at": datetime.now().isoformat(),
                "project_id": project_id,
                "user_prompt_description": user_prompt_description,
                "tracking": {
                    "feature": feature,
                    "component": component,
                    "deliverable": deliverable,
                    "subtask": subtask,
                    "task": task,
                    "workflow_id": workflow_id,
                    "is_from_waypoint": is_from_waypoint
                },
                "responses": []
            }
        
        # Update tracking with latest info
        qa_data["project_id"] = project_id
        qa_data["tracking"].update({
            "feature": feature,
            "component": component,
            "deliverable": deliverable,
            "subtask": subtask,
            "task": task,
            "workflow_id": workflow_id,
            "is_from_waypoint": is_from_waypoint
        })
        qa_data["last_updated"] = datetime.now().isoformat()
        
        # Determine response number
        response_num = len(qa_data["responses"]) + 1
        
        # 3. Save content to organized structure
        response_dir = qa_dir / "responses" / f"response_{response_num:03d}"
        response_dir.mkdir(parents=True, exist_ok=True)
        organized_response_path = response_dir / "response.md"
        
        if response_path:
            # Complex mode - copy from file
            try:
                shutil.copy2(response_path, organized_response_path)
                logger.info(f"Copied response file to organized structure: {organized_response_path}")
            except Exception as e:
                logger.error(f"Failed to copy response file: {e}", exc_info=True)
                return {"error": f"Failed to copy response file: {e}"}
            
            # Delete original response file (cleanup)
            try:
                os.remove(response_path)
                logger.info(f"Deleted original response file: {response_path}")
            except Exception as e:
                logger.warning(f"Failed to delete original response file {response_path}: {e}")
        else:
            # Simple mode - write content directly
            try:
                with open(organized_response_path, 'w', encoding='utf-8') as f:
                    f.write(response_content)
                logger.info(f"Wrote simple response to organized structure: {organized_response_path}")
            except Exception as e:
                logger.error(f"Failed to write simple response: {e}", exc_info=True)
                return {"error": f"Failed to write simple response: {e}"}
        
        # 5. Update QA conversation - JSON handles all escaping automatically
        response_entry = {
            "response_id": response_num,
            "timestamp": datetime.now().isoformat(),
            "response_content": response_content,  # JSON will escape all content automatically
            "one_liner": one_liner,
            "key_tags": key_tags,
            "involved_files": involved_files,
            "response_file": f"responses/response_{response_num:03d}/response.md"
        }
        
        qa_data["responses"].append(response_entry)
        
        # Save updated QA file - json.dump handles all escaping
        _save_qa_file(qa_file_path, qa_data)
        
        # 6. Log to STARLOG debug diary
        try:
            log_to_starlog_debug_diary(
                qa_id=qa_id,
                response_id=response_num,
                project_id=project_id,
                feature=feature,
                component=component,
                deliverable=deliverable,
                subtask=subtask,
                task=task,
                workflow_id=workflow_id,
                is_from_waypoint=is_from_waypoint,
                one_liner=one_liner
            )
        except Exception as e:
            # Non-fatal - STARLOG integration might not be available
            logger.warning(f"STARLOG logging failed: {e}")
        
        result = {
            "success": True,
            "qa_id": qa_id,
            "response_id": response_num,
            "organized_path": str(organized_response_path),
            "one_liner": one_liner,
            "user_prompt_description": user_prompt_description,
            "tracking": qa_data["tracking"],
            "mode": "simple" if simple_response_string else "complex"
        }
        
        if response_path:
            result["original_path_deleted"] = str(response_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error in respond(): {e}", exc_info=True)
        return {"error": f"Unexpected error: {e}"}


def report_tool_usage(
    tools_used: List[str],
    response_file_path: str,
    involved_files: List[str]
) -> Dict[str, Any]:
    """
    Archive tool usage details during work.
    
    Args:
        tools_used: List of tool names used
        response_file_path: Path to response file being built
        involved_files: Files that were created/modified
        
    Returns:
        Confirmation of tool usage archived
    """
    try:
        logger.info(f"Tool usage reported: {tools_used} for {response_file_path}")
        # For now, just return confirmation
        # Later we can implement actual archiving if needed
        return {
            "success": True,
            "tools_archived": tools_used,
            "files_tracked": involved_files,
            "response_file": response_file_path,
            "message": "Tool usage reported successfully"
        }
    except Exception as e:
        logger.error(f"Failed to report tool usage: {e}", exc_info=True)
        return {"error": f"Failed to report tool usage: {e}"}


def get_qa_context(qa_id: str, last_n: int = 3) -> Dict[str, Any]:
    """
    Get context from QA file.
    
    Args:
        qa_id: QA session identifier
        last_n: Number of recent responses to return
        
    Returns:
        QA context data
    """
    try:
        base_dir = Path(os.environ.get("LLM_INTELLIGENCE_DIR", "/tmp/llm_intelligence_responses"))
        qa_file_path = base_dir / "qa_sets" / qa_id / "qa.json"
        
        qa_data = _load_qa_file(qa_file_path)
        if not qa_data:
            return {"error": f"QA session {qa_id} not found"}
        
        # Return last N responses
        recent_responses = qa_data["responses"][-last_n:] if qa_data["responses"] else []
        
        return {
            "qa_id": qa_data["qa_id"],
            "project_id": qa_data["project_id"],
            "tracking": qa_data["tracking"],
            "total_responses": len(qa_data["responses"]),
            "recent_responses": recent_responses,
            "created_at": qa_data["created_at"],
            "last_updated": qa_data.get("last_updated")
        }
    except Exception as e:
        logger.error(f"Failed to load QA context: {e}", exc_info=True)
        return {"error": f"Failed to load QA context: {e}"}


def list_qa_sessions(project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    List all QA sessions.
    
    Args:
        project_id: Optional project filter
        
    Returns:
        List of QA sessions
    """
    try:
        base_dir = Path(os.environ.get("LLM_INTELLIGENCE_DIR", "/tmp/llm_intelligence_responses"))
        qa_sets_dir = base_dir / "qa_sets"
        
        if not qa_sets_dir.exists():
            return {"sessions": [], "total": 0}
        
        sessions = []
        for qa_dir in qa_sets_dir.iterdir():
            if qa_dir.is_dir():
                qa_file = qa_dir / "qa.json"
                qa_data = _load_qa_file(qa_file)
                if qa_data:
                    # Filter by project if specified
                    if project_id and qa_data.get("project_id") != project_id:
                        continue
                    
                    sessions.append({
                        "qa_id": qa_data["qa_id"],
                        "project_id": qa_data.get("project_id"),
                        "created_at": qa_data["created_at"],
                        "last_updated": qa_data.get("last_updated"),
                        "responses": len(qa_data.get("responses", [])),
                        "one_liner": qa_data["responses"][-1]["one_liner"] if qa_data.get("responses") else None
                    })
        
        # Sort by last updated
        sessions.sort(key=lambda x: x.get("last_updated") or x["created_at"], reverse=True)
        
        return {
            "sessions": sessions,
            "total": len(sessions),
            "filtered_by_project": project_id
        }
    except Exception as e:
        logger.error(f"Failed to list QA sessions: {e}", exc_info=True)
        return {"error": f"Failed to list QA sessions: {e}"}


def _load_qa_file(qa_file_path: Path) -> Optional[Dict[str, Any]]:
    """Load QA file with proper JSON handling."""
    if not qa_file_path.exists():
        return None
    
    try:
        with open(qa_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)  # json.load handles all unescaping automatically
    except Exception as e:
        logger.error(f"Failed to load QA file {qa_file_path}: {e}", exc_info=True)
        return None


def _save_qa_file(qa_file_path: Path, qa_data: Dict[str, Any]) -> None:
    """Save QA file with proper JSON handling."""
    try:
        with open(qa_file_path, 'w', encoding='utf-8') as f:
            # json.dump handles all escaping automatically - no manual escaping needed
            json.dump(qa_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved QA file: {qa_file_path}")
    except Exception as e:
        logger.error(f"Failed to save QA file {qa_file_path}: {e}", exc_info=True)
        raise


def llms_must_use_this_to_be_intelligent() -> str:
    """
    Returns a complete guide for LLMs to use the GIINT system.
    
    Returns:
        Complete usage instructions including decision branches
    """
    return """GIINT - General Intuitive Intelligence for Neural Transformers:

# GIINT Decision Branches
GIINT is a way of being. These two decision branches encapsulate how it works:
- Generally speaking, if the user prompt requires some simple response, just use the respond() tool with respond(..., simple_response_string="...")
  - But when the response is complex, use llms_must_use_this_to_be_intelligent() and then follow the complex workflow.
GIINT is very simple. You don't need to remember everything about it all the time, instead just remember to call llms_must_use_this_to_be_intelligent() and then follow the instructions.

# Complex Workflow (Multi-fire Intelligence)
1. Check/create project: create_project(project_id, project_dir) if needed
2. Write initial response: Write("/tmp/response.md", "Initial insight...")
3. Think more (use tools, explore, research)
4. Edit/expand response: Edit("/tmp/response.md", ...) - ADD MORE INSIGHTS
5. Continue cycle: Think → Edit → Think → Edit (response grows with understanding)
6. Harvest when complete: respond(qa_id, user_prompt_description, one_liner, tags, files, response_file_path="/tmp/response.md")

# Simple Workflow (Direct Response)
respond(qa_id, user_prompt_description, one_liner, tags, files, simple_response_string="Direct answer here")

KEY BREAKTHROUGH: You can edit the response file multiple times before harvesting!
This enables iterative intelligence development within cognitive separation.
Your thinking (tools) stays messy, your communication (response file) evolves and improves."""


def get_current_mode(project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current mode for project or global state.
    
    Args:
        project_id: Project to check mode for (None for global)
        
    Returns:
        Current mode information
    """
    if project_id is None:
        return {"project_id": None, "mode": "freestyle"}
    
    # Get mode from project JSON
    project_result = get_project(project_id)
    if "error" in project_result:
        return {"project_id": project_id, "mode": "planning"}  # Default if project not found
    
    mode = project_result["project"].get("mode", "planning")
    return {"project_id": project_id, "mode": mode}


def set_mode(planning: bool = False, execution: bool = False, freestyle: bool = False, project_id: Optional[str] = None) -> str:
    """
    Set the current working mode for GIINT.
    
    Args:
        planning: Planning mode - create projects, features, components, tasks
        execution: Execution mode - do work using TodoWrite for emergent subtasks  
        freestyle: Freestyle mode - work without project constraints
        project_id: Project to set mode for (required unless freestyle)
        
    Returns:
        Confirmation message with instructions
    """
    # Validate exactly one mode is True
    modes = [planning, execution, freestyle]
    if sum(modes) != 1:
        return "ERROR: Exactly one mode must be True (planning, execution, or freestyle)"
    
    if freestyle:
        if project_id:
            return "ERROR: Freestyle mode cannot have project_id"
        return "MODE SET TO FREESTYLE. Use get_mode_instructions() to continue"
    
    if not project_id:
        return "ERROR: Planning and execution modes require project_id"
    
    # Validate project exists
    project_result = get_project(project_id)
    if "error" in project_result:
        return f"ERROR: Project {project_id} not found"
    
    if execution:
        # Validate tasks are ready for execution mode
        if not _has_ready_tasks(project_id):
            return "ERROR: Mode cannot be execute if no tasks are ready"
        mode = "execution"
    else:
        mode = "planning"
    
    # Update mode in project JSON
    result = update_project_mode(project_id, mode)
    if "error" in result:
        return f"ERROR: Failed to update project mode: {result['error']}"
    
    logger.info(f"Mode set to {mode} for project {project_id}")
    
    return f"MODE SET TO {mode.upper()} for project {project_id}. Use get_mode_instructions() to continue"


def _has_ready_tasks(project_id: str) -> bool:
    """Check if project has any ready tasks."""
    project_result = get_project(project_id)
    if "error" in project_result:
        return False
    
    project = project_result["project"]
    for feature in project.get("features", {}).values():
        for component in feature.get("components", {}).values():
            for deliverable in component.get("deliverables", {}).values():
                for task in deliverable.get("tasks", {}).values():
                    if task.get("is_ready", False):
                        return True
    return False


def get_mode_instructions(freestyle: bool = False, execution: bool = False, planning: bool = False) -> str:
    """
    Get instructions for the specified mode.
    
    Args:
        freestyle: Get freestyle mode instructions
        execution: Get execution mode instructions  
        planning: Get planning mode instructions
    
    Returns:
        Mode-specific instructions
    """
    # Validate exactly one mode is True
    modes = [freestyle, execution, planning]
    if sum(modes) != 1:
        return "ERROR: Exactly one mode must be True (freestyle, execution, or planning)"
    
    if planning:
        return """PLANNING MODE INSTRUCTIONS

Focus: Structure-building mindset

Project Inspection Tools:
• list_projects() - View all existing projects
• get_project(project_id) - Inspect specific project structure
• get_current_mode(project_id) - Check project's current mode

Structure Creation Tools:
• create_project() → add_feature_to_project() → add_component_to_feature() → add_deliverable_to_component() → add_task_to_deliverable()

Spec Management Tools:
• add_spec_to_feature() → add_spec_to_component() → add_spec_to_deliverable() → add_spec_to_task()

Planning Workflow:
1. Inspect existing projects with list_projects() and get_project()
2. Create project structure or modify existing
3. Break down into features, components, deliverables, tasks  
4. Add specs at each level for complete specification
5. Tasks become ready automatically when all specs exist
6. Switch to execution mode when tasks are ready

This mode establishes the architectural foundation."""
    
    elif execution:
        return """EXECUTION MODE INSTRUCTIONS

Focus: Task-completion mindset

Two-Track System:
• TodoWrite - For emergent subtasks and implementation details
• update_task_status() - For formal project task status updates

Execution Workflow:
1. Use TodoWrite to break down current work into actionable steps
2. Complete implementation work iteratively using TodoWrite
3. Update formal project task status with update_task_status() as milestones complete
4. Focus on delivery and implementation details

This mode converts plans into reality."""
    
    else:  # freestyle
        return """FREESTYLE MODE INSTRUCTIONS

Focus: Exploratory mindset
Tools: Any GIINT tools without project constraints

Freestyle Workflow:
1. Work on any task without formal project structure
2. Use respond() for capturing insights
3. Explore, experiment, and iterate freely
4. Switch to planning mode when structure is needed

This mode enables unconstrained exploration."""


def remind_me_what_giint_is() -> str:
    """
    Reminds what GIINT stands for and its purpose.
    
    Returns:
        GIINT definition and welcome message
    """
    return "GIINT is what you think it is. General Intuitive Intelligence for Neural Transformers. Welcome to GIINT"


def log_to_starlog_debug_diary(
    qa_id: str,
    response_id: int,
    project_id: str,
    feature: str,
    component: str,
    deliverable: str,
    subtask: str,
    task: str,
    workflow_id: str,
    is_from_waypoint: bool,
    one_liner: str
) -> None:
    """
    Log to STARLOG debug diary with exact format specified.
    
    Format: {{DATETIME}}.{{QA_ID}}.{{RESPONSE_ID}}.{{PROJECT}}.{{FEATURE}}.{{COMPONENT}}.{{DELIVERABLE}}.{{SUBTASK}}.{{TASK}}.{{WORKFLOW}}.{{IS_FROM_WAYPOINT}}: {{one_liner}}
    """
    try:
        # This would call STARLOG MCP if available
        # For now, just print to show the format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        entry = f"{timestamp}.{qa_id}.{response_id}.{project_id}.{feature}.{component}.{deliverable}.{subtask}.{task}.{workflow_id}.{is_from_waypoint}: {one_liner}"
        
        logger.info(f"STARLOG DEBUG DIARY: {entry}")
        
        # TODO: Implement actual STARLOG integration
        # update_debug_diary(content=entry)
        
    except Exception as e:
        logger.error(f"STARLOG logging failed: {e}", exc_info=True)