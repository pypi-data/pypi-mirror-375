import json
import logging
import os
import shutil
import tempfile
import time
from abc import ABC, abstractmethod
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass

from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union
import uuid


from pydantic import BaseModel, Field
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from minienv.constants import TASKS_DIR
from minienv.backend.local import LocalBackend

console = Console()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# Rich formatting functions
class ConsoleLogger:
    """Unified console logger for all minienv output formatting."""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        
    def _truncate_with_suffix(self, text: str, max_length: int, suffix_length: int = 100) -> str:
        """Truncate text showing prefix, dimmed ellipsis, and suffix."""
        if len(text) <= max_length:
            return text
            
        prefix_length = max_length - suffix_length - 20  # Reserve space for ellipsis
        if prefix_length < 50:  # Ensure minimum prefix length
            prefix_length = max_length // 2
            suffix_length = max_length - prefix_length - 20
            
        prefix = text[:prefix_length]
        suffix = text[-suffix_length:] if suffix_length > 0 else ""
        
        if suffix:
            return f"{prefix}\n[dim]...[/]\n{suffix}"
        else:
            return f"{prefix}\n[dim]...[/]"
        
    def info(self, message: str, icon: str = "ℹ️") -> None:
        """Print info messages."""
        self.console.print(f"{icon} {message}", style="bold blue")
        
    def success(self, message: str, icon: str = "✅") -> None:
        """Print success messages."""
        self.console.print(f"{icon} {message}", style="bold green")
        
    def warning(self, message: str, icon: str = "⚠️") -> None:
        """Print warning messages."""
        self.console.print(f"{icon} {message}", style="bold yellow")
        
    def error(self, message: str, icon: str = "❌") -> None:
        """Print error messages."""
        self.console.print(f"{icon} {message}", style="bold red")
        
    def docker(self, message: str, status: str = "info") -> None:
        """Print Docker-related messages."""
        icon_map = {"info": "🐳", "success": "🐳", "error": "🐳", "warning": "🐳"}
        color_map = {"info": "blue", "success": "green", "error": "red", "warning": "yellow"}
        
        icon = icon_map.get(status, "🐳")
        color = color_map.get(status, "blue")
        
        self.console.print(f"{icon} {message}", style=f"bold {color}")
        
    def progress(self, message: str) -> None:
        """Print progress messages."""
        self.console.print(f"[bold yellow]Progress:[/] {message}")
        
    def model_input(self, messages: List[Any], tools: List[str]) -> None:
        """Print the exact input being sent to the LLM."""
        content_lines = []
        content_lines.append(f"[bold yellow]Available Tools:[/] {', '.join(tools)}")
        content_lines.append("")

        # Show all messages in the conversation
        for i, msg in enumerate(messages):
            if hasattr(msg, "role"):
                role_color = {
                    "system": "dim white",
                    "user": "cyan", 
                    "assistant": "bright_magenta",
                    "tool": "green",
                }.get(msg.role, "white")

                content_lines.append(f"[bold {role_color}]Message {i+1} ({msg.role}):[/]")
                # Truncate very long messages but show enough context
                msg_content = msg.content if hasattr(msg, "content") else str(msg)
                msg_content = self._truncate_with_suffix(msg_content, 500, 100)
                content_lines.append(msg_content)

                # Show tool calls if present
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        args_str = str(tc.arguments)
                        args_preview = self._truncate_with_suffix(args_str, 100, 30)
                        content_lines.append(f"[bold white]{tc.function}[/]([bold pink]{args_preview}[/])")

                content_lines.append("")

        self.console.print(
            Panel(
                "\n".join(content_lines),
                title="MODEL CONTEXT",
                border_style="bright_blue",
                box=box.DOUBLE,
                width=120,
            )
        )
        
    def model_output(self, response_content: str, tool_calls: List[Any]) -> None:
        """Print the exact output from the LLM."""
        content_lines = []

        if response_content and response_content.strip():
            content_lines.append("[bold bright_magenta]MODEL REASONING:[/]")
            content_lines.append(response_content.strip())
            content_lines.append("")

        if tool_calls:
            content_lines.append(f"[bold yellow]TOOL CALLS REQUESTED ({len(tool_calls)}):[/]")
            for i, tc in enumerate(tool_calls, 1):
                # Show full arguments
                args_str = (
                    json.dumps(tc.arguments, indent=2)
                    if hasattr(tc, "arguments")
                    else str(tc.arguments)
                )
                content_lines.append(f"[bold white]{tc.function}[/]([bold pink]{args_str}[/])")
                if i < len(tool_calls):
                    content_lines.append("")

        if not content_lines:
            content_lines = ["[dim]No response content or tool calls[/]"]

        self.console.print(
            Panel(
                "\n".join(content_lines),
                title="MODEL RESPONSE",
                border_style="bright_magenta",
                box=box.DOUBLE,
                width=120,
            )
        )
        
    def container_action(self, action_type: str, result: str = "", success: bool = True) -> None:
        """Print container action results."""
        content_lines = []

        # Action header
        content_lines.append(f"{action_type}")

        if result and result.strip():
            content_lines.append("")
            content_lines.append("[bold yellow]CONTAINER OUTPUT:[/]")
            # Limit output length but show key information
            if len(result) > 1000:
                lines = result.split("\n")
                if len(lines) > 20:
                    shown_result = (
                        "\n".join(lines[:10])
                        + f"\n[dim]... [{len(lines)-20} lines omitted] ...[/]\n"
                        + "\n".join(lines[-10:])
                    )
                else:
                    shown_result = self._truncate_with_suffix(result, 1000, 200)
            else:
                shown_result = result
            content_lines.append(f"[dim white]{shown_result}[/]")

        border_style = "green" if success else "red"
        self.console.print(
            Panel(
                "\n".join(content_lines),
                title="CONTAINER ACTION" if success else "CONTAINER ERROR",
                border_style=border_style,
                box=box.DOUBLE,
                width=120,
            )
        )
        
    def turn_header(self, turn: int, max_turns: int) -> None:
        """Print turn header with progress bar."""
        # Create a simple progress indicator
        progress_bar = "█" * min(turn, 20) + "░" * max(0, 20 - turn)

        # Add clear separator
        self.console.print("\n" + "=" * 120, style="dim white")
        self.console.print(f"[bold blue]TURN {turn}/{max_turns}[/] [{progress_bar}]", style="bold blue")
        self.console.print("=" * 120, style="dim white")
        
    def task_header(self, task_id: str, tools: List[str], time_limit: int, max_turns: int) -> None:
        """Print beautiful task header."""
        # Create a beautiful header panel
        header_content = f"""
[bold green]Task:[/] {task_id}
[bold blue]Available Tools:[/] {', '.join(tools)}
[bold yellow]Time Limit:[/] {time_limit}s
[bold cyan]Max Turns:[/] {max_turns}
        """

        self.console.print(
            Panel(
                header_content.strip(),
                title="Agent Config",
                border_style="bright_blue",
                box=box.ROUNDED,
            )
        )
        
    def final_result(self, success: bool, score: float, execution_time: float, output: str) -> None:
        """Print final results with rich formatting."""
        # Create results table
        table = Table(title="🏁 Results", box=box.ROUNDED)
        table.add_column("Metric", style="bold cyan")
        table.add_column("Value", style="bold")

        success_style = "bold green" if success else "bold red"
        success_text = "✅ Success" if success else "❌ Failed"

        table.add_row("Status", f"[{success_style}]{success_text}[/]")
        table.add_row("Score", f"[bold yellow]{score:.1f}[/]")
        table.add_row("Execution Time", f"[bold blue]{execution_time:.2f}s[/]")

        self.console.print(table)

        if output:
            self.console.print(Panel(output, title="Output", border_style="green" if success else "red"))


# Global console logger instance
console_logger = ConsoleLogger(console)


# =============================================================================
# TRACE LOGGING
# =============================================================================


class TraceLogger:
    """Handles logging of conversation traces to JSONL files."""

    def __init__(self, traces_dir: str = "traces"):
        self.traces_dir = Path(traces_dir)
        self.traces_dir.mkdir(exist_ok=True)

    def save_trace(
        self, task_id: str, messages: List["ChatMessage"], metadata: Dict[str, Any] = None
    ) -> str:
        """Save conversation trace to JSONL file."""
        timestamp = int(time.time())
        trace_filename = f"{task_id}_{timestamp}.jsonl"
        trace_path = self.traces_dir / trace_filename

        # Convert messages to dict format
        trace_data = {
            "task_id": task_id,
            "timestamp": timestamp,
            "metadata": metadata or {},
            "messages": [msg.to_dict() for msg in messages],
        }

        # Save as JSONL (one JSON object per line)
        with open(trace_path, "w") as f:
            f.write(json.dumps(trace_data, indent=None, separators=(",", ":")) + "\n")

        console_logger.docker(f"Trace saved to {trace_path}", "success")
        return str(trace_path)

    def load_trace(self, trace_path: str) -> Dict[str, Any]:
        """Load a trace from JSONL file."""
        with open(trace_path, "r") as f:
            return json.loads(f.readline())


# =============================================================================
# CORE ABSTRACTIONS
# =============================================================================





class ExecutionResult(BaseModel):
    """Result of executing a shell command."""

    output: bytes
    exit_code: int

    @property
    def text_output(self) -> str:
        return self.output.decode("utf-8", errors="replace")


class JupyterExecutionResult(BaseModel):
    """Result of executing code in Jupyter kernel."""

    status: str
    output: str
    final_expression_output: Optional[str] = None
    exception: Optional[Dict[str, Any]] = None


@dataclass
class ContainerConfig:
    """Configuration for a Docker container."""

    image: str
    environment: Dict[str, str] = None
    volumes: Dict[str, str] = None  # host_path -> container_path
    ports: List[int] = None
    privileged: bool = False
    gpu_access: bool = False
    network_mode: str = "bridge"  # Default network mode
    memory_limit: Optional[str] = None
    timeout: int = 3600  # seconds
    export_results: bool = True  # Export /results to host
    results_host_path: str = (
        "./minienv_results"  # Where to save results on host (relative to current dir)
    )

    def __post_init__(self):
        if self.environment is None:
            self.environment = {}
        if self.volumes is None:
            self.volumes = {}
        if self.ports is None:
            self.ports = []


# =============================================================================
# CONTAINER INTERFACE ABSTRACTION
# =============================================================================


class ComputerInterface(ABC):
    """Abstract interface for interacting with containerized environments."""

    @abstractmethod
    async def execute_shell(self, command: str, timeout: int = 60) -> ExecutionResult:
        """Execute a shell command in the container."""
        pass

    @abstractmethod
    async def execute_python(self, code: str, timeout: int = 60) -> JupyterExecutionResult:
        """Execute Python code in the container's Jupyter kernel."""
        pass

    @abstractmethod
    async def upload_file(self, content: bytes, destination: str) -> None:
        """Upload file content to the container."""
        pass

    @abstractmethod
    async def download_file(self, source: str) -> bytes:
        """Download file content from the container."""
        pass

    @abstractmethod
    async def disable_internet(self) -> None:
        """Disable internet access for the container."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up container resources."""
        pass


# =============================================================================
# TASK ABSTRACTION AND ORCHESTRATION
# =============================================================================


class Task(BaseModel):
    """Represents a computational task to be executed in a container."""

    task_id: str
    instructions: str
    config: ContainerConfig
    timeout: int = 3600
    task_folder: Optional[str] = None  # Path to task folder for mounting
    _is_temp_folder: bool = False  # Internal flag to track if task_folder is temporary

    class Config:
        arbitrary_types_allowed = True

    def cleanup_temp_files(self) -> None:
        """Clean up temporary task files if they were created."""
        if self._is_temp_folder and self.task_folder and os.path.exists(self.task_folder):
            try:
                shutil.rmtree(self.task_folder, ignore_errors=True)
                console_logger.docker(f"Cleaned up temporary task directory: {self.task_folder}", "info")
            except Exception as e:
                console_logger.docker(
                    f"Failed to clean up temporary directory {self.task_folder}: {e}", "warning"
                )


class TaskLoader:
    """Loads tasks from the tasks/ directory structure."""

    def __init__(self, tasks_dir: str = TASKS_DIR):
        self.tasks_dir = Path(tasks_dir)

    def list_tasks(self) -> List[str]:
        """List all available task IDs."""
        if not self.tasks_dir.exists():
            return []

        tasks = []
        for item in self.tasks_dir.iterdir():
            if item.is_dir():
                tasks.append(item.name)
        return tasks

    def load_task(self, task_id: str, base_config: ContainerConfig) -> Task:
        """Load a specific task by ID."""
        task_folder = self.tasks_dir / task_id
        instructions_file = task_folder / "instructions.md"

        if not task_folder.exists():
            raise ValueError(f"Task folder not found: {task_folder}")

        if not instructions_file.exists():
            raise ValueError(f"Instructions file not found: {instructions_file}")

        # Read instructions
        instructions = instructions_file.read_text(encoding="utf-8")

        # Create a temporary directory for the task files (Docker-accessible)
        # Use a temp directory within the current working directory to ensure Docker can access it
        temp_base_dir = Path.cwd() / "temp_tasks"
        temp_base_dir.mkdir(exist_ok=True)
        temp_task_dir = tempfile.mkdtemp(prefix=f"nanoeval_task_{task_id}_", dir=str(temp_base_dir))

        # Copy all task files to the temporary directory
        try:
            for item in task_folder.iterdir():
                if item.is_file():
                    shutil.copy2(item, temp_task_dir)
                elif item.is_dir():
                    shutil.copytree(item, Path(temp_task_dir) / item.name)
        except Exception as e:
            # Clean up temp dir if copy fails
            shutil.rmtree(temp_task_dir, ignore_errors=True)
            raise ValueError(f"Failed to copy task files: {e}")

        # Create config with temporary task folder mounted
        config = ContainerConfig(
            image=base_config.image,
            environment=base_config.environment.copy() if base_config.environment else {},
            volumes=base_config.volumes.copy() if base_config.volumes else {},
            ports=base_config.ports.copy() if base_config.ports else [],
            privileged=base_config.privileged,
            gpu_access=base_config.gpu_access,
            network_mode=base_config.network_mode,
            memory_limit=base_config.memory_limit,
            timeout=base_config.timeout,
            export_results=base_config.export_results,
            results_host_path=base_config.results_host_path,
        )

        # Mount the temporary task folder to /task in the container
        config.volumes[temp_task_dir] = "/task"

        task = Task(
            task_id=task_id,
            instructions=instructions,
            config=config,
            timeout=base_config.timeout,
            task_folder=temp_task_dir,
        )
        task._is_temp_folder = True
        return task

    def get_task_instructions(self, task_id: str) -> str:
        """Get just the instructions for a task without loading full config."""
        task_folder = self.tasks_dir / task_id
        instructions_file = task_folder / "instructions.md"

        if not instructions_file.exists():
            raise ValueError(f"Instructions file not found: {instructions_file}")

        return instructions_file.read_text(encoding="utf-8")


class Step(BaseModel):
    """Represents a step in task execution."""

    step_type: str
    content: str
    timestamp: float = Field(default_factory=time.time)


class FinalResult(BaseModel):
    """Final result of task execution."""

    success: bool
    score: float
    output: str
    execution_time: float
    error: Optional[str] = None


class TaskSolver(ABC):
    """Abstract base class for task solvers."""

    @abstractmethod
    async def solve(
        self, task: Task, computer: ComputerInterface
    ) -> AsyncGenerator[Union[Step, FinalResult], None]:
        """Solve the given task using the computer interface."""
        pass


class SimpleTaskSolver(TaskSolver):
    """Simple example task solver."""

    async def solve(
        self, task: Task, computer: ComputerInterface
    ) -> AsyncGenerator[Union[Step, FinalResult], None]:
        """Example solver that runs some basic commands."""
        start_time = time.time()

        try:
            # Step 1: Check environment
            yield Step(step_type="setup", content="Checking environment")
            result = await computer.execute_shell("python3 --version")
            if result.exit_code != 0:
                raise RuntimeError("Python not available")

            # Step 2: Create and run a simple program directly
            yield Step(step_type="coding", content="Creating and running test program")
            program = """
print("Hello from container!")
import sys
print(f"Python version: {sys.version}")
result = 2 + 2
print(f"2 + 2 = {result}")
"""

            # Step 3: Execute the program directly (no file upload needed)
            yield Step(step_type="execution", content="Running test program")
            result = await computer.execute_python(program)

            # Final result
            execution_time = time.time() - start_time
            yield FinalResult(
                success=result.status == "success",
                score=1.0 if result.status == "success" else 0.0,
                output=result.output,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            yield FinalResult(
                success=False, score=0.0, output="", execution_time=execution_time, error=str(e)
            )


# =============================================================================
# REACT AGENT WITH TOOLS (PAPERBENCH STYLE)
# =============================================================================


class ToolCall(BaseModel):
    """Represents a tool call made by the model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    function: str
    arguments: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool call to a dictionary for serialization."""
        return {"id": self.id, "function": self.function, "arguments": self.arguments}


class ToolResult(BaseModel):
    """Result of executing a tool."""

    tool_call_id: str
    content: str
    success: bool = True
    error: Optional[str] = None


class ChatMessage(BaseModel):
    """A single message in the conversation."""

    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: List[ToolCall] = Field(default_factory=list)
    tool_call_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "tool_call_id": self.tool_call_id,
            "timestamp": self.timestamp,
        }


class ConversationState(BaseModel):
    """Manages the conversation state for the ReAct agent."""

    messages: List[ChatMessage] = Field(default_factory=list)
    max_turns: int = 50
    current_turn: int = 0
    time_limit: Optional[float] = None
    start_time: float = Field(default_factory=time.time)

    @property
    def completed(self) -> bool:
        """Check if the conversation should end."""
        if self.current_turn >= self.max_turns:
            return True
        if self.time_limit and (time.time() - self.start_time) > self.time_limit:
            return True
        return False

    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)

    def get_recent_context(self, max_messages: int = 20) -> List[ChatMessage]:
        """Get recent messages for context management."""
        if len(self.messages) <= max_messages:
            return self.messages
            
        # Get the last max_messages, but ensure we don't break tool call/tool result pairs
        recent_messages = self.messages[-max_messages:]
        
        # If the first message is a tool message, we need to include its corresponding assistant message
        if recent_messages and recent_messages[0].role == "tool":
            # Find the corresponding assistant message with tool calls
            tool_call_id = recent_messages[0].tool_call_id
            for i in range(len(self.messages) - max_messages - 1, -1, -1):
                if (self.messages[i].role == "assistant" and 
                    any(tc.id == tool_call_id for tc in self.messages[i].tool_calls)):
                    # Include this assistant message and everything after it
                    return self.messages[i:]
            # If we can't find the corresponding assistant message, just return recent messages
            # The _messages_to_openai_format will handle orphaned tool messages
        
        return recent_messages


class Tool(ABC):
    """Abstract base class for agent tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the model."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments."""
        pass


class BashTool(Tool):
    """Tool for executing bash commands."""

    def __init__(self, computer: ComputerInterface):
        self.computer = computer

    @property
    def name(self) -> str:
        return "bash"

    @property
    def description(self) -> str:
        return """Execute bash commands in the container.
        
        Args:
            cmd (str): The bash command to execute
            
        Returns:
            The output of the command (stdout/stderr)
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Execute a bash command."""
        cmd = kwargs.get("cmd", "")
        if not cmd:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No command provided",
                success=False,
                error="Missing 'cmd' argument",
            )

        try:
            result = await self.computer.execute_shell(cmd, timeout=300)  # 5 min timeout
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Exit code: {result.exit_code}\n{result.text_output}",
                success=result.exit_code == 0,
            )
        except Exception as e:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Error executing command: {str(e)}",
                success=False,
                error=str(e),
            )


class PythonTool(Tool):
    """Tool for executing Python code."""

    def __init__(self, computer: ComputerInterface):
        self.computer = computer

    @property
    def name(self) -> str:
        return "python"

    @property
    def description(self) -> str:
        return """Execute Python code in the container.
        
        Args:
            code (str): The Python code to execute
            
        Returns:
            The output of the Python code (stdout/stderr)
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Execute Python code."""
        code = kwargs.get("code", "")
        if not code:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No code provided",
                success=False,
                error="Missing 'code' argument",
            )

        try:
            result = await self.computer.execute_python(code, timeout=300)
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=result.output,
                success=result.status == "success",
            )
        except Exception as e:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Error executing Python code: {str(e)}",
                success=False,
                error=str(e),
            )


class ReadFileTool(Tool):
    """Tool for reading files (paginated like PaperBench)."""

    def __init__(self, computer: ComputerInterface):
        self.computer = computer

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return """Read a chunk of lines from a file (paginated).
        
        Args:
            file (str): Path to the file to read
            start_line (int): Line number to start reading from (1-indexed, default: 1)
            max_lines (int): Maximum number of lines to read (default: 50, max: 100)
            
        Returns:
            The requested lines from the file with line numbers
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Read a file chunk."""
        file_path = kwargs.get("file", "")
        start_line = kwargs.get("start_line", 1)
        max_lines = min(kwargs.get("max_lines", 50), 100)  # Cap at 100 lines

        if not file_path:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No file path provided",
                success=False,
                error="Missing 'file' argument",
            )

        try:
            # Read the entire file first
            result = await self.computer.execute_shell(f"cat '{file_path}'")
            if result.exit_code != 0:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error reading file: {result.text_output}",
                    success=False,
                    error=result.text_output,
                )

            lines = result.text_output.splitlines()
            total_lines = len(lines)

            if start_line > total_lines:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error: start_line ({start_line}) is beyond total lines ({total_lines})",
                    success=False,
                    error="Invalid start_line",
                )

            # Get the requested chunk
            end_line = min(start_line + max_lines - 1, total_lines)
            chunk = lines[start_line - 1 : end_line]

            # Add line numbers
            numbered_lines = [f"{i+start_line}: {line}" for i, line in enumerate(chunk)]

            # Add summary
            summary = (
                f"File has {total_lines} total lines. Showing lines {start_line} to {end_line}.\n\n"
            )
            content = summary + "\n".join(numbered_lines)

            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""), content=content, success=True
            )

        except Exception as e:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Error reading file: {str(e)}",
                success=False,
                error=str(e),
            )


class WriteFileTool(Tool):
    """Tool for writing content to files."""

    def __init__(self, computer: ComputerInterface):
        self.computer = computer

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return """Write content to a file.
        
        Args:
            file (str): Path to the file to write
            content (str): Content to write to the file
            
        Returns:
            Confirmation of file creation
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Write content to a file using Python."""
        file_path = kwargs.get("file", "")
        content = kwargs.get("content", "")

        if not file_path:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No file path provided",
                success=False,
                error="Missing 'file' argument",
            )

        try:
            # Use Python to write the file - this avoids shell escaping issues
            python_code = f"""
import os
# Ensure directory exists
os.makedirs(os.path.dirname('{file_path}'), exist_ok=True)

# Write the file
with open('{file_path}', 'w') as f:
    f.write({repr(content)})

# Verify it was written
import os
size = os.path.getsize('{file_path}')
print(f"Successfully wrote {{size}} bytes to {file_path}")
"""

            result = await self.computer.execute_python(python_code)

            if result.status == "success":
                # Also verify with ls
                ls_result = await self.computer.execute_shell(f"ls -la '{file_path}'")
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"{result.output}\n{ls_result.text_output}",
                    success=True,
                )
            else:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Python write failed: {result.output}",
                    success=False,
                    error=result.output,
                )

        except Exception as e:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Error writing file: {str(e)}",
                success=False,
                error=str(e),
            )


class EndTaskTool(Tool):
    """Tool for ending the task (submission)."""

    @property
    def name(self) -> str:
        return "end_task"

    @property
    def description(self) -> str:
        return """Signal that you are completely finished with the task.
        
        Args:
            message (str): Optional final message about completion
            
        Returns:
            Confirmation of task completion
        """

    async def execute(self, **kwargs) -> ToolResult:
        """End the task."""
        message = kwargs.get("message", "Task completed")
        return ToolResult(
            tool_call_id=kwargs.get("tool_call_id", ""),
            content=f"Task ended: {message}",
            success=True,
        )


class StrReplaceTool(Tool):
    """Tool for advanced string replacement in files."""

    def __init__(self, computer: ComputerInterface):
        self.computer = computer

    @property
    def name(self) -> str:
        return "str_replace"

    @property
    def description(self) -> str:
        return """Replace a specific string in a file with a new string.
        
        Args:
            file (str): Path to the file to edit
            old_str (str): The exact string to replace (must be unique in the file)
            new_str (str): The new string to replace with (optional, defaults to empty string for deletion)
            
        Returns:
            Confirmation of replacement with a snippet of the changed area
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Replace a string in a file."""
        file_path = kwargs.get("file", "")
        old_str = kwargs.get("old_str", "")
        new_str = kwargs.get("new_str", "")

        if not file_path:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No file path provided",
                success=False,
                error="Missing 'file' argument",
            )

        if not old_str:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: old_str cannot be empty. Use write_file or insert instead.",
                success=False,
                error="Empty 'old_str' argument",
            )

        try:
            # Read the current file content
            result = await self.computer.execute_shell(f"cat '{file_path}'")
            if result.exit_code != 0:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error reading file: {result.text_output}",
                    success=False,
                    error=result.text_output,
                )

            file_content = result.text_output
            
            # Check if old_str exists and is unique
            occurrences = file_content.count(old_str)
            if occurrences == 0:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error: old_str '{old_str}' not found in {file_path}",
                    success=False,
                    error="String not found",
                )
            elif occurrences > 1:
                # Find line numbers where the string appears
                lines = file_content.split('\n')
                line_numbers = [i+1 for i, line in enumerate(lines) if old_str in line]
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error: old_str '{old_str}' appears {occurrences} times in lines {line_numbers}. Please make it unique.",
                    success=False,
                    error="Multiple occurrences found",
                )

            # Perform the replacement
            new_content = file_content.replace(old_str, new_str)

            # Write the new content using Python to avoid shell escaping issues
            python_code = f"""
import os
# Write the file
with open('{file_path}', 'w') as f:
    f.write({repr(new_content)})

# Show a snippet around the change
lines = {repr(new_content)}.split('\\n')
# Find the line where replacement occurred
old_lines = {repr(file_content)}.split('\\n')
new_lines = lines

# Find the changed line by comparing
changed_line = -1
for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
    if old_line != new_line:
        changed_line = i
        break

if changed_line == -1 and len(old_lines) != len(new_lines):
    # Lines were added/removed
    changed_line = min(len(old_lines), len(new_lines))

 if changed_line >= 0:
     start = max(0, changed_line - 3)
     end = min(len(lines), changed_line + 4)
     snippet_lines = [f"{{i+1:4d}}: {{line}}" for i, line in enumerate(lines[start:end], start)]
     print("File edited successfully!")
     print("\\nSnippet around the change:")
     print("\\n".join(snippet_lines))
 else:
     print("File edited successfully!")

size = os.path.getsize('{file_path}')
print(f"\\nFile size: {{size}} bytes")
"""

            python_result = await self.computer.execute_python(python_code)
            
            if python_result.status == "success":
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=python_result.output,
                    success=True,
                )
            else:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error during replacement: {python_result.output}",
                    success=False,
                    error=python_result.output,
                )

        except Exception as e:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Error during str_replace: {str(e)}",
                success=False,
                error=str(e),
            )


class InsertTool(Tool):
    """Tool for inserting text at a specific line in a file."""

    def __init__(self, computer: ComputerInterface):
        self.computer = computer

    @property
    def name(self) -> str:
        return "insert"

    @property
    def description(self) -> str:
        return """Insert text at a specific line number in a file.
        
        Args:
            file (str): Path to the file to edit
            line (int): Line number to insert after (0 = beginning of file)
            text (str): Text to insert
            
        Returns:
            Confirmation of insertion with a snippet around the inserted area
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Insert text at a specific line."""
        file_path = kwargs.get("file", "")
        insert_line = kwargs.get("line", 0)
        text = kwargs.get("text", "")

        if not file_path:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No file path provided",
                success=False,
                error="Missing 'file' argument",
            )

        try:
            # Read the current file content
            result = await self.computer.execute_shell(f"cat '{file_path}' 2>/dev/null || echo ''")
            file_content = result.text_output
            
            # Split into lines
            lines = file_content.split('\n') if file_content else ['']
            
            # Validate insert_line
            if insert_line < 0 or insert_line > len(lines):
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error: line {insert_line} is out of range. File has {len(lines)} lines.",
                    success=False,
                    error="Invalid line number",
                )

            # Insert the text
            text_lines = text.split('\n')
            new_lines = lines[:insert_line] + text_lines + lines[insert_line:]
            new_content = '\n'.join(new_lines)

            # Write the new content
            python_code = f"""
import os
# Ensure directory exists
os.makedirs(os.path.dirname('{file_path}'), exist_ok=True)

# Write the file
with open('{file_path}', 'w') as f:
    f.write({repr(new_content)})

# Show a snippet around the insertion
lines = {repr(new_content)}.split('\\n')
start = max(0, {insert_line} - 3)
end = min(len(lines), {insert_line} + len({repr(text_lines)}) + 3)
snippet_lines = [f"{{i+1:4d}}: {{line}}" for i, line in enumerate(lines[start:end], start)]

print("Text inserted successfully!")
print("\\nSnippet around the insertion:")
print("\\n".join(snippet_lines))

size = os.path.getsize('{file_path}')
print(f"\\nFile size: {{size}} bytes")
"""

            python_result = await self.computer.execute_python(python_code)
            
            if python_result.status == "success":
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=python_result.output,
                    success=True,
                )
            else:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error during insertion: {python_result.output}",
                    success=False,
                    error=python_result.output,
                )

        except Exception as e:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Error during insert: {str(e)}",
                success=False,
                error=str(e),
            )


class ThinkTool(Tool):
    """Tool for explicit reasoning and thinking steps."""

    @property
    def name(self) -> str:
        return "think"

    @property
    def description(self) -> str:
        return """Use this tool to think through a problem or record reasoning steps.
        
        This tool doesn't change the environment or obtain new information, but helps
        you organize your thoughts and reasoning process.
        
        Args:
            thought (str): Your reasoning, analysis, or thoughts about the current situation
            
        Returns:
            Confirmation that the thought was recorded
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Record a thought or reasoning step."""
        thought = kwargs.get("thought", "")
        
        if not thought:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No thought provided",
                success=False,
                error="Missing 'thought' argument",
            )
        
        # The thought is just recorded in the conversation - no action needed
        return ToolResult(
            tool_call_id=kwargs.get("tool_call_id", ""),
            content="",
            success=True,
        )


class WebSearchTool(Tool):
    """Tool for searching the web (simplified implementation)."""

    def __init__(self, computer: ComputerInterface):
        self.computer = computer

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return """Search the web for information.
        
        Args:
            query (str): Search query to look up
            num_results (int): Number of results to return (default: 3, max: 10)
            
        Returns:
            Search results with URLs and snippets
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Perform a web search using curl and basic scraping."""
        query = kwargs.get("query", "")
        num_results = min(kwargs.get("num_results", 3), 10)

        if not query:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No search query provided",
                success=False,
                error="Missing 'query' argument",
            )

        try:
            # Use Python to perform a basic web search simulation
            # In a real implementation, you'd use Google Custom Search API or similar
            python_code = f"""
import urllib.parse
import json

# Simulate web search results (in real implementation, use actual search API)
query = {repr(query)}
encoded_query = urllib.parse.quote_plus(query)

# Simulate search results based on query
search_results = []

# Add some generic helpful results based on common queries
if any(term in query.lower() for term in ['python', 'programming', 'code']):
    search_results.extend([
        {{
            "title": "Python Documentation",
            "url": "https://docs.python.org/3/",
            "snippet": "Official Python documentation with tutorials, library reference, and language reference."
        }},
        {{
            "title": "Stack Overflow - Python",
            "url": "https://stackoverflow.com/questions/tagged/python",
            "snippet": "Questions and answers about Python programming."
        }}
    ])

if any(term in query.lower() for term in ['machine learning', 'ml', 'ai']):
    search_results.extend([
        {{
            "title": "Scikit-learn Documentation",
            "url": "https://scikit-learn.org/stable/",
            "snippet": "Machine learning library for Python with simple and efficient data mining tools."
        }},
        {{
            "title": "TensorFlow Documentation",
            "url": "https://www.tensorflow.org/",
            "snippet": "Open source machine learning platform with comprehensive ecosystem of tools."
        }}
    ])

if any(term in query.lower() for term in ['github', 'git', 'repository']):
    search_results.extend([
        {{
            "title": "GitHub",
            "url": "https://github.com/",
            "snippet": "Platform for version control and collaboration for software development projects."
        }}
    ])

# Add generic search results if no specific matches
if not search_results:
    search_results = [
        {{
            "title": f"Search results for: {{query}}",
            "url": f"https://www.google.com/search?q={{encoded_query}}",
            "snippet": f"Web search results for your query: {{query}}"
        }}
    ]

# Limit results
search_results = search_results[:{num_results}]

print("Web Search Results:")
print("=" * 50)
for i, result in enumerate(search_results, 1):
    print(f"{{i}}. {{result['title']}}")
    print(f"   URL: {{result['url']}}")
    print(f"   {{result['snippet']}}")
    print()

print(f"Found {{len(search_results)}} results for query: {{query}}")
"""

            result = await self.computer.execute_python(python_code)
            
            if result.status == "success":
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=result.output,
                    success=True,
                )
            else:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Error during web search: {result.output}",
                    success=False,
                    error=result.output,
                )

        except Exception as e:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Error during web search: {str(e)}",
                success=False,
                error=str(e),
            )


class WebBrowserTool(Tool):
    """Tool for basic web browsing (simplified implementation)."""

    def __init__(self, computer: ComputerInterface):
        self.computer = computer

    @property
    def name(self) -> str:
        return "web_browser"

    @property
    def description(self) -> str:
        return """Navigate to a web page and extract its content.
        
        Args:
            url (str): URL to navigate to
            action (str): Action to perform - 'go' to navigate, 'extract' to get text content
            
        Returns:
            Web page content or navigation result
        """

    async def execute(self, **kwargs) -> ToolResult:
        """Navigate to a web page and extract content."""
        url = kwargs.get("url", "")
        action = kwargs.get("action", "go")

        if not url:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content="Error: No URL provided",
                success=False,
                error="Missing 'url' argument",
            )

        try:
            # Use curl to fetch web content
            if action == "go" or action == "extract":
                python_code = f"""
import subprocess
import re
from urllib.parse import urlparse

url = {repr(url)}
print(f"Navigating to: {{url}}")

try:
    # Use curl to fetch the webpage
    result = subprocess.run([
        'curl', '-s', '-L', '--max-time', '10', 
        '--user-agent', 'Mozilla/5.0 (compatible; WebBrowser/1.0)',
        url
    ], capture_output=True, text=True, timeout=15)
    
    if result.returncode != 0:
        print(f"Error fetching URL: {{result.stderr}}")
    else:
        html_content = result.stdout
        
        # Basic HTML parsing to extract text content
        # Remove HTML tags
        text_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text_content = re.sub(r'<style[^>]*>.*?</style>', '', text_content, flags=re.DOTALL | re.IGNORECASE)
        text_content = re.sub(r'<[^>]+>', '', text_content)
        
        # Clean up whitespace
        text_content = re.sub(r'\\s+', ' ', text_content).strip()
        
        # Limit content length
        if len(text_content) > 2000:
            text_content = text_content[:2000] + "... [content truncated]"
        
        print("Successfully fetched webpage content:")
        print("-" * 50)
        print(text_content)
        print("-" * 50)
        print(f"Content length: {{len(result.stdout)}} characters (showing first 2000)")
        
except subprocess.TimeoutExpired:
    print("Error: Request timed out")
except Exception as e:
    print(f"Error fetching webpage: {{e}}")
"""

                result = await self.computer.execute_python(python_code)
                
                if result.status == "success":
                    return ToolResult(
                        tool_call_id=kwargs.get("tool_call_id", ""),
                        content=result.output,
                        success=True,
                    )
                else:
                    return ToolResult(
                        tool_call_id=kwargs.get("tool_call_id", ""),
                        content=f"Error during web browsing: {result.output}",
                        success=False,
                        error=result.output,
                    )
            else:
                return ToolResult(
                    tool_call_id=kwargs.get("tool_call_id", ""),
                    content=f"Unknown action: {action}. Use 'go' or 'extract'.",
                    success=False,
                    error="Invalid action",
                )

        except Exception as e:
            return ToolResult(
                tool_call_id=kwargs.get("tool_call_id", ""),
                content=f"Error during web browsing: {str(e)}",
                success=False,
                error=str(e),
            )


class MockLLMClient:
    """Mock LLM client that provides hardcoded responses for testing."""

    def __init__(self, model: str = "mock"):
        self.model = model
        self.turn_count = 0

    async def generate_response(
        self, messages: List[ChatMessage], tools: List[Tool]
    ) -> ChatMessage:
        """Generate a mock response based on the task."""
        self.turn_count += 1

        # Look for task context to determine appropriate response
        _ = messages[-1] if messages else None

        # Check for tool results to determine next step
        has_read_instructions = any(
            msg.role == "tool" and "fibonacci" in msg.content.lower() for msg in messages
        )

        _ = any(msg.role == "tool" and "fibonacci.py" in msg.content.lower() for msg in messages)

        if self.turn_count == 1:
            # First turn: read instructions
            return ChatMessage(
                role="assistant",
                content="I'll start by reading the task instructions to understand what needs to be done.",
                tool_calls=[
                    ToolCall(function="read_file", arguments={"file": "/task/instructions.md"})
                ],
            )
        elif self.turn_count == 2 and has_read_instructions:
            # Second turn: think about the approach
            return ChatMessage(
                role="assistant",
                content="Let me think about the best approach for this task.",
                tool_calls=[
                    ToolCall(
                        function="think",
                        arguments={"thought": "I need to create a fibonacci function that generates the first 100 numbers. I'll create a Python script that implements this efficiently and saves it to the results directory."},
                    )
                ],
            )
        elif self.turn_count == 3:
            # Third turn: create fibonacci script
            fibonacci_code = """def fibonacci(n):
    fib_sequence = []
    a, b = 0, 1
    for _ in range(n):
        fib_sequence.append(a)
        a, b = b, a + b
    return fib_sequence

if __name__ == "__main__":
    fib_numbers = fibonacci(100)
    print("Fibonacci numbers:")
    print(", ".join(map(str, fib_numbers)))"""

            return ChatMessage(
                role="assistant",
                content="Now I'll create the fibonacci function and save it to the results directory.",
                tool_calls=[
                    ToolCall(
                        function="write_file",
                        arguments={"file": "/results/fibonacci.py", "content": fibonacci_code},
                    )
                ],
            )
        elif self.turn_count == 4:
            # Fourth turn: test the code
            return ChatMessage(
                role="assistant",
                content="Let me test the fibonacci function to make sure it works correctly.",
                tool_calls=[
                    ToolCall(
                        function="python",
                        arguments={
                            "code": """def fibonacci(n):
    fib_sequence = []
    a, b = 0, 1
    for _ in range(n):
        fib_sequence.append(a)
        a, b = b, a + b
    return fib_sequence

fib_numbers = fibonacci(100)
print("Fibonacci numbers:")
print(", ".join(map(str, fib_numbers)))"""
                        },
                    )
                ],
            )
        else:
            # Final turn: end task
            return ChatMessage(
                role="assistant",
                content="Perfect! I've successfully created the fibonacci function that generates the first 100 Fibonacci numbers. The script has been saved to /results/fibonacci.py and tested.",
                tool_calls=[
                    ToolCall(
                        function="end_task",
                        arguments={"message": "Fibonacci script created and tested successfully."},
                    )
                ],
            )


class OpenAILLMClient:
    """Real OpenAI client for GPT-4o-mini."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        try:
            import openai

            self.client = openai.AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = model
        except ImportError:
            raise RuntimeError("OpenAI package not installed. Run: pip install openai")

    def _format_tools_for_openai(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """Format tools for OpenAI API."""
        formatted_tools = []
        for tool in tools:
            # Extract parameter info from description
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            }

            # Add basic parameters based on tool type
            if tool.name == "bash":
                tool_def["function"]["parameters"]["properties"]["cmd"] = {
                    "type": "string",
                    "description": "The bash command to execute",
                }
                tool_def["function"]["parameters"]["required"] = ["cmd"]
            elif tool.name == "python":
                tool_def["function"]["parameters"]["properties"]["code"] = {
                    "type": "string",
                    "description": "The Python code to execute",
                }
                tool_def["function"]["parameters"]["required"] = ["code"]
            elif tool.name == "read_file":
                tool_def["function"]["parameters"]["properties"] = {
                    "file": {"type": "string", "description": "Path to the file to read"},
                    "start_line": {
                        "type": "integer",
                        "description": "Line to start reading from (1-indexed)",
                        "default": 1,
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "Maximum lines to read",
                        "default": 50,
                    },
                }
                tool_def["function"]["parameters"]["required"] = ["file"]
            elif tool.name == "write_file":
                tool_def["function"]["parameters"]["properties"] = {
                    "file": {"type": "string", "description": "Path to the file to write"},
                    "content": {"type": "string", "description": "Content to write to the file"},
                }
                tool_def["function"]["parameters"]["required"] = ["file", "content"]
            elif tool.name == "str_replace":
                tool_def["function"]["parameters"]["properties"] = {
                    "file": {"type": "string", "description": "Path to the file to edit"},
                    "old_str": {"type": "string", "description": "The exact string to replace (must be unique)"},
                    "new_str": {"type": "string", "description": "The new string to replace with", "default": ""},
                }
                tool_def["function"]["parameters"]["required"] = ["file", "old_str"]
            elif tool.name == "insert":
                tool_def["function"]["parameters"]["properties"] = {
                    "file": {"type": "string", "description": "Path to the file to edit"},
                    "line": {"type": "integer", "description": "Line number to insert after (0 = beginning)", "default": 0},
                    "text": {"type": "string", "description": "Text to insert"},
                }
                tool_def["function"]["parameters"]["required"] = ["file", "text"]
            elif tool.name == "think":
                tool_def["function"]["parameters"]["properties"]["thought"] = {

                    "type": "string",
                    "description": "Your reasoning or thoughts about the current situation",
                }
                tool_def["function"]["parameters"]["required"] = ["thought"]
            elif tool.name == "web_search":
                tool_def["function"]["parameters"]["properties"] = {
                    "query": {"type": "string", "description": "Search query to look up"},
                    "num_results": {"type": "integer", "description": "Number of results (max 10)", "default": 3},
                }
                tool_def["function"]["parameters"]["required"] = ["query"]
            elif tool.name == "web_browser":
                tool_def["function"]["parameters"]["properties"] = {
                    "url": {"type": "string", "description": "URL to navigate to"},
                    "action": {"type": "string", "description": "Action: 'go' or 'extract'", "default": "go"},
                }
                tool_def["function"]["parameters"]["required"] = ["url"]
            elif tool.name == "end_task":
                tool_def["function"]["parameters"]["properties"]["message"] = {
                    "type": "string",
                    "description": "Optional completion message",
                }
                tool_def["function"]["parameters"]["required"] = []

            formatted_tools.append(tool_def)

        return formatted_tools

    def _messages_to_openai_format(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """Convert internal messages to OpenAI format."""
        openai_messages = []
        
        # Track tool calls to ensure proper pairing
        pending_tool_calls = {}  # tool_call_id -> tool_call_info
        
        for i, msg in enumerate(messages):
            if msg.role == "system":
                openai_messages.append({"role": "system", "content": msg.content})
            elif msg.role == "user":
                openai_messages.append({"role": "user", "content": msg.content})
            elif msg.role == "assistant":
                openai_msg = {"role": "assistant", "content": msg.content}
                if msg.tool_calls:
                    openai_msg["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function,
                                "arguments": json.dumps(tc.arguments),
                            },
                        }
                        for tc in msg.tool_calls
                    ]
                    # Track these tool calls
                    for tc in msg.tool_calls:
                        pending_tool_calls[tc.id] = {
                            "function": tc.function,
                            "arguments": tc.arguments
                        }
                openai_messages.append(openai_msg)
            elif msg.role == "tool":
                # Only add tool messages if we have the corresponding tool call
                if msg.tool_call_id in pending_tool_calls:
                    openai_messages.append(
                        {"role": "tool", "tool_call_id": msg.tool_call_id, "content": msg.content}
                    )
                    # Remove from pending since it's been handled
                    del pending_tool_calls[msg.tool_call_id]
                else:
                    # Skip orphaned tool messages that don't have corresponding tool calls
                    # This can happen when context is truncated
                    continue

        return openai_messages

    async def generate_response(
        self, messages: List[ChatMessage], tools: List[Tool]
    ) -> ChatMessage:
        """Generate response using OpenAI API."""
        try:
            openai_messages = self._messages_to_openai_format(messages)
            openai_tools = self._format_tools_for_openai(tools)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                tools=openai_tools,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=2000,
            )

            message = response.choices[0].message

            # Convert back to our format
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append(
                        ToolCall(
                            id=tc.id,
                            function=tc.function.name,
                            arguments=json.loads(tc.function.arguments),
                        )
                    )

            return ChatMessage(
                role="assistant", content=message.content or "", tool_calls=tool_calls
            )

        except Exception as e:
            # Fallback message if API fails
            return ChatMessage(
                role="assistant",
                content=f"I encountered an error calling the API: {str(e)}. Let me try to complete the task anyway.",
                tool_calls=[
                    ToolCall(function="end_task", arguments={"message": f"API Error: {str(e)}"})
                ],
            )


class ReActAgent(TaskSolver):
    """ReAct agent implementation similar to PaperBench."""

    def __init__(
        self,
        llm_client: Optional[OpenAILLMClient] = None,
        verbose: bool = True,
        trace_logger: Optional[TraceLogger] = None,
    ):
        self.llm_client = llm_client or OpenAILLMClient()
        self.tools: Dict[str, Tool] = {}
        self.verbose = verbose
        self.trace_logger = trace_logger or TraceLogger()

    def add_tool(self, tool: Tool) -> None:
        """Add a tool to the agent."""
        self.tools[tool.name] = tool

    async def solve(
        self, task: Task, computer: ComputerInterface
    ) -> AsyncGenerator[Union[Step, FinalResult], None]:
        """Solve the task using ReAct pattern with tools."""
        start_time = time.time()

        # Initialize tools
        self.add_tool(BashTool(computer))
        self.add_tool(PythonTool(computer))
        self.add_tool(ReadFileTool(computer))
        self.add_tool(WriteFileTool(computer))
        self.add_tool(StrReplaceTool(computer))
        self.add_tool(InsertTool(computer))
        self.add_tool(ThinkTool())
        self.add_tool(WebSearchTool(computer))
        self.add_tool(WebBrowserTool(computer))
        self.add_tool(EndTaskTool())

        # Initialize conversation
        state = ConversationState(max_turns=50, time_limit=task.timeout)

        # System message
        system_message = ChatMessage(
            role="system",
            content="""You are a helpful AI agent that can use tools to solve programming tasks. 

Available tools:
- bash: Execute bash commands in the container
- python: Execute Python code directly
- read_file: Read files with pagination (supports files in /task and other locations)
- write_file: Write files (save outputs to /results for export)
- str_replace: Replace specific strings in files (for precise editing)
- insert: Insert text at specific line numbers in files
- think: Record your reasoning and thought process
- web_search: Search the web for information (simplified implementation)
- web_browser: Navigate to web pages and extract content
- end_task: Signal task completion

You should work step by step, using tools to explore, code, test, and verify your solution.
Always test your code to make sure it works correctly before completing the task.

IMPORTANT: 
- You have access to bash, so you can install any dependencies if you need them.
- The task instructions and any supporting files are mounted at /task in the container
- Save any output files to the /results directory so they can be exported to the host system
- You can read /task/instructions.md to see the full task instructions
- The /results directory is automatically mounted and will be available on the host after task completion
- Use str_replace for precise file editing when you need to modify specific parts of existing files
- Use the think tool to organize your reasoning and planning
- Web tools provide basic functionality for research (simplified implementations)
- Try not to write over and over again to a file and edit when applicable instead.""",
        )
        state.add_message(system_message)

        # Initial user message with task-specific instructions
        user_message = ChatMessage(
            role="user",
            content=f"""Please solve this task: {task.task_id}

The task instructions are available at /task/instructions.md in the container. Please start by reading the instructions to understand what you need to do.

Task preview:
{task.instructions}

Work through this step by step, using the available tools to complete the task.""",
        )
        state.add_message(user_message)

        if self.verbose:
            console_logger.task_header(task.task_id, list(self.tools.keys()), task.timeout, state.max_turns)

        try:
            # Main ReAct loop
            while not state.completed:
                state.current_turn += 1

                if self.verbose:
                    console_logger.turn_header(state.current_turn, state.max_turns)

                yield Step(
                    step_type="reasoning",
                    content=f"Turn {state.current_turn}: Generating response with {len(self.tools)} tools available",
                )

                # Show what we're sending to the LLM
                if self.verbose:
                    console_logger.model_input(state.get_recent_context(), list(self.tools.keys()))

                # Get model response with spinner
                if self.verbose:
                    from rich.spinner import Spinner
                    from rich.live import Live
                    from rich.text import Text
                    
                    spinner_text = Text("Sampling from language model...", style="bold blue")
                    spinner = Spinner("dots", text=spinner_text)
                    
                    with Live(spinner, console=console, refresh_per_second=10) as live:
                        response = await self.llm_client.generate_response(
                            state.get_recent_context(), list(self.tools.values())
                        )
                        live.update("")  # Clear spinner text when done
                else:
                    response = await self.llm_client.generate_response(
                        state.get_recent_context(), list(self.tools.values())
                    )
                
                state.add_message(response)

                # Show what we got back from the LLM
                if self.verbose:
                    console_logger.model_output(response.content, response.tool_calls)

                # Execute tool calls if any
                if response.tool_calls:
                    yield Step(
                        step_type="tool_execution",
                        content=f"Executing {len(response.tool_calls)} tool call(s): {[tc.function for tc in response.tool_calls]}",
                    )

                    for tool_call in response.tool_calls:
                        if tool_call.function in self.tools:
                            tool = self.tools[tool_call.function]

                            # Execute tool
                            tool_result = await tool.execute(
                                tool_call_id=tool_call.id, **tool_call.arguments
                            )

                            if self.verbose:
                                console_logger.container_action(
                                    f"[bold white]{tool_call.function}[/]([bold pink]{json.dumps(tool_call.arguments, indent=2)}[/])",
                                    tool_result.content,
                                    tool_result.success,
                                )

                            # Add tool result to conversation
                            result_message = ChatMessage(
                                role="tool", content=tool_result.content, tool_call_id=tool_call.id
                            )
                            state.add_message(result_message)

                            # Check if this was an end_task call
                            if tool_call.function == "end_task":
                                execution_time = time.time() - start_time

                                # Save trace before returning
                                metadata = {
                                    "success": True,
                                    "score": 1.0,
                                    "execution_time": execution_time,
                                    "turns": state.current_turn,
                                    "end_reason": "end_task_called",
                                }
                                self.trace_logger.save_trace(task.task_id, state.messages, metadata)

                                if self.verbose:
                                    console_logger.final_result(
                                        True,
                                        1.0,
                                        execution_time,
                                        f"Task completed successfully. Tool result: {tool_result.content}",
                                    )
                                yield FinalResult(
                                    success=True,
                                    score=1.0,
                                    output=f"Task completed successfully. Tool result: {tool_result.content}",
                                    execution_time=execution_time,
                                )
                                return
                        else:
                            # Unknown tool
                            error_message = ChatMessage(
                                role="tool",
                                content=f"Error: Unknown tool '{tool_call.function}'",
                                tool_call_id=tool_call.id,
                            )
                            state.add_message(error_message)
                            if self.verbose:
                                console_logger.error(f"Unknown tool '{tool_call.function}'")

                # Add progress update
                if state.current_turn % 3 == 0:
                    elapsed = time.time() - start_time
                    console_logger.progress(
                        f"Turn {state.current_turn}, {elapsed:.1f}s elapsed. Continue working or use end_task when complete."
                    )

                if self.verbose:
                    print()  # Add spacing between turns

            # If we exit the loop without end_task, return final result
            execution_time = time.time() - start_time

            # Save trace for timeout/limit case
            metadata = {
                "success": False,
                "score": 0.5,
                "execution_time": execution_time,
                "turns": state.current_turn,
                "end_reason": "limits_reached",
            }
            self.trace_logger.save_trace(task.task_id, state.messages, metadata)

            if self.verbose:
                console_logger.final_result(
                    False,
                    0.5,
                    execution_time,
                    f"Task ended due to limits (turns: {state.current_turn}, time: {execution_time:.1f}s)",
                )
            yield FinalResult(
                success=False,
                score=0.5,  # Partial credit for attempting
                output=f"Task ended due to limits (turns: {state.current_turn}, time: {execution_time:.1f}s)",
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time

            # Save trace for error case
            metadata = {
                "success": False,
                "score": 0.0,
                "execution_time": execution_time,
                "turns": state.current_turn,
                "end_reason": "error",
                "error": str(e),
            }
            self.trace_logger.save_trace(task.task_id, state.messages, metadata)

            if self.verbose:
                console_logger.final_result(False, 0.0, execution_time, f"Error during execution: {str(e)}")
            yield FinalResult(
                success=False,
                score=0.0,
                output=f"Error during execution: {str(e)}",
                execution_time=execution_time,
                error=str(e),
            )


# =============================================================================
# ORCHESTRATION RUNTIME
# =============================================================================


class ContainerRuntime:
    """Manages the lifecycle of containerized task execution."""

    def __init__(self):
        self.exit_stack = AsyncExitStack()

    @asynccontextmanager
    async def create_computer(
        self, config: ContainerConfig, backend_type: str = "local"
    ) -> AsyncGenerator[ComputerInterface, None]:
        """Create and manage a computer interface for the given configuration."""
        # Create backend based on type
        if backend_type == "beaker":
            from minienv.backend.beaker import BeakerBackend
            backend = BeakerBackend()
        else:  # default to local
            backend = LocalBackend(
                environment=config.environment or {"PYTHONUNBUFFERED": "1"},
                volumes=config.volumes or {},
                ports=config.ports or [],
                privileged=config.privileged,
                gpu_access=config.gpu_access,
                memory_limit=config.memory_limit,
                timeout=config.timeout,
                results_host_path=config.results_host_path
            )

        try:
            # Create interface using the backend adapter
            from minienv.backend.adapter import BackendComputerInterface
            computer = BackendComputerInterface(backend)

            # Register cleanup
            self.exit_stack.push_async_callback(computer.cleanup)

            yield computer

        except Exception as e:
            await backend.teardown()
            raise e

    async def run_task(self, task: Task, solver: TaskSolver, backend_type: str = "local") -> List[Union[Step, FinalResult]]:
        """Run a task with the given solver."""
        results = []

        try:
            async with self.create_computer(task.config, backend_type) as computer:
                logger.info(f"Running task {task.task_id}")

                # Initialize the backend environment with task info and existing task folder
                await computer.backend.create_env(
                    task_name=task.task_id, 
                    image=task.config.image,
                    task_files=[task.task_folder]
                )

                async for result in solver.solve(task, computer):
                    results.append(result)
                    logger.info(f"Task {task.task_id}: {result}")

        finally:
            # Clean up temporary task files
            task.cleanup_temp_files()

        return results

    async def cleanup(self) -> None:
        """Clean up all managed resources."""
        await self.exit_stack.aclose()


# =============================================================================
# MULTI-STAGE EVALUATION PIPELINE
# =============================================================================


class EvaluationPipeline:
    """Multi-stage evaluation pipeline similar to PaperBench."""

    def __init__(self):
        self.runtime = ContainerRuntime()

    async def run_evaluation(
        self,
        agent_config: ContainerConfig,
        reproduction_config: ContainerConfig,
        judge_config: ContainerConfig,
        task_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run a complete 3-stage evaluation."""

        results = {"task_id": task_data.get("id", "unknown"), "stages": {}, "final_score": 0.0}

        try:
            # Stage 1: Agent Rollout
            logger.info("Stage 1: Agent Rollout")
            agent_task = Task(task_id=f"{task_data['id']}-agent", config=agent_config)
            agent_solver = SimpleTaskSolver()  # Replace with actual agent solver
            agent_results = await self.runtime.run_task(agent_task, agent_solver)
            results["stages"]["agent"] = [r.model_dump() for r in agent_results]

            # Stage 2: Reproduction
            logger.info("Stage 2: Reproduction")
            reproduction_task = Task(
                task_id=f"{task_data['id']}-reproduction", config=reproduction_config
            )
            reproduction_solver = SimpleTaskSolver()  # Replace with reproduction solver
            reproduction_results = await self.runtime.run_task(
                reproduction_task, reproduction_solver
            )
            results["stages"]["reproduction"] = [r.model_dump() for r in reproduction_results]

            # Stage 3: Judging
            logger.info("Stage 3: Judging")
            judge_task = Task(task_id=f"{task_data['id']}-judge", config=judge_config)
            judge_solver = SimpleTaskSolver()  # Replace with judge solver
            judge_results = await self.runtime.run_task(judge_task, judge_solver)
            results["stages"]["judge"] = [r.model_dump() for r in judge_results]

            # Calculate final score
            final_results = [r for r in judge_results if isinstance(r, FinalResult)]
            if final_results:
                results["final_score"] = final_results[-1].score

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            results["error"] = str(e)

        finally:
            await self.runtime.cleanup()

        return results


# =============================================================================
# UPDATED EXAMPLE USAGE
# =============================================================================


async def run_task_example(task_id: str = None, backend: str = "local", traces_dir: str = "traces"):
    """Example using the PaperBench-style ReAct agent with dynamic task loading."""

    # Configure base container with Python and common tools
    base_config = ContainerConfig(
        image="python:3.11-slim",
        environment={"PYTHONUNBUFFERED": "1", "DEBIAN_FRONTEND": "noninteractive"},
        timeout=1800,  # 30 minutes
    )

    # Load tasks from the tasks/ directory
    task_loader = TaskLoader("tasks")
    available_tasks = task_loader.list_tasks()

    if not available_tasks:
        print("❌ No tasks found in tasks/ directory")
        return

    if task_id not in available_tasks:
        print(f"Available tasks: {', '.join(available_tasks)}")
        return
    else:
        console.rule(f"[bold green]Task:[/] [bold red]{task_id}[/]", style="bold green")

    # Load the specific task
    try:
        task = task_loader.load_task(task_id, base_config)
        print(f"Loaded task '{task_id}' from {task.task_folder}")
    except Exception as e:
        print(f"❌ Failed to load task '{task_id}': {e}")
        return

    # Create runtime and run ReAct agent
    runtime = ContainerRuntime()

    # Create trace logger
    trace_logger = TraceLogger(traces_dir)

    # Use ReAct agent
    try:
        openai_client = OpenAILLMClient(model="gpt-4o-mini")
        react_agent = ReActAgent(llm_client=openai_client, verbose=True, trace_logger=trace_logger)
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        print("Make sure you have OPENAI_API_KEY set in your environment")
        print("Falling back to mock agent...")
        mock_client = MockLLMClient()
        react_agent = ReActAgent(llm_client=mock_client, verbose=True, trace_logger=trace_logger)

    try:
        results = await runtime.run_task(task, react_agent, backend_type=backend)
        
    finally:
        await runtime.cleanup()


async def list_tasks_example():
    """Example showing how to list available tasks."""
    task_loader = TaskLoader("tasks")
    available_tasks = task_loader.list_tasks()

    if not available_tasks:
        print("❌ No tasks found in tasks/ directory")
        return

    print("Available tasks:")
    for task_id in available_tasks:
        try:
            instructions = task_loader.get_task_instructions(task_id)
            # Show first line of instructions as preview
            preview = instructions.split("\n")[0][:80] + (
                "..." if len(instructions.split("\n")[0]) > 80 else ""
            )
            print(f"  • {task_id}: {preview}")
        except Exception as e:
            print(f"  • {task_id}: (error reading instructions: {e})")


async def load_and_display_trace(trace_path: str):
    """Example showing how to load and display a trace file."""
    trace_logger = TraceLogger()

    try:
        trace_data = trace_logger.load_trace(trace_path)

        print(f"\n=== Trace: {trace_data['task_id']} ===")
        print(f"Timestamp: {trace_data['timestamp']}")
        print(f"Metadata: {json.dumps(trace_data['metadata'], indent=2)}")
        print(f"Total Messages: {len(trace_data['messages'])}")

        print("\n=== Message History ===")
        for i, msg in enumerate(trace_data["messages"], 1):
            print(f"\n[{i}] {msg['role'].upper()}")
            if msg["content"]:
                content_preview = msg["content"][:200] + (
                    "..." if len(msg["content"]) > 200 else ""
                )
                print(f"Content: {content_preview}")

            if msg["tool_calls"]:
                print(f"Tool Calls ({len(msg['tool_calls'])}):")
                for tc in msg["tool_calls"]:
                    print(f"  - {tc['function']}({json.dumps(tc['arguments'])})")

            if msg["tool_call_id"]:
                print(f"Tool Call ID: {msg['tool_call_id']}")

    except Exception as e:
        print(f"❌ Failed to load trace: {e}")
