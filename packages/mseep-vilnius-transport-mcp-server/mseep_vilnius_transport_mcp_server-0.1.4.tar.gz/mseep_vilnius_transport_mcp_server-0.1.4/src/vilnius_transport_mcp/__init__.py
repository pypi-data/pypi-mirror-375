from . import transport
import asyncio

def main():
    """Main entry point for the package."""
    asyncio.run(transport.main())

# Optionally expose other important items at package level
__all__ = ['main', 'transport']