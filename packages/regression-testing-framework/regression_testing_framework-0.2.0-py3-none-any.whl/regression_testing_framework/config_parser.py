import yaml
from typing import Dict, Any, List, Optional

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load and parse a YAML configuration file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Dictionary with the parsed configuration
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_test_config(config: Dict[str, Any], test_name: str) -> Dict[str, Any]:
    """
    Get the configuration for a specific test.
    
    Args:
        config: The parsed configuration dictionary
        test_name: The name of the test to get the configuration for
        
    Returns:
        Dictionary with the test configuration or empty dict if not found
    """
    return config.get(test_name, {})

def get_base_command(config: Dict[str, Any], test_config: Dict[str, Any]) -> str:
    """
    Get the base command for a test, with test-specific command taking precedence.
    
    Args:
        config: The parsed configuration dictionary
        test_config: The test-specific configuration
        
    Returns:
        The base command to use for the test
    """
    # Prefer the direct command from test_config, without defaulting to /bin/bash
    return test_config.get('base_command', config.get('base_command', ''))

def get_test_names(config: Dict[str, Any]) -> List[str]:
    """
    Get the list of test names from the configuration.
    
    Args:
        config: The parsed configuration dictionary
        
    Returns:
        List of test names (excluding 'base_command' and 'tests')
    """
    # Exclude special keys that are not tests
    excluded_keys = ['base_command', 'tests']
    return [name for name in config.keys() if name not in excluded_keys]

def process_params(test_config: Dict[str, Any]) -> List[str]:
    """
    Process parameters for a test command.
    
    Args:
        test_config: The test-specific configuration
        
    Returns:
        List of command parameters exactly as provided in the config
    """
    if 'params' in test_config and isinstance(test_config['params'], list):
        return [str(param) for param in test_config['params']]
    return []

def process_environment(test_config: Dict[str, Any]) -> Dict[str, str]:
    """
    Process environment variables for a test.
    
    Args:
        test_config: The test-specific configuration
        
    Returns:
        Dictionary with environment variables to add to the current environment
    """
    env_vars = {}
    
    if 'environment' in test_config and isinstance(test_config['environment'], list):
        for env_var in test_config['environment']:
            if isinstance(env_var, str) and '=' in env_var:
                key, value = env_var.split('=', 1)
                env_vars[key] = value
            elif isinstance(env_var, dict):
                for key, value in env_var.items():
                    env_vars[key] = str(value)
    
    return env_vars