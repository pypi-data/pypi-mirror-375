"""
Command-line interface for Pantheon Legends
"""

import sys
from .scaffold import setup_scanner_as_legend

def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        setup_scanner_as_legend()
    else:
        print("🏛️  Pantheon Legends Commands:")
        print("=" * 30)
        print("  python -m legends create                              - Convert scanner to legend")
        print("  python -c 'import legends; legends.test_installation()'  - Test installation")
        print("\n📚 Documentation: https://github.com/SpartanDigitalDotNet/pantheon-legends")

if __name__ == "__main__":
    main()
