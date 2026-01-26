# comparison_visualizer.py - Side-by-side comparison of sorting algorithms
import pygame
import random
import os
import sys

# Add current directory to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BACKGROUND_COLOR, FRAMES_FOLDER
from colors import get_rainbow_color
from sorting_algorithms import ALGORITHM_MAP

# 4:5 aspect ratio window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 1000
FPS = 60


class ComparisonVisualizer:
    """Side-by-side comparison of multiple sorting algorithms."""
    
    def __init__(self, settings=None):
        """
        Initialize the comparison visualizer.
        
        Args:
            settings: Dict with runtime settings:
                - ALGORITHMS: List of algorithm names to compare
                - SPEED: Animation speed
                - NUM_BARS: Number of bars per visualization
                - SAVE_FRAMES: Whether to save frames
        """
        pygame.init()
        
        settings = settings or {}
        self.algorithms = settings.get('ALGORITHMS', ['Bubble Sort', 'Quick Sort'])
        self.speed = settings.get('SPEED', 5)
        self.num_bars = settings.get('NUM_BARS', 100)
        self.save_frames_enabled = settings.get('SAVE_FRAMES', True)
        
        # Calculate layout based on number of algorithms
        self.num_algorithms = len(self.algorithms)
        self._calculate_layout()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sorting Algorithm Comparison")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Initialize arrays and generators for each algorithm
        self.arrays = []
        self.generators = []
        self.highlighted = []
        self.completed = []
        
        self._initialize_algorithms()
        
        # Recording
        self.recording = self.save_frames_enabled
        self.frame_count = 0
        self._setup_frames_folder()
        
        # State
        self.all_complete = False
    
    def _calculate_layout(self):
        """Calculate the layout grid based on number of algorithms."""
        if self.num_algorithms <= 2:
            self.cols = 1
            self.rows = self.num_algorithms
        elif self.num_algorithms <= 4:
            self.cols = 2
            self.rows = (self.num_algorithms + 1) // 2
        else:
            self.cols = 3
            self.rows = (self.num_algorithms + 2) // 3
        
        # Calculate cell dimensions
        self.cell_width = WINDOW_WIDTH // self.cols
        self.cell_height = WINDOW_HEIGHT // self.rows
        self.bar_width = max(1, self.cell_width // self.num_bars)
    
    def _initialize_algorithms(self):
        """Initialize arrays and generators for each algorithm."""
        # Create the same shuffled array for all
        base_array = list(range(1, self.num_bars + 1))
        random.shuffle(base_array)
        
        for algo_name in self.algorithms:
            # Each algorithm gets a copy of the same shuffled array
            array = base_array.copy()
            self.arrays.append(array)
            
            algo_func = ALGORITHM_MAP.get(algo_name)
            if algo_func:
                self.generators.append(algo_func(array))
            else:
                self.generators.append(iter([]))  # Empty iterator if unknown
            
            self.highlighted.append((-1, -1))
            self.completed.append(False)
    
    def _setup_frames_folder(self):
        """Create frames folder if it doesn't exist."""
        comparison_folder = os.path.join(os.path.dirname(FRAMES_FOLDER), "comparison_frames")
        self.frames_folder = comparison_folder
        if self.save_frames_enabled and not os.path.exists(comparison_folder):
            os.makedirs(comparison_folder)
    
    def update(self):
        """Update all sorting algorithms."""
        if self.all_complete:
            return
        
        for i in range(self.num_algorithms):
            if self.completed[i]:
                continue
            
            for _ in range(self.speed):
                try:
                    self.arrays[i], idx1, idx2 = next(self.generators[i])
                    self.highlighted[i] = (idx1, idx2)
                except StopIteration:
                    self.completed[i] = True
                    self.highlighted[i] = (-1, -1)
                    break
        
        # Check if all are complete
        self.all_complete = all(self.completed)
        if self.all_complete:
            self.recording = False
    
    def draw(self):
        """Draw all algorithm visualizations."""
        self.screen.fill(BACKGROUND_COLOR)
        
        for i, algo_name in enumerate(self.algorithms):
            # Calculate position in grid
            col = i % self.cols
            row = i // self.cols
            
            x_offset = col * self.cell_width
            y_offset = row * self.cell_height
            
            self._draw_algorithm_panel(i, algo_name, x_offset, y_offset)
        
        pygame.display.flip()
    
    def _draw_algorithm_panel(self, idx, algo_name, x_offset, y_offset):
        """Draw a single algorithm panel."""
        # Draw title
        title = self.title_font.render(algo_name, True, (255, 255, 255))
        title_rect = title.get_rect(centerx=x_offset + self.cell_width // 2, y=y_offset + 10)
        self.screen.blit(title, title_rect)
        
        # Draw completion status
        if self.completed[idx]:
            status = self.font.render("✓ Complete", True, (100, 255, 100))
            status_rect = status.get_rect(centerx=x_offset + self.cell_width // 2, y=y_offset + 40)
            self.screen.blit(status, status_rect)
        
        # Draw bars
        array = self.arrays[idx]
        max_value = max(array)
        bar_area_height = self.cell_height - 80  # Leave space for title
        bar_height_unit = bar_area_height / max_value
        
        for j, value in enumerate(array):
            bar_x = x_offset + j * self.bar_width + 5
            bar_height = int(value * bar_height_unit)
            bar_y = y_offset + self.cell_height - bar_height - 10
            
            # Get color
            color = get_rainbow_color(value, max_value)
            
            # Highlight compared bars
            if j in self.highlighted[idx]:
                color = (255, 255, 255)
            
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, max(1, self.bar_width - 1), bar_height))
        
        # Draw border around panel
        pygame.draw.rect(
            self.screen, 
            (60, 60, 60), 
            (x_offset, y_offset, self.cell_width, self.cell_height), 
            2
        )
    
    def save_frame(self):
        """Save current frame as PNG."""
        if self.recording and self.save_frames_enabled:
            filename = os.path.join(self.frames_folder, f"frame_{self.frame_count:06d}.png")
            pygame.image.save(self.screen, filename)
            self.frame_count += 1
    
    def handle_events(self):
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def run(self):
        """Main visualization loop."""
        running = True
        
        while running:
            running = self.handle_events()
            
            self.update()
            self.draw()
            
            if self.recording:
                self.save_frame()
            
            self.clock.tick(FPS)
        
        pygame.quit()


def main():
    """Entry point for comparison visualizer."""
    # Load runtime settings if available
    settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comparison_settings.py")
    settings = {}
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                exec(f.read(), settings)
            os.remove(settings_file)
        except Exception:
            pass
    
    if not settings:
        # Default comparison
        settings = {
            'ALGORITHMS': ['Bubble Sort', 'Quick Sort', 'Merge Sort'],
            'SPEED': 5,
            'NUM_BARS': 100,
            'SAVE_FRAMES': True
        }
    
    visualizer = ComparisonVisualizer(settings)
    visualizer.run()


if __name__ == "__main__":
    main()
