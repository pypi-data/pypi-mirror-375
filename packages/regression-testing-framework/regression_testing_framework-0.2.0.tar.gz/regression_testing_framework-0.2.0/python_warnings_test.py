#!/usr/bin/env python3
import warnings
import sys
import time

def function_with_deprecation_warning():
    warnings.warn("This function is deprecated and will be removed in a future version", 
                 DeprecationWarning, stacklevel=2)
    print("Function executed despite deprecation warning")

def function_with_user_warning():
    warnings.warn("This is a custom user warning", UserWarning)
    print("Function executed despite user warning")

def function_with_runtime_warning():
    warnings.warn("This is a runtime warning", RuntimeWarning)
    print("Function executed despite runtime warning")

def main():
    # Show all warnings (normally some may be filtered)
    warnings.filterwarnings("always")
    
    print("Starting test with Python warning module...")
    
    # Call functions that generate various warnings
    function_with_deprecation_warning()
    time.sleep(0.5)
    
    # Also write directly to stderr
    print("Direct stderr message between warnings", file=sys.stderr)
    time.sleep(0.5)
    
    function_with_user_warning()
    time.sleep(0.5)
    
    function_with_runtime_warning()
    
    # Final success message
    print("All Python warnings test completed successfully!")
    
    # Exit with success code
    return 0

if __name__ == "__main__":
    sys.exit(main())