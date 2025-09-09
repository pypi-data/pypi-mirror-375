#!/usr/bin/env python3
"""
Basic validation script for the regression testing framework.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that basic imports work."""
    try:
        print("Testing basic imports...")
        
        # Test CLI imports
        from regression_testing_framework.cli import cli
        print("✓ CLI imports successfully")
        
        # Test Celery imports
        from regression_testing_framework.celery_app import celery_app
        print("✓ Celery app imports successfully")
        
        # Test web imports (only if web dependencies are available)
        try:
            from regression_testing_framework.web.main import create_app
            print("✓ Web interface imports successfully")
        except ImportError as e:
            print(f"⚠ Web interface not available: {e}")
        
        print("\n✅ All core imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_docker_setup():
    """Test Docker setup."""
    dockerfile = Path("Dockerfile")
    compose_basic = Path("docker-compose.yml")
    compose_web = Path("docker-compose.web.yml")
    
    print("\nTesting Docker setup...")
    
    if dockerfile.exists():
        print("✓ Dockerfile exists")
    else:
        print("❌ Dockerfile missing")
        
    if compose_basic.exists():
        print("✓ docker-compose.yml exists")
    else:
        print("❌ docker-compose.yml missing")
        
    if compose_web.exists():
        print("✓ docker-compose.web.yml exists")
    else:
        print("❌ docker-compose.web.yml missing")

def test_config_files():
    """Test configuration files."""
    print("\nTesting configuration files...")
    
    config_files = list(Path(".").glob("*.yaml")) + list(Path(".").glob("*.yml"))
    if config_files:
        print(f"✓ Found {len(config_files)} configuration files:")
        for config in config_files:
            print(f"  - {config}")
    else:
        print("⚠ No YAML configuration files found")
    
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        print("✓ pyproject.toml exists")
    else:
        print("❌ pyproject.toml missing")

def main():
    """Run all validation tests."""
    print("🧪 Reggie Validation Script")
    print("=" * 40)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Run tests
    imports_ok = test_imports()
    test_docker_setup()
    test_config_files()
    
    print("\n" + "=" * 40)
    if imports_ok:
        print("✅ Validation completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -e .")
        print("2. Start Redis: docker run -d -p 6379:6379 redis")
        print("3. Start workers: reggie worker")
        print("4. Run tests: reggie run config.yaml")
        print("5. Start web (optional): reggie web")
        sys.exit(0)
    else:
        print("❌ Validation failed - fix import errors first")
        sys.exit(1)

if __name__ == "__main__":
    main()