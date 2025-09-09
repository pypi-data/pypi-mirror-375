#!/usr/bin/env python3
import sys
import time

def main():
    # Print some normal output to stdout
    print("Starting test with multiple stderr warnings...")
    
    # Generate a few warnings to stderr
    print("First warning message to stderr", file=sys.stderr)
    time.sleep(0.5)  # Small delay to make warnings appear separately
    
    # Continue with normal execution
    print("Continuing normal execution...")
    
    # Generate another warning
    print("Second warning message to stderr", file=sys.stderr)
    time.sleep(0.5)
    
    # More normal output
    print("More normal output...")
    
    # Multiple consecutive warnings
    print("Third warning message to stderr", file=sys.stderr)
    print("Fourth warning message to stderr", file=sys.stderr)
    print("Fifth warning message to stderr", file=sys.stderr)
    
    # Final success message
    print("Test completed successfully!")
    
    # Exit with status code 0 (success)
    return 0

if __name__ == "__main__":
    sys.exit(main())