#!/usr/bin/env python
import sys
import cowsay

def main():
    """Simple script to use cowsay with command line arguments"""
    message = "Hello World"
    if len(sys.argv) > 1:
        message = sys.argv[1]
    
    # Print the message using cowsay
    cowsay.cow(message)

if __name__ == "__main__":
    main()