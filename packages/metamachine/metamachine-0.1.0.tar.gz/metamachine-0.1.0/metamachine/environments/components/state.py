"""
Copyright 2025 Chen Yu <chenyu@u.northwestern.edu>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import numpy as np
from omegaconf import OmegaConf
from ...utils.math_utils import quat_rotate_inverse, quat_apply, AverageFilter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable

@dataclass
class RawState:
    """Raw state values received from environment."""
    # Position and orientation
    pos_world: np.ndarray = field(default_factory=lambda: np.zeros(3))
    quat: np.ndarray = field(default_factory=lambda: np.zeros(4))
    quats: List[np.ndarray] = field(default_factory=list)
    
    # Velocities
    vel_body: np.ndarray = field(default_factory=lambda: np.zeros(3))
    vel_world: np.ndarray = field(default_factory=lambda: np.zeros(3))
    ang_vel_body: np.ndarray = field(default_factory=lambda: np.zeros(3))
    ang_vel_world: np.ndarray = field(default_factory=lambda: np.zeros(3))
    
    # Joint state - size will be set after initialization
    dof_pos: np.ndarray = field(default_factory=lambda: np.zeros(1))  # Will be resized
    dof_vel: np.ndarray = field(default_factory=lambda: np.zeros(1))  # Will be resized
    
    # Sensor data
    gyros: Optional[np.ndarray] = None
    accs: Optional[np.ndarray] = None
    
    # Contact information
    contact_floor_balls: List[int] = field(default_factory=list)
    contact_floor_geoms: List[int] = field(default_factory=list)
    contact_floor_socks: List[int] = field(default_factory=list)

    def __init__(self, num_dof: int = 1):
        """Initialize RawState with specified number of degrees of freedom."""
        # Position and orientation
        self.pos_world = np.zeros(3)
        self.quat = np.zeros(4)
        self.quats = []
        
        # Velocities
        self.vel_body = np.zeros(3)
        self.vel_world = np.zeros(3)
        self.ang_vel_body = np.zeros(3)
        self.ang_vel_world = np.zeros(3)
        
        # Joint state with correct size
        self.dof_pos = np.zeros(num_dof)
        self.dof_vel = np.zeros(num_dof)
        
        # Sensor data
        self.gyros = None
        self.accs = None
        
        # Contact information
        self.contact_floor_balls = []
        self.contact_floor_geoms = []
        self.contact_floor_socks = []
        
        # Store initial shapes for validation
        self.__post_init__()

    def __post_init__(self):
        """Store initial shapes for validation."""
        self._initial_shapes = {}
        for key, value in self.__dict__.items():
            if isinstance(value, np.ndarray):
                self._initial_shapes[key] = value.shape
            elif isinstance(value, list):
                self._initial_shapes[key] = (len(value),)
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update raw state with new data."""
        for key, value in data.items():
            if hasattr(self, key):
                # Skip validation for None values and list-type fields
                if value is None or key in ['contact_floor_balls', 'contact_floor_geoms', 'contact_floor_socks', 'quats']:
                    setattr(self, key, value)
                    continue
                
                # For numpy arrays, validate shape
                if isinstance(value, np.ndarray):
                    expected_shape = self._initial_shapes.get(key)
                    if expected_shape is not None and value.shape != expected_shape:
                        raise ValueError(f"Shape mismatch for {key}: expected {expected_shape}, got {value.shape}")
                
                setattr(self, key, value)

@dataclass
class AccurateState:
    """Accurate state values for reward computation (simulation only)."""
    quat: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(4))
    vel_body: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(3))
    vel_world: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(3))
    pos_world: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(3))
    ang_vel_body: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(3))

    def update(self, data: Dict[str, Any]) -> None:
        """Update accurate state with new data."""
        for key, value in data.items():
            # Only update if the key exists and starts with 'accurate_'
            if key.startswith('accurate_'):
                attr_name = key.replace('accurate_', '')
                if hasattr(self, attr_name):
                    setattr(self, attr_name, value)
    
    def is_available(self) -> bool:
        """Check if accurate state data is available."""
        return any(getattr(self, attr) is not None for attr in 
                  ['quat', 'vel_body', 'vel_world', 'pos_world', 'ang_vel_body'])
    
    def reset(self):
        """Reset all accurate state values to None."""
        self.quat = None
        self.vel_body = None
        self.vel_world = None
        self.pos_world = None
        self.ang_vel_body = None

@dataclass
class DerivedState:
    """Derived state values computed from raw state."""
    height: np.ndarray = field(default_factory=lambda: np.zeros(1))
    projected_gravity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    projected_gravities: List[np.ndarray] = field(default_factory=list)
    heading: np.ndarray = field(default_factory=lambda: np.zeros(1))
    speed: np.ndarray = field(default_factory=lambda: np.zeros(1))

    def __post_init__(self):
        """Store initial shapes for validation."""
        self._initial_shapes = {}
        for key, value in self.__dict__.items():
            if isinstance(value, np.ndarray):
                self._initial_shapes[key] = value.shape
            elif isinstance(value, list):
                self._initial_shapes[key] = (len(value),)

    def update(self, data: Dict[str, Any]) -> None:
        """Update derived state with new data."""
        for key, value in data.items():
            if hasattr(self, key):
                # Skip validation for None values and list fields
                if value is None or key in ['projected_gravities']:
                    setattr(self, key, value)
                    continue
                
                # For numpy arrays, validate shape
                if isinstance(value, np.ndarray):
                    expected_shape = self._initial_shapes.get(key)
                    if expected_shape is not None and value.shape != expected_shape:
                        raise ValueError(f"Shape mismatch for {key}: expected {expected_shape}, got {value.shape}")
                
                setattr(self, key, value)

class ObservationComponent:
    """A component that can be included in the observation vector."""
    def __init__(self, name: str, data_fn: Callable, transform_fn: Optional[Callable] = None):
        """Initialize observation component.
        
        Args:
            name: Name of the component
            data_fn: Function that returns the component data
            transform_fn: Optional function to transform the data before including in observation
        """
        self.name = name
        self.data_fn = data_fn
        self.transform_fn = transform_fn if transform_fn else lambda x: x
        
    def get_data(self, state) -> np.ndarray:
        """Get the component data and apply any transformations."""
        data = self.data_fn(state)
        return self.transform_fn(data)

class ActionHistoryBuffer:
    """Handles action history for environments that need multiple timesteps of past actions."""
    
    def __init__(self, num_actions: int, history_steps: int = 3):
        """Initialize action history buffer.
        
        Args:
            num_actions: Number of actions per timestep
            history_steps: Number of timesteps to store in history
        """
        self.num_actions = num_actions
        self.history_steps = history_steps
        self.action_history = np.zeros((history_steps, num_actions))
        
    def reset(self, initial_action=None):
        """Reset buffer with initial action (or zeros)."""
        if initial_action is None:
            initial_action = np.zeros(self.num_actions)
        self.action_history = np.tile(initial_action, (self.history_steps, 1))
        
    def update(self, new_action):
        """Update history with new action, shifting older actions."""
        # Shift history: [t-2, t-1, t-0] -> [t-1, t-0, new]
        self.action_history[:-1] = self.action_history[1:]
        self.action_history[-1] = new_action
        
    def get_action(self, steps_back: int = 0):
        """Get action from history.
        
        Args:
            steps_back: How many steps back (0 = most recent, 1 = last_action, 2 = last_last_action)
            
        Returns:
            numpy.ndarray: Action at specified timestep
        """
        if steps_back >= self.history_steps:
            raise ValueError(f"Cannot access {steps_back} steps back, only {self.history_steps} steps stored")
        return self.action_history[-(steps_back + 1)]
    
    @property
    def last_action(self):
        """Get most recent action (equivalent to get_action(0))."""
        return self.get_action(0)
    
    @property
    def last_last_action(self):
        """Get previous action (equivalent to get_action(1))."""
        return self.get_action(1)
    
    @property
    def last_last_last_action(self):
        """Get action from 2 steps ago (equivalent to get_action(2))."""
        return self.get_action(2)
    
    def get_history_vector(self, num_steps: int = None):
        """Get flattened history vector for observations.
        
        Args:
            num_steps: Number of recent steps to include (default: all)
            
        Returns:
            numpy.ndarray: Flattened action history
        """
        if num_steps is None:
            num_steps = self.history_steps
        
        if num_steps > self.history_steps:
            raise ValueError(f"Cannot get {num_steps} steps, only {self.history_steps} stored")
        
        # Return most recent num_steps actions, flattened
        return self.action_history[-num_steps:].flatten()

class RewardHistoryBuffer:
    """Handles reward history for environments that need multiple timesteps of past rewards."""
    
    def __init__(self, history_steps: int = 3):
        """Initialize reward history buffer.
        
        Args:
            history_steps: Number of timesteps to store in history
        """
        self.history_steps = history_steps
        self.reward_history = np.zeros(history_steps)
        
    def reset(self, initial_reward=None):
        """Reset buffer with initial reward (or zeros)."""
        if initial_reward is None:
            initial_reward = 0.0
        self.reward_history = np.full(self.history_steps, initial_reward)
        
    def update(self, new_reward):
        """Update history with new reward, shifting older rewards."""
        # Shift history: [t-2, t-1, t-0] -> [t-1, t-0, new]
        self.reward_history[:-1] = self.reward_history[1:]
        self.reward_history[-1] = new_reward
        
    def get_reward(self, steps_back: int = 0):
        """Get reward from history.
        
        Args:
            steps_back: How many steps back (0 = most recent, 1 = last_reward, 2 = last_last_reward)
            
        Returns:
            float: Reward at specified timestep
        """
        if steps_back >= self.history_steps:
            raise ValueError(f"Cannot access {steps_back} steps back, only {self.history_steps} steps stored")
        return self.reward_history[-(steps_back + 1)]
    
    @property
    def last_reward(self):
        """Get most recent reward (equivalent to get_reward(0))."""
        return self.get_reward(0)
    
    @property
    def last_last_reward(self):
        """Get previous reward (equivalent to get_reward(1))."""
        return self.get_reward(1)
    
    @property
    def last_last_last_reward(self):
        """Get reward from 2 steps ago (equivalent to get_reward(2))."""
        return self.get_reward(2)
    
    def get_history_vector(self, num_steps: int = None):
        """Get reward history vector for observations.
        
        Args:
            num_steps: Number of recent steps to include (default: all)
            
        Returns:
            numpy.ndarray: Reward history
        """
        if num_steps is None:
            num_steps = self.history_steps
        
        if num_steps > self.history_steps:
            raise ValueError(f"Cannot get {num_steps} steps, only {self.history_steps} stored")
        
        # Return most recent num_steps rewards
        return self.reward_history[-num_steps:]

class ObservationBuffer:
    """Handles observation history for environments that use multiple timesteps."""
    
    def __init__(self, num_obs: int, include_history_steps: int):
        """Initialize observation buffer.
        
        Args:
            num_obs: Number of observations per timestep
            include_history_steps: Number of timesteps to include in history
        """
        self.num_obs = num_obs
        self.include_history_steps = include_history_steps
        self.num_obs_total = num_obs * include_history_steps
        self.obs_buf = np.zeros(self.num_obs_total)
        
    def reset(self, new_obs):
        """Reset buffer with new observation."""
        self.obs_buf = np.tile(new_obs, self.include_history_steps)
        
    def insert(self, new_obs):
        """Insert new observation and shift history."""
        self.obs_buf[:-self.num_obs] = self.obs_buf[self.num_obs:]
        self.obs_buf[-self.num_obs:] = new_obs
        
    def get_obs_vec(self, obs_ids=None):
        """Get observation vector for specified timesteps.
        
        Args:
            obs_ids: Indices of timesteps to include (0 is latest)
            
        Returns:
            numpy.ndarray: Concatenated observations
        """
        if obs_ids is None:
            obs_ids = np.arange(self.include_history_steps)
            
        obs = []
        for obs_id in reversed(sorted(obs_ids)):
            slice_idx = self.include_history_steps - obs_id - 1
            obs.append(
                self.obs_buf[slice_idx * self.num_obs:(slice_idx + 1) * self.num_obs]
            )
        return np.concatenate(obs)

class State:
    """Manages environment state and generates configurable observations."""
    
    # Define available observation components
    OBSERVATION_COMPONENTS = {
        'projected_gravity': lambda s: s.derived.projected_gravity,
        'projected_gravities': lambda s: s.derived.projected_gravities,
        'ang_vel_body': lambda s: s.raw.ang_vel_body,
        'dof_pos': lambda s: s.raw.dof_pos,
        'dof_vel': lambda s: s.raw.dof_vel,
        'gyros': lambda s: s.raw.gyros,
        'last_action': lambda s: s.action_history.last_action,
        'last_last_action': lambda s: s.action_history.last_last_action,
        'last_last_last_action': lambda s: s.action_history.last_last_last_action,
        'action_history': lambda s: s.action_history.get_history_vector(),
        'last_reward': lambda s: s.reward_history.last_reward,
        'last_last_reward': lambda s: s.reward_history.last_last_reward,
        'last_last_last_reward': lambda s: s.reward_history.last_last_last_reward,
        'reward_history': lambda s: s.reward_history.get_history_vector(),
        'commands': lambda s: s.commands,
        'vel_body': lambda s: s.raw.vel_body,
        'height': lambda s: s.derived.height,
        'heading': lambda s: s.derived.heading,
        'speed': lambda s: s.derived.speed,
        # Simulation-specific components (will return None if not available)
        'mj_data': lambda s: getattr(s, 'mj_data', None),
        'mj_model': lambda s: getattr(s, 'mj_model', None),
        'contact_geoms': lambda s: getattr(s, 'contact_geoms', []),
        'contact_floor_geoms': lambda s: getattr(s, 'contact_floor_geoms', []),
        'contact_floor_socks': lambda s: getattr(s, 'contact_floor_socks', []),
        'contact_floor_balls': lambda s: getattr(s, 'contact_floor_balls', []),
        'num_jointfloor_contact': lambda s: getattr(s, 'num_jointfloor_contact', 0),
        'com_vel_world': lambda s: getattr(s, 'com_vel_world', np.zeros(3)),
    }
    
    # Define common transformations
    TRANSFORMATIONS = {
        'cos': np.cos,
        'sin': np.sin,
        'normalize': lambda x: x / np.linalg.norm(x) if np.linalg.norm(x) > 0 else x,
        'clip': lambda x: np.clip(x, -1, 1),
        'slice': lambda x, start=None, end=None: x[slice(start, end)],
        'expand_dims': lambda x, axis=0: np.expand_dims(x, axis=axis),
        'flatten': lambda x: x.flatten(),
        'reshape': lambda x, shape: x.reshape(shape),
    }
    
    def __init__(self, cfg: OmegaConf):
        """Initialize state manager with configurable observation components.
        
        Args:
            cfg: Configuration object that includes:
                - observation_components: List of components to include
                - observation_transforms: Dict of component transforms
        """
        self.cfg = cfg

        self.num_act = cfg.control.num_actions
        self.num_envs = cfg.environment.num_envs
        self.include_history_steps = cfg.observation.include_history_steps
        # self.num_obs = cfg.observation.num_obs
        self.clip_observations = cfg.observation.clip_observations
        self.gravity_vec = np.array(cfg.observation.gravity_vec)
        self.forward_vec = np.array(cfg.observation.forward_vec)
        self.projected_forward_vec = None
        self.dt = cfg.control.dt
        
        # State containers
        self.raw = RawState(num_dof=self.num_act)
        self.derived = DerivedState()
        self.accurate = AccurateState()  # Only used in simulation environments
        
        # Action history
        action_history_steps = getattr(cfg.observation, 'action_history_steps', 3)  # Default to 3 steps
        self.action_history = ActionHistoryBuffer(self.num_act, action_history_steps)
        
        # Reward history
        reward_history_steps = getattr(cfg.observation, 'reward_history_steps', 3)  # Default to 3 steps
        self.reward_history = RewardHistoryBuffer(reward_history_steps)
        
        # Reward history
        reward_history_steps = getattr(cfg.observation, 'reward_history_steps', 3)  # Default to 3 steps
        self.reward_history = RewardHistoryBuffer(reward_history_steps)
        
        # Commands
        
        
        # Tracking and visualization
        self.observable_data = {}
        self.step_counter = 0
        self.render_lookat_filter = AverageFilter(10)
        
        # Initialize reward-related state
        self.reset_reward_state()
        
        # Set up observation components
        self.observation_components = []
        self._setup_observation_components()
        
        # Calculate total observation size
        obs = self._construct_observation()
        self.num_obs = len(obs)

        # Initialize observation buffer
        self.obs_buf = ObservationBuffer(
            self.num_obs * self.num_envs,
            self.include_history_steps
        )
        
    def __getattr__(self, name):
        """Automatically forward attribute access to raw, derived, accurate state objects, or observable_data.
        
        This allows accessing state.vel_body instead of state.raw.vel_body.
        Priority: raw state -> derived state -> accurate state -> observable_data -> AttributeError
        """
        # Try raw state first
        if hasattr(self.raw, name):
            return getattr(self.raw, name)
        
        # Then try derived state
        if hasattr(self.derived, name):
            return getattr(self.derived, name)
        
        # Then try accurate state (with accurate_ prefix handling)
        if hasattr(self.accurate, name):
            return getattr(self.accurate, name)
        
        # Handle accurate_ prefixed attributes
        if name.startswith('accurate_'):
            attr_name = name.replace('accurate_', '')
            if hasattr(self.accurate, attr_name):
                return getattr(self.accurate, attr_name)
        
        # Try action_history attributes
        if hasattr(self, 'action_history') and hasattr(self.action_history, name):
            return getattr(self.action_history, name)
        
        # Try reward_history attributes
        if hasattr(self, 'reward_history') and hasattr(self.reward_history, name):
            return getattr(self.reward_history, name)
        
        # Try observable_data (for mj_data, mj_model, etc.)
        if hasattr(self, 'observable_data') and name in self.observable_data:
            return self.observable_data[name]
        
        # For simulation data that might not be available, return None instead of raising error
        simulation_keys = ['mj_data', 'mj_model', 'contact_geoms', 'contact_floor_geoms', 
                          'contact_floor_socks', 'contact_floor_balls', 'num_jointfloor_contact', 
                          'com_vel_world', 'adjusted_forward_vec']
        if name in simulation_keys:
            return None
        
        # If not found in any state container, raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """Handle attribute setting with forwarding to state objects when appropriate."""
        # Always allow setting of State's own attributes during initialization
        if (name in ['cfg', 'num_act', 'num_envs', 'include_history_steps', 'clip_observations', 
                     'gravity_vec', 'forward_vec', 'projected_forward_vec', 'dt', 'raw', 'derived', 'accurate',
                     'commands', 'observable_data', 'step_counter', 'action_history', 'reward_history',
                     'render_lookat_filter', 'observation_components', 'num_obs', 'obs_buf',
                     'ang_vel_history', 'vel_history', 'pos_history', 'last_dof_vel', 
                     'contact_counter', 'fly_counter', 'jump_timer', 'vel_filter'] or
            not hasattr(self, 'raw') or not hasattr(self, 'derived') or not hasattr(self, 'accurate')):
            super().__setattr__(name, value)
            return
        
        # Handle accurate_ prefixed attributes
        if name.startswith('accurate_'):
            attr_name = name.replace('accurate_', '')
            if hasattr(self.accurate, attr_name):
                setattr(self.accurate, attr_name, value)
                return
        
        # If the attribute exists in raw state, set it there
        if hasattr(self.raw, name):
            setattr(self.raw, name, value)
        # If the attribute exists in derived state, set it there
        elif hasattr(self.derived, name):
            setattr(self.derived, name, value)
        # If the attribute exists in accurate state, set it there
        elif hasattr(self.accurate, name):
            setattr(self.accurate, name, value)
        # Otherwise, set it on State itself
        else:
            super().__setattr__(name, value)
        
    def _setup_observation_components(self):
        """Set up observation components based on config."""
        # Get observation components from config
        if not hasattr(self.cfg.observation, 'components'):
            # Default observation components if not specified
            components = [
                {'name': 'projected_gravity'},
                {'name': 'ang_vel_body'},
                {'name': 'dof_pos', 'transform': 'cos'},
                {'name': 'dof_vel'},
                {'name': 'last_action'}
            ]
        else:
            components = self.cfg.observation.components

        # Process each component
        for comp_spec in components:
            if isinstance(comp_spec, (str, list, tuple)):
                # Handle legacy format (name, transform)
                if isinstance(comp_spec, str):
                    comp_name, transform_name = comp_spec, None
                else:
                    comp_name, transform_name = comp_spec
                comp_spec = {'name': comp_name, 'transform': transform_name}
            
            # Get component name and data function
            comp_name = comp_spec['name']
            if comp_name not in self.OBSERVATION_COMPONENTS:
                raise ValueError(f"Unknown observation component: {comp_name}")
            data_fn = self.OBSERVATION_COMPONENTS[comp_name]
            
            # Build transform function chain
            transform_fn = lambda x: x  # Identity transform by default
            if 'transform' in comp_spec:
                if isinstance(comp_spec['transform'], str):
                    # Single transform
                    transform_name = comp_spec['transform']
                    if transform_name not in self.TRANSFORMATIONS:
                        raise ValueError(f"Unknown transform: {transform_name}")
                    transform_fn = self.TRANSFORMATIONS[transform_name]
                elif isinstance(comp_spec['transform'], list):
                    # Chain of transforms
                    transforms = []
                    for t in comp_spec['transform']:
                        if isinstance(t, str):
                            if t not in self.TRANSFORMATIONS:
                                raise ValueError(f"Unknown transform: {t}")
                            transforms.append(self.TRANSFORMATIONS[t])
                        elif isinstance(t, dict):
                            # Transform with parameters
                            t_name = t['name']
                            if t_name not in self.TRANSFORMATIONS:
                                raise ValueError(f"Unknown transform: {t_name}")
                            t_params = {k: v for k, v in t.items() if k != 'name'}
                            transforms.append(lambda x, fn=self.TRANSFORMATIONS[t_name], params=t_params: fn(x, **params))
                    
                    # Create transform chain
                    def chain_transform(x, transforms=transforms):
                        for t in transforms:
                            x = t(x)
                        return x
                    transform_fn = chain_transform
            
            # Create and add component
            self.observation_components.append(
                ObservationComponent(
                    comp_name,
                    data_fn,
                    transform_fn
                )
            )
    
    def reset(self):
        """Reset state variables."""
        # # Reset raw state
        # self.raw = RawState(num_dof=self.num_act)
        
        # # Reset derived state
        # self.derived = DerivedState()
        
        # # Reset accurate state
        # self.accurate = AccurateState()
        
        # Reset action history
        action_history_steps = getattr(self.cfg.observation, 'action_history_steps', 3)
        self.action_history = ActionHistoryBuffer(self.num_act, action_history_steps)
        
        # Reset reward history
        reward_history_steps = getattr(self.cfg.observation, 'reward_history_steps', 3)
        self.reward_history = RewardHistoryBuffer(reward_history_steps)
        
        # Reset commands
        # self.commands = np.zeros(3)
        
        # Reset tracking
        # self.observable_data = {}
        self.step_counter = 0
        self.render_lookat_filter = AverageFilter(10)
        
        # Reset reward-related state
        self.reset_reward_state()
        
    def reset_reward_state(self):
        """Reset state variables used for reward calculation."""
        self.ang_vel_history = []
        self.vel_history = []
        self.pos_history = []
        self.last_dof_vel = np.zeros(self.num_act)
        self.contact_counter = {}
        self.fly_counter = 0
        self.jump_timer = 0
        self.vel_filter = AverageFilter(int(0.5/self.dt))
    
    def set_command_manager(self, command_manager):
        """Set the command manager reference for named command access.
        
        Args:
            command_manager: The CommandManager instance from the environment
        """
        self.command_manager = command_manager
    
    def get_command_by_name(self, name: str):
        """Get a command value by name.
        
        Args:
            name: Command dimension name
            
        Returns:
            Current value of the named command
            
        Raises:
            AttributeError: If no command manager is set
            ValueError: If command name is not found
        """
        if not hasattr(self, 'command_manager') or self.command_manager is None:
            raise AttributeError("No command manager set. Call set_command_manager() first.")
        return self.command_manager.get_command_by_name(name)
    
    def set_command_by_name(self, name: str, value: float):
        """Set a command value by name.
        
        Args:
            name: Command dimension name
            value: New command value
            
        Raises:
            AttributeError: If no command manager is set
            ValueError: If command name is not found
        """
        if not hasattr(self, 'command_manager') or self.command_manager is None:
            raise AttributeError("No command manager set. Call set_command_manager() first.")
        self.command_manager.set_command_by_name(name, value)
    
    def get_commands_dict(self):
        """Get all commands as a dictionary mapping names to values.
        
        Returns:
            Dictionary with command names as keys and current values as values
            
        Raises:
            AttributeError: If no command manager is set
        """
        if not hasattr(self, 'command_manager') or self.command_manager is None:
            raise AttributeError("No command manager set. Call set_command_manager() first.")
        return self.command_manager.get_commands_dict()
    
    @property
    def command_names(self):
        """Get list of available command names.
        
        Returns:
            List of command dimension names
            
        Raises:
            AttributeError: If no command manager is set
        """
        if not hasattr(self, 'command_manager') or self.command_manager is None:
            raise AttributeError("No command manager set. Call set_command_manager() first.")
        return self.command_manager.command_names
    
    @property
    def commands(self):
        """Get current command values.
        
        Returns:
            numpy.ndarray: Current command values
            
        Raises:
            AttributeError: If no command manager is set
        """
        if not hasattr(self, 'command_manager') or self.command_manager is None:
            num_commands = len(getattr(self.cfg.task.commands, 'dimensions', {}))  # Default to 0 if not specified
            return np.zeros(num_commands)
        return np.array(list(self.command_manager.get_commands_dict().values()))
        
    def update(self, data: Dict[str, Any]) -> None:
        """Update state with new data.
        
        Args:
            data: Dictionary of new state data
        """
        # Update raw state
        self.raw.update(data)
        
        # Update accurate state (simulation only)
        self.accurate.update(data)
        
        # Update action history if last_action is provided
        if 'last_action' in data:
            self.action_history.update(data['last_action'])
            
        # Update reward history if last_reward is provided
        if 'last_reward' in data:
            self.reward_history.update(data['last_reward'])
        
        # Update reward history if reward is provided
        if 'reward' in data:
            self.reward_history.update(data['reward'])
        
        # Update position history for speed calculation
        self.pos_history.append(self.raw.pos_world.copy())
        # Keep only a limited history (e.g., last 10 steps for speed calculation)
        max_history_length = 1000
        if len(self.pos_history) > max_history_length:
            self.pos_history.pop(0)
        
        # Compute derived state
        self._compute_derived_state()
        
        # Update observable data
        self.observable_data = data.copy()
        self.observable_data.update({
            "projected_gravity": self.derived.projected_gravity,
            "heading": self.derived.heading,
            "dof_pos": self.raw.dof_pos,
            "dof_vel": self.raw.dof_vel
        })
        
        # Update step counter
        self.step_counter += 1
        
    def _compute_derived_state(self) -> None:
        """Compute derived state from raw state."""
        # Height
        self.derived.height = np.expand_dims(self.raw.pos_world[2], axis=0)
        
        # Projected gravity
        self.derived.projected_gravity = quat_rotate_inverse(
            self.raw.quat, 
            self.gravity_vec
        )
        
        # Projected gravities for each quaternion
        self.derived.projected_gravities = [
            quat_rotate_inverse(quat, self.gravity_vec) 
            for quat in self.raw.quats
        ]
        
        # Heading
        forward = quat_apply(self.raw.quat, self.forward_vec)
        self.derived.heading = np.expand_dims(
            np.arctan2(forward[1], forward[0]), 
            axis=0
        )
        
        # Speed (using position history)
        if len(self.pos_history) >= 2:
            # Calculate speed using current position and N steps back
            # Use configuration or default to 1 step back
            speed_calculation_steps = getattr(self.cfg.observation, 'speed_calculation_steps', 100)
            steps_back = min(speed_calculation_steps, len(self.pos_history) - 1)
            
            current_pos = self.pos_history[-1]
            past_pos = self.pos_history[-(steps_back + 1)]
            
            # Calculate displacement and speed
            displacement = current_pos - past_pos
            distance = np.linalg.norm(displacement)
            # Speed = distance / (time_steps * dt)
            time_elapsed = steps_back * self.dt
            speed = distance / time_elapsed if time_elapsed > 0 else 0.0
            
            self.derived.speed = np.expand_dims(speed, axis=0)
        else:
            # Not enough history yet, set speed to 0
            self.derived.speed = np.zeros(1)
        
    def get_observation(self, insert=True, reset=False):
        """Get observation vector based on current state.
        
        Args:
            insert: Whether to insert observation into buffer
            reset: Whether to reset observation buffer
            
        Returns:
            numpy.ndarray: Observation vector
        """
        obs = self._construct_observation()
        obs = np.clip(obs, -self.clip_observations, self.clip_observations)
        
        if reset:
            self.obs_buf.reset(obs)
        elif insert:
            # print(f"!!Inserting observation of size {obs.shape}")
            self.obs_buf.insert(obs)
            
        return self.obs_buf.get_obs_vec()
    
    def _construct_observation(self):
        """Construct observation vector based on components.
        
        Returns:
            numpy.ndarray: Raw observation vector
        """
        obs_parts = []
        for component in self.observation_components:
            data = component.get_data(self)
            flattened_data = data.flatten()
            
            # Check for NaN values in this component
            if np.any(np.isnan(flattened_data)):
                nan_indices = np.where(np.isnan(flattened_data))[0]
                print(f"WARNING: NaN detected in observation component '{component.name}'")
                print(f"  Original data shape: {data.shape}")
                print(f"  Flattened data shape: {flattened_data.shape}")
                print(f"  NaN indices: {nan_indices}")
                print(f"  Data sample: {flattened_data[:min(10, len(flattened_data))]}")
                
                # Optionally replace NaN with zeros (uncomment if desired)
                # flattened_data = np.nan_to_num(flattened_data, nan=0.0)
                # print(f"  Replaced NaN values with zeros")
            
            obs_parts.append(flattened_data)
            
        # Ensure 1D array for concatenation
        observation = np.concatenate(obs_parts)
        
        # Final check for any remaining NaN values in the complete observation
        if np.any(np.isnan(observation)):
            nan_count = np.sum(np.isnan(observation))
            total_count = len(observation)
            print(f"ERROR: Final observation contains {nan_count}/{total_count} NaN values!")
            print(f"Step counter: {self.step_counter}")
            
            # Optionally replace all NaN with zeros in final observation
            # observation = np.nan_to_num(observation, nan=0.0)
            # print("Replaced all NaN values in final observation with zeros")
        
        return observation
    
    def get_custom_commands(self, command_type):
        """Get custom commands based on command type."""
        info = {}
        if command_type == "onehot_dirichlet":
            if self.step_counter < self.cfg.trainer.total_steps/2:
                commands = np.zeros(3)
                commands[np.random.randint(3)] = 1
            else:
                commands = np.random.dirichlet(np.ones(3))
        elif command_type == "onehot":
            commands = np.zeros(3)
            commands[np.random.randint(3)] = 1
        return commands, info

    def get_available_attributes(self):
        """Get a list of all available state attributes for debugging/inspection."""
        state_attrs = []
        
        # Raw state attributes
        raw_attrs = [attr for attr in dir(self.raw) if not attr.startswith('_')]
        state_attrs.extend([f"raw.{attr}" for attr in raw_attrs])
        
        # Derived state attributes  
        derived_attrs = [attr for attr in dir(self.derived) if not attr.startswith('_')]
        state_attrs.extend([f"derived.{attr}" for attr in derived_attrs])
        
        # Accurate state attributes
        accurate_attrs = [attr for attr in dir(self.accurate) if not attr.startswith('_') and 
                         attr not in ['update', 'is_available', 'reset']]
        state_attrs.extend([f"accurate.{attr}" for attr in accurate_attrs])
        
        # Direct State attributes
        direct_attrs = [attr for attr in dir(self) if not attr.startswith('_') and 
                       attr not in ['raw', 'derived', 'accurate', 'get_available_attributes']]
        state_attrs.extend([f"direct.{attr}" for attr in direct_attrs])
        
        return sorted(state_attrs)

    def update_action_history(self, action: np.ndarray) -> None:
        """Manually update action history (useful when actions are applied outside of state updates).
        
        Args:
            action: New action to add to history
        """
        self.action_history.update(action)

    def get_mujoco_data(self):
        """Get MuJoCo data object if available.
        
        Returns:
            MuJoCo data object or None if not available
        """
        return getattr(self, 'mj_data', None)
    
    def get_mujoco_model(self):
        """Get MuJoCo model object if available.
        
        Returns:
            MuJoCo model object or None if not available
        """
        return getattr(self, 'mj_model', None)
    
    def get_simulation_data(self) -> Dict[str, Any]:
        """Get all simulation-specific data.
        
        Returns:
            Dictionary containing simulation data like mj_data, mj_model, etc.
        """
        sim_data = {}
        sim_keys = ['mj_data', 'mj_model', 'adjusted_forward_vec', 'contact_geoms', 
                   'num_jointfloor_contact', 'contact_floor_geoms', 'contact_floor_socks', 
                   'contact_floor_balls', 'com_vel_world']
        
        for key in sim_keys:
            if hasattr(self, key):
                sim_data[key] = getattr(self, key)
        
        return sim_data
    
    def get_sensor_data(self) -> Dict[str, Any]:
        """Get all sensor data.
        
        Returns:
            Dictionary containing sensor readings like gyros, accs, etc.
        """
        sensor_data = {}
        sensor_keys = ['gyros', 'accs', 'quats']
        
        for key in sensor_keys:
            if hasattr(self, key):
                sensor_data[key] = getattr(self, key)
        
        return sensor_data
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get all available state data including observable_data.
        
        Returns:
            Dictionary containing all available data
        """
        all_data = {}
        
        # Add raw state data
        for attr in ['pos_world', 'quat', 'quats', 'vel_body', 'vel_world', 
                    'ang_vel_body', 'ang_vel_world', 'dof_pos', 'dof_vel', 'gyros', 'accs']:
            if hasattr(self.raw, attr):
                all_data[f'raw_{attr}'] = getattr(self.raw, attr)
        
        # Add derived state data
        for attr in ['height', 'projected_gravity', 'projected_gravities', 'heading', 'speed']:
            if hasattr(self.derived, attr):
                all_data[f'derived_{attr}'] = getattr(self.derived, attr)
        
        # Add accurate state data
        for attr in ['quat', 'vel_body', 'vel_world', 'pos_world', 'ang_vel_body']:
            if hasattr(self.accurate, attr) and getattr(self.accurate, attr) is not None:
                all_data[f'accurate_{attr}'] = getattr(self.accurate, attr)
        
        # Add observable data
        if hasattr(self, 'observable_data'):
            all_data.update(self.observable_data)
        
        return all_data
    
    def has_simulation_data(self) -> bool:
        """Check if simulation data (MuJoCo) is available.
        
        Returns:
            True if simulation data is available
        """
        mj_data = getattr(self, 'mj_data', None)
        return mj_data is not None
    
    def get_data(self, key: str, default=None):
        """Get data with fallback to default.
        
        Args:
            key: Data key to retrieve
            default: Default value if key not found
            
        Returns:
            Data value or default
        """
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    @classmethod 
    def register_observation_component(cls, name: str, data_fn: Callable):
        """Register a new observation component.
        
        Args:
            name: Component name for configuration
            data_fn: Function that takes a state object and returns numpy array data
            
        Example:
            # Register a custom observation component
            def custom_energy(state):
                return np.array([np.sum(np.square(state.dof_vel))])
            
            State.register_observation_component('energy', custom_energy)
            
            # Use in configuration:
            observation:
              components:
                - name: energy
                  transform: normalize
        """
        if not callable(data_fn):
            raise ValueError(f"data_fn must be callable")
        
        cls.OBSERVATION_COMPONENTS[name] = data_fn
        
    @classmethod
    def register_transformation(cls, name: str, transform_fn: Callable):
        """Register a new transformation function.
        
        Args:
            name: Transform name for configuration
            transform_fn: Function that takes and returns numpy array
            
        Example:
            # Register a custom transformation
            def square_transform(x):
                return np.square(x)
            
            State.register_transformation('square', square_transform)
            
            # Use in configuration:
            observation:
              components:
                - name: dof_pos
                  transform: square
        """
        if not callable(transform_fn):
            raise ValueError(f"transform_fn must be callable")
        
        cls.TRANSFORMATIONS[name] = transform_fn
        
    @classmethod
    def list_observation_components(cls) -> List[str]:
        """Get list of all available observation component names.
        
        Returns:
            List of component names that can be used in configurations
        """
        return list(cls.OBSERVATION_COMPONENTS.keys())
        
    @classmethod 
    def list_transformations(cls) -> List[str]:
        """Get list of all available transformation names.
        
        Returns:
            List of transformation names that can be used in configurations
        """
        return list(cls.TRANSFORMATIONS.keys())

# Convenience functions for registration
def register_observation_component(name: str, data_fn: Callable):
    """Register a new observation component.
    
    Args:
        name: Component name for configuration
        data_fn: Function that takes a state object and returns numpy array data
        
    Example:
        # Register a custom observation component
        def custom_energy(state):
            return np.array([np.sum(np.square(state.dof_vel))])
        
        register_observation_component('energy', custom_energy)
    """
    State.register_observation_component(name, data_fn)


def register_transformation(name: str, transform_fn: Callable):
    """Register a new transformation function.
    
    Args:
        name: Transform name for configuration  
        transform_fn: Function that takes and returns numpy array
        
    Example:
        # Register a custom transformation
        def square_transform(x):
            return np.square(x)
        
        register_transformation('square', square_transform)
    """
    State.register_transformation(name, transform_fn)


def list_observation_components() -> List[str]:
    """Get list of all available observation component names."""
    return State.list_observation_components()


def list_transformations() -> List[str]:
    """Get list of all available transformation names."""
    return State.list_transformations()