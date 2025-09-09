# Copyright [2021-2025] Thanh Nguyen
# Copyright [2022-2023] [CNRS, Toward SAS]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pinocchio as pin
import numpy as np
from scipy import signal
import operator


def get_param_from_yaml(robot, identif_data):
    """Parse identification parameters from YAML configuration file.

    Extracts robot parameters, problem settings, signal processing options and total
    least squares parameters from a YAML config file.

    Args:
        robot (pin.RobotWrapper): Robot instance containing model
        identif_data (dict): YAML configuration containing:
            - robot_params: Joint limits, friction, inertia settings
            - problem_params: External wrench, friction, actuator settings
            - processing_params: Sample rate, filter settings
            - tls_params: Load mass and location

    Returns:
        dict: Parameter dictionary with unified settings

    Example:
        >>> config = yaml.safe_load(config_file)
        >>> params = get_param_from_yaml(robot, config)
        >>> print(params["nb_samples"])
    """

    # robot_name: anchor as a reference point for executing
    robot_name = robot.model.name

    robots_params = identif_data["robot_params"][0]
    problem_params = identif_data["problem_params"][0]
    process_params = identif_data["processing_params"][0]
    tls_params = identif_data["tls_params"][0]

    identif_config = {
        "robot_name": robot_name,
        "nb_samples": int(1 / (process_params["ts"])),
        "q_lim_def": robots_params["q_lim_def"],
        "dq_lim_def": robots_params["dq_lim_def"],
        "is_external_wrench": problem_params["is_external_wrench"],
        "is_joint_torques": problem_params["is_joint_torques"],
        "force_torque": problem_params["force_torque"],
        "external_wrench_offsets": problem_params["external_wrench_offsets"],
        "has_friction": problem_params["has_friction"],
        "fv": robots_params["fv"],
        "fs": robots_params["fs"],
        "has_actuator_inertia": problem_params["has_actuator_inertia"],
        "Ia": robots_params["Ia"],
        "has_joint_offset": problem_params["has_joint_offset"],
        "off": robots_params["offset"],
        "has_coupled_wrist": problem_params["has_coupled_wrist"],
        "Iam6": robots_params["Iam6"],
        "fvm6": robots_params["fvm6"],
        "fsm6": robots_params["fsm6"],
        "reduction_ratio": robots_params["reduction_ratio"],
        "ratio_essential": robots_params["ratio_essential"],
        "cut_off_frequency_butterworth": process_params[
            "cut_off_frequency_butterworth"
        ],
        "ts": process_params["ts"],
        "mass_load": tls_params["mass_load"],
        "which_body_loaded": tls_params["which_body_loaded"],
    }
    return identif_config


def unified_to_legacy_identif_config(robot, unified_identif_config) -> dict:
    """Convert unified identification format to legacy identif_config format.
    
    Maps the new unified identification configuration structure to produce
    the exact same output as get_param_from_yaml. This ensures backward
    compatibility while using the new unified parser.
    
    Args:
        robot (pin.RobotWrapper): Robot instance containing model and data
        unified_identif_config (dict): Configuration from create_task_config
        
    Returns:
        dict: Identification configuration matching get_param_from_yaml output
        
    Example:
        >>> unified_config = create_task_config(robot, parsed_config,
        ...                                    "identification")
        >>> legacy_config = unified_to_legacy_identif_config(robot,
        ...                                                  unified_config)
        >>> # legacy_config has same keys as get_param_from_yaml output
    """
    # Extract unified config sections
    mechanics = unified_identif_config.get("mechanics", {})
    joints = unified_identif_config.get("joints", {})
    problem = unified_identif_config.get("problem", {})
    coupling = unified_identif_config.get("coupling", {})
    signal_processing = unified_identif_config.get("signal_processing", {})
    
    # Get robot name
    robot_name = robot.model.name
    
    # Extract values from unified config with defaults
    joint_limits = joints.get("joint_limits", {})
    velocity_limits = joint_limits.get("velocity", [0.05] * 12)
    model_components = problem.get("model_components", {})
    ft_sensors = problem.get("force_torque_sensors", [])
    force_torque = ft_sensors[0] if ft_sensors else None
    
    # Get sampling parameters
    sampling_freq = signal_processing.get("sampling_frequency", 5000.0)
    ts = 1.0 / sampling_freq
    cutoff_freq = signal_processing.get("cutoff_frequency", 100.0)
    
    # Build the exact same structure as get_param_from_yaml returns
    identif_config = {
        "robot_name": robot_name,
        "nb_samples": int(1 / ts),  # Same calculation as get_param_from_yaml
        "q_lim_def": 1.57,  # Default joint position limit
        "dq_lim_def": velocity_limits,
        "is_external_wrench": problem.get("include_external_forces", False),
        "is_joint_torques": problem.get("use_joint_torques", True),
        "force_torque": force_torque,
        "external_wrench_offsets": problem.get(
            "external_wrench_offsets", False
        ),
        "has_friction": model_components.get("friction", True),
        "fv": mechanics.get("friction_coefficients", {}).get(
            "viscous", [0] * 12
        ),
        "fs": mechanics.get("friction_coefficients", {}).get(
            "static", [0] * 12
        ),
        "has_actuator_inertia": model_components.get("actuator_inertia", True),
        "Ia": mechanics.get("actuator_inertias", [0] * 12),
        "has_joint_offset": model_components.get("joint_offset", True),
        "off": mechanics.get("joint_offsets", [0] * 12),
        "has_coupled_wrist": coupling.get("has_coupled_wrist", True),
        "Iam6": coupling.get("Iam6", 0),
        "fvm6": coupling.get("fvm6", 0),
        "fsm6": coupling.get("fsm6", 0),
        "reduction_ratio": mechanics.get(
            "reduction_ratios", [32.0, 32.0, 45.0, -48.0, 45.0, 32.0]
        ),
        "ratio_essential": mechanics.get("ratio_essential", 30.0),
        "cut_off_frequency_butterworth": cutoff_freq,
        "ts": ts,
        "mass_load": 0.0,  # Default: no external mass
        "which_body_loaded": 0.0,  # Default: no external load
    }
    
    return identif_config


def base_param_from_standard(phi_standard, params_base):
    """Convert standard parameters to base parameters.

    Takes standard dynamic parameters and calculates the corresponding base
    parameters using analytical relationships between them.

    Args:
        phi_standard (dict): Standard parameters from model/URDF
        params_base (list): Analytical parameter relationships

    Returns:
        list: Base parameter values calculated from standard parameters
    """
    phi_base = []
    ops = {"+": operator.add, "-": operator.sub}
    for ii in range(len(params_base)):
        param_base_i = params_base[ii].split(" ")
        values = []
        list_ops = []
        for jj in range(len(param_base_i)):
            param_base_j = param_base_i[jj].split("*")
            if len(param_base_j) == 2:
                value = float(param_base_j[0]) * phi_standard[param_base_j[1]]
                values.append(value)
            elif param_base_j[0] != "+" and param_base_j[0] != "-":
                value = phi_standard[param_base_j[0]]
                values.append(value)
            else:
                list_ops.append(ops[param_base_j[0]])
        value_phi_base = values[0]
        for kk in range(len(list_ops)):
            value_phi_base = list_ops[kk](value_phi_base, values[kk + 1])
        phi_base.append(value_phi_base)
    return phi_base


def relative_stdev(W_b, phi_b, tau):
    """Calculate relative standard deviation of identified parameters.

    Implements the residual error method from [Pressé & Gautier 1991] to
    estimate parameter uncertainty.

    Args:
        W_b (ndarray): Base regressor matrix
        phi_b (list): Base parameter values
        tau (ndarray): Measured joint torques/forces

    Returns:
        ndarray: Relative standard deviation (%) for each base parameter
    """
    # stdev of residual error ro
    sig_ro_sqr = np.linalg.norm((tau - np.dot(W_b, phi_b))) ** 2 / (
        W_b.shape[0] - phi_b.shape[0]
    )

    # covariance matrix of estimated parameters
    C_x = sig_ro_sqr * np.linalg.inv(np.dot(W_b.T, W_b))

    # relative stdev of estimated parameters
    std_x_sqr = np.diag(C_x)
    std_xr = np.zeros(std_x_sqr.shape[0])
    for i in range(std_x_sqr.shape[0]):
        std_xr[i] = np.round(100 * np.sqrt(std_x_sqr[i]) / np.abs(phi_b[i]), 2)

    return std_xr


def index_in_base_params(params, id_segments):
    """Map segment IDs to their base parameters.

    For each segment ID, finds which base parameters contain inertial
    parameters from that segment.

    Args:
        params (list): Base parameter expressions
        id_segments (list): Segment IDs to map

    Returns:
        dict: Maps segment IDs to lists of base parameter indices
    """
    base_index = []
    params_name = [
        "Ixx",
        "Ixy",
        "Ixz",
        "Iyy",
        "Iyz",
        "Izz",
        "mx",
        "my",
        "mz",
        "m",
    ]

    id_segments_new = [i for i in range(len(id_segments))]

    for id in id_segments:
        for ii in range(len(params)):
            param_base_i = params[ii].split(" ")
            for jj in range(len(param_base_i)):
                param_base_j = param_base_i[jj].split("*")
                for ll in range(len(param_base_j)):
                    for kk in params_name:
                        if kk + str(id) == param_base_j[ll]:
                            base_index.append((id, ii))

    base_index[:] = list(set(base_index))
    base_index = sorted(base_index)

    dictio = {}

    for i in base_index:
        dictio.setdefault(i[0], []).append(i[1])

    values = []
    for ii in dictio:
        values.append(dictio[ii])

    return dict(zip(id_segments_new, values))


def weigthed_least_squares(robot, phi_b, W_b, tau_meas, tau_est, identif_config):
    """Compute weighted least squares solution for parameter identification.

    Implements iteratively reweighted least squares method from
    [Gautier, 1997]. Accounts for heteroscedastic noise.

    Args:
        robot (pin.Robot): Robot model
        phi_b (ndarray): Initial base parameters
        W_b (ndarray): Base regressor matrix
        tau_meas (ndarray): Measured joint torques
        tau_est (ndarray): Estimated joint torques
        param (dict): Settings including idx_tau_stop

    Returns:
        ndarray: Identified base parameters
    """
    sigma = np.zeros(robot.model.nq)  # For ground reaction force model
    P = np.zeros((len(tau_meas), len(tau_meas)))
    nb_samples = int(identif_config["idx_tau_stop"][0])
    start_idx = int(0)
    for ii in range(robot.model.nq):
        tau_slice = slice(int(start_idx), int(identif_config["idx_tau_stop"][ii]))
        diff = tau_meas[tau_slice] - tau_est[tau_slice]
        denom = len(tau_meas[tau_slice]) - len(phi_b)
        sigma[ii] = np.linalg.norm(diff) / denom

        start_idx = identif_config["idx_tau_stop"][ii]

        for jj in range(nb_samples):
            idx = jj + ii * nb_samples
            P[idx, idx] = 1 / sigma[ii]

        phi_b = np.matmul(
            np.linalg.pinv(np.matmul(P, W_b)), np.matmul(P, tau_meas)
        )

    phi_b = np.around(phi_b, 6)

    return phi_b


def calculate_first_second_order_differentiation(model, q, identif_config, dt=None):
    """Calculate joint velocities and accelerations from positions.

    Computes first and second order derivatives of joint positions using central
    differences. Handles both constant and variable timesteps.

    Args:
        model (pin.Model): Robot model
        q (ndarray): Joint position matrix (n_samples, n_joints)
        param (dict): Parameters containing:
            - is_joint_torques: Whether using joint torques
            - is_external_wrench: Whether using external wrench
            - ts: Timestep if constant
        dt (ndarray, optional): Variable timesteps between samples.

    Returns:
        tuple:
            - q (ndarray): Trimmed position matrix
            - dq (ndarray): Joint velocity matrix
            - ddq (ndarray): Joint acceleration matrix

    Note:
        Two samples are removed from start/end due to central differences
    """

    if identif_config["is_joint_torques"]:
        dq = np.zeros([q.shape[0] - 1, q.shape[1]])
        ddq = np.zeros([q.shape[0] - 1, q.shape[1]])

    if identif_config["is_external_wrench"]:
        dq = np.zeros([q.shape[0] - 1, q.shape[1] - 1])
        ddq = np.zeros([q.shape[0] - 1, q.shape[1] - 1])

    if dt is None:
        dt = identif_config["ts"]
        for ii in range(q.shape[0] - 1):
            dq[ii, :] = pin.difference(model, q[ii, :], q[ii + 1, :]) / dt

        for jj in range(model.nq - 1):
            ddq[:, jj] = np.gradient(dq[:, jj], edge_order=1) / dt
    else:
        for ii in range(q.shape[0] - 1):
            dq[ii, :] = pin.difference(model, q[ii, :], q[ii + 1, :]) / dt[ii]

        for jj in range(model.nq - 1):
            ddq[:, jj] = np.gradient(dq[:, jj], edge_order=1) / dt

    q = np.delete(q, len(q) - 1, 0)
    q = np.delete(q, len(q) - 1, 0)

    dq = np.delete(dq, len(dq) - 1, 0)
    ddq = np.delete(ddq, len(ddq) - 1, 0)

    return q, dq, ddq


def low_pass_filter_data(data, identif_config, nbutter=5):
    """Apply zero-phase Butterworth low-pass filter to measurement data.

    Uses scipy's filtfilt for zero-phase digital filtering. Removes high
    frequency noise while preserving signal phase. Handles border effects by
    trimming filtered data.

    Args:
        data (ndarray): Raw measurement data to filter
        param (dict): Filter parameters containing:
            - ts: Sample time
            - cut_off_frequency_butterworth: Cutoff frequency in Hz
        nbutter (int, optional): Filter order. Higher order gives sharper
            frequency cutoff. Defaults to 5.

    Returns:
        ndarray: Filtered data with border regions removed

    Note:
        Border effects are handled by removing nborder = 5*nbutter samples
        from start and end of filtered signal.
    """
    cutoff = identif_config["ts"] * identif_config["cut_off_frequency_butterworth"] / 2
    b, a = signal.butter(nbutter, cutoff, "low")

    padlen = 3 * (max(len(b), len(a)) - 1)
    data = signal.filtfilt(b, a, data, axis=0, padtype="odd", padlen=padlen)

    # Remove border effects
    nbord = 5 * nbutter
    data = np.delete(data, np.s_[0:nbord], axis=0)
    end_slice = slice(data.shape[0] - nbord, data.shape[0])
    data = np.delete(data, end_slice, axis=0)

    return data


def reorder_inertial_parameters(pinocchio_params):
    """Reorder inertial parameters from Pinocchio format to desired format.
    
    Args:
        pinocchio_params: Parameters in Pinocchio order
            [m, mx, my, mz, Ixx, Ixy, Iyy, Ixz, Iyz, Izz]
        
    Returns:
        list: Parameters in desired order
            [Ixx, Ixy, Ixz, Iyy, Iyz, Izz, mx, my, mz, m]
    """
    if len(pinocchio_params) != 10:
        raise ValueError(
            f"Expected 10 inertial parameters, got {len(pinocchio_params)}"
        )
    
    # Mapping from Pinocchio indices to desired indices
    reordered = np.zeros_like(pinocchio_params)
    reordered[0] = pinocchio_params[4]  # Ixx
    reordered[1] = pinocchio_params[5]  # Ixy
    reordered[2] = pinocchio_params[7]  # Ixz
    reordered[3] = pinocchio_params[6]  # Iyy
    reordered[4] = pinocchio_params[8]  # Iyz
    reordered[5] = pinocchio_params[9]  # Izz
    reordered[6] = pinocchio_params[1]  # mx
    reordered[7] = pinocchio_params[2]  # my
    reordered[8] = pinocchio_params[3]  # mz
    reordered[9] = pinocchio_params[0]  # m
    
    return reordered.tolist()


def add_standard_additional_parameters(phi, params, identif_config, model):
    """Add standard additional parameters (actuator inertia, friction,
    offsets).
    
    Args:
        phi: Current parameter values list
        params: Current parameter names list
        identif_config: Configuration dictionary
        model: Robot model
        
    Returns:
        tuple: Updated (phi, params) lists
    """
    num_joints = len(model.inertias) - 1  # Exclude world link
    
    # Standard additional parameters configuration
    additional_params = [
        {
            'name': 'Ia',
            'enabled_key': 'has_actuator_inertia',
            'values_key': 'Ia',
            'default': 0.0,
            'description': 'actuator inertia'
        },
        {
            'name': 'fv',
            'enabled_key': 'has_friction',
            'values_key': 'fv',
            'default': 0.0,
            'description': 'viscous friction'
        },
        {
            'name': 'fs',
            'enabled_key': 'has_friction',
            'values_key': 'fs',
            'default': 0.0,
            'description': 'static friction'
        },
        {
            'name': 'off',
            'enabled_key': 'has_joint_offset',
            'values_key': 'off',
            'default': 0.0,
            'description': 'joint offset'
        }
    ]
    
    for link_idx in range(1, num_joints + 1):
        for param_def in additional_params:
            param_name = f"{param_def['name']}{link_idx}"
            params.append(param_name)
            
            # Get parameter value
            if identif_config.get(param_def['enabled_key'], False):
                try:
                    values_list = identif_config.get(param_def['values_key'], [])
                    if len(values_list) >= link_idx:
                        value = values_list[link_idx - 1]
                    else:
                        value = param_def['default']
                        print(f"Warning: Missing {param_def['description']} "
                              f"for joint {link_idx}, using default: {value}")
                except (KeyError, IndexError, TypeError) as e:
                    value = param_def['default']
                    print(f"Warning: Error getting {param_def['description']} "
                          f"for joint {link_idx}: {e}, using default: {value}")
            else:
                value = param_def['default']
            
            phi.append(value)
    
    return phi, params


def add_custom_parameters(phi, params, custom_params, model):
    """Add custom user-defined parameters.
    
    Args:
        phi: Current parameter values list
        params: Current parameter names list
        custom_params: Custom parameter definitions
        model: Robot model
        
    Returns:
        tuple: Updated (phi, params) lists
    """
    num_joints = len(model.inertias) - 1  # Exclude world link
    
    for param_name, param_def in custom_params.items():
        if not isinstance(param_def, dict):
            print(f"Warning: Invalid custom parameter definition for "
                  f"'{param_name}', skipping")
            continue
            
        values = param_def.get('values', [])
        per_joint = param_def.get('per_joint', True)
        default_value = param_def.get('default', 0.0)
        
        if per_joint:
            # Add parameter for each joint
            for link_idx in range(1, num_joints + 1):
                param_full_name = f"{param_name}{link_idx}"
                params.append(param_full_name)
                
                try:
                    if len(values) >= link_idx:
                        value = values[link_idx - 1]
                    else:
                        value = default_value
                        # Only warn if values were provided but insufficient
                        if values:
                            print(f"Warning: Missing value for custom "
                                  f"parameter '{param_name}' joint "
                                  f"{link_idx}, using default: {value}")
                except (IndexError, TypeError):
                    value = default_value
                    print(f"Warning: Error accessing custom parameter "
                          f"'{param_name}' for joint {link_idx}, "
                          f"using default: {value}")
                
                phi.append(value)
        else:
            # Global parameter (not per joint)
            params.append(param_name)
            try:
                value = values[0] if values else default_value
            except (IndexError, TypeError):
                value = default_value
                print(f"Warning: Error accessing global custom parameter "
                      f"'{param_name}', using default: {value}")
            
            phi.append(value)
    
    return phi, params


def get_standard_parameters(model, identif_config=None, include_additional=True,
                            custom_params=None):
    """Get standard inertial parameters from robot model with extensible
    parameter support.
    
    Args:
        model: Robot model (Pinocchio model)
        param (dict, optional): Dictionary of parameter settings for
            additional parameters. Expected keys:
            - has_actuator_inertia (bool): Include actuator inertia parameters
            - has_friction (bool): Include friction parameters
            - has_joint_offset (bool): Include joint offset parameters
            - Ia (list): Actuator inertia values
            - fv (list): Viscous friction coefficients
            - fs (list): Static friction coefficients
            - off (list): Joint offset values
        include_additional (bool): Whether to include additional parameters
            beyond inertial
        custom_params (dict, optional): Custom parameter definitions
            Format: {param_name: {values: list, per_joint: bool,
            default: float}}
            
    Returns:
        dict: Parameter names mapped to their values
        
    Examples:
        # Basic usage - only inertial parameters
        params = get_standard_parameters(robot.model)
        
        # Include standard additional parameters
        identif_config = {
            'has_actuator_inertia': True,
            'has_friction': True,
            'Ia': [0.1, 0.2, 0.3],
            'fv': [0.01, 0.02, 0.03],
            'fs': [0.001, 0.002, 0.003]
        }
        params = get_standard_parameters(robot.model, identif_config)
        
        # Add custom parameters
        custom = {
            'gear_ratio': {'values': [100, 50, 25], 'per_joint': True,
                          'default': 1.0},
            'temperature': {'values': [20.0], 'per_joint': False,
                           'default': 25.0}
        }
        params = get_standard_parameters(robot.model, identif_config,
                                        custom_params=custom)
    """
    if identif_config is None:
        identif_config = {}
    
    if custom_params is None:
        custom_params = {}
    
    phi = []
    params = []
    
    # Standard inertial parameter names in desired order
    inertial_params = [
        "Ixx", "Ixy", "Ixz", "Iyy", "Iyz", "Izz",
        "mx", "my", "mz", "m"
    ]
    
    # Extract and rearrange inertial parameters for each link
    for link_idx in range(1, len(model.inertias)):
        # Get dynamic parameters from Pinocchio (in Pinocchio order)
        pinocchio_params = model.inertias[link_idx].toDynamicParameters()
        
        # Rearrange from Pinocchio order [m, mx, my, mz, Ixx, Ixy, Iyy, Ixz,
        # Iyz, Izz] to desired order [Ixx, Ixy, Ixz, Iyy, Iyz, Izz, mx, my,
        # mz, m]
        reordered_params = reorder_inertial_parameters(pinocchio_params)
        
        # Add parameter names and values
        for param_name in inertial_params:
            params.append(f"{param_name}{link_idx}")
        phi.extend(reordered_params)
    
    # Add additional standard parameters if requested
    if include_additional:
        phi, params = add_standard_additional_parameters(
            phi, params, identif_config, model
        )
    
    # Add custom parameters if provided
    if custom_params:
        phi, params = add_custom_parameters(phi, params, custom_params, model)
    
    return dict(zip(params, phi))


def get_parameter_info():
    """Get information about available parameter types.
    
    Returns:
        dict: Information about standard and custom parameter types
    """
    return {
        'inertial_parameters': [
            "Ixx", "Ixy", "Ixz", "Iyy", "Iyz", "Izz",
            "mx", "my", "mz", "m"
        ],
        'standard_additional': {
            'actuator_inertia': {
                'name': 'Ia',
                'enabled_key': 'has_actuator_inertia',
                'values_key': 'Ia',
                'description': 'Actuator/rotor inertia'
            },
            'viscous_friction': {
                'name': 'fv',
                'enabled_key': 'has_friction',
                'values_key': 'fv',
                'description': 'Viscous friction coefficient'
            },
            'static_friction': {
                'name': 'fs',
                'enabled_key': 'has_friction',
                'values_key': 'fs',
                'description': 'Static friction coefficient'
            },
            'joint_offset': {
                'name': 'off',
                'enabled_key': 'has_joint_offset',
                'values_key': 'off',
                'description': 'Joint position offset'
            }
        },
        'custom_parameters_format': {
            'parameter_name': {
                'values': 'list of values',
                'per_joint': 'boolean - if True, creates param for each joint',
                'default': 'default value if not enough values provided'
            }
        }
    }


# Backward compatibility wrapper for get_param_from_yaml
def get_param_from_yaml_legacy(robot, identif_data) -> dict:
    """Legacy identification parameter parser - kept for backward compatibility.
    
    This is the original implementation. New code should use the unified
    config parser from figaroh.utils.config_parser.
    
    Args:
        robot: Robot instance
        identif_data: Identification data dictionary
        
    Returns:
        Identification configuration dictionary
    """
    # Keep the original implementation here for compatibility
    return get_param_from_yaml(robot, identif_data)


# Import the new unified parser as the default
try:
    from ..utils.config_parser import (
        get_param_from_yaml as unified_get_param_from_yaml
    )
    
    # Replace the function with unified version while maintaining signature
    def get_param_from_yaml_unified(robot, identif_data) -> dict:
        """Enhanced parameter parser using unified configuration system.
        
        This function provides backward compatibility while using the new
        unified configuration parser when possible.
        
        Args:
            robot: Robot instance
            identif_data: Configuration data (dict or file path)
            
        Returns:
            Identification configuration dictionary
        """
        try:
            return unified_get_param_from_yaml(
                robot, identif_data, "identification"
            )
        except Exception as e:
            # Fall back to legacy parser if unified parser fails
            import warnings
            warnings.warn(
                f"Unified parser failed ({e}), falling back to legacy parser. "
                "Consider updating your configuration format.",
                UserWarning
            )
            return get_param_from_yaml_legacy(robot, identif_data)
    
    # Keep the old function available but with warning
    def get_param_from_yaml_with_warning(robot, identif_data) -> dict:
        """Original function with deprecation notice."""
        import warnings
        warnings.warn(
            "Direct use of get_param_from_yaml is deprecated. "
            "Consider using the unified config parser from "
            "figaroh.utils.config_parser",
            DeprecationWarning,
            stacklevel=2
        )
        return get_param_from_yaml_unified(robot, identif_data)
        
except ImportError:
    # If unified parser is not available, keep using original function
    pass

