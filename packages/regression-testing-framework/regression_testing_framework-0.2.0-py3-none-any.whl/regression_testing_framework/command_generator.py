from .config_parser import (
    load_config,
    get_test_config,
    get_base_command,
    get_test_names,
    process_params,
    process_environment
)

def generate_commands(config_path):
    """
    Generate command representations for dry-run display.
    These aren't the actual commands that will be executed,
    but rather a representation for the user to understand what will run.
    """
    # Load and parse the configuration
    config = load_config(config_path)
    test_names = get_test_names(config)
    
    # Generate command representations
    commands = []
    
    for test_name in test_names:
        test_config = get_test_config(config, test_name)
        
        if not isinstance(test_config, dict):
            commands.append(f"{test_name}: <Invalid configuration>")
            continue
            
        # Get test-specific base command or use global
        base_command = get_base_command(config, test_config)
        if not base_command:
            commands.append(f"{test_name}: <No command specified>")
            continue
            
        # Process parameters
        params = process_params(test_config)
        
        # Build command string
        cmd_str = base_command
        if params:
            cmd_str = f"{base_command} {' '.join(params)}"
        
        # Process environment variables for display
        env_vars = process_environment(test_config)
        env_str = ""
        if env_vars:
            env_vars_list = [f"{k}={v}" for k, v in env_vars.items()]
            env_str = " [Environment: " + ", ".join(env_vars_list) + "]"
        
        commands.append(f"{test_name}: {cmd_str}{env_str}")
    
    return commands
