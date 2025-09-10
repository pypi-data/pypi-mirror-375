"""
Background Notification Daemon
Monitors saved searches and sends real-time terminal notifications
THE REVOLUTIONARY FEATURE: Job alerts while coding!
"""

import os
import sys
import time
import signal
import asyncio
import subprocess
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from .saved_searches import SavedSearchManager
from .display import console
from ..models.saved_search import JobMatch, NotificationFrequency

class JobNotificationDaemon:
    """Background daemon for terminal job notifications"""
    
    def __init__(self):
        self.manager = SavedSearchManager()
        self.is_running = False
        self.pid_file = Path.home() / ".jobtty" / "daemon.pid"
        self.log_file = Path.home() / ".jobtty" / "daemon.log"
        
        # Ensure config directory exists
        self.pid_file.parent.mkdir(exist_ok=True)
    
    def start(self, daemonize: bool = True):
        """Start the notification daemon"""
        
        if self.is_daemon_running():
            print("🟢 Notification daemon is already running")
            return
        
        if daemonize:
            self._daemonize()
        else:
            self._run_daemon()
    
    def stop(self):
        """Stop the notification daemon"""
        
        if not self.is_daemon_running():
            print("⚪ Notification daemon is not running")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            self.pid_file.unlink()
            print("🔴 Notification daemon stopped")
            
        except (ProcessLookupError, FileNotFoundError, ValueError):
            print("⚠️  Daemon process not found - cleaning up PID file")
            if self.pid_file.exists():
                self.pid_file.unlink()
    
    def status(self):
        """Check daemon status"""
        
        if self.is_daemon_running():
            print("🟢 Notification daemon is running")
            
            # Show recent activity
            if self.log_file.exists():
                print("\n📋 Recent activity:")
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
        else:
            print("🔴 Notification daemon is stopped")
            print("\n💡 Start with: jobtty daemon start")
    
    def is_daemon_running(self) -> bool:
        """Check if daemon is currently running"""
        
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
            
        except (ProcessLookupError, FileNotFoundError, ValueError):
            # Clean up stale PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def _daemonize(self):
        """Run as background daemon using multiprocessing (macOS compatible)"""
        
        # Use multiprocessing to avoid macOS fork() issues
        process = multiprocessing.Process(target=self._run_daemon_process)
        process.start()
        
        # Save PID 
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        print(f"🚀 Notification daemon started (PID: {process.pid})")
        
        # Don't wait for process - it should run independently
    
    def _run_daemon_process(self):
        """Daemon process entry point"""
        # Redirect stdout/stderr to log file
        with open(self.log_file, 'a') as log:
            sys.stdout = log
            sys.stderr = log
            self._run_daemon()
    
    def _run_daemon(self):
        """Main daemon event loop"""
        
        self.is_running = True
        self._log("🚀 Jobtty notification daemon started")
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        try:
            while self.is_running:
                self._check_for_new_jobs()
                time.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            self._log(f"❌ Daemon error: {e}")
        finally:
            self._log("🔴 Notification daemon stopped")
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        self.is_running = False
        self._log("📤 Received shutdown signal")
    
    def _check_for_new_jobs(self):
        """Check all saved searches for new job matches"""
        
        try:
            new_matches = self.manager.check_all_searches()
            
            if new_matches:
                self._log(f"🔍 Found {len(new_matches)} new job matches")
                
                for match in new_matches:
                    if self._should_send_notification(match):
                        self._send_terminal_notification(match)
                        self.manager.mark_notification_sent(match)
            
        except Exception as e:
            self._log(f"❌ Error checking searches: {e}")
    
    def _should_send_notification(self, match: JobMatch) -> bool:
        """Check if we should send notification for this match"""
        
        # Get the saved search
        searches = self.manager.load_all_searches()
        search = next((s for s in searches if s.id == match.search_id), None)
        
        if not search or not search.notifications_enabled:
            return False
        
        # Check notification frequency rules
        return search.should_notify_now()
    
    def _send_terminal_notification(self, match: JobMatch):
        """Send terminal notification to all active terminals"""
        
        notification_data = match.to_notification_format()
        
        # Format the terminal notification
        notification_text = self._format_notification(notification_data)
        
        # Send to all active terminal sessions
        self._broadcast_to_terminals(notification_text)
        
        self._log(f"📢 Sent notification: {notification_data['title']} at {notification_data['company']}")
    
    def _format_notification(self, job_data: Dict) -> str:
        """Format job notification for terminal display"""
        
        company_logo = job_data.get("company_logo", "")
        
        notification = f"""
╭─────────────────────────────────────────────────────────────╮
│  🎯 NEW JOB MATCH! ({job_data['match_score']}% match)      │
╰─────────────────────────────────────────────────────────────╯

{company_logo}

🏢 {job_data['company']}
💼 {job_data['title']}
📍 {job_data['location']} {'🏠 Remote' if job_data['remote'] else ''}
💰 {job_data['salary']}
⏰ {job_data['posted_ago']}

🚀 Quick actions:
   jobtty show {job_data['job_id']}     # View details
   jobtty apply {job_data['job_id']}    # Apply now!
   jobtty dismiss {job_data['job_id']}  # Not interested

╭─────────────────────────────────────────────────────────────╮
│  Press any key to dismiss this notification                │
╰─────────────────────────────────────────────────────────────╯
"""
        return notification
    
    def _broadcast_to_terminals(self, notification: str):
        """Send notification to all active terminal sessions"""
        
        try:
            # Get all terminal sessions for current user
            terminals = self._get_active_terminals()
            
            for terminal in terminals:
                self._send_to_terminal(terminal, notification)
                
        except Exception as e:
            self._log(f"❌ Error broadcasting notification: {e}")
    
    def _get_active_terminals(self) -> List[str]:
        """Get list of active terminal sessions"""
        
        try:
            # Use who/w command to find active terminals
            result = subprocess.run(['who'], capture_output=True, text=True)
            
            terminals = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        terminals.append(parts[1])  # TTY device
            
            return terminals
            
        except Exception as e:
            self._log(f"❌ Error getting terminals: {e}")
            return []
    
    def _send_to_terminal(self, terminal: str, message: str):
        """Send message to specific terminal"""
        
        try:
            # Write notification to terminal device
            terminal_path = f"/dev/{terminal}"
            
            if os.path.exists(terminal_path) and os.access(terminal_path, os.W_OK):
                with open(terminal_path, 'w') as f:
                    f.write(f"\n{message}\n")
                    f.flush()
            
        except Exception as e:
            self._log(f"❌ Error writing to {terminal}: {e}")
    
    def _log(self, message: str):
        """Write log message with timestamp"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if self.is_running:
            # Daemon mode - write to file
            try:
                with open(self.log_file, 'a') as f:
                    f.write(f"{log_entry}\n")
                    f.flush()
            except:
                pass
        else:
            # Interactive mode - print to console
            print(log_entry)

# CLI convenience functions
def start_daemon(background: bool = True):
    """Start the notification daemon"""
    daemon = JobNotificationDaemon()
    daemon.start(daemonize=background)

def stop_daemon():
    """Stop the notification daemon"""
    daemon = JobNotificationDaemon()
    daemon.stop()

def daemon_status():
    """Check daemon status"""
    daemon = JobNotificationDaemon()
    daemon.status()

def check_notifications_once():
    """Manually check for notifications (for testing)"""
    daemon = JobNotificationDaemon()
    daemon._check_for_new_jobs()