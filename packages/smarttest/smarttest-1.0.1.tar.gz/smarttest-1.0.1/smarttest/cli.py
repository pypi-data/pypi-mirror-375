#!/usr/bin/env python3
"""
SmartTest Command Line Interface
Professional CLI for code testing and monitoring
"""

import sys
import argparse
from . import SmartTest

def main():
    parser = argparse.ArgumentParser(
        description="SmartTest - Intelligent Code Testing Library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  smarttest                    # Start monitoring
  smarttest --file test.py     # Check specific file
  smarttest --help             # Show this help
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Check specific file instead of monitoring'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='SmartTest 1.0.1'
    )
    
    args = parser.parse_args()
    
    if args.file:
        smarttest = SmartTest()
        results = smarttest.check_file(args.file)
        if results:
            print(f"Found {len(results)} errors in {args.file}")
            for error in results:
                print(f"  • {error}")
        else:
            print(f"✅ No errors found in {args.file}")
    else:
        smarttest = SmartTest()
        smarttest.start()
        
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\n👋 SmartTest stopped!")
            smarttest.stop()

if __name__ == "__main__":
    main()
