import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
import asyncio
import pathlib
import base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
import uuid

from .models import Workflow, SystemInfo, CodeResult
from . import co_datascientist_api
from .executors import ExecutorFactory
from .kpi_extractor import extract_kpi_from_stdout
from .settings import settings
from .qa_cache import get_answers, QACache
from .user_steering import get_steering_handler, wrap_spinner_with_coordination

OUTPUT_FOLDER = "co_datascientist_output"
CHECKPOINTS_FOLDER = "co_datascientist_checkpoints"
CURRENT_RUNS_FOLDER = "current_runs"


def print_workflow_info(message: str):
    """Print workflow info with consistent formatting"""
    print(f"   {message}")


def print_workflow_step(message: str):
    """Print workflow step with consistent formatting"""
    print(f"   {message}")


def print_workflow_success(message: str):
    """Print workflow success with consistent formatting"""
    print(f"   {message}")


def print_workflow_error(message: str):
    """Print workflow error with consistent formatting"""
    print(f"   {message}")


class _WorkflowRunner:
    def __init__(self):
        self.workflow: Workflow | None = None
        self.start_timestamp = 0
        self.should_stop_workflow = False
        self.debug_mode = True
        # Track best KPI seen when polling backend
        self._checkpoint_counter: int = 0
        # Track current hypothesis to detect transitions
        self._current_hypothesis: str | None = None
        # User steering handler
        self.steering_handler = get_steering_handler()
        # Track if steering bar has been started (to start only after first batch)
        self._steering_bar_started: bool = False

    async def run_workflow(self, code: str, python_path: str, project_absolute_path: str, config: dict, spinner=None, debug: bool = True):
        """Run a complete code evolution workflow.

        - Sequential mode (default): run one code version at a time.
        - Parallel mode: set config['parallel']=N (>1) to run batches of up to N in parallel.
        """
        self.should_stop_workflow = False
        # Set debug mode for the class instance
        self.debug_mode = debug
        
        # Wrap spinner for coordination with status bar
        spinner = wrap_spinner_with_coordination(spinner)
        # Defer starting the steering bar until after preflight completes
        
        try:
            if spinner:
                spinner.text = "Waking up the Co-DataScientist"
                
            self.start_timestamp = time.time()
            self.should_stop_workflow = False 
            self.workflow = Workflow(status_text="Workflow started", user_id="")

            system_info = get_system_info(python_path)
            logging.info(f"user system info: {system_info}")

            if bool(config.get('preflight', True)):
                # Start preflight: engine generates questions
                preflight = await co_datascientist_api.start_preflight(code, system_info)
                self.workflow = preflight.workflow
                # Stop spinner to allow clean input UX
                if spinner:
                    spinner.stop()
                # Get observation text
                observation = getattr(preflight, 'observation', '') or ''

                # Clean questions
                questions = [re.sub(r'^\d+\.\s*', '', q.strip()) for q in preflight.questions]

                # Get answers (cached or interactive)
                use_cache = config.get('use_cached_qa', False)
                answers = get_answers(questions, str(project_absolute_path), observation, use_cache)
                # Complete preflight: engine summarizes and starts baseline
                response = await co_datascientist_api.complete_preflight(self.workflow.workflow_id, answers)
                self.workflow = response.workflow
            else:
                # Skip preflight entirely for clean backward-compatibility
                response = await co_datascientist_api.start_workflow(code, system_info)
                self.workflow = response.workflow
            if spinner:
                spinner.stop()  # stop spinner without emoji
            print("Running your baseline to start")
            print("--------------------------------")
            
            # Unified batch system: batch_size=1 for sequential, >1 for parallel
            batch_size = int(config.get('parallel', 1) or 1)
            await self._run_unified_batch_mode(response, python_path, project_absolute_path, config, spinner, batch_size)

            # Stop user steering handler
            await self.steering_handler.stop_listening()
            
            if self.should_stop_workflow:
                # Check if this was a baseline failure (already handled) or user stop
                if (hasattr(self.workflow, 'baseline_code') and 
                    self.workflow.baseline_code.result is not None and 
                    self.workflow.baseline_code.result.return_code != 0):
                    # Baseline failure - already handled in _handle_baseline_result, just clean up
                    try:
                        await co_datascientist_api.stop_workflow(self.workflow.workflow_id)
                    except Exception as e:
                        logging.warning(f"Failed to stop workflow on backend: {e}")
                    if spinner:
                        spinner.text = "Workflow failed"
                else:
                    # User-initiated stop
                    await co_datascientist_api.stop_workflow(self.workflow.workflow_id)
                    print_workflow_info("Workflow stopped by user.")
                    if spinner:
                        spinner.text = "Workflow stopped"
            else:
                # Normal successful completion
                print_workflow_success("Workflow completed successfully.")
                if spinner:
                    spinner.text = "Workflow completed"
        
        except Exception as e:
            if spinner:
                spinner.stop()

            err_msg = str(e)
            # Detect user-facing validation errors coming from backend
            if err_msg.startswith("ERROR:") and not self.debug_mode:
                # Show concise guidance without stack trace
                print_workflow_error(err_msg)
                return  # Do not re-raise, end gracefully

            # Otherwise, show generic workflow error and re-raise for full trace
            print_workflow_error(f"Workflow error: {err_msg}")
            raise


## Preflight logic moved to backend/engine – no frontend LLM usage

    async def _run_unified_batch_mode(self, initial_response, python_path: str,
                                     project_absolute_path: str, config: dict,
                                     spinner=None, batch_size: int = 1):
        """Unified batch processing: batch_size=1 for sequential, >1 for parallel.
        
        Always uses batch endpoints and parallel execution (even for batch_size=1).
        Adapts UI display based on batch_size for user experience.
        """
        # Handle baseline from initial response if present
        if initial_response.code_to_run is not None:
            if spinner:
                spinner.stop()
            
            # Run baseline using batch system
            if initial_response.code_to_run.name == "baseline":
                executor = ExecutorFactory.create_executor(python_path, config)
                result = executor.execute(initial_response.code_to_run.code)
                
                await self._handle_baseline_result(result, initial_response, spinner)
                
                # Submit baseline result using batch API
                kpi_value = extract_kpi_from_stdout(result.stdout)
                result.kpi = kpi_value
                code_version = initial_response.code_to_run
                code_version.result = result
                
                try:
                    await self._save_current_run_snapshot(code_version, project_absolute_path, config)
                except Exception as e:
                    logging.warning(f"Failed saving baseline snapshot: {e}")
                
                # Use batch API for consistency
                batch_resp = await co_datascientist_api.finished_running_batch(
                    self.workflow.workflow_id,
                    "baseline_batch",
                    [(code_version.code_version_id, result)],
                )
                self.workflow = batch_resp.workflow

        # Set spinner message based on batch size
        if batch_size == 1:
            if spinner:
                spinner.text = "Testing hypothesis"
                spinner.start()
        else:
            if spinner:
                spinner.text = f"Running {batch_size} programs in parallel..."
                spinner.start()

        # Now get batches for hypothesis testing
        batch_resp = await co_datascientist_api.get_batch_to_run(self.workflow.workflow_id, batch_size=batch_size)

        # If no batch yet, keep polling until we get one or finish
        while (batch_resp.batch_to_run is None
               and not self.workflow.finished
               and not self.should_stop_workflow):
            if spinner:
                spinner.text = "Thinking... (regenerating batch)"
            await asyncio.sleep(1)
            batch_resp = await co_datascientist_api.get_batch_to_run(self.workflow.workflow_id, batch_size=batch_size)
            self.workflow = batch_resp.workflow

        while (not self.workflow.finished
               and not self.should_stop_workflow):

            # Check for user direction updates
            await self._check_user_direction()

            if batch_resp.batch_to_run is None:
                if spinner:
                    spinner.text = "Thinking... (regenerating batch)"
                await asyncio.sleep(1)
                batch_resp = await co_datascientist_api.get_batch_to_run(self.workflow.workflow_id, batch_size=batch_size)
                self.workflow = batch_resp.workflow
                continue

            code_versions = batch_resp.batch_to_run
            batch_id = batch_resp.batch_id

            # Stop spinner to show batch hypotheses
            if spinner:
                spinner.stop()

            # Temporarily suspend bottom bar for clean hypothesis prints
            try:
                self.steering_handler.suspend_bar()
            except Exception:
                pass
            # Display batch information adapted to batch size
            await self._display_batch_info(code_versions, batch_size)

            # Execute batch (single or multiple) using helper method
            executor = ExecutorFactory.create_executor(python_path, config)
            results = await self._execute_batch(executor, code_versions, spinner, batch_size, python_path, config)

            # Stop spinner to show results
            if spinner:
                spinner.stop()

            # Attach KPI values and prepare payload tuples
            tuples: list[tuple[str, CodeResult]] = []
            for cv, res in zip(code_versions, results):
                # For distributed execution, KPI is already extracted by the executor
                # For thread-based execution, we need to extract it here
                if res.kpi is None:
                    kpi_value = extract_kpi_from_stdout(res.stdout)
                    res.kpi = kpi_value
                tuples.append((cv.code_version_id, res))

            # Display results adapted to batch size
            await self._display_batch_results(code_versions, results, batch_size)
            # Resume bottom bar after large prints
            try:
                self.steering_handler.resume_bar()
            except Exception:
                pass

            # Start steering bar only once, after first batch results are shown
            if not self._steering_bar_started:
                try:
                    await self.steering_handler.start_listening()
                    self._steering_bar_started = True
                except Exception:
                    pass

            # Save a simple snapshot of the most recently processed run in this batch
            try:
                if code_versions and results:
                    last_cv = code_versions[-1]
                    last_cv.result = results[-1]
                    await self._save_current_run_snapshot(last_cv, project_absolute_path, config)
            except Exception as e:
                logging.warning(f"Failed saving current run snapshot (parallel): {e}")

            # Submit batch results and get next batch
            batch_resp = await co_datascientist_api.finished_running_batch(
                self.workflow.workflow_id,
                batch_id,
                tuples,
            )
            # Update workflow state
            self.workflow = batch_resp.workflow

            # Optionally display live best KPI (only for meaningful attempts, not retries)
            has_meaningful_results = any(cv.retry_count == 0 or cv.hypothesis_outcome in ["supported", "refuted", "failed"] 
                                       for cv in code_versions)
            if has_meaningful_results:
                try:
                    best_info = await co_datascientist_api.get_workflow_population_best(self.workflow.workflow_id)
                    best_kpi = best_info.get("best_kpi") if best_info else None
                    if best_kpi is not None and spinner:
                        spinner.write(f"Current best KPI: {best_kpi}")
                    # Save checkpoint snapshot of current best (parity with sequential mode)
                    best_cv = best_info.get("best_code_version") if best_info else None
                    if best_cv and best_kpi is not None:
                        await self._save_population_best_checkpoint(best_cv, best_kpi, project_absolute_path, config)

                    elif best_kpi is not None and spinner:
                        spinner.write(f"No code version available for checkpoint (KPI: {best_kpi})")
                except Exception:
                    pass

    # NOTE: _run_sequential_mode removed - unified batch system only
    
    async def _check_user_direction(self):
        """Check for new user direction and update the workflow if needed."""
        try:
            latest_direction = await self.steering_handler.get_latest_direction()
            current_direction = getattr(self.workflow, 'user_direction', None)
            
            # Only update if direction has changed
            if latest_direction != current_direction:
                await co_datascientist_api.update_user_direction(
                    self.workflow.workflow_id, 
                    latest_direction
                )
                # Update local workflow state
                self.workflow.user_direction = latest_direction
                
                # Silent: no echo after steering to keep UI clean
                    
        except Exception as e:
            logging.warning(f"Failed to check user direction: {e}")
    
    async def _display_batch_info(self, code_versions: list, batch_size: int):
        """Silenced: avoid verbose batch info prints."""
        return

    async def _execute_batch(self, executor, code_versions: list, spinner, batch_size: int, python_path: str, config: dict):
        """Execute batch with appropriate concurrency."""
        if batch_size == 1:
            # Sequential execution with adapted spinner
            cv = code_versions[0]
            if cv.name != "baseline" and cv.retry_count > 0:
                if spinner:
                    spinner.text = f"Debugging attempt {cv.retry_count}"
                    spinner.start()
            elif cv.name != "baseline":
                if spinner:
                    spinner.text = "Testing hypothesis"
                    spinner.start()
            
            return [executor.execute(cv.code) for cv in code_versions]
        else:
            # Parallel execution (existing logic)
            if hasattr(executor, 'supports_distributed_execution') and executor.supports_distributed_execution():
                if spinner:
                    spinner.text = f"Submitting {len(code_versions)} jobs to {executor.platform_name}..."
                    spinner.start()
                return await executor.execute_batch_distributed(code_versions)
            else:
                if spinner:
                    spinner.text = f"Running {len(code_versions)} programs in parallel..."
                    spinner.start()
                def _execute(cv):
                    single_executor = ExecutorFactory.create_executor(python_path, config)
                    return single_executor.execute(cv.code)
                tasks = [asyncio.to_thread(_execute, cv) for cv in code_versions]
                return await asyncio.gather(*tasks, return_exceptions=False)

    async def _display_batch_results(self, code_versions: list, results: list, batch_size: int):
        """Display results adapted to batch size."""
        if batch_size == 1:
            # Sequential mode: existing sequential display logic
            cv, result = code_versions[0], results[0]
            kpi_value = getattr(result, 'kpi', None) or extract_kpi_from_stdout(result.stdout)
            
            if cv.name != "baseline":
                if kpi_value is not None and result.return_code == 0:
                    baseline_kpi = self._get_baseline_kpi()
                    hypothesis_outcome = baseline_kpi < kpi_value if baseline_kpi is not None else None
                    print()
                    print(f"Hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                    print(f" - Result: {hypothesis_outcome}, KPI: {kpi_value}")
                    print("--------------------------------")
                else:
                    # Handle failed executions like parallel mode
                    print()
                    print(f"Hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                    if getattr(cv, 'hypothesis_outcome', None) == "failed":
                        print(" - Failed after all retries - moving on")
                    else:
                        print(" - Debugging and queuing for retry...")
                    print("--------------------------------")
        else:
            # Parallel mode: existing parallel display logic
            baseline_kpi = self._get_baseline_kpi()
            successful_results = []
            failed_results = []
            
            for cv, res in zip(code_versions, results):
                kpi_value = getattr(res, 'kpi', None) or extract_kpi_from_stdout(res.stdout)
                if hasattr(res, 'kpi') and res.kpi is None:
                    res.kpi = kpi_value
                    
                if kpi_value is not None and res.return_code == 0:
                    hypothesis_outcome = baseline_kpi < kpi_value if baseline_kpi is not None else None
                    successful_results.append((cv, kpi_value, hypothesis_outcome))
                else:
                    failed_results.append((cv, res))
            
            # Display successful results
            for cv, kpi_value, hypothesis_outcome in successful_results:
                print()
                print(f"Hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                if hypothesis_outcome is not None:
                    print(f" - Result: {hypothesis_outcome}, KPI: {kpi_value}")
                else:
                    print(f" - Result: KPI = {kpi_value}")
            
            # Display failed results - show debugging status
            for cv, res in failed_results:
                print()
                print(f"Hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                if getattr(cv, 'hypothesis_outcome', None) == "failed":
                    print(" - Failed after all retries - moving on")
                else:
                    print(" - Debugging and queuing for retry...")
            
            if code_versions:
                print("--------------------------------")

    def _get_baseline_kpi(self):
        """Get baseline KPI for comparison."""
        if self.workflow.baseline_code and self.workflow.baseline_code.result:
            return extract_kpi_from_stdout(self.workflow.baseline_code.result.stdout)
        return None

    async def _handle_baseline_result(self, result: CodeResult, response, spinner=None):
        """Handle result in standard mode (original behavior)"""
        # Check if code execution failed and provide clear feedback
        if result.return_code != 0:
            # Code failed - show error details
            print_workflow_error(f"'{response.code_to_run.name}' failed with exit code {result.return_code}")
            if result.stderr:
                print("   Error details:")
                # Print each line of stderr with proper indentation
                for line in result.stderr.strip().split('\n'):
                    if spinner:
                        spinner.write(f"      {line}")
                    else:
                        print(f"      {line}")
            
            # For baseline failures, give specific guidance and STOP immediately
            if response.code_to_run.name == "baseline":
                print("   The baseline code failed to run. This will stop the workflow.")
                print("   Check the error above and fix your script before running again.")
                if "ModuleNotFoundError" in (result.stderr or ""):
                    print("   Missing dependencies? Try: pip install <missing-package>")
                
                # Set flag to stop workflow immediately - don't wait for backend
                self.should_stop_workflow = True
                print_workflow_error("Workflow terminated due to baseline failure.")
                return
        else:
            # Code succeeded - show success message
            kpi_value = extract_kpi_from_stdout(result.stdout)
            if kpi_value is not None:
                msg = f"Completed '{response.code_to_run.name}' | KPI = {kpi_value}"
                if spinner:
                    spinner.write(msg)
                    print("--------------------------------")
                else:
                    print_workflow_success(msg)
            elif response.code_to_run.name == "baseline":
                # Debug: baseline succeeded but no KPI extracted
                logging.info(f"Baseline succeeded but no KPI found. Stdout: {result.stdout[:200] if result.stdout else 'None'}...")
                msg = f"Completed '{response.code_to_run.name}' (no KPI found)"
                if spinner:
                    spinner.write(msg)
                    print("--------------------------------")
                else:
                    print_workflow_success(msg)
            else:
                msg = f"Completed '{response.code_to_run.name}'"
                if spinner:
                    spinner.write(msg)
                else:
                    print_workflow_success(msg)

    async def _save_population_best_checkpoint(self, best_cv, best_kpi: float, project_absolute_path: str, config: dict):
        """Persist best code/KPI - to Databricks volume if using Databricks, locally otherwise."""
        try:
            if not best_cv or best_kpi is None:
                return

            # Convert best_cv to CodeVersion model if it is raw dict
            from .models import CodeVersion, CodeResult
            if isinstance(best_cv, dict):
                try:
                    # Nested result may also be dict – handle gracefully
                    if isinstance(best_cv.get("result"), dict):
                        # Ensure runtime_ms field may be missing; allow extra
                        best_cv["result"] = CodeResult.model_validate(best_cv["result"])  # type: ignore
                    best_cv = CodeVersion.model_validate(best_cv)  # type: ignore
                except Exception as e:
                    logging.warning(f"Cannot parse best_code_version payload: {e}")
                    return

            safe_name = _make_filesystem_safe(best_cv.name or "best")
            base_filename = f"best_{self._checkpoint_counter}_{safe_name}"

            # Prepare metadata
            meta = {
                "code_version_id": best_cv.code_version_id,
                "name": best_cv.name,
                "kpi": best_kpi,
                "stdout": getattr(best_cv.result, "stdout", None) if best_cv.result else None,
            }

            # Check if using Databricks
            is_databricks = config and config.get('databricks')
            if is_databricks:
                # Save directly to Databricks volume using CLI (no local storage)
                await self._save_checkpoint_to_databricks_volume(
                    best_cv.code, 
                    json.dumps(meta, indent=4), 
                    base_filename, 
                    config
                )
            else:
                # Original behavior for local runs
                checkpoints_base = Path(project_absolute_path) / CHECKPOINTS_FOLDER
                checkpoints_base.mkdir(parents=True, exist_ok=True)
                
                code_path = checkpoints_base / f"{base_filename}.py"
                meta_path = checkpoints_base / f"{base_filename}.json"
                
                code_path.write_text(best_cv.code, encoding="utf-8")
                meta_path.write_text(json.dumps(meta, indent=4))

            self._checkpoint_counter += 1
        except Exception as e:
            logging.warning(f"Failed saving best checkpoint: {e}")

    async def _save_checkpoint_to_databricks_volume(self, code_content: str, meta_content: str, base_filename: str, config: dict):
        """Save checkpoint files directly to Databricks volume using CLI (following existing upload pattern)."""
        try:
            # Extract databricks configuration (same pattern as _databricks_run_python_code)
            if isinstance(config.get('databricks'), dict):
                databricks_config = config['databricks']
            else:
                databricks_config = config
            
            CLI = databricks_config.get('cli', "databricks")
            VOLUME_URI = databricks_config.get('volume_uri', "dbfs:/Volumes/workspace/default/volume")
            
            # Ensure checkpoints directory exists
            checkpoints_dir = f"{VOLUME_URI}/{CHECKPOINTS_FOLDER}"
            mkdir_result = subprocess.run([CLI, "fs", "mkdir", checkpoints_dir], 
                                        capture_output=True, text=True)
            # mkdir is okay to fail if directory already exists
            
            # Create remote paths
            remote_code_path = f"{checkpoints_dir}/{base_filename}.py"
            remote_meta_path = f"{checkpoints_dir}/{base_filename}.json"
            
            # Save code file using temp file + CLI upload pattern (following existing code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code_content.encode())
                local_tmp_code = pathlib.Path(f.name)
            
            # Try uploading code file
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code), remote_code_path,
                           "--overwrite", "--output", "json"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Failed to upload checkpoint code: {result.stderr}")
                return
            os.unlink(local_tmp_code)
            
            # Save metadata file using temp file + CLI upload pattern
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
                f.write(meta_content.encode())
                local_tmp_meta = pathlib.Path(f.name)
            
            # Try uploading metadata file
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta), remote_meta_path,
                           "--overwrite", "--output", "json"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Failed to upload checkpoint metadata: {result.stderr}")
                return
            os.unlink(local_tmp_meta)
            
            # print(f"Checkpoint uploaded to: {VOLUME_URI}/{CHECKPOINTS_FOLDER}/{base_filename}.*")
            
        except Exception as e:
            print(f"Checkpoint upload error: {e}")

    async def _save_current_run_to_databricks_volume(self, code_content: str, meta_content: str, config: dict, unique_id: str, timestamp: str):
        """Save current run files directly to Databricks volume under `current_runs` directory."""
        try:
            if isinstance(config.get('databricks'), dict):
                databricks_config = config['databricks']
            else:
                databricks_config = config

            CLI = databricks_config.get('cli', "databricks")
            VOLUME_URI = databricks_config.get('volume_uri', "dbfs:/Volumes/workspace/default/volume")

            # Ensure current_runs directory exists
            current_dir = f"{VOLUME_URI}/{CURRENT_RUNS_FOLDER}"
            subprocess.run([CLI, "fs", "mkdir", current_dir], capture_output=True, text=True)

            remote_code_path = f"{current_dir}/latest.py"
            remote_meta_path = f"{current_dir}/latest.json"
            uid_safe = _make_filesystem_safe(unique_id)
            ts_safe = _make_filesystem_safe(timestamp)
            remote_code_uid_path = f"{current_dir}/run_{ts_safe}_{uid_safe}.py"
            remote_meta_uid_path = f"{current_dir}/run_{ts_safe}_{uid_safe}.json"

            # Upload code
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code_content.encode())
                local_tmp_code = pathlib.Path(f.name)
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code), remote_code_path,
                                     "--overwrite", "--output", "json"], capture_output=True, text=True)
            os.unlink(local_tmp_code)
            if result.returncode != 0:
                print(f"Failed to upload current run code: {result.stderr}")
                return

            # Upload code (UUID version)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code_content.encode())
                local_tmp_code_uid = pathlib.Path(f.name)
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code_uid), remote_code_uid_path,
                                     "--overwrite", "--output", "json"], capture_output=True, text=True)
            os.unlink(local_tmp_code_uid)
            if result.returncode != 0:
                print(f"Failed to upload current run code (uuid): {result.stderr}")
                return

            # Upload metadata
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
                f.write(meta_content.encode())
                local_tmp_meta = pathlib.Path(f.name)
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta), remote_meta_path,
                                     "--overwrite", "--output", "json"], capture_output=True, text=True)
            os.unlink(local_tmp_meta)
            if result.returncode != 0:
                print(f"Failed to upload current run metadata: {result.stderr}")
                return

            # Upload metadata (UUID version)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
                f.write(meta_content.encode())
                local_tmp_meta_uid = pathlib.Path(f.name)
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta_uid), remote_meta_uid_path,
                                     "--overwrite", "--output", "json"], capture_output=True, text=True)
            os.unlink(local_tmp_meta_uid)
            if result.returncode != 0:
                print(f"Failed to upload current run metadata (uuid): {result.stderr}")
                return

            # print(f"Current run uploaded to: {VOLUME_URI}/{CURRENT_RUNS_FOLDER}/latest.* and run_{uid_safe}.*")
        except Exception as e:
            print(f"Current run upload error: {e}")

    async def _save_current_run_snapshot(self, code_version, project_absolute_path: str, config: dict):
        """Persist the most recent run (code + minimal meta) to `current_runs`.

        Keeps it simple: always overwrite `latest.py` and `latest.json`.
        Mirrors Databricks behavior if configured.
        """
        try:
            if not code_version:
                return

            from .models import CodeVersion, CodeResult
            if isinstance(code_version, dict):
                try:
                    if isinstance(code_version.get("result"), dict):
                        code_version["result"] = CodeResult.model_validate(code_version["result"])  # type: ignore
                    code_version = CodeVersion.model_validate(code_version)  # type: ignore
                except Exception as e:
                    logging.warning(f"Cannot parse code_version payload for current run: {e}")
                    return

            meta = {
                "code_version_id": code_version.code_version_id,
                "name": code_version.name,
                "kpi": getattr(code_version.result, "kpi", None) if code_version.result else None,
                "stdout": getattr(code_version.result, "stdout", None) if code_version.result else None,
            }

            is_databricks = config and config.get('databricks')
            unique_id = getattr(code_version, 'code_version_id', None) or str(uuid.uuid4())
            uid_safe = _make_filesystem_safe(unique_id)
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            ts_safe = _make_filesystem_safe(timestamp)
            if is_databricks:
                await self._save_current_run_to_databricks_volume(
                    code_version.code,
                    json.dumps(meta, indent=4),
                    config,
                    unique_id,
                    timestamp
                )
            else:
                current_runs_base = Path(project_absolute_path) / CURRENT_RUNS_FOLDER
                current_runs_base.mkdir(parents=True, exist_ok=True)

                code_path = current_runs_base / "latest.py"
                meta_path = current_runs_base / "latest.json"
                code_uid_path = current_runs_base / f"run_{ts_safe}_{uid_safe}.py"
                meta_uid_path = current_runs_base / f"run_{ts_safe}_{uid_safe}.json"

                code_path.write_text(code_version.code, encoding="utf-8")
                meta_path.write_text(json.dumps(meta, indent=4))
                code_uid_path.write_text(code_version.code, encoding="utf-8")
                meta_uid_path.write_text(json.dumps(meta, indent=4))
        except Exception as e:
            logging.warning(f"Failed saving current run: {e}")


def _make_filesystem_safe(name):
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", '_', name)


# Local execution logic moved to executors/local_executor.py


# Databricks execution logic moved to executors/databricks_executor.py




# GCloud execution logic moved to executors/gcloud_executor.py


def get_system_info(python_path: str) -> SystemInfo:
    return SystemInfo(
        python_libraries=_get_python_libraries(python_path),
        python_version=_get_python_version(python_path),
        os=sys.platform
    )


def _get_python_libraries(python_path: str) -> list[str]:
    try:
        # Use importlib.metadata to get installed packages (works in all Python 3.8+ environments)
        python_code = """
import importlib.metadata
for dist in importlib.metadata.distributions():
    print(f"{dist.metadata['Name']}=={dist.version}")
"""
        installed_libraries = subprocess.check_output(
            [python_path, "-c", python_code],
            universal_newlines=True
        ).strip()
        return [lib.strip() for lib in installed_libraries.split("\n") if lib.strip()]
    except subprocess.CalledProcessError:
        # If that fails, return empty list
        return []


def _get_python_version(python_path: str) -> str:
    return subprocess.check_output(
        [python_path, "--version"],
        universal_newlines=True
    ).strip()


workflow_runner = _WorkflowRunner()
    
