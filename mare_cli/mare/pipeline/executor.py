"""
MARE CLI - Pipeline Executor
High-level interface for executing MARE pipeline from CLI
"""

from typing import Any, Dict, Optional, List
from pathlib import Path
import json
from datetime import datetime

from mare.pipeline.mare_pipeline import MAREPipeline, PipelineConfig, PipelineState, PipelineStatus
from mare.utils.logging import MARELoggerMixin
from mare.utils.exceptions import PipelineExecutionError, ConfigurationError
from mare.utils.helpers import read_yaml_file, write_json_file, read_text_file


class PipelineExecutor(MARELoggerMixin):
    """
    High-level executor for the MARE pipeline.
    
    Provides a simple interface for CLI commands to execute the pipeline
    with proper configuration management and result handling.
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize the pipeline executor.
        
        Args:
            project_path: Path to the MARE project directory
        """
        self.project_path = project_path
        self.config_path = project_path / ".mare" / "config.yaml"
        self.workspace_path = project_path / ".mare" / "workspace"
        
        # Load configuration
        self.project_config = self._load_project_config()
        self.pipeline_config = self._create_pipeline_config()
        
        # Initialize pipeline
        self.pipeline = MAREPipeline(self.pipeline_config)
        
        self.log_info(f"Pipeline executor initialized for project: {project_path.name}")
    
    def _load_project_config(self) -> Dict[str, Any]:
        """Load project configuration from config.yaml."""
        try:
            if not self.config_path.exists():
                raise ConfigurationError(
                    "Project configuration file not found",
                    config_file=str(self.config_path)
                )
            
            config = read_yaml_file(self.config_path)
            self.log_info("Project configuration loaded successfully")
            return config
            
        except Exception as e:
            self.log_error(f"Failed to load project configuration: {e}")
            raise ConfigurationError(
                f"Failed to load project configuration: {e}",
                config_file=str(self.config_path)
            )
    
    def _create_pipeline_config(self) -> PipelineConfig:
        """Create pipeline configuration from project config."""
        pipeline_settings = self.project_config.get("pipeline", {})
        agent_settings = self.project_config.get("agents", {})
        
        return PipelineConfig(
            max_iterations=pipeline_settings.get("max_iterations", 5),
            quality_threshold=pipeline_settings.get("quality_threshold", 0.8),
            auto_advance=pipeline_settings.get("auto_advance", True),
            interactive_mode=False,  # Will be set by CLI
            agent_configs=agent_settings
        )
    
    def execute_pipeline(
        self,
        input_file: Optional[str] = None,
        interactive: bool = False,
        max_iterations: Optional[int] = None,
        timeout: Optional[int] = 300,  # 5 minutes default timeout
        progress_tracker = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the complete MARE pipeline.
        
        Args:
            input_file: Optional input file with requirements
            interactive: Run in interactive mode
            max_iterations: Override max iterations
            timeout: Maximum execution time in seconds
            
        Returns:
            Execution results
        """
        import signal
        import time
        
        self.log_info("Starting full pipeline execution")
        
        # Check for recent successful execution
        recent_execution = self._check_recent_execution()
        if recent_execution and recent_execution.get('status') == 'completed':
            quality_score = recent_execution.get('quality_score', 0)
            if quality_score >= self.pipeline_config.quality_threshold:
                self.log_info(f"Found recent successful execution with quality {quality_score}")
                # Load artifacts from workspace for recent execution
                recent_execution = self._load_artifacts_for_execution(recent_execution)
                return recent_execution
        
        try:
            # Set timeout handler
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Pipeline execution timed out after {timeout} seconds")
            
            if timeout:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)
            
            start_time = time.time()
            
            # Update configuration if needed
            if max_iterations is not None:
                self.pipeline_config.max_iterations = max_iterations
            self.pipeline_config.interactive_mode = interactive
            
            # Get input requirements
            system_idea = self._get_system_idea(input_file)
            project_name = self.project_config.get("project", {}).get("name", "Unnamed Project")
            domain = self._infer_domain()
            
            # Execute pipeline with progress monitoring
            self.log_info(f"Executing pipeline for: {project_name}")
            
            if progress_tracker:
                progress_tracker.start_phase("elicitation", "Starting requirements elicitation")
            
            final_state = self.pipeline.execute(
                system_idea, 
                domain, 
                project_name,
                workspace_path=self.workspace_path
            )
            
            execution_time = time.time() - start_time
            self.log_info(f"Pipeline completed in {execution_time:.2f} seconds")
            
            # Cancel timeout
            if timeout:
                signal.alarm(0)
            
            # Save results
            self._save_execution_results(final_state)
            
            # Prepare return data
            result = {
                "status": final_state["status"].value,
                "execution_id": final_state["execution_id"],
                "project_name": project_name,
                "domain": domain,
                "quality_score": final_state["quality_score"],
                "iterations": final_state["iteration_count"],
                "artifacts": {
                    "user_stories": final_state["user_stories"],
                    "requirements": final_state["requirements_draft"],
                    "entities": final_state["entities"],
                    "relationships": final_state["relationships"],
                    "check_results": final_state["check_results"],
                    "final_srs": final_state["final_srs"]
                },
                "issues_found": final_state.get("issues_found", []),
                "error_message": final_state.get("error_message")
            }
            
            self.log_info(f"Pipeline execution completed with status: {final_state['status'].value}")
            return result
            
        except Exception as e:
            self.log_error(f"Pipeline execution failed: {e}")
            raise PipelineExecutionError(f"Pipeline execution failed: {e}")
    
    def execute_phase(
        self,
        phase: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a specific phase of the pipeline.
        
        Args:
            phase: Phase name to execute
            input_data: Optional input data for the phase
            
        Returns:
            Phase execution results
        """
        self.log_info(f"Executing specific phase: {phase}")
        
        # For now, this is a placeholder - full implementation would require
        # more complex state management and partial execution capabilities
        raise NotImplementedError("Phase-specific execution not yet implemented")
    
    def _load_artifacts_for_execution(self, execution_record: Dict[str, Any]) -> Dict[str, Any]:
        """Load artifacts from workspace for a given execution."""
        try:
            execution_id = execution_record["execution_id"]
            artifacts_dir = self.workspace_path / "artifacts" / execution_id
            
            # Load artifacts if they exist
            artifacts = {}
            artifact_files = {
                "user_stories": "user_stories.md",
                "requirements": "requirements.md", 
                "entities": "entities.md",
                "relationships": "relationships.md",
                "check_results": "check_results.md",
                "final_srs": "final_srs.md"
            }
            
            for key, filename in artifact_files.items():
                file_path = artifacts_dir / filename
                if file_path.exists():
                    artifacts[key] = file_path.read_text(encoding='utf-8')
                else:
                    artifacts[key] = ""
            
            # Add artifacts to execution record
            execution_record["artifacts"] = artifacts
            execution_record["issues_found"] = []  # Default empty list
            
            self.log_info(f"Loaded artifacts for execution {execution_id[:8]}...")
            return execution_record
            
        except Exception as e:
            self.log_error(f"Failed to load artifacts for execution: {e}")
            # Return original record if loading fails
            execution_record["artifacts"] = {}
            execution_record["issues_found"] = []
            return execution_record

    def _check_recent_execution(self) -> Optional[Dict[str, Any]]:
        """Check for recent successful execution within the last hour."""
        try:
            from datetime import datetime, timedelta
            import json
            
            executions_file = self.workspace_path / "executions.json"
            if not executions_file.exists():
                return None
            
            with open(executions_file, 'r') as f:
                executions = json.load(f)
            
            if not executions:
                return None
            
            # Get most recent execution
            latest = executions[-1]
            
            # Check if it's within the last hour and successful
            execution_time = datetime.fromisoformat(latest['timestamp'].replace('Z', '+00:00'))
            one_hour_ago = datetime.now().replace(tzinfo=execution_time.tzinfo) - timedelta(hours=1)
            
            if (execution_time > one_hour_ago and 
                latest.get('status') == 'completed' and 
                latest.get('quality_score', 0) >= self.pipeline_config.quality_threshold):
                return latest
            
            return None
            
        except Exception as e:
            self.log_error(f"Error checking recent execution: {e}")
            return None
    
    def _get_system_idea(self, input_file: Optional[Path] = None) -> str:
        """Get system idea from input file or default location."""
        if input_file and input_file.exists():
            return read_text_file(input_file)
        
        # Try default input file
        default_input = self.project_path / "input" / "requirements.md"
        if default_input.exists():
            return read_text_file(default_input)
        
        # Fallback to project description
        project_info = self.project_config.get("project", {})
        return f"Project: {project_info.get('name', 'Unnamed Project')}\nDomain: {project_info.get('domain', 'General Software')}"
    
    def _infer_domain(self) -> str:
        """Infer domain from project configuration or template."""
        project_info = self.project_config.get("project", {})
        
        # Check if domain is explicitly set
        if "domain" in project_info:
            return project_info["domain"]
        
        # Infer from template
        template = project_info.get("template", "basic")
        domain_mapping = {
            "web_app": "web application development",
            "mobile_app": "mobile application development",
            "enterprise": "enterprise software development",
            "basic": "general software system"
        }
        
        return domain_mapping.get(template, "general software system")
    
    def _save_execution_results(self, final_state: PipelineState) -> None:
        """Save execution results to workspace."""
        try:
            # Create execution record
            execution_record = {
                "execution_id": final_state["execution_id"],
                "timestamp": final_state["start_time"].isoformat(),
                "status": final_state["status"].value,
                "project_name": final_state["project_name"],
                "domain": final_state["domain"],
                "quality_score": final_state["quality_score"],
                "iterations": final_state["iteration_count"],
                "error_message": final_state.get("error_message")
            }
            
            # Save execution record
            executions_file = self.workspace_path / "executions.json"
            if executions_file.exists():
                executions = json.loads(executions_file.read_text())
            else:
                executions = []
            
            executions.append(execution_record)
            write_json_file(executions_file, executions)
            
            # Save artifacts if execution was successful
            if final_state["status"] == PipelineStatus.COMPLETED:
                artifacts_dir = self.workspace_path / "artifacts" / final_state["execution_id"]
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                
                # Save individual artifacts
                artifacts = {
                    "user_stories.md": final_state["user_stories"],
                    "requirements.md": final_state["requirements_draft"],
                    "entities.md": final_state["entities"],
                    "relationships.md": final_state["relationships"],
                    "check_results.md": final_state["check_results"],
                    "final_srs.md": final_state["final_srs"]
                }
                
                for filename, content in artifacts.items():
                    if content:
                        (artifacts_dir / filename).write_text(content, encoding='utf-8')
                
                # Copy final SRS to output directory
                output_dir = self.project_path / "output"
                output_dir.mkdir(exist_ok=True)
                if final_state["final_srs"]:
                    (output_dir / "requirements_specification.md").write_text(
                        final_state["final_srs"], 
                        encoding='utf-8'
                    )
            
            self.log_info("Execution results saved successfully")
            
        except Exception as e:
            self.log_error(f"Failed to save execution results: {e}")
            # Don't raise exception here - execution was successful, just saving failed
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of pipeline executions."""
        try:
            executions_file = self.workspace_path / "executions.json"
            if executions_file.exists():
                return json.loads(executions_file.read_text())
            return []
            
        except Exception as e:
            self.log_error(f"Failed to load execution history: {e}")
            return []
    
    def get_latest_execution(self) -> Optional[Dict[str, Any]]:
        """Get the latest pipeline execution."""
        history = self.get_execution_history()
        return history[-1] if history else None
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get comprehensive project status."""
        latest_execution = self.get_latest_execution()
        
        status = {
            "project_name": self.project_config.get("project", {}).get("name", "Unnamed Project"),
            "project_path": str(self.project_path),
            "configuration": {
                "template": self.project_config.get("project", {}).get("template"),
                "llm_provider": self.project_config.get("llm", {}).get("provider"),
                "max_iterations": self.pipeline_config.max_iterations,
                "quality_threshold": self.pipeline_config.quality_threshold
            },
            "execution_status": {
                "last_execution": latest_execution,
                "total_executions": len(self.get_execution_history())
            },
            "artifacts": self._get_artifacts_summary()
        }
        
        return status
    
    def _get_artifacts_summary(self) -> Dict[str, Any]:
        """Get summary of available artifacts."""
        artifacts_dir = self.workspace_path / "artifacts"
        output_dir = self.project_path / "output"
        
        summary = {
            "workspace_artifacts": 0,
            "output_files": 0,
            "latest_srs": None
        }
        
        if artifacts_dir.exists():
            summary["workspace_artifacts"] = len(list(artifacts_dir.glob("*")))
        
        if output_dir.exists():
            output_files = list(output_dir.glob("*"))
            summary["output_files"] = len(output_files)
            
            # Check for latest SRS
            srs_file = output_dir / "requirements_specification.md"
            if srs_file.exists():
                summary["latest_srs"] = str(srs_file)
        
        return summary

