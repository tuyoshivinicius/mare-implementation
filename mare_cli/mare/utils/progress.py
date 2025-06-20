"""
MARE CLI - Enhanced Progress Tracking
Provides detailed progress feedback during pipeline execution
"""

from typing import Dict, Any, Optional, Callable
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

console = Console()

class PhaseStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class PhaseProgress:
    name: str
    status: PhaseStatus
    progress: float
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_step: str = ""
    estimated_duration: Optional[int] = None
    
    @property
    def elapsed_time(self) -> Optional[timedelta]:
        if self.start_time:
            end = self.end_time or datetime.now()
            return end - self.start_time
        return None
    
    @property
    def estimated_remaining(self) -> Optional[timedelta]:
        if self.elapsed_time and self.progress > 0 and self.estimated_duration:
            total_estimated = timedelta(seconds=self.estimated_duration)
            if self.progress < 100:
                remaining_ratio = (100 - self.progress) / 100
                return total_estimated * remaining_ratio
        return None

class EnhancedProgressTracker:
    """Enhanced progress tracker with detailed phase and step visibility."""
    
    def __init__(self):
        self.phases: Dict[str, PhaseProgress] = {}
        self.current_phase: Optional[str] = None
        self.start_time = datetime.now()
        self.console = Console()
        self.progress = None
        self.live = None
        
        # Estimated durations based on typical execution times (seconds)
        self.phase_estimates = {
            "initialization": 10,
            "elicitation": 45,
            "modeling": 30,
            "verification": 25,
            "specification": 20,
            "finalization": 5
        }
    
    def initialize_phases(self):
        """Initialize all pipeline phases."""
        phase_configs = [
            ("initialization", "Initializing agents and workspace"),
            ("elicitation", "Gathering requirements from stakeholders"),
            ("modeling", "Extracting entities and relationships"),
            ("verification", "Checking quality and consistency"),
            ("specification", "Generating final documentation"),
            ("finalization", "Saving results and cleanup")
        ]
        
        for phase_id, description in phase_configs:
            self.phases[phase_id] = PhaseProgress(
                name=description,
                status=PhaseStatus.PENDING,
                progress=0.0,
                estimated_duration=self.phase_estimates.get(phase_id, 30)
            )
    
    def start_tracking(self):
        """Start the progress tracking interface."""
        self.initialize_phases()
        
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        )
        
        # Create tasks for each phase
        self.phase_tasks = {}
        for phase_id, phase in self.phases.items():
            task_id = self.progress.add_task(
                f"[dim]{phase.name}[/dim]",
                total=100,
                visible=False
            )
            self.phase_tasks[phase_id] = task_id
        
        # Create overall progress task
        self.overall_task = self.progress.add_task(
            "[bold blue]Overall Progress[/bold blue]",
            total=len(self.phases) * 100
        )
        
        self.live = Live(self._create_display(), refresh_per_second=2)
        self.live.start()
    
    def start_phase(self, phase_id: str, step: str = ""):
        """Start a specific phase."""
        if phase_id not in self.phases:
            return
        
        # Complete previous phase if any
        if self.current_phase and self.current_phase != phase_id:
            self.complete_phase(self.current_phase)
        
        phase = self.phases[phase_id]
        phase.status = PhaseStatus.RUNNING
        phase.start_time = datetime.now()
        phase.current_step = step
        phase.progress = 0.0
        
        self.current_phase = phase_id
        
        # Update progress display
        if self.progress:
            self.progress.update(
                self.phase_tasks[phase_id],
                description=f"[yellow]{phase.name}[/yellow]",
                visible=True,
                completed=0
            )
    
    def update_phase_progress(self, phase_id: str, progress: float, step: str = ""):
        """Update progress for a specific phase."""
        if phase_id not in self.phases:
            return
        
        phase = self.phases[phase_id]
        phase.progress = min(100.0, max(0.0, progress))
        if step:
            phase.current_step = step
        
        # Update progress display
        if self.progress:
            self.progress.update(
                self.phase_tasks[phase_id],
                completed=phase.progress
            )
            
            # Update overall progress
            total_progress = sum(p.progress for p in self.phases.values())
            self.progress.update(self.overall_task, completed=total_progress)
    
    def complete_phase(self, phase_id: str):
        """Mark a phase as completed."""
        if phase_id not in self.phases:
            return
        
        phase = self.phases[phase_id]
        phase.status = PhaseStatus.COMPLETED
        phase.end_time = datetime.now()
        phase.progress = 100.0
        phase.current_step = "Completed"
        
        # Update progress display
        if self.progress:
            self.progress.update(
                self.phase_tasks[phase_id],
                description=f"[green]✓ {phase.name}[/green]",
                completed=100
            )
    
    def fail_phase(self, phase_id: str, error: str = ""):
        """Mark a phase as failed."""
        if phase_id not in self.phases:
            return
        
        phase = self.phases[phase_id]
        phase.status = PhaseStatus.FAILED
        phase.end_time = datetime.now()
        phase.current_step = f"Failed: {error}" if error else "Failed"
        
        # Update progress display
        if self.progress:
            self.progress.update(
                self.phase_tasks[phase_id],
                description=f"[red]✗ {phase.name}[/red]"
            )
    
    def log_activity(self, message: str, level: str = "info"):
        """Log an activity message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "info":
            color = "dim"
        elif level == "success":
            color = "green"
        elif level == "warning":
            color = "yellow"
        elif level == "error":
            color = "red"
        else:
            color = "dim"
        
        # This would be displayed in a separate log area
        # For now, we'll store it for potential display
        pass
    
    def stop_tracking(self):
        """Stop the progress tracking interface."""
        if self.live:
            self.live.stop()
        if self.progress:
            self.progress.stop()
    
    def _create_display(self):
        """Create the rich display layout."""
        if not self.progress:
            return Panel("Initializing...")
        
        # Create status table
        status_table = Table(title="Pipeline Status", show_header=True, header_style="bold magenta")
        status_table.add_column("Phase", style="cyan", no_wrap=True)
        status_table.add_column("Status", style="magenta")
        status_table.add_column("Progress", style="green")
        status_table.add_column("Current Step", style="yellow")
        status_table.add_column("Time", style="blue")
        
        for phase_id, phase in self.phases.items():
            # Status icon
            if phase.status == PhaseStatus.COMPLETED:
                status = "[green]✓ Completed[/green]"
            elif phase.status == PhaseStatus.RUNNING:
                status = "[yellow]⚡ Running[/yellow]"
            elif phase.status == PhaseStatus.FAILED:
                status = "[red]✗ Failed[/red]"
            else:
                status = "[dim]⏳ Pending[/dim]"
            
            # Progress bar
            progress_bar = f"{phase.progress:.1f}%"
            
            # Time info
            if phase.elapsed_time:
                elapsed = str(phase.elapsed_time).split('.')[0]  # Remove microseconds
                if phase.estimated_remaining and phase.status == PhaseStatus.RUNNING:
                    remaining = str(phase.estimated_remaining).split('.')[0]
                    time_info = f"{elapsed} / ~{remaining}"
                else:
                    time_info = elapsed
            else:
                time_info = "-"
            
            status_table.add_row(
                phase.name,
                status,
                progress_bar,
                phase.current_step or "-",
                time_info
            )
        
        # Combine progress and status
        from rich.columns import Columns
        return Columns([self.progress, status_table], equal=True)

# Global tracker instance
_tracker: Optional[EnhancedProgressTracker] = None

def get_progress_tracker() -> EnhancedProgressTracker:
    """Get the global progress tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = EnhancedProgressTracker()
    return _tracker

def start_progress_tracking():
    """Start progress tracking."""
    tracker = get_progress_tracker()
    tracker.start_tracking()
    return tracker

def stop_progress_tracking():
    """Stop progress tracking."""
    global _tracker
    if _tracker:
        _tracker.stop_tracking()
        _tracker = None

