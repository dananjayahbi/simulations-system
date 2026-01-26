#!/usr/bin/env python3
# launcher.py - Master launcher for all simulations
"""
Loops - Simulation Collection Launcher
=======================================
A collection of visual simulations using pygame.

Available Simulations:
1. Sorting Visualizer - Visualize Bubble, Quick, and Merge sort algorithms

Usage:
    python launcher.py [simulation_name]
    
    Without arguments: Shows menu to select simulation
    With argument: Directly launches the specified simulation
"""

import sys
import os

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Available simulations registry
SIMULATIONS = {
    "sorting": {
        "name": "Sorting Visualizer",
        "description": "Visualize Bubble, Quick, and Merge sort algorithms",
        "module": "simulations.sorting_visualizer",
        "entry": "main"
    },
    # Add more simulations here as they are created
    # "pendulum": {
    #     "name": "Pendulum Simulation",
    #     "description": "Physics-based pendulum simulation",
    #     "module": "simulations.pendulum",
    #     "entry": "main"
    # },
}


def run_simulation(sim_key):
    """Run a simulation by its key."""
    if sim_key not in SIMULATIONS:
        print(f"❌ Unknown simulation: {sim_key}")
        print(f"Available: {', '.join(SIMULATIONS.keys())}")
        return False
    
    sim = SIMULATIONS[sim_key]
    print(f"🚀 Launching: {sim['name']}")
    print(f"   {sim['description']}")
    print("-" * 50)
    
    # Change to simulation directory and run
    sim_dir = os.path.join(PROJECT_ROOT, "simulations", sim_key + "_visualizer")
    if not os.path.exists(sim_dir):
        # Try without _visualizer suffix
        sim_dir = os.path.join(PROJECT_ROOT, "simulations", sim_key)
    
    if sim_key == "sorting":
        sim_dir = os.path.join(PROJECT_ROOT, "simulations", "sorting_visualizer")
    
    os.chdir(sim_dir)
    
    # Import and run
    from simulations.sorting_visualizer.visualizer import SortingVisualizer
    visualizer = SortingVisualizer()
    visualizer.run()
    
    return True


def show_menu():
    """Display interactive menu for simulation selection."""
    print("=" * 50)
    print("  🔄 LOOPS - Simulation Collection")
    print("=" * 50)
    print()
    
    for i, (key, sim) in enumerate(SIMULATIONS.items(), 1):
        print(f"  [{i}] {sim['name']}")
        print(f"      {sim['description']}")
        print()
    
    print("  [Q] Quit")
    print()
    print("-" * 50)
    
    choice = input("Select simulation (number or name): ").strip().lower()
    
    if choice in ('q', 'quit', 'exit'):
        return None
    
    # Handle numeric choice
    if choice.isdigit():
        idx = int(choice) - 1
        keys = list(SIMULATIONS.keys())
        if 0 <= idx < len(keys):
            return keys[idx]
    
    # Handle name/key choice
    if choice in SIMULATIONS:
        return choice
    
    # Partial match
    for key in SIMULATIONS:
        if choice in key or choice in SIMULATIONS[key]['name'].lower():
            return key
    
    print(f"❌ Invalid choice: {choice}")
    return show_menu()


def main():
    """Main entry point."""
    # Direct launch if argument provided
    if len(sys.argv) > 1:
        sim_key = sys.argv[1].lower()
        run_simulation(sim_key)
        return
    
    # Interactive menu
    while True:
        choice = show_menu()
        if choice is None:
            print("👋 Goodbye!")
            break
        
        run_simulation(choice)
        print()
        input("Press Enter to return to menu...")
        print()


if __name__ == "__main__":
    main()
