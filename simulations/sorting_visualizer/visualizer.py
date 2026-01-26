# visualizer.py - Main visualizer class for sorting animation
import pygame
import random
import os
import sys

# Add current directory to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, NUM_BARS, BAR_WIDTH,
    BACKGROUND_COLOR, FRAMES_FOLDER, SAVE_FRAMES,
    DEFAULT_SPEED, MIN_SPEED, MAX_SPEED, SPEED_INCREMENT, ALGORITHMS
)
from colors import get_rainbow_color
from sorting_algorithms import ALGORITHM_MAP


class SortingVisualizer:
    """Main class for sorting algorithm visualization."""
    
    def __init__(self, settings=None):
        """
        Initialize the visualizer.
        
        Args:
            settings: Optional dict with runtime settings from control panel:
                - ALGORITHM: Starting algorithm name
                - SPEED: Starting speed
                - NUM_BARS: Number of bars to display
                - SAVE_FRAMES: Whether to save frames
                - AUTO_START: Whether to auto-start sorting
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sorting Algorithm Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        
        # Apply settings from control panel if provided
        settings = settings or {}
        self.num_bars = settings.get('NUM_BARS', NUM_BARS)
        self.save_frames_enabled = settings.get('SAVE_FRAMES', SAVE_FRAMES)
        self.auto_start = settings.get('AUTO_START', False)
        
        # Calculate bar width based on number of bars
        self.bar_width = WINDOW_WIDTH // self.num_bars
        
        # Initialize array with values
        self.array = list(range(1, self.num_bars + 1))
        self.max_value = max(self.array)
        
        # State tracking
        self.current_algorithm = settings.get('ALGORITHM', "Bubble Sort")
        self.algorithm_index = ALGORITHMS.index(self.current_algorithm) if self.current_algorithm in ALGORITHMS else 0
        self.sorting = False
        self.sort_generator = None
        self.highlighted = (-1, -1)
        
        # Speed control
        self.speed = settings.get('SPEED', DEFAULT_SPEED)
        self.in_menu = not self.auto_start  # Skip menu if auto-starting
        
        # Recording
        self.recording = False
        self.frame_count = 0
        self._setup_frames_folder()
    
    def _setup_frames_folder(self):
        """Create frames folder if it doesn't exist."""
        if self.save_frames_enabled and not os.path.exists(FRAMES_FOLDER):
            os.makedirs(FRAMES_FOLDER)
    
    def scramble_array(self):
        """Randomly shuffle the array."""
        random.shuffle(self.array)
        self.sorting = False
        self.sort_generator = None
        self.highlighted = (-1, -1)
    
    def start_sorting(self, algorithm_name):
        """Initialize sorting with the specified algorithm."""
        self.current_algorithm = algorithm_name
        algorithm_func = ALGORITHM_MAP.get(algorithm_name)
        if algorithm_func:
            self.sort_generator = algorithm_func(self.array.copy())
            self.array = list(range(1, self.num_bars + 1))
            random.shuffle(self.array)
            self.sort_generator = algorithm_func(self.array)
            self.sorting = True
            self.frame_count = 0
            self.recording = self.save_frames_enabled  # Start recording if enabled
    
    def draw_bars(self, for_recording=False):
        """Draw all bars with rainbow colors."""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Use full height during sorting/recording (no space for UI)
        # Only reserve space for UI in menu mode
        if for_recording or not self.in_menu:
            bar_height_unit = (WINDOW_HEIGHT - 20) / self.max_value
            y_offset = 10
        else:
            bar_height_unit = (WINDOW_HEIGHT - 100) / self.max_value
            y_offset = 50
        
        for i, value in enumerate(self.array):
            # Calculate bar dimensions
            x = i * self.bar_width
            height = int(value * bar_height_unit)
            y = WINDOW_HEIGHT - height - y_offset
            
            # Get rainbow color based on value
            color = get_rainbow_color(value, self.max_value)
            
            # Highlight compared bars
            if i in self.highlighted:
                color = (255, 255, 255)  # White highlight
            
            pygame.draw.rect(self.screen, color, (x, y, self.bar_width - 1, height))
    
    def draw_ui(self, show_controls=True):
        """Draw UI elements (algorithm name, controls info)."""
        # Algorithm name and speed - only show when in menu
        if self.in_menu:
            text = self.font.render(f"Algorithm: {self.current_algorithm}", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))
            
            speed_text = self.font.render(f"Speed: {self.speed}x", True, (100, 255, 100))
            self.screen.blit(speed_text, (10, 40))
        
        # Recording indicator - only for user display, never during recording
        if self.recording and not show_controls:
            pass  # Don't show REC indicator in final display either
        elif self.recording:
            rec_text = self.font.render("● REC", True, (255, 50, 50))
            self.screen.blit(rec_text, (WINDOW_WIDTH - 80, 10))
        
        # Controls - only show in menu mode
        if show_controls and self.in_menu:
            controls = "UP/DOWN: Select Algorithm | SPACE: Start | +/-: Speed | ESC: Quit"
            ctrl_text = self.font.render(controls, True, (180, 180, 180))
            self.screen.blit(ctrl_text, (10, WINDOW_HEIGHT - 35))
    
    def draw_menu(self):
        """Draw algorithm selection menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.SysFont('Arial', 48)
        title = title_font.render("Select Sorting Algorithm", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Algorithm options
        menu_font = pygame.font.SysFont('Arial', 36)
        for i, algo in enumerate(ALGORITHMS):
            color = (100, 255, 100) if i == self.algorithm_index else (180, 180, 180)
            prefix = "> " if i == self.algorithm_index else "  "
            algo_text = menu_font.render(f"{prefix}{algo}", True, color)
            algo_rect = algo_text.get_rect(center=(WINDOW_WIDTH // 2, 280 + i * 60))
            self.screen.blit(algo_text, algo_rect)
        
        # Speed display
        speed_info = self.font.render(f"Speed: {self.speed}x (Use +/- to adjust)", True, (255, 200, 100))
        speed_rect = speed_info.get_rect(center=(WINDOW_WIDTH // 2, 500))
        self.screen.blit(speed_info, speed_rect)
        
        # Instructions
        instr = self.font.render("Press SPACE to start sorting", True, (150, 150, 150))
        instr_rect = instr.get_rect(center=(WINDOW_WIDTH // 2, 580))
        self.screen.blit(instr, instr_rect)
    
    def save_frame(self):
        """Save current frame as PNG - only the simulation, no UI."""
        if self.recording and SAVE_FRAMES:
            # Draw bars only (for_recording=True means no UI space reserved)
            self.draw_bars(for_recording=True)
            filename = os.path.join(FRAMES_FOLDER, f"frame_{self.frame_count:06d}.png")
            pygame.image.save(self.screen, filename)
            self.frame_count += 1
            # Redraw with UI for display (will be drawn in main loop anyway)
    
    def update_sorting(self):
        """Advance sorting by speed steps per frame."""
        if self.sorting and self.sort_generator:
            for _ in range(self.speed):
                try:
                    self.array, idx1, idx2 = next(self.sort_generator)
                    self.highlighted = (idx1, idx2)
                except StopIteration:
                    self.sorting = False
                    self.highlighted = (-1, -1)
                    # Save final sorted frame before stopping recording
                    if self.recording:
                        self.draw_bars(for_recording=True)
                        filename = os.path.join(FRAMES_FOLDER, f"frame_{self.frame_count:06d}.png")
                        pygame.image.save(self.screen, filename)
                        self.frame_count += 1
                        self.recording = False
                    break
    
    def handle_events(self):
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.in_menu:
                        return False
                    else:
                        self.in_menu = True
                        self.sorting = False
                        self.recording = False
                
                # Speed controls (work anytime)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.speed = min(self.speed + SPEED_INCREMENT, MAX_SPEED)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed = max(self.speed - SPEED_INCREMENT, MIN_SPEED)
                
                # Menu mode controls
                elif self.in_menu:
                    if event.key == pygame.K_UP:
                        self.algorithm_index = (self.algorithm_index - 1) % len(ALGORITHMS)
                        self.current_algorithm = ALGORITHMS[self.algorithm_index]
                    elif event.key == pygame.K_DOWN:
                        self.algorithm_index = (self.algorithm_index + 1) % len(ALGORITHMS)
                        self.current_algorithm = ALGORITHMS[self.algorithm_index]
                    elif event.key == pygame.K_SPACE:
                        self.in_menu = False
                        self.scramble_array()
                        self.start_sorting(self.current_algorithm)
                
                # Visualization mode controls
                else:
                    if event.key == pygame.K_SPACE and not self.sorting:
                        self.start_sorting(self.current_algorithm)
                    elif event.key == pygame.K_r and not self.sorting:
                        self.scramble_array()
                    elif event.key == pygame.K_m and not self.sorting:
                        self.in_menu = True
                    elif event.key == pygame.K_1 and not self.sorting:
                        self.current_algorithm = "Bubble Sort"
                        self.algorithm_index = 0
                    elif event.key == pygame.K_2 and not self.sorting:
                        self.current_algorithm = "Quick Sort"
                        self.algorithm_index = 1
                    elif event.key == pygame.K_3 and not self.sorting:
                        self.current_algorithm = "Merge Sort"
                        self.algorithm_index = 2
        
        return True
    
    def run(self):
        """Main visualization loop."""
        running = True
        self.scramble_array()  # Start with scrambled array
        
        # Auto-start if launched from control panel
        if self.auto_start:
            self.start_sorting(self.current_algorithm)
        
        while running:
            running = self.handle_events()
            
            # Update sorting state (only if not in menu)
            if not self.in_menu:
                self.update_sorting()
            
            # Draw everything
            self.draw_bars()
            self.draw_ui()
            
            # Draw menu overlay if in menu mode
            if self.in_menu:
                self.draw_menu()
            
            # Save frame if recording
            if self.recording:
                self.save_frame()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
