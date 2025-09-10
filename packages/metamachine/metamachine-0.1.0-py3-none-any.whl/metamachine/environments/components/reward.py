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
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
from ...utils.math_utils import quat_rotate_inverse, normalize_angle
from ...utils.curves import isaac_reward, plateau


class RewardComponent(ABC):
    """Base class for reward components."""
    
    def __init__(self, name: str, weight: float = 1.0, **kwargs):
        self.name = name
        self.weight = weight
        self.params = kwargs
        
    @abstractmethod
    def calculate(self, state, calculator) -> float:
        """Calculate the reward component value."""
        pass
        
    def reset(self):
        """Reset component state if needed."""
        pass


class LinearVelocityTrackingComponent(RewardComponent):
    """Tracks linear velocity in forward direction."""
    
    def calculate(self, state, calculator) -> float:
        target_vel = self.params.get('target_velocity', 1.0)
        if isinstance(target_vel, str) and target_vel.startswith("cmd:"):
            target_vel = state.get_command_by_name(target_vel[4:])
            # print(f"Using command value for target velocity: {target_vel}")
        tracking_sigma = self.params.get('tracking_sigma', 0.15)
        
        projected_forward_vel = np.dot(state.accurate_vel_body, 
                                     calculator.projected_forward_vec)
        lin_vel_error = np.sum(np.square(target_vel - projected_forward_vel))
        return np.exp(-lin_vel_error / tracking_sigma)


class AngularVelocityTrackingComponent(RewardComponent):
    """Tracks angular velocity around gravity axis."""
    
    def calculate(self, state, calculator) -> float:
        target_ang_vel = self.params.get('target_angular_velocity', 0.0)
        if isinstance(target_ang_vel, str) and target_ang_vel.startswith("cmd:"):
            target_ang_vel = state.get_command_by_name(target_ang_vel[4:])
            # print(f"Using command value for target angular velocity: {target_ang_vel}")

        tracking_sigma = self.params.get('tracking_sigma', 0.15)
        
        accurate_projected_gravity = quat_rotate_inverse(state.accurate_quat, 
                                                       calculator.gravity_vec)
        projected_z_ang = np.dot(state.accurate_ang_vel_body, 
                               accurate_projected_gravity)
        ang_vel_error = np.sum(np.square(target_ang_vel - projected_z_ang))
        return np.exp(-ang_vel_error / tracking_sigma)


# class LinearVelocityTrackingCMDComponent(RewardComponent):
#     """Tracks linear velocity in forward direction."""
    
#     def calculate(self, state, calculator) -> float:
#         target_vel = state.get_command_by_name('forward_speed')
#         tracking_sigma = self.params.get('tracking_sigma', 0.15)
        
#         projected_forward_vel = np.dot(state.accurate_vel_body, 
#                                      calculator.projected_forward_vec)
#         lin_vel_error = np.sum(np.square(target_vel - projected_forward_vel))
#         return np.exp(-lin_vel_error / tracking_sigma)


# class AngularVelocityTrackingCMDComponent(RewardComponent):
#     """Tracks angular velocity around gravity axis."""
    
#     def calculate(self, state, calculator) -> float:
#         target_ang_vel = state.get_command_by_name('turn_rate')
#         tracking_sigma = self.params.get('tracking_sigma', 0.15)
        
#         accurate_projected_gravity = quat_rotate_inverse(state.accurate_quat, 
#                                                        calculator.gravity_vec)
#         projected_z_ang = np.dot(state.accurate_ang_vel_body, 
#                                accurate_projected_gravity)
#         ang_vel_error = np.sum(np.square(target_ang_vel - projected_z_ang))
#         return np.exp(-ang_vel_error / tracking_sigma)



class ContactFlightTimeComponent(RewardComponent):
    """Rewards flight time between contacts."""
    
    def __init__(self, name: str, weight: float = 1.0, **kwargs):
        super().__init__(name, weight, **kwargs)
        self.contact_counter = {}
        
    def calculate(self, state, calculator) -> float:
        allowed_contacts = self.params.get('allowed_num_contacts', 1)
        
        # Update contact counters
        for key in self.contact_counter:
            self.contact_counter[key] += 1
        for c in state.contact_floor_socks:
            self.contact_counter[c] = 0
            
        if (len(state.contact_floor_socks) >= allowed_contacts + 1 
            or len(state.contact_floor_balls)):
            self.contact_counter = dict.fromkeys(self.contact_counter, 0)
            
        feet_air_time = np.array([value for value in self.contact_counter.values()]) * calculator.dt
        return np.sum(feet_air_time)
        
    def reset(self):
        self.contact_counter = {}


class DOFVelocityPenaltyComponent(RewardComponent):
    """Penalizes excessive DOF velocities."""
    
    def calculate(self, state, calculator) -> float:
        velocity_limit = self.params.get('velocity_limit', 10.0)
        return -np.sum((np.abs(state.dof_vel) - velocity_limit).clip(0, 1e5))


class DOFAccelerationPenaltyComponent(RewardComponent):
    """Penalizes DOF accelerations."""
    
    def __init__(self, name: str, weight: float = 1.0, **kwargs):
        super().__init__(name, weight, **kwargs)
        self.last_dof_vel = None
        
    def calculate(self, state, calculator) -> float:
        if self.last_dof_vel is not None:
            dof_acc_penalty = np.sum(np.square((self.last_dof_vel - state.dof_vel) / calculator.dt))
        else:
            dof_acc_penalty = 0
        self.last_dof_vel = state.dof_vel.copy()
        return -dof_acc_penalty
        
    def reset(self):
        self.last_dof_vel = None


class ContactPenaltyComponent(RewardComponent):
    """Penalizes unwanted contacts."""
    
    def calculate(self, state, calculator) -> float:
        return -len(state.contact_floor_balls)


class JumpRewardComponent(RewardComponent):
    """Rewards upward velocity."""
    
    def calculate(self, state, calculator) -> float:
        accurate_projected_gravity = quat_rotate_inverse(state.accurate_quat, 
                                                       calculator.gravity_vec)
        upward_vel = np.dot(state.accurate_vel_body, -accurate_projected_gravity)
        max_vel = self.params.get('max_velocity', 1.0)
        return np.clip(upward_vel, 0, max_vel)


class OrientationRewardComponent(RewardComponent):
    """Rewards maintaining upright orientation."""
    
    def calculate(self, state, calculator) -> float:
        accurate_projected_gravity = quat_rotate_inverse(state.accurate_quat, 
                                                       calculator.gravity_vec)
        return np.dot(calculator.projected_upward_vec, -accurate_projected_gravity)


class HeightTrackingComponent(RewardComponent):
    """Tracks desired height."""
    
    def calculate(self, state, calculator) -> float:
        desired_height = self.params.get('desired_height')
        if desired_height is None or desired_height == -1:
            desired_height = state.sim_init_pos[2]
        tracking_sigma = self.params.get('tracking_sigma', 0.005)
        
        height = state.accurate_pos_world[2]
        return isaac_reward(desired_height, height, tracking_sigma)


class TorsoContactPenaltyComponent(RewardComponent):
    """Penalizes torso touching the ground."""
    
    def calculate(self, state, calculator) -> float:
        torso_geoms = self.params.get('torso_geoms', ["left0", "right0"])
        torso_touch_floor = np.any([state.mj_model.geom(geom).name in torso_geoms 
                                  for geom in state.contact_floor_balls])
        return -float(torso_touch_floor)


class DOFPositionTrackingComponent(RewardComponent):
    """Tracks desired DOF positions."""
    
    def calculate(self, state, calculator) -> float:
        tracking_sigma = self.params.get('tracking_sigma', 10.0)
        target_positions = self.params.get('target_positions', state.default_dof_pos)
        
        return isaac_reward(
            normalize_angle(np.array(target_positions)),
            normalize_angle(state.accurate_dof_pos), 
            tracking_sigma
        )


class PlateauAngularVelocityComponent(RewardComponent):
    """Plateau-style reward for angular velocity using jing vector."""
    
    def calculate(self, state, calculator) -> float:
        from ..utils.visual_utils import get_jing_vector
        
        ang_vel = state.accurate_ang_vel_body
        jing_vec = get_jing_vector(state.dof_pos[0], calculator.theta)
        ang_vel_forward = np.dot(jing_vec, ang_vel)
        
        target_velocity = self.params.get('target_velocity', 6.0)
        max_step_limit = self.params.get('max_step_velocity_limit', 2e5)
        velocity_cap = self.params.get('velocity_cap', 12.0)
        
        # Apply velocity cap if still in early training
        if target_velocity > velocity_cap and calculator.step_counter < max_step_limit:
            target_velocity = velocity_cap
            
        return plateau(ang_vel_forward, target_velocity)


class PlateauSpinComponent(RewardComponent):
    """Plateau-style reward for spinning around gravity axis."""
    
    def calculate(self, state, calculator) -> float:
        accurate_projected_gravity = quat_rotate_inverse(state.accurate_quat, 
                                                       calculator.gravity_vec)
        spin_value = np.dot(-accurate_projected_gravity, state.accurate_ang_vel_body)
        
        target_spin = self.params.get('target_spin', 0.0)
        
        if target_spin > 0:
            return plateau(spin_value, target_spin)
        elif target_spin < 0:
            return plateau(-spin_value, -target_spin)
        else:
            return -np.square(spin_value)


class PlateauHeightComponent(RewardComponent):
    """Plateau-style reward for height tracking."""
    
    def calculate(self, state, calculator) -> float:
        height = state.accurate_pos_world[2]
        target_height = self.params.get('target_height', 0.0)
        return plateau(height, target_height)


class RecoveryRewardComponent(RewardComponent):
    """Combined DOF position tracking and orientation reward."""
    
    def calculate(self, state, calculator) -> float:
        tracking_sigma = self.params.get('tracking_sigma', 10.0)
        
        # DOF position tracking
        dof_reward = isaac_reward(
            normalize_angle(np.array(state.default_dof_pos)),
            normalize_angle(state.accurate_dof_pos), 
            tracking_sigma
        )
        
        # Orientation reward
        accurate_projected_gravity = quat_rotate_inverse(state.accurate_quat, 
                                                       calculator.gravity_vec)
        upward_reward = np.dot(calculator.projected_upward_vec, -accurate_projected_gravity)
        
        return dof_reward * upward_reward


class JumpTimerComponent(RewardComponent):
    """Manages jump timing without providing reward."""
    
    def __init__(self, name: str, weight: float = 0.0, **kwargs):
        super().__init__(name, weight, **kwargs)
        self.jump_timer = 0
        
    def calculate(self, state, calculator) -> float:
        jump_time = self.params.get('jump_time', 50)
        jump_sig = state.commands[0]
        
        if jump_sig:
            self.jump_timer += 1
            if self.jump_timer > jump_time:
                state.commands[0] = 0
                self.jump_timer = 0
                
        return 0
        
    def reset(self):
        self.jump_timer = 0


class TripodJumpComponent(RewardComponent):
    """Complex tripod jumping behavior with state-dependent rewards."""
    
    def __init__(self, name: str, weight: float = 1.0, **kwargs):
        super().__init__(name, weight, **kwargs)
        self.jump_timer = 0
        
    def calculate(self, state, calculator) -> float:
        jump_sig = state.commands[0]
        flying = len(state.contact_floor_geoms) == 0
        
        stationary_height = self.params.get('stationary_height', 0.5)
        jumping_height = self.params.get('jumping_height', 1.0)
        spinning_speed = self.params.get('spinning_speed', 5.0)
        weights = self.params.get('sub_weights', [1, 1, 100, 0, 0, 0])
        
        desired_height = jumping_height if jump_sig else stationary_height
        height = state.accurate_pos_world[2]
        
        # DOF tracking
        dof_reward = isaac_reward(
            normalize_angle(np.array(state.default_dof_pos)),
            normalize_angle(state.accurate_dof_pos),
            10.0
        )
        
        # Orientation
        accurate_projected_gravity = quat_rotate_inverse(state.accurate_quat,
                                                       calculator.gravity_vec)
        upward_reward = np.dot(calculator.projected_upward_vec, -accurate_projected_gravity)
        
        if not jump_sig:
            pos_reward = dof_reward * upward_reward
            height_track_reward = 0
            jump_bonus = 0
        else:
            pos_reward = 0
            height_track_reward = plateau(height, desired_height)
            self.jump_timer += 1
            
            if height > desired_height and flying:
                height_track_reward = 0
                jump_bonus = 1
                state.commands[0] = 0
                self.jump_timer = 0
            else:
                jump_bonus = 0
                
        # Spin rewards
        spin = np.dot(-accurate_projected_gravity, state.accurate_ang_vel_body)
        if jump_sig:
            spin_reward = plateau(spin, spinning_speed)
            spin_bonus = plateau(spin, spinning_speed)
        else:
            spin_reward = isaac_reward(0, spin, 0.1)
            spin_bonus = 0
            
        up_dir_dot = np.dot([0, 0, 1], -accurate_projected_gravity)
        
        reward_terms = np.array([
            pos_reward,
            height_track_reward,
            jump_bonus,
            spin_reward,
            up_dir_dot,
            spin_bonus
        ])
        
        return np.sum(weights * reward_terms)
        
    def reset(self):
        self.jump_timer = 0


class ActionRateComponent(RewardComponent):
    """Rewards action rate."""
    
    def calculate(self, state, calculator) -> float:
        last_action = state.action_history.last_last_action
        current_action = state.action_history.last_action
        action_rate = np.sum(np.square(current_action - last_action)) / calculator.dt
        return action_rate


# Component registry for easy lookup
COMPONENT_REGISTRY = {
    'linear_velocity_tracking': LinearVelocityTrackingComponent,
    'angular_velocity_tracking': AngularVelocityTrackingComponent,
    # 'linear_velocity_cmd_tracking': LinearVelocityTrackingCMDComponent,
    # 'angular_velocity_cmd_tracking': AngularVelocityTrackingCMDComponent,
    'contact_flight_time': ContactFlightTimeComponent,
    'dof_velocity_penalty': DOFVelocityPenaltyComponent,
    'dof_acceleration_penalty': DOFAccelerationPenaltyComponent,
    'contact_penalty': ContactPenaltyComponent,
    'jump_reward': JumpRewardComponent,
    'orientation_reward': OrientationRewardComponent,
    'height_tracking': HeightTrackingComponent,
    'torso_contact_penalty': TorsoContactPenaltyComponent,
    'dof_position_tracking': DOFPositionTrackingComponent,
    'plateau_angular_velocity': PlateauAngularVelocityComponent,
    'plateau_spin': PlateauSpinComponent,
    'plateau_height': PlateauHeightComponent,
    'recovery_reward': RecoveryRewardComponent,
    'jump_timer': JumpTimerComponent,
    'tripod_jump': TripodJumpComponent,
    'action_rate': ActionRateComponent,
}


class RewardCalculator:
    """Elegant component-based reward calculator."""
    
    def __init__(self, cfg: OmegaConf):
        """Initialize reward calculator with component-based configuration.
        
        Args:
            cfg: Configuration with task.reward_components specification
        """
        self.cfg = cfg
        
        # Environment parameters
        self.dt = cfg.control.dt
        self.theta = getattr(cfg.environment, 'theta', 0.610865)  # Default theta for robot
        
        # Reference vectors - get from observation section or use defaults
        observation = getattr(cfg, 'observation', {})
        self.gravity_vec = observation.get('gravity_vec', [0, 0, -1])
        self.projected_forward_vec = observation.get('projected_forward_vec', [1, 0, 0])
        self.projected_upward_vec = observation.get('projected_upward_vec', [0, 0, 1])

        # Create components from configuration
        task = getattr(cfg, 'task', {})
        reward_components = task.get('reward_components', [])
        self.components = self._create_components(reward_components)
        
        # Initialize state
        self.reset()
        
    def reset(self):
        """Reset reward calculator state."""
        self.step_counter = 0
        for component in self.components:
            component.reset()
        
    def calculate(self, state) -> Tuple[float, Dict[str, Any]]:
        """Calculate reward based on current state.
        
        Args:
            state: Current environment state
            
        Returns:
            tuple: (total_reward, info_dict)
        """
        component_values = {}
        total_reward = 0.0
        
        for component in self.components:
            value = component.calculate(state, self)
            weighted_value = component.weight * value
            total_reward += weighted_value
            component_values[component.name] = value
            
        info = {
            "component_values": component_values,
            "component_weights": {comp.name: comp.weight for comp in self.components},
            "total_reward": total_reward,
            "num_components": len(self.components)
        }
        
        self.step_counter += 1
        return total_reward, info
        
    def _create_components(self, component_configs: List) -> List[RewardComponent]:
        """Create reward components from configuration.
        
        Args:
            component_configs: List of component configuration dictionaries
            
        Returns:
            List of initialized reward components
        """
        if not component_configs:
            raise ValueError("No reward_components specified in config")
            
        components = []
        for config in component_configs:
            component_type = config['type']
            component_name = config.get('name', component_type)
            component_weight = config.get('weight', 1.0)
            component_params = config.get('params', {})
            
            if component_type not in COMPONENT_REGISTRY:
                available_types = ', '.join(COMPONENT_REGISTRY.keys())
                raise ValueError(f"Unknown component type: {component_type}. "
                               f"Available types: {available_types}")
                               
            component_class = COMPONENT_REGISTRY[component_type]
            component = component_class(component_name, component_weight, **component_params)
            components.append(component)
            
        return components
    
    @property 
    def component_names(self) -> List[str]:
        """Get list of component names."""
        return [comp.name for comp in self.components]
    
    def get_component(self, name: str) -> Optional[RewardComponent]:
        """Get component by name."""
        for comp in self.components:
            if comp.name == name:
                return comp
        return None
    
    def __str__(self) -> str:
        """String representation of the reward calculator."""
        lines = [f"RewardCalculator with {len(self.components)} components:"]
        for comp in self.components:
            lines.append(f"  - {comp.name}: {comp.__class__.__name__} (weight: {comp.weight})")
        return "\n".join(lines)


def create_reward_calculator(cfg: OmegaConf) -> RewardCalculator:
    """Factory function to create a reward calculator.
    
    Args:
        cfg: Configuration object with task.reward_components
        
    Returns:
        Initialized RewardCalculator instance
    """
    return RewardCalculator(cfg)


def register_component(name: str, component_class: type):
    """Register a new reward component type.
    
    Args:
        name: Component type name for configuration
        component_class: RewardComponent subclass
    """
    if not issubclass(component_class, RewardComponent):
        raise ValueError(f"Component class must inherit from RewardComponent")
    
    COMPONENT_REGISTRY[name] = component_class


def list_available_components() -> List[str]:
    """Get list of all available component types."""
    return list(COMPONENT_REGISTRY.keys()) 