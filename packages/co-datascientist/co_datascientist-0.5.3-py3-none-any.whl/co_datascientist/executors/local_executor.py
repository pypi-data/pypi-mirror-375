"""Local Python code executor."""

import os
import subprocess
import tempfile
import time
import logging
from typing import Dict, Any

from .base_executor import BaseExecutor
from ..models import CodeResult
from ..settings import settings


class LocalExecutor(BaseExecutor):
    """Executor for running Python code locally."""
    
    @property
    def platform_name(self) -> str:
        return "local"
    
    def execute(self, code: str) -> CodeResult:
        """Execute Python code locally using subprocess.
        
        Args:
            code: Python code to execute
            
        Returns:
            CodeResult containing stdout, stderr, return_code, and runtime_ms
        """
        start_time = time.time()
        
        # Write the code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file_path = temp_file.name

        command = [self.python_path, temp_file_path]

        # Run the command
        logging.info(f"Running local command: {command}")
        try:
            output = subprocess.run(
                command,
                capture_output=True,
                text=True,
                input="",  # prevents it from blocking on stdin
                timeout=settings.script_execution_timeout
            )
            return_code = output.returncode
            out = output.stdout
            err = output.stderr
        except subprocess.TimeoutExpired:
            # Handle timeout gracefully - mark as failed case and continue
            return_code = -9  # Standard timeout return code
            out = None
            err = f"Process timed out after {settings.script_execution_timeout} seconds"
            logging.info(f"Process timed out after {settings.script_execution_timeout} seconds")
        
        # Clean up empty strings
        if isinstance(out, str) and out.strip() == "":
            out = None
        if isinstance(err, str) and err.strip() == "":
            err = None

        logging.info(f"Local execution stdout: {out}")
        logging.info(f"Local execution stderr: {err}")

        # Delete the temporary file
        try:
            os.remove(temp_file_path)
        except OSError:
            pass  # Ignore cleanup errors
            
        runtime_ms = int((time.time() - start_time) * 1000)
        return CodeResult(
            stdout=out, 
            stderr=err, 
            return_code=return_code, 
            runtime_ms=runtime_ms
        )
    
    def is_available(self) -> bool:
        """Check if Python interpreter is available."""
        try:
            result = subprocess.run(
                [self.python_path, "--version"], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
