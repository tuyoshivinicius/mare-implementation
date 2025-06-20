"""
MARE CLI - Pipeline Implementation
LangGraph-based pipeline for orchestrating MARE agents
"""

from typing import Any, Dict, List, Optional, TypedDict, Annotated
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime
from pathlib import Path

from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage

from mare.agents import (
    AgentFactory, AgentRole, ActionType, AgentConfig,
    StakeholderAgent, CollectorAgent, ModelerAgent, CheckerAgent, DocumenterAgent
)
from mare.workspace import SharedWorkspace
from mare.utils.logging import MARELoggerMixin
from mare.utils.exceptions import PipelineExecutionError


class PipelinePhase(Enum):
    """Enumeration of MARE pipeline phases."""
    ELICITATION = "elicitation"
    MODELING = "modeling"
    VERIFICATION = "verification"
    SPECIFICATION = "specification"


class PipelineStatus(Enum):
    """Enumeration of pipeline execution status."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class PipelineConfig:
    """Configuration for the MARE pipeline."""
    max_iterations: int = 5
    quality_threshold: float = 0.8
    auto_advance: bool = True
    interactive_mode: bool = False
    agent_configs: Optional[Dict[str, Dict[str, Any]]] = None


class PipelineState(TypedDict):
    """State object for the MARE pipeline."""
    # Input data
    system_idea: str
    domain: str
    project_name: str
    
    # Phase tracking
    current_phase: PipelinePhase
    iteration_count: int
    
    # Artifacts
    user_stories: str
    questions: List[str]
    qa_pairs: List[Dict[str, str]]
    requirements_draft: str
    entities: str
    relationships: str
    check_results: str
    final_srs: str
    
    # Quality metrics
    quality_score: float
    issues_found: List[Dict[str, Any]]
    
    # Execution metadata
    execution_id: str
    start_time: datetime
    status: PipelineStatus
    error_message: Optional[str]
    
    # Agent states
    agent_histories: Dict[str, List[Dict[str, Any]]]


class MAREPipeline(MARELoggerMixin):
    """
    MARE Pipeline implementation using LangGraph.
    
    Orchestrates the multi-agent collaboration process through the four phases:
    1. Elicitation - Stakeholder expresses needs, Collector asks questions
    2. Modeling - Modeler extracts entities and relationships
    3. Verification - Checker validates quality and consistency
    4. Specification - Documenter creates final SRS or problem report
    """
    
    def __init__(self, config: PipelineConfig):
        """
        Initialize the MARE pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.agents: Dict[AgentRole, Any] = {}
        self.graph: Optional[StateGraph] = None
        self.workspace: Optional[SharedWorkspace] = None
        self._initialize_agents()
        self._build_graph()
        
        self.log_info("MARE Pipeline initialized")
    
    def _initialize_agents(self) -> None:
        """Initialize all MARE agents."""
        try:
            if self.config.agent_configs:
                self.agents = AgentFactory.create_all_agents(self.config.agent_configs)
            else:
                # Create agents with default configurations
                for role in AgentRole:
                    config = AgentFactory.get_default_config(role)
                    self.agents[role] = AgentFactory.create_agent(role, config)
            
            self.log_info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            self.log_error(f"Failed to initialize agents: {e}")
            raise PipelineExecutionError(f"Agent initialization failed: {e}")
    
    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        try:
            # Create the state graph
            workflow = StateGraph(PipelineState)
            
            # Add nodes for each phase
            workflow.add_node("elicitation", self._elicitation_phase)
            workflow.add_node("modeling", self._modeling_phase)
            workflow.add_node("verification", self._verification_phase)
            workflow.add_node("specification", self._specification_phase)
            workflow.add_node("quality_check", self._quality_check_node)
            workflow.add_node("iteration_control", self._iteration_control_node)
            
            # Define the workflow edges
            workflow.set_entry_point("elicitation")
            
            # Elicitation -> Modeling
            workflow.add_edge("elicitation", "modeling")
            
            # Modeling -> Verification
            workflow.add_edge("modeling", "verification")
            
            # Verification -> Quality Check
            workflow.add_edge("verification", "quality_check")
            
            # Quality Check -> Iteration Control
            workflow.add_edge("quality_check", "iteration_control")
            
            # Iteration Control -> Specification (if quality is good) or back to Elicitation (if needs improvement)
            workflow.add_conditional_edges(
                "iteration_control",
                self._should_continue_iterations,
                {
                    "continue": "elicitation",
                    "specification": "specification",
                    "end": END
                }
            )
            
            # Specification -> END
            workflow.add_edge("specification", END)
            
            # Compile the graph with recursion limit
            self.graph = workflow.compile(
                checkpointer=None,
                interrupt_before=None,
                interrupt_after=None,
                debug=False
            )
            
            # Set recursion limit for the graph
            if hasattr(self.graph, 'config'):
                self.graph.config = {"recursion_limit": self.config.max_iterations + 5}
            
            self.log_info("Pipeline graph built successfully")
            
        except Exception as e:
            self.log_error(f"Failed to build pipeline graph: {e}")
            raise PipelineExecutionError(f"Graph building failed: {e}")
    
    def _elicitation_phase(self, state: PipelineState) -> PipelineState:
        """
        Execute the elicitation phase.
        
        Stakeholder expresses user stories, Collector proposes questions,
        Stakeholder answers questions.
        """
        self.log_info("Executing elicitation phase")
        
        try:
            state["current_phase"] = PipelinePhase.ELICITATION
            
            stakeholder = self.agents[AgentRole.STAKEHOLDER]
            collector = self.agents[AgentRole.COLLECTOR]
            
            # Step 1: Stakeholder expresses user stories (if first iteration)
            if state["iteration_count"] == 0:
                self.log_info("Stakeholder expressing initial user stories")
                stories_result = stakeholder.express_initial_requirements(
                    state["system_idea"],
                    state["domain"]
                )
                state["user_stories"] = stories_result["user_stories"]
            
            # Step 2: Collector proposes questions
            self.log_info("Collector analyzing and proposing questions")
            questions_result = collector.analyze_and_question(
                state["user_stories"],
                state["domain"],
                f"iteration_{state['iteration_count']}"
            )
            
            # Extract questions from the response
            questions_text = questions_result["questions"]
            state["questions"] = self._extract_questions_list(questions_text)
            
            # Step 3: Stakeholder answers questions
            qa_pairs = []
            for question in state["questions"][:3]:  # Limit to top 3 questions
                self.log_info(f"Stakeholder answering question: {question[:50]}...")
                answer_result = stakeholder.respond_to_question(
                    question,
                    context=state["domain"],
                    previous_stories=state["user_stories"]
                )
                qa_pairs.append({
                    "question": question,
                    "answer": answer_result["answer"]
                })
            
            state["qa_pairs"] = qa_pairs
            
            # Step 4: Collector updates requirements draft
            self.log_info("Collector drafting updated requirements")
            qa_text = "\n\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs])
            draft_result = collector.draft_requirements(
                state["user_stories"],
                qa_text,
                state["domain"]
            )
            state["requirements_draft"] = draft_result["requirements_draft"]
            
            self.log_info("Elicitation phase completed")
            return state
            
        except Exception as e:
            self.log_error(f"Elicitation phase failed: {e}")
            state["status"] = PipelineStatus.FAILED
            state["error_message"] = str(e)
            return state
    
    def _modeling_phase(self, state: PipelineState) -> PipelineState:
        """
        Execute the modeling phase.
        
        Modeler extracts entities and relationships from requirements.
        """
        self.log_info("Executing modeling phase")
        
        try:
            state["current_phase"] = PipelinePhase.MODELING
            
            modeler = self.agents[AgentRole.MODELER]
            
            # Step 1: Extract entities
            self.log_info("Modeler extracting entities")
            entities_result = modeler.extract_system_entities(
                state["requirements_draft"],
                state["domain"]
            )
            state["entities"] = entities_result["entities"]
            
            # Step 2: Extract relationships
            self.log_info("Modeler extracting relationships")
            relationships_result = modeler.extract_entity_relationships(
                state["entities"],
                state["requirements_draft"],
                state["domain"]
            )
            state["relationships"] = relationships_result["relationships"]
            
            self.log_info("Modeling phase completed")
            return state
            
        except Exception as e:
            self.log_error(f"Modeling phase failed: {e}")
            state["status"] = PipelineStatus.FAILED
            state["error_message"] = str(e)
            return state
    
    def _verification_phase(self, state: PipelineState) -> PipelineState:
        """
        Execute the verification phase.
        
        Checker validates quality and consistency of requirements.
        """
        self.log_info("Executing verification phase")
        
        try:
            state["current_phase"] = PipelinePhase.VERIFICATION
            
            checker = self.agents[AgentRole.CHECKER]
            
            # Perform comprehensive quality check
            self.log_info("Checker performing quality analysis")
            check_result = checker.perform_quality_check(
                state["requirements_draft"],
                state["entities"],
                state["relationships"],
                state["user_stories"],
                state["domain"]
            )
            
            state["check_results"] = check_result["check_results"]
            
            # Extract quality score and issues
            quality_score, issues = self._parse_check_results(check_result["check_results"])
            state["quality_score"] = quality_score
            state["issues_found"] = issues
            
            self.log_info(f"Verification completed - Quality score: {quality_score}")
            return state
            
        except Exception as e:
            self.log_error(f"Verification phase failed: {e}")
            state["status"] = PipelineStatus.FAILED
            state["error_message"] = str(e)
            return state
    
    def _specification_phase(self, state: PipelineState) -> PipelineState:
        """
        Execute the specification phase.
        
        Documenter creates final SRS or problem report.
        """
        self.log_info("Executing specification phase")
        
        try:
            state["current_phase"] = PipelinePhase.SPECIFICATION
            
            documenter = self.agents[AgentRole.DOCUMENTER]
            
            if state["quality_score"] >= self.config.quality_threshold:
                # Generate final SRS
                self.log_info("Generating final SRS document")
                srs_result = documenter.generate_srs_document(
                    state["requirements_draft"],
                    state["entities"],
                    state["relationships"],
                    state["user_stories"],
                    state["check_results"],
                    state["project_name"],
                    state["domain"]
                )
                state["final_srs"] = srs_result["srs_document"]
            else:
                # Generate problem report
                self.log_info("Generating quality problem report")
                report_result = documenter.generate_quality_report(
                    state["check_results"],
                    state["project_name"],
                    state["domain"]
                )
                state["final_srs"] = report_result["check_report"]
            
            state["status"] = PipelineStatus.COMPLETED
            self.log_info("Specification phase completed")
            return state
            
        except Exception as e:
            self.log_error(f"Specification phase failed: {e}")
            state["status"] = PipelineStatus.FAILED
            state["error_message"] = str(e)
            return state
    
    def _quality_check_node(self, state: PipelineState) -> PipelineState:
        """Check if quality threshold is met."""
        self.log_info(f"Quality check - Score: {state['quality_score']}, Threshold: {self.config.quality_threshold}")
        return state
    
    def _iteration_control_node(self, state: PipelineState) -> PipelineState:
        """Control iteration flow based on quality and iteration count."""
        state["iteration_count"] += 1
        self.log_info(f"Iteration control - Count: {state['iteration_count']}, Max: {self.config.max_iterations}")
        return state
    
    def _should_continue_iterations(self, state: PipelineState) -> str:
        """Determine if iterations should continue."""
        # Increment iteration count first
        current_iteration = state["iteration_count"] + 1
        
        self.log_info(f"Checking iteration control - Current: {current_iteration}, Max: {self.config.max_iterations}")
        self.log_info(f"Quality score: {state['quality_score']}, Threshold: {self.config.quality_threshold}")
        
        # If max iterations reached, proceed to specification
        if current_iteration >= self.config.max_iterations:
            self.log_info("Max iterations reached, proceeding to specification")
            return "specification"
        
        # If quality is good enough, proceed to specification
        if state["quality_score"] >= self.config.quality_threshold:
            self.log_info("Quality threshold met, proceeding to specification")
            return "specification"
        
        # If we have some results but quality is not good enough, continue iterating
        if state.get("requirements_draft") and current_iteration < self.config.max_iterations:
            self.log_info("Quality below threshold, continuing iterations")
            return "continue"
        
        # Fallback: proceed to specification to avoid infinite loop
        self.log_info("Fallback: proceeding to specification to avoid infinite loop")
        return "specification"
    
    def _extract_questions_list(self, questions_text: str) -> List[str]:
        """Extract individual questions from the questions text."""
        # Simple extraction - look for lines starting with "Question"
        questions = []
        lines = questions_text.split('\n')
        current_question = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('Question'):
                if current_question:
                    questions.append(current_question.strip())
                # Extract question text after the number
                if ':' in line:
                    current_question = line.split(':', 1)[1].strip()
                else:
                    current_question = line
            elif current_question and not line.startswith('Rationale'):
                current_question += " " + line
        
        if current_question:
            questions.append(current_question.strip())
        
        return questions[:5]  # Limit to 5 questions
    
    def _parse_check_results(self, check_results: str) -> tuple[float, List[Dict[str, Any]]]:
        """Parse check results to extract quality score and issues."""
        # Default values
        quality_score = 7.0  # Default score if parsing fails
        issues = []
        
        if not check_results or not isinstance(check_results, str):
            self.log_warning("Empty or invalid check results, using default quality score")
            return quality_score, issues
        
        # Try to extract overall quality score
        lines = check_results.split('\n')
        for line in lines:
            line = line.strip()
            if 'Overall Quality Score:' in line or 'Quality Score:' in line:
                try:
                    # Extract score from patterns like "Score: 8.5/10" or "Score: 8.5"
                    score_part = line.split(':')[1].strip()
                    if '/' in score_part:
                        score_part = score_part.split('/')[0].strip()
                    # Remove any non-numeric characters except decimal point
                    score_text = ''.join(c for c in score_part if c.isdigit() or c == '.')
                    if score_text:
                        quality_score = float(score_text)
                        # Ensure score is in valid range
                        quality_score = max(0.0, min(10.0, quality_score))
                        self.log_info(f"Extracted quality score: {quality_score}")
                        break
                except (ValueError, IndexError) as e:
                    self.log_warning(f"Failed to parse quality score from line '{line}': {e}")
                    continue
        
        # Extract issues (simplified)
        if 'Critical' in check_results.lower():
            issues.append({"severity": "critical", "count": 1})
        if 'Major' in check_results.lower():
            issues.append({"severity": "major", "count": 1})
        if 'Minor' in check_results.lower():
            issues.append({"severity": "minor", "count": 1})
        
        self.log_info(f"Parsed quality score: {quality_score}, issues: {len(issues)}")
        return quality_score, issues
    
    def execute(
        self, 
        system_idea: str,
        domain: str = "general software system",
        project_name: str = "Software Project",
        workspace_path: Optional[Path] = None
    ) -> PipelineState:
        """
        Execute the complete MARE pipeline.
        
        Args:
            system_idea: High-level description of the system to build
            domain: Domain or industry context
            project_name: Name of the project
            workspace_path: Path to workspace directory
            
        Returns:
            Final pipeline state with all artifacts
        """
        self.log_info(f"Starting MARE pipeline execution for project: {project_name}")
        
        # Initialize workspace if path provided
        if workspace_path:
            execution_id = str(uuid.uuid4())
            self.workspace = SharedWorkspace(workspace_path, execution_id)
            self.log_info(f"Workspace initialized at {workspace_path}")
        
        # Initialize pipeline state
        initial_state: PipelineState = {
            "system_idea": system_idea,
            "domain": domain,
            "project_name": project_name,
            "current_phase": PipelinePhase.ELICITATION,
            "iteration_count": 0,
            "user_stories": "",
            "questions": [],
            "qa_pairs": [],
            "requirements_draft": "",
            "entities": "",
            "relationships": "",
            "check_results": "",
            "final_srs": "",
            "quality_score": 0.0,
            "issues_found": [],
            "execution_id": self.workspace.execution_id if self.workspace else str(uuid.uuid4()),
            "start_time": datetime.now(),
            "status": PipelineStatus.RUNNING,
            "error_message": None,
            "agent_histories": {}
        }
        
        try:
            # Execute the pipeline with recursion limit configuration
            config = {"recursion_limit": self.config.max_iterations + 5}
            final_state = self.graph.invoke(initial_state, config=config)
            
            self.log_info(f"Pipeline execution completed with status: {final_state['status']}")
            return final_state
            
        except Exception as e:
            self.log_error(f"Pipeline execution failed: {e}")
            initial_state["status"] = PipelineStatus.FAILED
            initial_state["error_message"] = str(e)
            return initial_state

