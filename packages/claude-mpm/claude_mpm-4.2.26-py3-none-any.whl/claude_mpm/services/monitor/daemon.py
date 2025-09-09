"""
Unified Monitor Daemon for Claude MPM
=====================================

WHY: This is the main daemon process that provides a single, stable way to
launch all monitoring functionality. It combines HTTP dashboard serving,
Socket.IO event handling, real AST analysis, and Claude Code hook ingestion.

DESIGN DECISIONS:
- Single process replaces multiple competing server implementations
- Daemon-ready with proper lifecycle management
- Real AST analysis using CodeTreeAnalyzer
- Single port (8765) for all functionality
- Built on proven aiohttp + socketio foundation
"""

import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from ...core.logging_config import get_logger
from ..hook_installer_service import HookInstallerService
from .management.health import HealthMonitor
from .management.lifecycle import DaemonLifecycle
from .server import UnifiedMonitorServer


class UnifiedMonitorDaemon:
    """Unified daemon process for all Claude MPM monitoring functionality.

    WHY: Provides a single, stable entry point for launching monitoring services.
    Replaces the multiple competing server implementations with one cohesive daemon.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
        daemon_mode: bool = False,
        pid_file: Optional[str] = None,
        log_file: Optional[str] = None,
    ):
        """Initialize the unified monitor daemon.

        Args:
            host: Host to bind to
            port: Port to bind to
            daemon_mode: Whether to run as background daemon
            pid_file: Path to PID file for daemon mode
            log_file: Path to log file for daemon mode
        """
        self.host = host
        self.port = port
        self.daemon_mode = daemon_mode
        self.logger = get_logger(__name__)

        # Daemon management with port for verification
        self.lifecycle = DaemonLifecycle(
            pid_file=pid_file or self._get_default_pid_file(),
            log_file=log_file,
            port=port,
        )

        # Core server
        self.server = UnifiedMonitorServer(host=host, port=port)

        # Health monitoring
        self.health_monitor = HealthMonitor(port=port)

        # Hook installer service
        self.hook_installer = HookInstallerService()

        # State
        self.running = False
        self.shutdown_event = threading.Event()

    def _get_default_pid_file(self) -> str:
        """Get default PID file path."""
        project_root = Path.cwd()
        claude_mpm_dir = project_root / ".claude-mpm"
        claude_mpm_dir.mkdir(exist_ok=True)
        return str(claude_mpm_dir / "monitor-daemon.pid")

    def start(self, force_restart: bool = False) -> bool:
        """Start the unified monitor daemon.

        Args:
            force_restart: If True, restart existing service if it's ours

        Returns:
            True if started successfully, False otherwise
        """
        try:
            if self.daemon_mode:
                return self._start_daemon(force_restart=force_restart)
            return self._start_foreground(force_restart=force_restart)
        except Exception as e:
            self.logger.error(f"Failed to start unified monitor daemon: {e}")
            return False

    def _cleanup_port_conflicts(self) -> bool:
        """Try to clean up any processes using our port.
        
        Returns:
            True if cleanup was successful, False otherwise
        """
        try:
            # Find process using the port
            import subprocess
            result = subprocess.run(
                ["lsof", "-ti", f":{self.port}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid_str in pids:
                    try:
                        pid = int(pid_str.strip())
                        self.logger.info(f"Found process {pid} using port {self.port}")
                        
                        # Check if it's a claude-mpm process
                        process_info = subprocess.run(
                            ["ps", "-p", str(pid), "-o", "comm="],
                            capture_output=True,
                            text=True
                        )
                        
                        if "python" in process_info.stdout.lower() or "claude" in process_info.stdout.lower():
                            self.logger.info(f"Killing process {pid} (appears to be Python/Claude related)")
                            os.kill(pid, signal.SIGTERM)
                            time.sleep(1)
                            
                            # Check if still alive
                            try:
                                os.kill(pid, 0)
                                # Still alive, force kill
                                self.logger.warning(f"Process {pid} didn't terminate, force killing")
                                os.kill(pid, signal.SIGKILL)
                                time.sleep(1)
                            except ProcessLookupError:
                                pass
                        else:
                            self.logger.warning(f"Process {pid} is not a Claude MPM process: {process_info.stdout}")
                            return False
                    except (ValueError, ProcessLookupError) as e:
                        self.logger.debug(f"Error handling PID {pid_str}: {e}")
                        continue
                
                return True
                
        except FileNotFoundError:
            # lsof not available, try alternative method
            self.logger.debug("lsof not available, using alternative cleanup")
            
            # Check if there's an orphaned service we can identify
            is_ours, pid = self.lifecycle.is_our_service(self.host)
            if is_ours and pid:
                try:
                    self.logger.info(f"Killing orphaned Claude MPM service (PID: {pid})")
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)
                    
                    # Check if still alive
                    try:
                        os.kill(pid, 0)
                        os.kill(pid, signal.SIGKILL)
                        time.sleep(1)
                    except ProcessLookupError:
                        pass
                    
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to kill process: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error during port cleanup: {e}")
            
        return False

    def _start_daemon(self, force_restart: bool = False) -> bool:
        """Start as background daemon process.

        Args:
            force_restart: If True, restart existing service if it's ours
        """
        self.logger.info("Starting unified monitor daemon in background mode")

        # Check if already running
        if self.lifecycle.is_running():
            existing_pid = self.lifecycle.get_pid()

            if force_restart:
                # Check if it's our service
                self.logger.debug(
                    f"Checking if existing daemon (PID: {existing_pid}) is our service..."
                )
                is_ours, detected_pid = self.lifecycle.is_our_service(self.host)

                if is_ours:
                    self.logger.info(
                        f"Force restarting our existing claude-mpm monitor daemon (PID: {detected_pid or existing_pid})"
                    )
                    # Stop the existing daemon
                    if self.lifecycle.stop_daemon():
                        # Wait a moment for port to be released
                        time.sleep(2)
                    else:
                        self.logger.error("Failed to stop existing daemon for restart")
                        return False
                else:
                    self.logger.warning(
                        f"Port {self.port} is in use by another service (PID: {existing_pid}). Cannot force restart."
                    )
                    self.logger.info(
                        "To restart the claude-mpm monitor, first stop the other service or use a different port."
                    )
                    return False
            else:
                self.logger.warning(f"Daemon already running with PID {existing_pid}")
                return False

        # Check for orphaned processes (service running but no PID file)
        elif force_restart:
            self.logger.debug(
                "No PID file found, checking for orphaned claude-mpm service..."
            )
            is_ours, pid = self.lifecycle.is_our_service(self.host)
            if is_ours and pid:
                self.logger.info(
                    f"Found orphaned claude-mpm monitor service (PID: {pid}), force restarting"
                )
                # Try to kill the orphaned process
                try:
                    os.kill(pid, signal.SIGTERM)
                    # Wait for it to exit
                    for _ in range(10):
                        try:
                            os.kill(pid, 0)  # Check if still exists
                            time.sleep(0.5)
                        except ProcessLookupError:
                            break
                    else:
                        # Force kill if still running
                        os.kill(pid, signal.SIGKILL)
                        time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Failed to kill orphaned process: {e}")
                    return False

        # Check port availability and clean up if needed
        port_available, error_msg = self.lifecycle.verify_port_available(self.host)
        if not port_available:
            self.logger.warning(f"Port {self.port} is not available: {error_msg}")
            
            # Try to identify and kill any process using the port
            self.logger.info("Attempting to clean up processes on port...")
            cleaned = self._cleanup_port_conflicts()
            
            if cleaned:
                # Wait a moment for port to be released
                time.sleep(2)
                # Check again
                port_available, error_msg = self.lifecycle.verify_port_available(self.host)
                
            if not port_available:
                self.logger.error(f"Port {self.port} is still not available after cleanup: {error_msg}")
                print(f"Error: {error_msg}", file=sys.stderr)
                print(f"Try 'claude-mpm monitor stop' or use --force flag", file=sys.stderr)
                return False

        # Wait for any pre-warming threads to complete before forking
        self._wait_for_prewarm_completion()

        # Daemonize the process
        success = self.lifecycle.daemonize()
        if not success:
            return False

        # Start the server in daemon mode
        # This will run in the child process
        try:
            result = self._run_server()
            if not result:
                # Report failure before exiting
                self.lifecycle._report_startup_error("Failed to start server")
            return result
        except Exception as e:
            # Report any exceptions during startup
            self.lifecycle._report_startup_error(f"Server startup exception: {e}")
            raise

    def _start_foreground(self, force_restart: bool = False) -> bool:
        """Start in foreground mode.

        Args:
            force_restart: If True, restart existing service if it's ours
        """
        self.logger.info(f"Starting unified monitor daemon on {self.host}:{self.port}")

        # Check if already running (check PID file even in foreground mode)
        if self.lifecycle.is_running():
            existing_pid = self.lifecycle.get_pid()

            if force_restart:
                # Check if it's our service
                self.logger.debug(
                    f"Checking if existing daemon (PID: {existing_pid}) is our service..."
                )
                is_ours, detected_pid = self.lifecycle.is_our_service(self.host)

                if is_ours:
                    self.logger.info(
                        f"Force restarting our existing claude-mpm monitor daemon (PID: {detected_pid or existing_pid})"
                    )
                    # Stop the existing daemon
                    if self.lifecycle.stop_daemon():
                        # Wait a moment for port to be released
                        time.sleep(2)
                    else:
                        self.logger.error("Failed to stop existing daemon for restart")
                        return False
                else:
                    self.logger.warning(
                        f"Port {self.port} is in use by another service (PID: {existing_pid}). Cannot force restart."
                    )
                    self.logger.info(
                        "To restart the claude-mpm monitor, first stop the other service or use a different port."
                    )
                    return False
            else:
                self.logger.warning(
                    f"Monitor daemon already running with PID {existing_pid}"
                )
                return False

        # Check for orphaned processes (service running but no PID file)
        elif force_restart:
            self.logger.debug(
                "No PID file found, checking for orphaned claude-mpm service..."
            )
            is_ours, pid = self.lifecycle.is_our_service(self.host)
            if is_ours and pid:
                self.logger.info(
                    f"Found orphaned claude-mpm monitor service (PID: {pid}), force restarting"
                )
                # Try to kill the orphaned process
                try:
                    os.kill(pid, signal.SIGTERM)
                    # Wait for it to exit
                    for _ in range(10):
                        try:
                            os.kill(pid, 0)  # Check if still exists
                            time.sleep(0.5)
                        except ProcessLookupError:
                            break
                    else:
                        # Force kill if still running
                        os.kill(pid, signal.SIGKILL)
                        time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Failed to kill orphaned process: {e}")
                    return False

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

        # Write PID file for foreground mode too (so other processes can detect it)
        self.lifecycle.write_pid_file()

        # Start the server
        return self._run_server()

    def _run_server(self) -> bool:
        """Run the main server loop."""
        try:
            # Ensure components exist before starting
            if not self.health_monitor:
                error_msg = "Health monitor not initialized"
                self.logger.error(error_msg)
                if self.daemon_mode:
                    self.lifecycle._report_startup_error(error_msg)
                return False

            if not self.server:
                error_msg = "Server not initialized"
                self.logger.error(error_msg)
                if self.daemon_mode:
                    self.lifecycle._report_startup_error(error_msg)
                return False

            # Check and install hooks if needed
            try:
                if not self.hook_installer.is_hooks_configured():
                    self.logger.info("Claude Code hooks not configured, installing...")
                    if self.hook_installer.install_hooks():
                        self.logger.info("Claude Code hooks installed successfully")
                    else:
                        # Don't fail startup if hook installation fails
                        # The monitor can still function without hooks
                        self.logger.warning(
                            "Failed to install Claude Code hooks. Monitor will run without hook integration."
                        )
                else:
                    self.logger.info("Claude Code hooks are already configured")
            except Exception as e:
                # Don't fail startup if hook checking fails
                self.logger.warning(
                    f"Error checking/installing hooks: {e}. Monitor will run without hook integration."
                )

            # Start health monitoring
            self.health_monitor.start()

            # Start the unified server
            success = self.server.start()
            if not success:
                error_msg = "Failed to start unified monitor server"
                self.logger.error(error_msg)
                if self.daemon_mode:
                    self.lifecycle._report_startup_error(error_msg)
                return False

            self.running = True
            self.logger.info("Unified monitor daemon started successfully")

            # Report successful startup to parent (for daemon mode)
            if self.daemon_mode:
                self.lifecycle._report_startup_success()

            # Keep running until shutdown
            if self.daemon_mode:
                # In daemon mode, run until shutdown signal
                while self.running and not self.shutdown_event.is_set():
                    time.sleep(1)
            else:
                # In foreground mode, run until interrupted
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.logger.info("Received keyboard interrupt, shutting down...")

            return True

        except Exception as e:
            self.logger.error(f"Error running unified monitor daemon: {e}")
            return False
        finally:
            self._cleanup()

    def stop(self) -> bool:
        """Stop the unified monitor daemon.

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            self.logger.info("Stopping unified monitor daemon")

            # If running in daemon mode and we're not the daemon process itself,
            # use lifecycle to stop the daemon properly
            if self.daemon_mode and self.lifecycle.is_running():
                pid = self.lifecycle.get_pid()
                if pid and pid != os.getpid():
                    # We're not the daemon process, so stop it via signal
                    # Don't log here - lifecycle.stop_daemon will log
                    success = self.lifecycle.stop_daemon()
                    if success:
                        # Clean up our local state
                        self.running = False
                        self.shutdown_event.set()
                        self.server = None
                        self.health_monitor = None
                    return success

            # Otherwise, stop normally (we are the daemon or running in foreground)
            # Signal shutdown
            self.running = False
            self.shutdown_event.set()

            # Stop server with proper cleanup
            if self.server:
                self.logger.debug("Initiating server shutdown...")
                self.server.stop()
                # Give asyncio loops adequate time to cleanup properly
                # This is critical to prevent kqueue errors
                time.sleep(2.0)
                self.server = None

            # Stop health monitoring
            if self.health_monitor:
                self.logger.debug("Stopping health monitor...")
                self.health_monitor.stop()
                self.health_monitor = None

            # Clean up any asyncio resources
            self._cleanup_asyncio_resources()

            # Give a final moment for OS-level cleanup
            time.sleep(0.5)

            # Cleanup daemon files (always cleanup PID file)
            self.lifecycle.cleanup()

            self.logger.info("Unified monitor daemon stopped")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping unified monitor daemon: {e}")
            return False

    def restart(self) -> bool:
        """Restart the unified monitor daemon.

        Returns:
            True if restarted successfully, False otherwise
        """
        self.logger.info("Restarting unified monitor daemon")

        # Save daemon mode setting before stopping
        was_daemon_mode = self.daemon_mode

        # Stop first (this will properly kill daemon process if needed)
        if not self.stop():
            return False

        # Wait longer for port to be released properly
        # This is needed because the daemon process may take time to fully cleanup
        self.logger.info("Waiting for port to be fully released...")

        # Check if port is actually free, wait up to 10 seconds
        import socket

        for i in range(10):
            try:
                # Try to bind to the port to see if it's free
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_sock.bind((self.host, self.port))
                test_sock.close()
                self.logger.info(f"Port {self.port} is now free")
                break
            except OSError:
                if i < 9:
                    self.logger.debug(
                        f"Port {self.port} still in use, waiting... ({i+1}/10)"
                    )
                    time.sleep(1)
                else:
                    self.logger.error(
                        f"Port {self.port} is still in use after 10 seconds"
                    )
                    return False

        # Recreate the server and health monitor after stop() sets them to None
        self.logger.info(f"Recreating server components for {self.host}:{self.port}")
        self.server = UnifiedMonitorServer(host=self.host, port=self.port)
        self.health_monitor = HealthMonitor(port=self.port)

        # Reset the shutdown event for the new run
        self.shutdown_event.clear()

        # Restore daemon mode setting
        self.daemon_mode = was_daemon_mode

        # Start again
        return self.start()

    def status(self) -> dict:
        """Get daemon status information.

        Returns:
            Dictionary with status information
        """
        # Always check the PID file to see if a daemon is running
        # This ensures we detect daemons started by other processes
        is_running = self.lifecycle.is_running()
        pid = self.lifecycle.get_pid()

        # If no PID file exists but we're running in the current process
        if not is_running and self.running:
            is_running = True
            pid = os.getpid()

        status = {
            "running": is_running,
            "pid": pid if is_running else None,
            "host": self.host,
            "port": self.port,
            "daemon_mode": self.daemon_mode,
            "health": (
                self.health_monitor.get_status() if self.health_monitor else "unknown"
            ),
        }

        if self.server:
            status.update(self.server.get_status())

        return status

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _cleanup(self):
        """Cleanup resources."""
        try:
            # Stop server first with proper cleanup
            if self.server:
                self.logger.debug("Stopping server and cleaning up event loops...")
                self.server.stop()
                # Give the server more time to cleanup event loops properly
                # This is critical to prevent kqueue errors
                time.sleep(1.5)
                self.server = None

            # Then stop health monitor
            if self.health_monitor:
                self.logger.debug("Stopping health monitor...")
                self.health_monitor.stop()
                self.health_monitor = None

            # Ensure PID file is removed
            if not self.daemon_mode:
                # In foreground mode, make sure we cleanup the PID file
                self.lifecycle.cleanup()

            # Clean up any remaining asyncio resources in the main thread
            self._cleanup_asyncio_resources()

            # Clear any remaining references
            self.shutdown_event.clear()

            self.logger.debug("Cleanup completed successfully")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def _cleanup_asyncio_resources(self):
        """Clean up any asyncio resources in the current thread."""
        try:
            import asyncio

            # Try to get the current event loop
            try:
                loop = asyncio.get_event_loop()
                if loop and not loop.is_closed():
                    # Cancel any pending tasks
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()

                    # Stop and close the loop
                    if loop.is_running():
                        loop.stop()

                    # Clear the event loop from the thread
                    asyncio.set_event_loop(None)

                    # Close the loop
                    loop.close()

            except RuntimeError:
                # No event loop in current thread, that's fine
                pass

        except Exception as e:
            self.logger.debug(f"Error cleaning up asyncio resources: {e}")

    def _wait_for_prewarm_completion(self, timeout: float = 5.0):
        """Wait for MCP pre-warming threads to complete before forking.

        This prevents inherited threads and event loops in the forked process.
        """
        try:
            import threading
            import time

            start_time = time.time()

            # Get all non-daemon threads (pre-warm threads are daemon threads)
            # but we still want to give them a moment to complete
            active_threads = [
                t
                for t in threading.enumerate()
                if t.is_alive() and t != threading.current_thread()
            ]

            if active_threads:
                self.logger.debug(
                    f"Waiting for {len(active_threads)} threads to complete"
                )

                # Wait briefly for threads to complete
                wait_time = min(timeout, 2.0)  # Max 2 seconds for daemon threads
                time.sleep(wait_time)

                elapsed = time.time() - start_time
                self.logger.debug(f"Waited {elapsed:.2f}s for thread completion")

        except Exception as e:
            self.logger.debug(f"Error waiting for threads: {e}")
