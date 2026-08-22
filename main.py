"""
Sports Dashboard Application Entry Point.
Launches the 100% Free Football Game Center desktop application.
"""

import sys
from ui.app import SportsDashboardApp


def main():
    """Initializes and runs the GUI application."""
    print("=" * 60)
    print("🏈 Launching 100% Free Football Dashboard (NFL & CFB)")
    print("=" * 60)
    print("• Free Tier Defense: Active (Rate Throttling & SQLite Cache)")
    print("• UI Framework: CustomTkinter (Theme Customizable)")
    print("=" * 60)

    try:
        app = SportsDashboardApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
