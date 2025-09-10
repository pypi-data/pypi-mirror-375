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

from collections import defaultdict
import copy
import os
os.environ["MUJOCO_GL"] = "egl"

from metamachine.robot_factory.factory_registry import get_default_draft_model_cfg, get_default_fine_model_cfg
from metamachine.robot_factory.pose_optimizer import optimize_pose
from typing import Any, Dict, List, Tuple
# from gymnasium.envs.mujoco import MujocoEnv
import cv2
import numpy as np
import mujoco
import mujoco.viewer
from omegaconf import OmegaConf

from .base import Base
from ..utils.math_utils import (
    AverageFilter, construct_quaternion, quat_rotate, quat_rotate_inverse, quaternion_multiply_alt, 
    quaternion_to_euler, rotate_vector2D, wxyz_to_xyzw
)
from ..robot_factory.core.xml_compiler import XMLCompiler
from ..utils.math_utils import quaternion_from_vectors
from ..utils.validation import is_list_like, is_number
from .gym.mujoco_env import MujocoEnv
from .. import robot_factory

# Try to get CONTROLLER_ROOT_DIR from environment or use default
try:
    from metamachine import METAMACHINE_ROOT_DIR
    ROOT_DIR = METAMACHINE_ROOT_DIR
except ImportError:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

DEFAULT_CAMERA_CONFIG = {
    "distance": 4.0,
}

class MetaMachine(Base, MujocoEnv):
    """
    MetaMachine Simulation Environment
    
    A comprehensive robotic simulation environment that provides:
    - Modular robot morphology support with pose optimization
    - Advanced action processing with filtering and multiple control modes
    - Configurable reward systems with multiple components
    - Real-time visualization and video recording capabilities
    - Command-based high-level control interface
    - Comprehensive observation space with temporal stacking
    
    This environment serves as the main interface for reinforcement learning
    research, evolutionary robotics research, and robotic control experiments 
    in the MetaMachine framework.
    
    Features high-fidelity physics simulation with comprehensive domain 
    randomization, sensor simulation, and advanced control features. Currently
    implemented with MuJoCo physics engine.
    
    Args:
        cfg: OmegaConf configuration object containing all environment parameters
        
    Example:
        >>> from metamachine.environments.configs.config_registry import ConfigRegistry
        >>> from metamachine.environments.env_sim import MetaMachine
        >>> cfg = ConfigRegistry.create_from_name("basic_quadruped")
        >>> env = MetaMachine(cfg)
        >>> obs, info = env.reset()
        >>> obs, reward, done, truncated, info = env.step(action)
    """
    
    metadata = {
        "render_modes": [
            "human",
            "rgb_array", 
            "depth_array",
        ],
    }

    def __init__(self, cfg: OmegaConf):
        """Initialize simulation environment.
        
        Args:
            cfg: Modern configuration object with simulation parameters
        """
        self.cfg = cfg


        # Validate simulation config
        self._validate_simulation_config(cfg)
        self._setup_logging()
        self._update_pose_cfg(cfg)

        # Initialize base class
        super().__init__(cfg)

        # Initialize simulation components
        self._initialize_environment(cfg)
        
        # Setup simulation-specific state
        self._setup_simulation_state()

        

    def _update_pose_cfg(self, cfg: OmegaConf):

        self._pose_setter = {
            "init_pos": lambda v: setattr(cfg.initialization, "init_pos", v),
            "init_quat": lambda v: setattr(cfg.initialization, "init_quat", v),
            "default_dof_pos": lambda v: setattr(cfg.control, "default_dof_pos", v),
            "forward_vec": lambda v: setattr(cfg.observation, "forward_vec", v),
            "projected_forward": lambda v: setattr(cfg.observation, "projected_forward_vec", v),
            "projected_upward": lambda v: setattr(cfg.observation, "projected_upward_vec", v),
        }

        if self.cfg.pose_optimization.enabled:
            # Perform pose optimization if enabled
            if self.cfg.pose_optimization.load_pose is None:
                self.pose_dict = self._optimize_pose()

                # Save optimized pose parameters
                pose_cfg = OmegaConf.create(self.pose_dict)
                pose_cfg_file = os.path.join(self._log_dir, "optimized_pose.yaml")
                with open(pose_cfg_file, "w") as fp:
                    OmegaConf.save(config=pose_cfg, f=fp.name)
            else:
                pose_cfg_file = self.cfg.pose_optimization.load_pose
                self.pose_dict = OmegaConf.load(pose_cfg_file)
                print(f"Loaded pose parameters from {pose_cfg_file}")

            for key, value in self.pose_dict.items():
                if key in self._pose_setter:
                    self._pose_setter[key](value)
                else:
                    print(f"Warning: Unrecognized pose parameter '{key}'")

    def _validate_simulation_config(self, cfg: OmegaConf):
        """Validate simulation configuration."""
        if 'simulation' not in cfg:
            raise ValueError("Missing 'simulation' section in config")
        
        required_sim_fields = ['mj_dt']
        missing = [f for f in required_sim_fields if f not in cfg.simulation]
        if missing:
            raise ValueError(f"Missing simulation config fields: {missing}")

    def _initialize_environment(self, cfg: OmegaConf):
        """Initialize MuJoCo simulation components."""
        self.sim_cfg = cfg.simulation

        if cfg.morphology.asset_file is not None:  
            # Load and compile robot asset
            self._load_robot_asset()
        elif cfg.morphology.configuration is not None:
            self._load_robot_asset_from_morphology(cfg.morphology.robot_type, cfg.morphology.configuration)
        else:
            raise ValueError("No robot asset file or morphology provided")
        
        # Setup MuJoCo environment
        self._setup_mujoco()
        
        # Initialize terrain system
        self._setup_terrain()

    def _optimize_pose(self):
        """Optimize robot pose using the specified optimization method."""
        if not self.cfg.pose_optimization.enabled:
            return {}
        else:
            print("Optimizing robot pose...")
            # Implement optimization logic here
            # This could involve running a physics simulation, adjusting joint angles, etc.
            self._load_draft_robot_asset_from_morphology(self.cfg.morphology.robot_type, self.cfg.morphology.configuration)

            pose_dict = optimize_pose(self._draft_robot_instance,
                                      drop_steps=self.cfg.pose_optimization.drop_steps,
                                      move_steps= self.cfg.pose_optimization.move_steps,
                                      optimization_type=self.cfg.pose_optimization.optimization_type,
                                      enable_progress_bar=True,
                                      spine_assumption=False,
                                      seed=0,
                                      log_dir=self._log_dir
                                      )
            return pose_dict

    def _load_robot_asset_from_morphology(self, robot_type, morphology):
        """Load robot asset from morphology using the new factory system."""
        # Get the factory using the new registry system
        factory = robot_factory.get_robot_factory(robot_type, 
                                                    sim_cfg=self.cfg.simulation,
                                                    **get_default_fine_model_cfg(robot_type))
        if factory is None:
            raise ValueError(f"Unknown robot factory type: {robot_type}")
        
        # # Prepare configuration for robot creation
        # robot_config = {
        #     'sim_cfg': OmegaConf.to_container(self.sim_cfg) if self.sim_cfg else None
        # }
        
        # Create robot using the new factory interface
        robot = factory.create_robot(morphology=morphology)

        
        
        # Validate the robot
        is_valid, errors = robot.validate()
        if not is_valid:
            print(f"Warning: Robot validation failed: {errors}")
        
        # Get the XML string
        self.xml_string = robot.get_xml_string()
        
        # Store robot instance for potential future use
        self._robot_instance = robot


    def _load_draft_robot_asset_from_morphology(self, robot_type, morphology):
        """Load robot asset from morphology using the new factory system."""
        # Get the factory using the new registry system
        draft_factory = robot_factory.get_robot_factory(robot_type,
                                                        sim_cfg=self.cfg.simulation,
                                                        **get_default_draft_model_cfg(robot_type))
                                                        
        
        if draft_factory is None:
            raise ValueError(f"Unknown robot factory type: {robot_type}")
        
        # # Prepare configuration for robot creation
        # robot_config = {
        #     'sim_cfg': OmegaConf.to_container(self.sim_cfg) if self.sim_cfg else None
        # }
        
        # Create robot using the new factory interface
        draft_robot = draft_factory.create_robot(morphology=morphology)
        
        # Validate the robot
        is_valid, errors = draft_robot.validate()
        if not is_valid:
            print(f"Warning: Robot validation failed: {errors}")
        
        # Get the XML string
        self.draft_xml_string = draft_robot.get_xml_string()

        # Store robot instance for potential future use
        self._draft_robot_instance = draft_robot


    def get_robot_instance(self):
        """Get the robot instance if available (new factory system only)."""
        return getattr(self, '_robot_instance', None)

    def _load_robot_asset(self):
        """Load and compile robot asset."""
        asset_files = self.cfg.morphology.asset_file
        self.randomize_asset = is_list_like(asset_files)
        
        asset_file = (np.random.choice(asset_files) if self.randomize_asset 
                     else asset_files)
        
        xml_path = os.path.join(ROOT_DIR, "assets", "robots", asset_file)
        
        # Initialize XML compiler with modifications
        self.xml_compiler = XMLCompiler(xml_path)
        self.xml_compiler.torque_control()
        self.xml_compiler.update_timestep(self.sim_cfg.mj_dt)
        
        # Apply asset modifications
        if self.sim_cfg.get('pyramidal_cone', False):
            self.xml_compiler.pyramidal_cone()
            
        if self.sim_cfg.get('randomize_mass', False):
            self.mass_range = self.xml_compiler.get_mass_range(
                self.sim_cfg.random_mass_percentage
            )
            
        self.xml_string = self.xml_compiler.get_string()

    def _setup_mujoco(self):
        """Setup MuJoCo environment."""
        # Calculate simulation parameters
        self.mj_dt = self.sim_cfg.mj_dt
        assert self.cfg.control.dt % self.mj_dt < 1e-9, \
            f"dt ({self.cfg.control.dt}) must be multiple of mj_dt ({self.mj_dt})"
        self.frame_skip = int(self.cfg.control.dt / self.mj_dt)
        
        # Rendering configuration
        self.render_size = self.sim_cfg.get('render_size', [426, 240])
        # self.render_on = self.sim_cfg.get('render', False)
        
        # New rendering mode configuration
        self.render_mode = self.sim_cfg.get('render_mode', 'none')  # 'none', 'viewer', 'mp4'
        self.video_path = self.sim_cfg.get('video_path', self._log_dir)
        self.video_path = self._log_dir if self.video_path is None else self.video_path
        
        # Video recording configuration
        self.video_record_interval = self.sim_cfg.get('video_record_interval', 1)  # Record every N episodes
        self.video_name_pattern = self.sim_cfg.get('video_name_pattern', 'episode_{episode}')  # Naming pattern
        self.video_base_name = self.sim_cfg.get('video_base_name', 'robot_video')  # Base name without extension

        # Setup EGL environment if needed
        if self.render_mode == 'mp4':
            self._setup_egl_environment()
            self._initialize_video_recording()
        
        # Initialize MuJoCo
        MujocoEnv.__init__(
            self,
            self.xml_string,
            self.frame_skip,
            observation_space=None,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            width=self.render_size[0],
            height=self.render_size[1],
        )

        self._setup_spaces()
        
        # Restore our render settings after MuJoCo init (it might overwrite them)
        self.render_mode = self.sim_cfg.get('render_mode', 'none')  # 'none', 'viewer', 'mp4'
        self.video_fps = self.sim_cfg.get('video_fps', None)
        if self.video_fps is None:
            self.video_fps = 1/self.cfg.control.dt

    def _setup_terrain(self):
        """Setup terrain generation system."""
        try:
            from ..robot_factory.core.terrain_builder import Terrain
            self.terrain_resetter = Terrain()
        except ImportError:
            self.terrain_resetter = None
            if self.sim_cfg.get('terrain'):
                print("Warning: Terrain requested but module unavailable")

    def _setup_egl_environment(self):
        """Setup EGL environment for headless rendering."""
        os.environ['MUJOCO_GL'] = 'egl'
        os.environ['MUJOCO_EGL_DEVICE_ID'] = '0'
        os.environ['PYOPENGL_PLATFORM'] = 'egl'

        print("EGL environment configured for headless rendering")

    def _initialize_video_recording(self):
        """Initialize video recording system."""
        self.video_frames = []
        self.egl_renderer = None
        self.recording_active = False
        print(f"Video recording initialized. Recording every {self.video_record_interval} episodes with pattern: {self.video_name_pattern}")

    def _create_egl_renderer(self):
        """Create EGL renderer for direct rendering."""
        if self.egl_renderer is None:
            try:
                # Ensure EGL is properly set up
                import os
                old_gl = os.environ.get('MUJOCO_GL', '')
                os.environ['MUJOCO_GL'] = 'egl'
                
                width, height = self.render_size
                self.egl_renderer = mujoco.Renderer(self.model, height=height, width=width)
                print(f"EGL renderer created ({width}x{height})")
                
                # Get preferred camera for rendering
                self.preferred_camera_id = self._get_preferred_camera()
                
                # Restore previous GL setting if it existed
                if old_gl:
                    os.environ['MUJOCO_GL'] = old_gl
                    
            except Exception as e:
                print(f"Failed to create EGL renderer: {e}")
                # Try alternative: use synthetic frames for headless environments
                print("EGL rendering not available, using synthetic mode")
                self.egl_renderer = "synthetic"  # Special marker for synthetic rendering
        return self.egl_renderer

        
    def _cleanup_egl_renderer(self):
        """Clean up EGL renderer."""
        if hasattr(self, 'egl_renderer') and self.egl_renderer is not None:
            if self.egl_renderer != "synthetic":
                try:
                    self.egl_renderer.close()
                except Exception as e:
                    print(f"Warning: Error closing EGL renderer: {e}")
            self.egl_renderer = None

    def _create_synthetic_frame(self, width, height):
        """Create a synthetic frame with robot state visualization."""
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from io import BytesIO
        
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1, 3)
        ax.set_aspect('equal')
        
        # Draw ground
        ground = patches.Rectangle((-2, -1), 4, 0.1, color='brown')
        ax.add_patch(ground)
        
        # Get robot position
        if hasattr(self, 'data') and self.data is not None:
            pos = self.data.qpos[:3]
            quat = self.data.qpos[3:7]
            
            # Draw robot as a simple circle
            robot = patches.Circle((pos[0], pos[2]), 0.2, color='blue', alpha=0.7)
            ax.add_patch(robot)
            
            # Draw velocity vector
            if hasattr(self, 'data'):
                vel = self.data.qvel[:3] * 0.5  # Scale for visibility
                ax.arrow(pos[0], pos[2], vel[0], vel[2], 
                        head_width=0.05, head_length=0.05, fc='red', ec='red')
            
            # Add text info
            ax.text(-1.8, 2.7, f"Step: {getattr(self, 'step_count', 0)}", fontsize=8)
            ax.text(-1.8, 2.5, f"Pos: ({pos[0]:.2f}, {pos[2]:.2f})", fontsize=8)
        
        ax.set_title('Robot Simulation (Synthetic View)', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Convert to numpy array
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
        buf.seek(0)
        
        from PIL import Image
        img = Image.open(buf)
        frame = np.array(img)[:, :, :3]  # Remove alpha channel if present
        
        plt.close(fig)
        buf.close()
        
        return frame

    def _capture_frame_egl(self):
        """Capture frame using EGL renderer."""
        if self.render_mode != 'mp4' or not self.recording_active:
            return
        
        renderer = self._create_egl_renderer()
        
        if renderer == "synthetic":
            # Create synthetic frame
            width, height = self.render_size
            frame = self._create_synthetic_frame(width, height)
        else:
            # Use real EGL renderer with preferred camera
            camera_id = getattr(self, 'preferred_camera_id', -1)
            renderer.update_scene(self.data, camera=camera_id)
            pixels = renderer.render()
            # frame = (pixels * 255).astype(np.uint8)
            frame = 1 - pixels
            frame = (frame * 255).astype(np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        frame = self._add_metrics_overlay(frame)

        self.video_frames.append(frame)
            

    def _save_video(self):
        """Save collected frames to MP4 video using moviepy."""
        if not self.video_frames:
            print("No frames to save")
            return False
        
        from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
        
        # Generate filename based on pattern
        filename = self._generate_video_filename()
        
        # Create clip from frames with fps specified
        clip = ImageSequenceClip(list(self.video_frames), fps=self.video_fps)
        
        # Write video file
        clip.write_videofile(
            filename, 
            codec='libx264',
            fps=self.video_fps,
            audio=False,
            logger=None  # Suppress moviepy logging
        )
        
        # Clean up
        clip.close()
        
        file_size = os.path.getsize(filename)
        print(f"✓ Video saved: {filename} ({file_size:,} bytes, {len(self.video_frames)} frames)")
        return True

    def _generate_video_filename(self):
        """Generate video filename based on pattern and episode counter."""
        # Extract base name and extension
        base_name, ext = os.path.splitext(self.video_path)
        if not ext:
            ext = '.mp4'
            video_dir = self.video_path
        else:
            video_dir = os.path.dirname(self.video_path)
        
        # Generate filename using pattern
        if '{episode}' in self.video_name_pattern:
            filename = self.video_name_pattern.format(episode=self.episode_counter+1)
        else:
            # Fallback to pattern as is if no {episode} placeholder
            filename = self.video_name_pattern
        
        # Ensure it has .mp4 extension
        if not filename.endswith('.mp4'):
            filename += ext
            
        # Use directory from original video_path if provided
        if video_dir:
            filename = os.path.join(video_dir, filename)

        os.makedirs(os.path.dirname(filename), exist_ok=True)
            
        return filename
        

    def _should_record_episode(self):
        """Check if current episode should be recorded based on interval."""
        return (self.episode_counter + 1) % self.video_record_interval == 0 or self.episode_counter == 0

    def start_video_recording(self):
        """Start video recording."""
        if self.render_mode == 'mp4':
            self.video_frames = []
            self.recording_active = True
            print(f"Video recording started for episode {self.episode_counter}")
        else:
            print("Video recording not available (render_mode must be 'mp4')")

    def stop_video_recording(self):
        """Stop video recording and save video."""
        if self.render_mode == 'mp4' and self.recording_active:
            self.recording_active = False
            success = self._save_video()
            self._cleanup_egl_renderer()
            return success
        return False

    def _setup_simulation_state(self):
        """Setup simulation-specific state and tracking."""
        # Robot configuration
        self._parse_robot_parameters()
        
        # Joint and body setup
        self._setup_robot_model()
        
        # Control tracking
        self._initialize_control_state()
        
        # Sensor and data tracking
        self._initialize_sensors()
        
        # External forces
        self._setup_external_forces()
        
        # Initialization parameters
        self._setup_initialization_parameters()
        
        # Initialize viewer for viewer mode
        self._passive_viewer = None
        self._viewer_context_manager = None

    def _parse_robot_parameters(self):
        """Parse robot-specific parameters."""
        # Get parameters from their correct config locations
        self.theta = getattr(self.cfg.environment, 'theta', 0.610865)
        self.kp = getattr(self.cfg.control, 'kp', 8.0)
        self.kd = getattr(self.cfg.control, 'kd', 0.2)
        
        control_cfg = self.cfg.control
        
        if control_cfg.num_actions is None:
            self.num_act = self.model.nu
        else:
            self.num_act = control_cfg.num_actions
        self.num_envs = self.cfg.environment.num_envs

    def _setup_robot_model(self):
        """Setup robot model parameters after MuJoCo initialization."""
        self.num_joint = self.model.nu
        
        # Extract joint module IDs
        self.jointed_module_ids = sorted([
            int(mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, j).replace("joint", ""))
            for j in self.model.actuator_trnid[:, 0]
        ])
        
        # Validate action space
        expected_joints = self.num_act * self.num_envs
        if expected_joints != self.num_joint:
            raise ValueError(f"Action space mismatch: expected {expected_joints}, got {self.num_joint}")
        
        # Setup joint and body indices
        self.joint_idx = [self.model.joint(f'joint{i}').id for i in self.jointed_module_ids]
        self.joint_geom_idx = (
            [self.model.geom(f'left{i}').id for i in self.jointed_module_ids] +
            [self.model.geom(f'right{i}').id for i in self.jointed_module_ids]
        )
        self.joint_body_idx = [
            self.model.geom(f'left{i}').bodyid.item() 
            for i in self.jointed_module_ids
        ]
        
        # Setup PD gains
        self.kps = np.full(self.num_act * self.num_envs, self.kp, dtype=np.float32)
        self.kds = np.full(self.num_act * self.num_envs, self.kd, dtype=np.float32)

    def _initialize_control_state(self):
        """Initialize control state tracking."""
        # Default DOF positions
        default_dof_pos = self.cfg.control.get('default_dof_pos', 0) 
        if isinstance(default_dof_pos, (list, np.ndarray)):
            self.default_dof_pos = np.array(default_dof_pos)
        else:
            self.default_dof_pos = np.full(self.num_joint, default_dof_pos)
        
        # Latency simulation tracking
        self.last_pos_sim = self.default_dof_pos.copy()
        self.last_last_pos_sim = self.default_dof_pos.copy()
        self.last_vel_sim = np.zeros(self.num_joint)
        self.last_last_vel_sim = np.zeros(self.num_joint)
        
        # Other tracking
        self.last_com_pos = np.zeros(3)
        self.episode_counter = 0

    def _initialize_sensors(self):
        """Initialize sensor data structures."""
        self.sensors = defaultdict(list)

    def _setup_external_forces(self):
        """Setup external force system."""
        self.external_forces_enabled = self.sim_cfg.get('random_external_force', False)
        if self.external_forces_enabled:
            self.external_force_config = {
                'ranges': self.sim_cfg.random_external_force_ranges,
                'bodies': self.sim_cfg.random_external_force_bodies,
                'positions': self.sim_cfg.random_external_force_positions,
                'directions': self.sim_cfg.random_external_force_directions,
                'durations': self.sim_cfg.random_external_force_durations,
                'interval': self.sim_cfg.random_external_force_interval,
            }
            self.external_force_counter = {
                i: 0 for i in range(len(self.external_force_config['bodies']))
            }

    def _setup_initialization_parameters(self):
        """Setup robot initialization parameters."""
        # Get initialization config
        self.init_cfg = getattr(self.cfg, 'initialization', {})
        
        # Position and orientation
        self.init_pos = self.init_cfg.get('init_pos', [0, 0, 0.1])
        self.init_joint_pos = self.init_cfg.get('init_joint_pos', 0)
        if self.init_joint_pos is None:
            self.init_joint_pos = self.cfg.control.default_dof_pos

        if isinstance(self.init_joint_pos, (list, np.ndarray)):
            self.init_joint_pos = np.array(self.init_joint_pos)
        else:
            self.init_joint_pos = np.full(self.num_joint, self.init_joint_pos)
        self.given_init_qpos = self.init_cfg.get('init_qpos')
        
        # Calculate initial quaternion
        self._calculate_initial_quaternion()
        
        # Forward vector
        forward_vec = self.cfg.observation.get('forward_vec')
        self.forward_vec = np.array(forward_vec) if forward_vec else None

    def _calculate_initial_quaternion(self):
        """Calculate initial robot orientation quaternion."""
        init_quat_cfg = self.init_cfg.get('init_quat', 'x')
        self.theta = 0.610865  # Default theta value
        lleg_vec = np.array([0, np.cos(self.theta), np.sin(self.theta)])
        
        if is_list_like(init_quat_cfg):
            if len(init_quat_cfg) == 4:
                self.init_quat = np.array(init_quat_cfg)
            elif len(init_quat_cfg) == 3:
                self.init_quat = quaternion_from_vectors(lleg_vec, np.array(init_quat_cfg))
            else:
                raise ValueError("init_quat list must have 3 or 4 elements")
        elif init_quat_cfg == "x":
            self.init_quat = quaternion_from_vectors(lleg_vec, np.array([1, 0, 0]))
        elif init_quat_cfg == "y":
            self.init_quat = quaternion_from_vectors(lleg_vec, np.array([0, 1, 0]))
        else:
            raise ValueError("init_quat must be list of 3/4 elements or 'x'/'y'")

    def _reset_external_forces(self):
        """Reset external force applications."""
        self.data.qfrc_applied = np.zeros(self.model.nv)
        if hasattr(self, 'external_force_counter'):
            self.external_force_counter = {k: 0 for k in self.external_force_counter}

    def _apply_force(self, force: float, body: str, position: List[float], 
                    direction: List[float]):
        """Apply external force to specified body.
        
        Args:
            force: Force magnitude
            body: Body name
            position: Force application point in local coordinates
            direction: Force direction in global coordinates
        """
        body_id = self.model.body(body).id
        rotation_matrix = self.data.xmat[body_id].reshape(3, 3)
        body_pos = self.data.xpos[body_id]
        
        # Transform to global coordinates
        force_global = np.array(direction) * force
        point_global = body_pos + rotation_matrix @ np.array(position)
        
        # Apply force
        torque = np.zeros(3)
        qfrc_result = np.zeros(len(self.data.qvel))
        mujoco.mj_applyFT(self.model, self.data, force_global, torque, 
                         point_global, body_id, qfrc_result)
        self.data.qfrc_applied = qfrc_result

    def _perform_action(self, action: np.ndarray) -> Dict[str, Any]:
        """Execute action with comprehensive control pipeline.
        
        Args:
            action: Processed action from action processor
            
        Returns:
            Action execution information
        """
        # Apply external forces
        if self.external_forces_enabled:
            self._handle_external_forces()
        
        # Validate frame skip for latency
        latency_scheme = self.sim_cfg.get('latency_scheme', -1)
        if latency_scheme >= 0 and self.frame_skip % 2 != 0:
            raise ValueError("frame_skip must be even for latency simulation")
        
        # Add action noise if enabled
        pos, vel = self._add_action_noise(action)
        
        # Record positions before action
        pos_before = self._record_positions()
        
        # Execute control with latency simulation
        self._execute_control(pos, vel, latency_scheme)
        
        # Capture frame for video recording if needed
        self.render()
        
        # Update latency tracking
        self._update_latency_tracking(pos, vel)
        
        # Record positions after action
        pos_after = self._record_positions()
        
        return self._create_action_info(pos_before, pos_after)

    def _handle_external_forces(self):
        """Handle external force application."""
        config = self.external_force_config
        
        if self.step_count % config['interval'] == 0:
            for i, (force_range, body, position, direction) in enumerate(zip(
                config['ranges'], config['bodies'], 
                config['positions'], config['directions']
            )):
                force = np.random.uniform(*force_range)
                self._apply_force(force, body, position, direction)

        # Update force duration counters
        for i, duration in enumerate(config['durations']):
            self.external_force_counter[i] += 1
            if self.external_force_counter[i] >= duration:
                self._reset_external_forces()

    def _add_action_noise(self, action: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Add noise to actions if enabled.
        
        Returns:
            (position_action, velocity_action)
        """
        pos = action.copy()
        vel = np.zeros_like(pos)
        
        if self.sim_cfg.get('noisy_actions', False):
            noise_std = self.sim_cfg.action_noise_std
            pos += self.np_random.normal(0, noise_std, size=pos.shape)
            vel += self.np_random.normal(0, noise_std, size=vel.shape)
        
        return pos, vel

    def _record_positions(self) -> Dict[str, np.ndarray]:
        """Record current robot positions."""
        return {
            'base_pos': self.data.qpos.flat[:2].copy(),
            'general_coords': np.array([
                self.data.qpos.flat[i:i+2] for i in self.free_joint_addr
            ]).reshape(-1, 2)
        }

    def _execute_control(self, pos: np.ndarray, vel: np.ndarray, latency_scheme: int):
        """Execute control with latency simulation."""
        if latency_scheme == -1:
            # No latency
            self._pd_control(pos, self.frame_skip, vel)
        elif latency_scheme == 0:
            # One step latency
            half_skip = self.frame_skip // 2
            self._pd_control(self.last_pos_sim, half_skip, self.last_vel_sim)
            self._pd_control(pos, half_skip, vel)
        elif latency_scheme == 1:
            # Two step latency
            half_skip = self.frame_skip // 2
            self._pd_control(self.last_last_pos_sim, half_skip, self.last_last_vel_sim)
            self._pd_control(self.last_pos_sim, half_skip, self.last_vel_sim)
        elif latency_scheme == -2:
            # Fine control with latency
            self._pd_control_fine(self.last_pos_sim, self.frame_skip // 2, self.last_vel_sim)

    def _update_latency_tracking(self, pos: np.ndarray, vel: np.ndarray):
        """Update latency simulation tracking variables."""
        self.last_last_pos_sim = self.last_pos_sim.copy()
        self.last_pos_sim = pos.copy()
        self.last_last_vel_sim = self.last_vel_sim.copy()
        self.last_vel_sim = vel.copy()

    def _create_action_info(self, pos_before: Dict, pos_after: Dict) -> Dict[str, Any]:
        """Create action execution info dictionary."""
        info = {
            'coordinates': pos_before['base_pos'],
            'next_coordinates': pos_after['base_pos'],
            'coordinates_general': pos_before['general_coords'],
            'next_coordinates_general': pos_after['general_coords'],
        }
        
        # Add render data if needed
        if getattr(self, 'render_on_bg', False):
            info['render'] = self.render().transpose(2, 0, 1)
            
        return info

    def _pd_control(self, pos_desired: np.ndarray, frame_skip: int, 
                   vel_desired: np.ndarray = None):
        """Execute PD control for joint positions.
        
        Args:
            pos_desired: Target joint positions
            frame_skip: Number of simulation steps
            vel_desired: Target joint velocities
        """
        if vel_desired is None:
            vel_desired = np.zeros_like(pos_desired)
            
        # Get current joint states
        dof_pos = self.data.qpos[self.model.jnt_qposadr[self.joint_idx]]
        dof_vel = self.data.qvel[self.model.jnt_dofadr[self.joint_idx]]

        # Calculate PD torques
        torques = self.kps * (pos_desired - dof_pos) + self.kds * (vel_desired - dof_vel)
        
        # Apply constraints
        torques = self._apply_torque_constraints(torques, dof_vel)
        
        # Execute simulation
        self.do_simulation(torques, int(frame_skip))

    def _apply_torque_constraints(self, torques: np.ndarray, 
                                 dof_vel: np.ndarray) -> np.ndarray:
        """Apply torque and velocity constraints."""
        # Torque-velocity constraints
        if self.sim_cfg.get('tn_constraint', True):
            torque_limits = self._calculate_torque_limits(dof_vel)
            torques = np.clip(torques, -torque_limits, torque_limits)
        
        # Handle disabled motors
        broken_motors = self.sim_cfg.get('broken_motors')
        if broken_motors is not None:
            torques[broken_motors] = 0
            
        return torques

    def _calculate_torque_limits(self, dof_vel: np.ndarray) -> np.ndarray:
        """Calculate velocity-dependent torque limits."""
        abs_vel = np.abs(dof_vel)
        torque_limits = np.where(
            abs_vel < 11.5,
            12.0,
            np.clip(-0.656 * abs_vel + 19.541, 0, None)
        )
        return torque_limits

    def _pd_control_fine(self, pos_desired: np.ndarray, frame_skip: int,
                        vel_desired: np.ndarray = None):
        """Execute fine-grained PD control with per-step updates."""
        if vel_desired is None:
            vel_desired = np.zeros_like(pos_desired)
            
        for _ in range(int(frame_skip)):
            dof_pos = self.data.qpos[self.model.jnt_qposadr[self.joint_idx]]
            dof_vel = self.data.qvel[self.model.jnt_dofadr[self.joint_idx]]
            
            torques = self.kps * (pos_desired - dof_pos) + self.kds * (vel_desired - dof_vel)
            torques = self._apply_torque_constraints(torques, dof_vel)
            
            self.do_simulation(torques, 1)

    def _get_observable_data(self) -> Dict[str, Any]:
        """Get comprehensive observable state data."""
        # Extract basic state
        qpos = self.data.qpos.flatten()
        qvel = self.data.qvel.flatten()
        
        # Core state components
        state_data = self._extract_core_state(qpos, qvel)
        
        # Sensor data
        self._update_sensor_readings()
        sensor_data = self._extract_sensor_data()
        
        # Extended data with noise handling
        extended_data = self._create_extended_state_data({**state_data, **sensor_data})
        
        # Simulation-specific data
        sim_data = self._extract_simulation_data()
        
        return {**extended_data, **sim_data}

    def _extract_core_state(self, qpos: np.ndarray, qvel: np.ndarray) -> Dict[str, Any]:
        """Extract core robot state information."""
        # Position and orientation
        self.pos_world = qpos[:3]
        quat = wxyz_to_xyzw(qpos[3:7])
        
        # Joint states
        dof_pos = qpos[self.model.jnt_qposadr[self.joint_idx]]
        dof_vel = qvel[self.model.jnt_dofadr[self.joint_idx]]
        
        # Velocities
        vel_world = qvel[:3]
        vel_body = quat_rotate_inverse(quat, vel_world)
        ang_vel_body = qvel[3:6]
        ang_vel_world = quat_rotate(quat, ang_vel_body)
        
        return {
            'pos_world': self.pos_world,
            'quat': quat,
            'dof_pos': dof_pos,
            'dof_vel': dof_vel,
            'vel_world': vel_world,
            'vel_body': vel_body,
            'ang_vel_body': ang_vel_body,
            'ang_vel_world': ang_vel_world,
            'qpos': qpos,
            'qvel': qvel,
        }

    def _update_sensor_readings(self):
        """Update all sensor readings from simulation."""
        sensor_specs = [
            ('quat', 4), ('gyro', 3), ('vel', 3), ('globvel', 3),
            ('back_quat', 4), ('back_gyro', 3), ('back_vel', 3), ('acc', 3)
        ]
        
        for sensor_type, size in sensor_specs:
            try:
                prefix = 'back_imu_' if sensor_type.startswith('back_') else 'imu_'
                clean_type = sensor_type.replace('back_', '')
                
                sensor_data = []
                for module_id in self.jointed_module_ids:
                    sensor_name = f"{prefix}{clean_type}{module_id}"
                    start_addr = self.model.sensor(sensor_name).adr[0]
                    sensor_data.append(self.data.sensordata[start_addr:start_addr + size])
                
                self.sensors[sensor_type] = np.array(sensor_data)
            except (KeyError, IndexError):
                continue

    def _extract_sensor_data(self) -> Dict[str, Any]:
        """Extract sensor data for observations."""
        sensor_data = {}
        
        if 'quat' in self.sensors:
            sensor_data['quats'] = np.array([
                wxyz_to_xyzw(q) for q in self.sensors['quat']
            ])
        if 'gyro' in self.sensors:
            sensor_data['gyros'] = self.sensors['gyro']
        if 'acc' in self.sensors:
            sensor_data['accs'] = self.sensors['acc']
            
        return sensor_data

    def _create_extended_state_data(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create extended data with accurate versions and noise."""
        extended = base_data.copy()
        
        # Add accurate (noise-free) versions
        for key, value in base_data.items():
            extended[f"accurate_{key}"] = copy.deepcopy(value)
            
            # Add observation noise if enabled
            if (self.sim_cfg.get('noisy_observations', False) and 
                isinstance(value, np.ndarray)):
                noise_std = self.sim_cfg.obs_noise_std
                extended[key] = value + self.np_random.normal(0, noise_std, size=value.shape)
        
        return extended

    def _extract_simulation_data(self) -> Dict[str, Any]:
        """Extract simulation-specific data."""
        sim_data = {
            'mj_data': self.data,
            'mj_model': self.model,
            'adjusted_forward_vec': getattr(self, 'adjusted_forward_vec', self.forward_vec),
        }
        
        # Contact information
        sim_data.update(self._extract_contact_data())
        
        # Additional sensor data
        if 'vel' in self.sensors:
            sim_data['vels'] = self.sensors['vel']
        if 'back_vel' in self.sensors:
            sim_data['back_vels'] = self.sensors['back_vel']
        if 'back_quat' in self.sensors:
            sim_data['back_quats'] = np.array([
                wxyz_to_xyzw(q) for q in self.sensors['back_quat']
            ])
        if 'back_gyro' in self.sensors:
            sim_data['back_gyros'] = self.sensors['back_gyro']
        
        # Center of mass data
        sim_data.update(self._calculate_com_data())
        
        return sim_data

    def _extract_contact_data(self) -> Dict[str, Any]:
        """Extract contact information."""
        contacts = [c.geom for c in self.data.contact]
        floor_contacts = [c.geom for c in self.data.contact if 0 in c.geom]
        
        # Count joint-floor contacts
        joint_floor_count = sum(
            (contact[0] in self.joint_geom_idx) or (contact[1] in self.joint_geom_idx)
            for contact in floor_contacts
        )
        
        return {
            'contact_geoms': contacts,
            'num_jointfloor_contact': joint_floor_count,
            'contact_floor_geoms': list(set(
                geom for pair in floor_contacts for geom in pair if geom != 0
            )),
            'contact_floor_socks': list(set(
                geom for pair in floor_contacts for geom in pair
                if self.model.geom(geom).name.startswith("sock")
            )),
            'contact_floor_balls': list(set(
                geom for pair in floor_contacts for geom in pair
                if (self.model.geom(geom).name.startswith("left") or
                    self.model.geom(geom).name.startswith("right"))
            )),
        }

    def _calculate_com_data(self) -> Dict[str, Any]:
        """Calculate center of mass data."""
        com_pos = np.mean(self.data.xpos[self.joint_body_idx], axis=0)
        com_vel_world = (com_pos - self.last_com_pos) / self.dt
        self.last_com_pos = com_pos.copy()
        
        return {'com_vel_world': com_vel_world}

    def _reset_robot(self):
        """Reset robot with domain randomization."""
        # Reset MuJoCo model
        self.reset_model()
        
        # Reset control tracking
        self.last_pos_sim = self.default_dof_pos.copy()
        self.last_last_pos_sim = self.default_dof_pos.copy()
        self.last_vel_sim = np.zeros(self.num_joint)
        self.last_last_vel_sim = np.zeros(self.num_joint)
        self.last_com_pos = np.zeros(3)
        
        # Initialize rendering filter
        self.render_lookat_filter = AverageFilter(10)

    def reset_model(self):
        """Reset MuJoCo model with comprehensive domain randomization."""

        # Check if this episode should be recorded
        if self._should_record_episode():
            self.start_video_recording()

        # Pre-reset operations
        self._pre_reset()
        
        # Handle model reloading if needed
        if self._need_model_reload():
            self._reload_model_with_randomization()
            
        # Reset external forces
        self._reset_external_forces()
        
        # Apply domain randomization
        self._apply_domain_randomization()
        
        # Set initial state
        self._set_initial_state()
        
        # Post-reset operations
        self._post_reset()

    def _pre_reset(self):
        """Pre-reset operations."""
        pass

    def _post_reset(self):
        """Post-reset operations."""
        pass

    def _post_done(self):
        """Post-done operations after an episode ends."""
        # Stop video recording if active
        if self.render_mode == 'mp4' and self.recording_active:
            success = self.stop_video_recording()
            if success:
                print(f"Episode {self.episode_counter} video recording completed")
            else:
                print(f"Episode {self.episode_counter} video recording failed")
        self.episode_counter += 1
        
        
    def _need_model_reload(self) -> bool:
        """Check if model needs to be reloaded for randomization."""
        self.randomize_asset = is_list_like(self.cfg.morphology.asset_file)
        return any([
            self.sim_cfg.get('randomize_mass', False),
            self.sim_cfg.get('randomize_damping', False),
            self.sim_cfg.get('add_scaffold_walls', False),
            self.randomize_asset
        ])

    def _reload_model_with_randomization(self):
        """Reload model with randomization applied."""
        # Asset randomization
        if self.randomize_asset:
            self._load_robot_asset()
        
        # Mass randomization
        if self.sim_cfg.get('randomize_mass', False):
            mass_dict = {
                key: np.random.uniform(*value) + self.sim_cfg.get('mass_offset', 0)
                for key, value in self.mass_range.items()
            }
            self.xml_compiler.update_mass(mass_dict)
        
        # Damping randomization
        if self.sim_cfg.get('randomize_damping', False):
            armature = np.random.uniform(*self.sim_cfg.random_armature_range)
            damping = np.random.uniform(*self.sim_cfg.random_damping_range)
            self.xml_compiler.update_damping(armature=armature, damping=damping)
        
        # Scaffold walls
        if self.sim_cfg.get('add_scaffold_walls', False):
            self.xml_compiler.remove_walls()
            angle = quaternion_to_euler(self.init_quat)[0] * 180/np.pi - 90
            self.xml_compiler.add_walls(transparent=False, angle=angle)
        
        # Reload MuJoCo environment
        self.reload_model(self.xml_compiler.get_string())

    def _apply_domain_randomization(self):
        """Apply domain randomization parameters."""
        # PD controller randomization
        randomization_cfg = getattr(self.cfg, 'randomization', {})
        pd_cfg = randomization_cfg.get('pd_controller', {})
        if pd_cfg.get('enabled', False):
            self.kp = np.random.uniform(*pd_cfg.get('kp_range', [8.0, 8.0]))
            self.kd = np.random.uniform(*pd_cfg.get('kd_range', [0.2, 0.2]))
            self.kps = np.full(self.num_act * self.num_envs, self.kp, dtype=np.float32)
            self.kds = np.full(self.num_act * self.num_envs, self.kd, dtype=np.float32)
        
        # Latency randomization
        if self.sim_cfg.get('random_latency_scheme', False):
            self.sim_cfg.latency_scheme = np.random.randint(0, 2)
        
        # Friction randomization
        self._randomize_friction()

    def _randomize_friction(self):
        """Apply friction randomization."""
        randomization_cfg = getattr(self.cfg, 'randomization', {})
        friction_cfg = randomization_cfg.get('friction', {})
        if not friction_cfg.get('enabled', False):
            return
            
        friction_range = friction_cfg.get('range', [0.8, 1.2])
        
        if is_number(friction_range[0]):
            # Single friction value
            friction = np.random.uniform(*friction_range)
            self.model.geom('floor').friction[0] = friction
            self.model.geom('floor').priority[0] = 10
        else:
            # Separate friction for different components
            stick_friction = np.random.uniform(*friction_range[0])
            ball_friction = np.random.uniform(*friction_range[1])
            
            self.model.geom('floor').priority[0] = 1
            for module_id in self.jointed_module_ids:
                self.model.geom(f'left{module_id}').friction[0] = ball_friction
                self.model.geom(f'right{module_id}').friction[0] = ball_friction
                self.model.geom(f'stick{module_id}').friction[0] = stick_friction
                
                for geom_name in [f'left{module_id}', f'right{module_id}', f'stick{module_id}']:
                    self.model.geom(geom_name).priority[0] = 2
        
        # Rolling friction
        rolling_cfg = friction_cfg.get('rolling', {})
        if rolling_cfg.get('enabled', False):
            roll_friction = np.random.uniform(*rolling_cfg.get('range', [0.0001, 0.0005]), size=2)
            self.model.geom('floor').friction[1:3] = roll_friction

    def _set_initial_state(self):
        """Set initial robot state with randomization."""
        # Handle orientation randomization
        final_quat = self._get_randomized_orientation()
        
        # Setup initial position
        self._setup_initial_positions(final_quat)
        
        # Apply initial state with noise
        qpos = self._apply_initial_noise()
        qvel = self._get_initial_velocities()
        
        # Set MuJoCo state
        self.set_state(qpos, qvel)
        
        # Record reset position
        self.reset_pos = self.data.qpos[:2].copy()

    def _get_randomized_orientation(self) -> np.ndarray:
        """Get randomized initial orientation."""
        if self.init_cfg.get('fully_randomize_orientation', False):
            # Fully random orientation
            rand_quat = self.np_random.normal(0, 1, 4)
            return rand_quat / np.linalg.norm(rand_quat)
        elif self.init_cfg.get('randomize_orientation', False):
            # Random rotation around Z-axis
            rotate_angle = self.np_random.uniform(0, 2*np.pi)
            rand_rotation = construct_quaternion([0,0,1], rotate_angle)
            final_quat = quaternion_multiply_alt(self.init_quat, rand_rotation)
            
            # Update forward vector
            if self.forward_vec is not None:
                self.adjusted_forward_vec = rotate_vector2D(
                    self.forward_vec[:2], -rotate_angle
                )
            return final_quat
        else:
            # No orientation randomization
            if self.forward_vec is not None:
                self.adjusted_forward_vec = self.forward_vec
            return self.init_quat

    def _setup_initial_positions(self, quat: np.ndarray):
        """Setup initial positions and joint states."""
        # Handle multiple initial positions
        if is_list_like(self.init_pos[0]):
            init_pos_list = copy.deepcopy(self.init_pos)
            quat_list = [quat] + [[1,0,0,0]] * 10  # Default quaternion list
            
            for i in range(self.model.njnt):
                if self.model.jnt_type[i] == 0:  # mjJNT_FREE
                    qpos_adr = self.model.jnt_qposadr[i]
                    self.init_qpos[qpos_adr:qpos_adr + 3] = init_pos_list.pop(0)
                    self.init_qpos[qpos_adr + 3:qpos_adr + 7] = quat_list.pop(0)
        else:
            self.init_qpos[:3] = self.init_pos
            self.init_qpos[3:7] = quat
        
        # Setup free joint addresses
        self.free_joint_addr = [
            self.model.jnt_qposadr[i] for i in range(self.model.njnt)
            if self.model.jnt_type[i] == 0
        ]
        
        # Joint position randomization
        randomization_cfg = getattr(self.cfg, 'randomization', {})
        dof_cfg = randomization_cfg.get('init_joint_pos', {})
        if dof_cfg.get('enabled', False):
            clip_actions = self.cfg.control.symmetric_limit
            joint_noise = self.np_random.uniform(-clip_actions, clip_actions, self.num_joint)
            self.init_qpos[self.model.jnt_qposadr[self.joint_idx]] = \
                self.default_dof_pos + joint_noise
            # TODO: consider frozen joints
        else:
            self.init_qpos[self.model.jnt_qposadr[self.joint_idx]] = self.init_joint_pos

    def _apply_initial_noise(self) -> np.ndarray:
        """Apply initial position noise."""
        if self.given_init_qpos is not None:
            return np.array(self.given_init_qpos)
        
        if self.init_cfg.get('noisy_init', True):
            return self.init_qpos + self.np_random.uniform(-0.1, 0.1, size=self.model.nq)
        else:
            return self.init_qpos.copy()

    def _get_initial_velocities(self) -> np.ndarray:
        """Get initial velocities with randomization."""
        init_qvel = getattr(self, 'init_qvel', np.zeros(self.model.nv))
        
        if self.init_cfg.get('randomize_ini_vel', True):
            randomize_vel = self.init_cfg.get('randomize_ini_vel', True)
            if is_list_like(randomize_vel):
                for i, vel_range in enumerate(randomize_vel):
                    init_qvel[i] = self.np_random.uniform(-vel_range, vel_range)
            else:
                init_qvel[:6] = self.np_random.uniform(-1, 1, 6)
        
        return init_qvel + self.np_random.normal(0, 0.1, self.model.nv)

    def reload_model(self, xml_string: str):
        """Reload MuJoCo model with new XML."""
        if hasattr(self, 'mujoco_renderer') and self.mujoco_renderer.viewer is not None:
            self.close()
        
        # Preserve render settings
        saved_render_mode = getattr(self, 'render_mode', 'none')
        saved_video_path = getattr(self, 'video_path', 'robot_video.mp4')
        saved_video_fps = getattr(self, 'video_fps', 20)
        saved_recording_active = getattr(self, 'recording_active', False)
        saved_video_frames = getattr(self, 'video_frames', [])
            
        MujocoEnv.__init__(
            self,
            xml_string,
            self.frame_skip,
            observation_space=None,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            render_mode="human" if self.render_on else "rgb_array",
            width=self.render_size[0],
            height=self.render_size[1],
        )
        
        # Restore render settings
        self.render_mode = saved_render_mode
        self.video_path = saved_video_path
        self.video_fps = saved_video_fps
        self.recording_active = saved_recording_active
        self.video_frames = saved_video_frames
        
        # Recreate EGL renderer if needed
        if self.render_mode == 'mp4':
            self.egl_renderer = None  # Force recreation
            self.preferred_camera_id = None  # Reset camera preference

    def render(self):
        """Render environment with different modes: 'none', 'viewer', 'mp4'."""
        if self.render_mode == 'none':
            # No rendering
            return None
            
        elif self.render_mode == 'viewer':
            # Use passive viewer with simulation loop
            if self._passive_viewer is None:
                # Initialize passive viewer on first call
                self._viewer_context_manager = mujoco.viewer.launch_passive(self.model, self.data)
                self._passive_viewer = self._viewer_context_manager.__enter__()
                print("Passive viewer initialized successfully")
            
            return None  # Passive viewer doesn't return frames
            
        elif self.render_mode == 'mp4':
            # EGL rendering for video recording
            self._capture_frame_egl()
        
        else:
            print(f"Warning: Unknown render mode '{self.render_mode}'. Using 'none'.")
            return None

    def close(self):
        """Close environment and cleanup resources."""
        # Stop any active video recording
        if hasattr(self, 'render_mode') and self.render_mode == 'mp4' and getattr(self, 'recording_active', False):
            self.stop_video_recording()
        
        # Cleanup passive viewer
        if hasattr(self, '_viewer_context_manager') and self._viewer_context_manager is not None:
            try:
                self._viewer_context_manager.__exit__(None, None, None)
            except:
                pass  # Ignore errors during cleanup
            finally:
                self._passive_viewer = None
                self._viewer_context_manager = None
        
        # Cleanup EGL renderer
        self._cleanup_egl_renderer()
        
        # Call parent close
        super().close()

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup

    def _get_available_cameras(self):
        """Get list of available cameras from the MuJoCo model."""
        if not hasattr(self, 'model') or self.model is None:
            return []
        
        cameras = []
        for i in range(self.model.ncam):
            camera_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_CAMERA, i)
            if camera_name:
                cameras.append({
                    'id': i,
                    'name': camera_name
                })
        return cameras

    def _get_preferred_camera(self):
        """Get the preferred camera for rendering, preferring XML-defined cameras."""
        cameras = self._get_available_cameras()
        
        if not cameras:
            # No cameras defined in XML, use default free camera
            return -1
        
        # Check if a specific camera is configured
        configured_camera = self.sim_cfg.get('render_camera', None)
        if configured_camera is not None:
            # Try to find camera by name or ID
            if isinstance(configured_camera, str):
                for camera in cameras:
                    if camera['name'] == configured_camera:
                        print(f"Using configured XML camera: {camera['name']} (ID: {camera['id']})")
                        return camera['id']
                print(f"Warning: Configured camera '{configured_camera}' not found")
            elif isinstance(configured_camera, int):
                if 0 <= configured_camera < len(cameras):
                    camera = cameras[configured_camera]
                    print(f"Using configured XML camera by ID: {camera['name']} (ID: {camera['id']})")
                    return configured_camera
                print(f"Warning: Configured camera ID {configured_camera} out of range")
        
        # Prefer cameras with specific names in order of preference
        preferred_names = ['follow_camera', 'main_camera', 'robot_camera', 'tracking_camera']
        
        for preferred_name in preferred_names:
            for camera in cameras:
                if preferred_name in camera['name'].lower():
                    print(f"Using XML camera: {camera['name']} (ID: {camera['id']})")
                    return camera['id']
        
        # If no preferred camera found, use the first available camera
        camera = cameras[0]
        print(f"Using first available XML camera: {camera['name']} (ID: {camera['id']})")
        return camera['id']

    def _add_metrics_overlay(self, frame):
        """Add text overlays with action, reward, and custom metrics."""
        if not getattr(self, 'video_show_metrics', True):
            return frame
            
        # Get current metrics
        # metrics = self._get_current_metrics()
        # np.array2string(self.state.action_history.last_action, precision=2, separator=',', suppress_small=True)
        metrics = {
            'Action': np.array2string(self.state.action_history.last_action, precision=2, separator=',', suppress_small=True),
            'Reward': f"{self.state.reward_history.last_reward:.2f}",
            "Speed": f"{self.state.speed[0]:.2f}",
            'Step': self.step_count,
            'Episode': self.episode_counter+1,
        }

        cmd_dict = self.state.command_manager.get_commands_dict()
        if cmd_dict:
            for key, value in cmd_dict.items():
                metrics["Cmd:"+key] = f"{value:.2f}" if isinstance(value, float) else str(value)

        if not metrics:
            return frame
        
        # Configure text appearance
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)  # White text
        thickness = 1
        line_height = 20
        start_y = 20
        
        # Draw semi-transparent background for better readability
        overlay = frame.copy()
        bg_height = len(metrics) * line_height + 10
        cv2.rectangle(overlay, (5, 5), (350, bg_height), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        for i, (label, value) in enumerate(metrics.items()):
            y_pos = start_y + (i * line_height)
            text = f"{label}: {value}"
            cv2.putText(frame, text, (10, y_pos), font, font_scale, color, thickness)

        return frame

    def do_simulation(self, ctrl, n_frames) -> None:
        """
        Step the simulation n number of frames and applying a control action.
        Integrates with passive viewer when in 'viewer' mode.
        """
        # Check control input is contained in the action space
        if np.array(ctrl).shape != (self.model.nu,):
            raise ValueError(
                f"Action dimension mismatch. Expected {(self.model.nu,)}, found {np.array(ctrl).shape}"
            )
        
        if self.render_mode == 'viewer' and self._passive_viewer is not None:
            # Use passive viewer with individual step control
            self.data.ctrl[:] = ctrl
            
            for i in range(n_frames):
                mujoco.mj_step(self.model, self.data)
                
                # Sync with viewer
                self._passive_viewer.sync()
                
                # Timing control - sleep for timestep duration
                # time.sleep(self.model.opt.timestep)
        else:
            # Standard simulation without viewer
            self._step_mujoco_simulation(ctrl, n_frames)
    
    def _step_mujoco_simulation(self, ctrl, n_frames):
        """
        Step over the MuJoCo simulation (standard implementation).
        """
        self.data.ctrl[:] = ctrl
        mujoco.mj_step(self.model, self.data, nstep=n_frames)
        
        # As of MuJoCo 2.0, force-related quantities like cacc are not computed
        # unless there's a force sensor in the model.
        mujoco.mj_rnePostConstraint(self.model, self.data)