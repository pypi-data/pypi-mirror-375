#!/usr/bin/env python3
"""
LLM Intelligence Projects Module

Project management with Pydantic validation and JSON registry.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator

# Setup logging
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status enum - exactly as specified by user."""
    READY = "ready"
    IN_PROGRESS = "in_progress" 
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"


class AssigneeType(str, Enum):
    """Assignee type enum."""
    HUMAN = "HUMAN"
    AI = "AI"


class Task(BaseModel):
    """Task model with status tracking."""
    task_id: str = Field(..., description="Task identifier")
    spec: Optional["TaskSpec"] = Field(None, description="Task rollup specification")
    status: TaskStatus = Field(TaskStatus.READY, description="Current task status")
    is_blocked: bool = Field(False, description="Whether task is blocked")
    blocked_description: Optional[str] = Field(None, description="Why task is blocked")
    is_ready: bool = Field(False, description="Whether task is ready to work on")
    assignee: AssigneeType = Field(..., description="Who is assigned to this task")
    agent_id: Optional[str] = Field(None, description="Agent ID if assignee is AI")
    human_name: Optional[str] = Field(None, description="Human name if assignee is HUMAN")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @validator('agent_id')
    def validate_agent_id(cls, v, values):
        assignee = values.get('assignee')
        if assignee == AssigneeType.AI and not v:
            raise ValueError('agent_id is required when assignee is AI')
        if assignee == AssigneeType.HUMAN and v:
            raise ValueError('agent_id should not be set when assignee is HUMAN')
        return v
    
    @validator('human_name')
    def validate_human_name(cls, v, values):
        assignee = values.get('assignee')
        if assignee == AssigneeType.HUMAN and not v:
            raise ValueError('human_name is required when assignee is HUMAN')
        if assignee == AssigneeType.AI and v:
            raise ValueError('human_name should not be set when assignee is AI')
        return v


class FeatureSpec(BaseModel):
    """Feature specification."""
    spec_file_path: str = Field(..., description="Path to feature spec JSON file")
    status: str = Field("draft", description="draft|review|approved")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ComponentSpec(BaseModel):
    """Component specification."""
    spec_file_path: str = Field(..., description="Path to component spec JSON file")
    status: str = Field("draft", description="draft|review|approved")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class DeliverableSpec(BaseModel):
    """Deliverable specification."""
    spec_file_path: str = Field(..., description="Path to deliverable spec JSON file")
    status: str = Field("draft", description="draft|review|approved")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class TaskSpec(BaseModel):
    """Task rollup specification containing all parent specs."""
    spec_file_path: str = Field(..., description="Path to task rollup spec JSON file")
    status: str = Field("draft", description="draft|review|approved")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Deliverable(BaseModel):
    """Deliverable containing tasks that produce it."""
    deliverable_name: str = Field(..., description="Deliverable name")
    spec: Optional[DeliverableSpec] = Field(None, description="Deliverable specification")
    tasks: Dict[str, Task] = Field(default_factory=dict, description="Tasks that produce this deliverable")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Component(BaseModel):
    """Component containing deliverables."""
    component_name: str = Field(..., description="Component name")
    spec: Optional[ComponentSpec] = Field(None, description="Component specification")
    deliverables: Dict[str, Deliverable] = Field(default_factory=dict, description="Deliverables in this component")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Feature(BaseModel):
    """Feature containing components."""
    feature_name: str = Field(..., description="Feature name")
    spec: Optional[FeatureSpec] = Field(None, description="Feature specification")
    components: Dict[str, Component] = Field(default_factory=dict, description="Components in this feature")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Project(BaseModel):
    """Pydantic model for project data validation."""
    
    project_id: str = Field(..., description="Unique project identifier")
    project_dir: str = Field(..., description="Path to project directory") 
    mode: str = Field("planning", description="Current project mode: planning|execution")
    starlog_path: Optional[str] = Field(None, description="Optional path to STARLOG project")
    features: Dict[str, Feature] = Field(default_factory=dict, description="Features in this project")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @validator('project_id')
    def validate_project_id(cls, v):
        if not v.strip():
            raise ValueError('project_id cannot be empty')
        return v.strip()
    
    @validator('project_dir')
    def validate_project_dir(cls, v):
        if not v.strip():
            raise ValueError('project_dir cannot be empty')
        return v.strip()
    
    @validator('starlog_path')
    def validate_starlog_path(cls, v):
        if v is not None and not v.strip():
            raise ValueError('starlog_path cannot be empty string, use None instead')
        return v.strip() if v else None


class ProjectRegistry:
    """Manages projects registry with JSON persistence."""
    
    def __init__(self, registry_path: Optional[str] = None):
        if registry_path:
            self.registry_path = Path(registry_path)
        else:
            base_dir = Path(os.environ.get("LLM_INTELLIGENCE_DIR", "/tmp/llm_intelligence_responses"))
            base_dir.mkdir(parents=True, exist_ok=True)
            self.registry_path = base_dir / "projects.json"
    
    def _load_projects(self) -> Dict[str, Project]:
        """Load projects from JSON file."""
        if not self.registry_path.exists():
            return {}
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to Project objects with Pydantic validation
            projects = {}
            for project_id, project_data in data.items():
                try:
                    projects[project_id] = Project(**project_data)
                except Exception as e:
                    logger.error(f"Invalid project data for {project_id}: {e}")
                    continue
            
            return projects
        except Exception as e:
            logger.error(f"Failed to load projects registry: {e}", exc_info=True)
            return {}
    
    def _save_projects(self, projects: Dict[str, Project]) -> None:
        """Save projects to JSON file."""
        try:
            # Convert Project objects to dict for JSON serialization
            data = {project_id: project.dict() for project_id, project in projects.items()}
            
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved projects registry: {self.registry_path}")
        except Exception as e:
            logger.error(f"Failed to save projects registry: {e}", exc_info=True)
            raise
    
    def create_project(
        self, 
        project_id: str, 
        project_dir: str, 
        starlog_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new project with validation."""
        try:
            # Validate through Pydantic
            project = Project(
                project_id=project_id,
                project_dir=project_dir,
                starlog_path=starlog_path
            )
            
            # Load existing projects
            projects = self._load_projects()
            
            # Check if project already exists
            if project_id in projects:
                return {"error": f"Project {project_id} already exists"}
            
            # Add new project
            projects[project_id] = project
            
            # Save to file
            self._save_projects(projects)
            
            logger.info(f"Created project: {project_id}")
            return {
                "success": True,
                "project": project.dict(),
                "message": f"Project {project_id} created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create project {project_id}: {e}", exc_info=True)
            return {"error": f"Failed to create project: {e}"}
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project by ID."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
            
            return {
                "success": True,
                "project": projects[project_id].dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}", exc_info=True)
            return {"error": f"Failed to get project: {e}"}
    
    def update_project(
        self,
        project_id: str,
        project_dir: Optional[str] = None,
        starlog_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update existing project."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
            
            # Get current project
            current_project = projects[project_id]
            
            # Update fields if provided
            updated_data = current_project.dict()
            if project_dir is not None:
                updated_data["project_dir"] = project_dir
            if starlog_path is not None:
                updated_data["starlog_path"] = starlog_path
            updated_data["updated_at"] = datetime.now().isoformat()
            
            # Validate updated project
            updated_project = Project(**updated_data)
            
            # Save updated project
            projects[project_id] = updated_project
            self._save_projects(projects)
            
            logger.info(f"Updated project: {project_id}")
            return {
                "success": True,
                "project": updated_project.dict(),
                "message": f"Project {project_id} updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}", exc_info=True)
            return {"error": f"Failed to update project: {e}"}
    
    def list_projects(self) -> Dict[str, Any]:
        """List all projects."""
        try:
            projects = self._load_projects()
            
            project_list = [project.dict() for project in projects.values()]
            # Sort by created_at
            project_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return {
                "success": True,
                "projects": project_list,
                "total": len(project_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to list projects: {e}", exc_info=True)
            return {"error": f"Failed to list projects: {e}"}
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete project by ID."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
            
            # Remove project
            del projects[project_id]
            
            # Save updated registry
            self._save_projects(projects)
            
            logger.info(f"Deleted project: {project_id}")
            return {
                "success": True,
                "message": f"Project {project_id} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}", exc_info=True)
            return {"error": f"Failed to delete project: {e}"}
    
    def add_feature_to_project(self, project_id: str, feature_name: str) -> Dict[str, Any]:
        """Add feature to project."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
            
            if feature_name in projects[project_id].features:
                return {"error": f"Feature {feature_name} already exists in project {project_id}"}
            
            # Add feature
            projects[project_id].features[feature_name] = Feature(feature_name=feature_name)
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Added feature {feature_name} to project {project_id}")
            return {"success": True, "message": f"Feature {feature_name} added to project {project_id}"}
            
        except Exception as e:
            logger.error(f"Failed to add feature {feature_name} to project {project_id}: {e}", exc_info=True)
            return {"error": f"Failed to add feature: {e}"}
    
    def add_component_to_feature(self, project_id: str, feature_name: str, component_name: str) -> Dict[str, Any]:
        """Add component to feature."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
                
            if feature_name not in projects[project_id].features:
                return {"error": f"Feature {feature_name} not found in project {project_id}"}
            
            if component_name in projects[project_id].features[feature_name].components:
                return {"error": f"Component {component_name} already exists in feature {feature_name}"}
            
            # Add component
            projects[project_id].features[feature_name].components[component_name] = Component(component_name=component_name)
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Added component {component_name} to feature {feature_name} in project {project_id}")
            return {"success": True, "message": f"Component {component_name} added to feature {feature_name}"}
            
        except Exception as e:
            logger.error(f"Failed to add component {component_name} to feature {feature_name}: {e}", exc_info=True)
            return {"error": f"Failed to add component: {e}"}
    
    def add_deliverable_to_component(self, project_id: str, feature_name: str, component_name: str, deliverable_name: str) -> Dict[str, Any]:
        """Add deliverable to component."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
                
            if feature_name not in projects[project_id].features:
                return {"error": f"Feature {feature_name} not found in project {project_id}"}
            
            if component_name not in projects[project_id].features[feature_name].components:
                return {"error": f"Component {component_name} not found in feature {feature_name}"}
            
            if deliverable_name in projects[project_id].features[feature_name].components[component_name].deliverables:
                return {"error": f"Deliverable {deliverable_name} already exists in component {component_name}"}
            
            # Add deliverable
            projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name] = Deliverable(
                deliverable_name=deliverable_name
            )
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Added deliverable {deliverable_name} to component {component_name}")
            return {"success": True, "message": f"Deliverable {deliverable_name} added to component {component_name}"}
            
        except Exception as e:
            logger.error(f"Failed to add deliverable {deliverable_name} to component {component_name}: {e}", exc_info=True)
            return {"error": f"Failed to add deliverable: {e}"}

    def add_task_to_deliverable(self, project_id: str, feature_name: str, component_name: str, deliverable_name: str, task_id: str, is_human_only_task: bool, agent_id: Optional[str] = None, human_name: Optional[str] = None) -> Dict[str, Any]:
        """Add task to deliverable."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
                
            if feature_name not in projects[project_id].features:
                return {"error": f"Feature {feature_name} not found in project {project_id}"}
            
            if component_name not in projects[project_id].features[feature_name].components:
                return {"error": f"Component {component_name} not found in feature {feature_name}"}
            
            if deliverable_name not in projects[project_id].features[feature_name].components[component_name].deliverables:
                return {"error": f"Deliverable {deliverable_name} not found in component {component_name}"}
            
            if task_id in projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name].tasks:
                return {"error": f"Task {task_id} already exists in deliverable {deliverable_name}"}
            
            # Determine assignee based on is_human_only_task
            if is_human_only_task:
                assignee = AssigneeType.HUMAN
                if not human_name:
                    return {"error": "human_name is required for human-only tasks"}
            else:
                assignee = AssigneeType.AI
                if not agent_id:
                    return {"error": "agent_id is required for AI tasks"}
            
            # Add task
            projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name].tasks[task_id] = Task(
                task_id=task_id,
                assignee=assignee,
                agent_id=agent_id,
                human_name=human_name
            )
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Added task {task_id} to deliverable {deliverable_name}")
            return {"success": True, "message": f"Task {task_id} added to deliverable {deliverable_name}"}
            
        except Exception as e:
            logger.error(f"Failed to add task {task_id} to deliverable {deliverable_name}: {e}", exc_info=True)
            return {"error": f"Failed to add task: {e}"}
    
    def add_spec_to_feature(self, project_id: str, feature_name: str, spec_file_path: str) -> Dict[str, Any]:
        """Add spec to feature."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
                
            if feature_name not in projects[project_id].features:
                return {"error": f"Feature {feature_name} not found in project {project_id}"}
            
            # Add feature spec
            projects[project_id].features[feature_name].spec = FeatureSpec(spec_file_path=spec_file_path)
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Added spec to feature {feature_name}")
            return {"success": True, "message": f"Spec added to feature {feature_name}"}
            
        except Exception as e:
            logger.error(f"Failed to add spec to feature {feature_name}: {e}", exc_info=True)
            return {"error": f"Failed to add spec: {e}"}
    
    def add_spec_to_component(self, project_id: str, feature_name: str, component_name: str, spec_file_path: str) -> Dict[str, Any]:
        """Add spec to component."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
                
            if feature_name not in projects[project_id].features:
                return {"error": f"Feature {feature_name} not found in project {project_id}"}
            
            if component_name not in projects[project_id].features[feature_name].components:
                return {"error": f"Component {component_name} not found in feature {feature_name}"}
            
            # Add component spec
            projects[project_id].features[feature_name].components[component_name].spec = ComponentSpec(spec_file_path=spec_file_path)
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Added spec to component {component_name}")
            return {"success": True, "message": f"Spec added to component {component_name}"}
            
        except Exception as e:
            logger.error(f"Failed to add spec to component {component_name}: {e}", exc_info=True)
            return {"error": f"Failed to add spec: {e}"}
    
    def add_spec_to_deliverable(self, project_id: str, feature_name: str, component_name: str, deliverable_name: str, spec_file_path: str) -> Dict[str, Any]:
        """Add spec to deliverable."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
                
            if feature_name not in projects[project_id].features:
                return {"error": f"Feature {feature_name} not found in project {project_id}"}
            
            if component_name not in projects[project_id].features[feature_name].components:
                return {"error": f"Component {component_name} not found in feature {feature_name}"}
            
            if deliverable_name not in projects[project_id].features[feature_name].components[component_name].deliverables:
                return {"error": f"Deliverable {deliverable_name} not found in component {component_name}"}
            
            # Add deliverable spec
            projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name].spec = DeliverableSpec(spec_file_path=spec_file_path)
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Added spec to deliverable {deliverable_name}")
            return {"success": True, "message": f"Spec added to deliverable {deliverable_name}"}
            
        except Exception as e:
            logger.error(f"Failed to add spec to deliverable {deliverable_name}: {e}", exc_info=True)
            return {"error": f"Failed to add spec: {e}"}
    
    def add_spec_to_task(self, project_id: str, feature_name: str, component_name: str, deliverable_name: str, task_id: str, spec_file_path: str) -> Dict[str, Any]:
        """Add rollup spec to task."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
                
            if feature_name not in projects[project_id].features:
                return {"error": f"Feature {feature_name} not found in project {project_id}"}
            
            if component_name not in projects[project_id].features[feature_name].components:
                return {"error": f"Component {component_name} not found in feature {feature_name}"}
            
            if deliverable_name not in projects[project_id].features[feature_name].components[component_name].deliverables:
                return {"error": f"Deliverable {deliverable_name} not found in component {component_name}"}
            
            if task_id not in projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name].tasks:
                return {"error": f"Task {task_id} not found in deliverable {deliverable_name}"}
            
            # Add task rollup spec
            projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name].tasks[task_id].spec = TaskSpec(spec_file_path=spec_file_path)
            
            # Check if task now has complete specs and mark as ready if so
            if self._task_has_complete_specs(projects[project_id], feature_name, component_name, deliverable_name, task_id):
                projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name].tasks[task_id].is_ready = True
                logger.info(f"Task {task_id} now has complete specs and is marked ready")
            
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Added rollup spec to task {task_id}")
            return {"success": True, "message": f"Rollup spec added to task {task_id}"}
            
        except Exception as e:
            logger.error(f"Failed to add spec to task {task_id}: {e}", exc_info=True)
            return {"error": f"Failed to add spec: {e}"}
    
    def update_project_mode(self, project_id: str, mode: str) -> Dict[str, Any]:
        """Update project mode and save to JSON."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
            
            # Update mode
            projects[project_id].mode = mode
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Updated project {project_id} mode to {mode}")
            return {"success": True, "message": f"Project {project_id} mode updated to {mode}"}
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id} mode: {e}", exc_info=True)
            return {"error": f"Failed to update project mode: {e}"}
    
    def _task_has_complete_specs(self, project: Project, feature_name: str, component_name: str, deliverable_name: str, task_id: str) -> bool:
        """Check if task has complete spec hierarchy (feature, component, deliverable, task specs)."""
        try:
            feature = project.features.get(feature_name)
            if not feature or not feature.spec:
                return False
            
            component = feature.components.get(component_name) 
            if not component or not component.spec:
                return False
                
            deliverable = component.deliverables.get(deliverable_name)
            if not deliverable or not deliverable.spec:
                return False
                
            task = deliverable.tasks.get(task_id)
            if not task or not task.spec:
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error checking task specs: {e}")
            return False
    
    def update_task_status(
        self, 
        project_id: str, 
        feature_name: str, 
        component_name: str, 
        deliverable_name: str,
        task_id: str,
        is_done: bool,
        is_blocked: bool,
        blocked_description: Optional[str],
        is_ready: bool
    ) -> Dict[str, Any]:
        """Update task status."""
        try:
            projects = self._load_projects()
            
            if project_id not in projects:
                return {"error": f"Project {project_id} not found"}
                
            if feature_name not in projects[project_id].features:
                return {"error": f"Feature {feature_name} not found in project {project_id}"}
            
            if component_name not in projects[project_id].features[feature_name].components:
                return {"error": f"Component {component_name} not found in feature {feature_name}"}
            
            if deliverable_name not in projects[project_id].features[feature_name].components[component_name].deliverables:
                return {"error": f"Deliverable {deliverable_name} not found in component {component_name}"}
            
            if task_id not in projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name].tasks:
                return {"error": f"Task {task_id} not found in deliverable {deliverable_name}"}
            
            # Get task
            task = projects[project_id].features[feature_name].components[component_name].deliverables[deliverable_name].tasks[task_id]
            
            # Update status based on parameters
            if is_blocked:
                task.status = TaskStatus.BLOCKED
                task.blocked_description = blocked_description
            elif is_done:
                task.status = TaskStatus.IN_REVIEW  # is_done sets to in_review, not done
            elif task.status == TaskStatus.READY and is_ready:
                task.status = TaskStatus.IN_PROGRESS
            
            # Validate specs before allowing is_ready=True
            if is_ready and not self._task_has_complete_specs(projects[project_id], feature_name, component_name, deliverable_name, task_id):
                return {"error": f"Task {task_id} cannot be ready - missing required specs (feature, component, deliverable, and task specs must all exist)"}
            
            task.is_blocked = is_blocked
            task.is_ready = is_ready
            task.updated_at = datetime.now().isoformat()
            
            projects[project_id].updated_at = datetime.now().isoformat()
            
            # Save
            self._save_projects(projects)
            
            logger.info(f"Updated task {task_id} status to {task.status}")
            return {
                "success": True, 
                "task": task.dict(),
                "message": f"Task {task_id} status updated to {task.status}"
            }
            
        except Exception as e:
            logger.error(f"Failed to update task {task_id} status: {e}", exc_info=True)
            return {"error": f"Failed to update task status: {e}"}


# Global registry instance
_registry = None

def get_registry() -> ProjectRegistry:
    """Get or create global project registry."""
    global _registry
    if _registry is None:
        _registry = ProjectRegistry()
    return _registry


# Convenience functions
def create_project(project_id: str, project_dir: str, starlog_path: Optional[str] = None) -> Dict[str, Any]:
    """Create a new project."""
    return get_registry().create_project(project_id, project_dir, starlog_path)

def get_project(project_id: str) -> Dict[str, Any]:
    """Get project by ID.""" 
    return get_registry().get_project(project_id)

def update_project(project_id: str, project_dir: Optional[str] = None, starlog_path: Optional[str] = None) -> Dict[str, Any]:
    """Update existing project."""
    return get_registry().update_project(project_id, project_dir, starlog_path)

def list_projects() -> Dict[str, Any]:
    """List all projects."""
    return get_registry().list_projects()

def delete_project(project_id: str) -> Dict[str, Any]:
    """Delete project by ID."""
    return get_registry().delete_project(project_id)

def add_feature_to_project(project_id: str, feature_name: str) -> Dict[str, Any]:
    """Add feature to project."""
    return get_registry().add_feature_to_project(project_id, feature_name)

def add_component_to_feature(project_id: str, feature_name: str, component_name: str) -> Dict[str, Any]:
    """Add component to feature."""
    return get_registry().add_component_to_feature(project_id, feature_name, component_name)

def add_deliverable_to_component(project_id: str, feature_name: str, component_name: str, deliverable_name: str) -> Dict[str, Any]:
    """Add deliverable to component."""
    return get_registry().add_deliverable_to_component(project_id, feature_name, component_name, deliverable_name)

def add_task_to_deliverable(project_id: str, feature_name: str, component_name: str, deliverable_name: str, task_id: str, is_human_only_task: bool, agent_id: Optional[str] = None, human_name: Optional[str] = None) -> Dict[str, Any]:
    """Add task to deliverable."""
    return get_registry().add_task_to_deliverable(project_id, feature_name, component_name, deliverable_name, task_id, is_human_only_task, agent_id, human_name)

def update_task_status(
    project_id: str, 
    feature_name: str, 
    component_name: str, 
    deliverable_name: str,
    task_id: str,
    is_done: bool,
    is_blocked: bool,
    blocked_description: Optional[str],
    is_ready: bool
) -> Dict[str, Any]:
    """Update task status."""
    return get_registry().update_task_status(
        project_id, feature_name, component_name, deliverable_name, task_id,
        is_done, is_blocked, blocked_description, is_ready
    )

def add_spec_to_feature(project_id: str, feature_name: str, spec_file_path: str) -> Dict[str, Any]:
    """Add spec to feature."""
    return get_registry().add_spec_to_feature(project_id, feature_name, spec_file_path)

def add_spec_to_component(project_id: str, feature_name: str, component_name: str, spec_file_path: str) -> Dict[str, Any]:
    """Add spec to component."""
    return get_registry().add_spec_to_component(project_id, feature_name, component_name, spec_file_path)

def add_spec_to_deliverable(project_id: str, feature_name: str, component_name: str, deliverable_name: str, spec_file_path: str) -> Dict[str, Any]:
    """Add spec to deliverable."""
    return get_registry().add_spec_to_deliverable(project_id, feature_name, component_name, deliverable_name, spec_file_path)

def add_spec_to_task(project_id: str, feature_name: str, component_name: str, deliverable_name: str, task_id: str, spec_file_path: str) -> Dict[str, Any]:
    """Add rollup spec to task."""
    return get_registry().add_spec_to_task(project_id, feature_name, component_name, deliverable_name, task_id, spec_file_path)

def update_project_mode(project_id: str, mode: str) -> Dict[str, Any]:
    """Update project mode."""
    return get_registry().update_project_mode(project_id, mode)