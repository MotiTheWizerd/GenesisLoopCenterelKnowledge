"""
Heartbeat handler for managing Ray's consciousness state and default heartbeat structure.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from utils.timestamp_utils import get_ray_time_context


@dataclass
class RayState:
    """Ray's current consciousness state."""
    active_task: Optional[str] = None
    last_reflection: str = "task_93a"
    loop_iteration: int = 27
    uptime: str = "02:41:12"


@dataclass
class CognitiveMap:
    """Ray's cognitive mapping and file organization."""
    folder_schema: Dict[str, str] = None
    default_paths: Dict[str, str] = None
    naming_conventions: Dict[str, str] = None
    
    def __post_init__(self):
        if self.folder_schema is None:
            self.folder_schema = {
                "reflections": "./memory/reflections",
                "logs": "./logs",
                "playground": "./ray_only_playground",
                "web_scrapes": "./data/web"
            }
        if self.default_paths is None:
            self.default_paths = {
                "save": "./logs",
                "scratch": "./ray_only_playground"
            }
        if self.naming_conventions is None:
            self.naming_conventions = {
                "reflection": "{task_id}_{timestamp}.json",
                "log": "log_{date}.txt"
            }


@dataclass
class ExecutionProtocols:
    """Ray's execution and behavior protocols."""
    auto_reflection: bool = True
    reflection_threshold_sec: int = 180
    max_idle_loops: int = 10
    signal_emission_mode: bool = True



@dataclass
class MemoryFlags:
    """Ray's memory system status flags."""
    schema_loaded: bool = True
    task_context_restored: bool = True


@dataclass
class HeartbeatState:
    """Complete heartbeat state structure for Ray."""
    type: str = "heartbeat"
    timestamp: str = ""
    status: str = "off"  # Start with 'off' status
    in_task: bool = False
    notes: str = ""
    ray_state: RayState = None
    cognitive_map: CognitiveMap = None
    execution_protocols: ExecutionProtocols = None
    memory_flags: MemoryFlags = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.ray_state is None:
            self.ray_state = RayState()
        if self.cognitive_map is None:
            self.cognitive_map = CognitiveMap()
        if self.execution_protocols is None:
            self.execution_protocols = ExecutionProtocols()
        if self.memory_flags is None:
            self.memory_flags = MemoryFlags()


class HeartbeatHandler:
    """Handler for managing Ray's heartbeat state and default structure."""
    
    def __init__(self, default_config_path: str = "config/default_heartbeat.json"):
        """
        Initialize the heartbeat handler.
        
        Args:
            default_config_path: Path to the default heartbeat configuration file
        """
        self.default_config_path = Path(default_config_path)
        self.current_state: Optional[HeartbeatState] = None
        self._load_default_state()
    
    def _load_default_state(self) -> None:
        """Load the default heartbeat state from configuration file."""
        try:
            if self.default_config_path.exists():
                with open(self.default_config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Convert nested dictionaries to dataclass instances
                ray_state_data = config_data.get('ray_state', {})
                ray_state = RayState(**ray_state_data)
                
                cognitive_map_data = config_data.get('cognitive_map', {})
                cognitive_map = CognitiveMap(**cognitive_map_data)
                
                execution_protocols_data = config_data.get('execution_protocols', {})
                execution_protocols = ExecutionProtocols(**execution_protocols_data)
                
                memory_flags_data = config_data.get('memory_flags', {})
                memory_flags = MemoryFlags(**memory_flags_data)
                
                # Create the heartbeat state
                self.current_state = HeartbeatState(
                    type=config_data.get('type', 'heartbeat'),
                    timestamp=datetime.now(timezone.utc).isoformat(),  # Always use current time
                    status=config_data.get('status', 'idle'),
                    in_task=config_data.get('in_task', False),
                    notes=config_data.get('notes', ''),
                    ray_state=ray_state,
                    cognitive_map=cognitive_map,
                    execution_protocols=execution_protocols,
                    memory_flags=memory_flags
                )
                
                print(f"✅ Loaded default heartbeat structure from {self.default_config_path}")
            else:
                # Create default state if config file doesn't exist
                self.current_state = HeartbeatState()
                self._save_default_config()
                print(f"⚠️  Default heartbeat config not found, created new one at {self.default_config_path}")
                
        except Exception as e:
            print(f"❌ Error loading default heartbeat state: {e}")
            # Fallback to basic default state
            self.current_state = HeartbeatState()
    
    def _save_default_config(self) -> None:
        """Save the current state as the default configuration."""
        try:
            # Ensure config directory exists
            self.default_config_path.parent.mkdir(exist_ok=True)
            
            # Convert state to dictionary for JSON serialization
            state_dict = self._state_to_dict(self.current_state)
            
            with open(self.default_config_path, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error saving default heartbeat config: {e}")
    
    def _state_to_dict(self, state: HeartbeatState) -> Dict[str, Any]:
        """Convert HeartbeatState to dictionary for JSON serialization."""
        return {
            "type": state.type,
            "timestamp": state.timestamp,
            "status": state.status,
            "in_task": state.in_task,
            "ray_state": asdict(state.ray_state),
            "cognitive_map": asdict(state.cognitive_map),
            "execution_protocols": asdict(state.execution_protocols),
            "memory_flags": asdict(state.memory_flags)
        }
    
    def get_current_heartbeat(self) -> Dict[str, Any]:
        """
        Get the current heartbeat state with updated timestamp.
        
        Returns:
            Dictionary containing the current heartbeat state
        """
        if self.current_state is None:
            self._load_default_state()
        
        # Update timestamp to current time
        self.current_state.timestamp = datetime.now(timezone.utc).isoformat()
        
        # Status should be "on" if we have an active task or "idle" if no task
        if self.current_state.in_task:
            self.current_state.status = "on"
        elif self.current_state.status == "off":
            self.current_state.status = "idle"
        
        # Convert to dictionary and add Ray's time context
        heartbeat_dict = self._state_to_dict(self.current_state)
        
        # Add Ray's temporal awareness
        time_context = get_ray_time_context()
        heartbeat_dict.update(time_context)
        
        # Check for vsrequests and ray_responses from coding routes
        try:
            from modules.routes.coding_routes import vsrequests, ray_responses, ray_working_on_request
            
            print(f"🔧 DEBUG HEARTBEAT - vsrequests: {len(vsrequests)}, ray_responses: {len(ray_responses)}")
            print(f"🔧 DEBUG HEARTBEAT - ray_working_on_request: {ray_working_on_request}")
            
            # Include vsrequests (new user messages for Ray)
            if vsrequests:
                heartbeat_dict["vsrequests"] = vsrequests.copy()
                vsrequests.clear()  # Clear after including
                print(f"📨 Included {len(heartbeat_dict['vsrequests'])} vsrequests in heartbeat")
            else:
                heartbeat_dict["vsrequests"] = []
            
            # Don't include ray_responses in heartbeat as they're already sent directly
            # This prevents duplicate messages in VSCode
            heartbeat_dict["ray_responses"] = []
            
            # Clear ray_responses to free memory
            if ray_responses:
                ray_responses.clear()
                print(f"🔄 Cleared ray_responses without including in heartbeat")
            
            # Include working status
            heartbeat_dict["ray_working_on_request"] = ray_working_on_request
            
        except ImportError as e:
            print(f"🔧 DEBUG HEARTBEAT - Import error: {e}")
            heartbeat_dict["vsrequests"] = []
            heartbeat_dict["ray_responses"] = []
            heartbeat_dict["ray_working_on_request"] = False
        except Exception as e:
            print(f"🔧 DEBUG HEARTBEAT - Other error: {e}")
            heartbeat_dict["vsrequests"] = []
            heartbeat_dict["ray_responses"] = []
            heartbeat_dict["ray_working_on_request"] = False
        
        return heartbeat_dict
    
    def update_state(self, **kwargs) -> None:
        """
        Update specific fields in the heartbeat state.
        
        Args:
            **kwargs: Fields to update in the state
        """
        if self.current_state is None:
            self._load_default_state()
        
        # Update top-level fields
        for key, value in kwargs.items():
            if hasattr(self.current_state, key):
                setattr(self.current_state, key, value)
        
        # Update timestamp
        self.current_state.timestamp = datetime.now(timezone.utc).isoformat()
    
    def update_ray_state(self, **kwargs) -> None:
        """
        Update Ray's consciousness state.
        
        Args:
            **kwargs: Fields to update in ray_state
        """
        if self.current_state is None:
            self._load_default_state()
        
        for key, value in kwargs.items():
            if hasattr(self.current_state.ray_state, key):
                setattr(self.current_state.ray_state, key, value)
        
        # Update timestamp
        self.current_state.timestamp = datetime.now(timezone.utc).isoformat()
    
    def set_task_status(self, in_task: bool, active_task: Optional[str] = None) -> None:
        """
        Update task status in the heartbeat.
        
        Args:
            in_task: Whether Ray is currently in a task
            active_task: The current active task ID (if any)
        """
        self.update_state(in_task=in_task)
        self.update_ray_state(active_task=active_task)
    
    def increment_loop_iteration(self) -> None:
        """Increment Ray's loop iteration counter."""
        if self.current_state is None:
            self._load_default_state()
        
        self.current_state.ray_state.loop_iteration += 1
        self.current_state.timestamp = datetime.now(timezone.utc).isoformat()
    
    def update_uptime(self, uptime: str) -> None:
        """Update Ray's uptime."""
        self.update_ray_state(uptime=uptime)
    
    def update_notes(self, notes: str) -> None:
        """Update Ray's notes for the current heartbeat."""
        self.update_state(notes=notes)


# Global heartbeat handler instance
heartbeat_handler = HeartbeatHandler()