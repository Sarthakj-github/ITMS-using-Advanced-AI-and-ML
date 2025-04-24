import time
import emoji
from pathlib import Path

class TrafficController:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.inpro_dir = self.base_dir / "inpro_imgs"
        self.current_green = None
        self.green_duration = 30  # Base duration in seconds

    def read_counts(self):
        """Read vehicle counts from files"""
        counts = []
        for i in range(1, 5):
            count_file = self.inpro_dir / f"lane{i}_count.txt"
            try:
                with open(count_file) as f:
                    counts.append(int(f.read()))
            except:
                counts.append(0)
        return counts

    def display_lanes(self, active_lane=None):
        """Show lane status with emoji indicators"""
        lanes = ["Lane 1", "Lane 2", "Lane 3", "Lane 4"]
        status = []
        
        for i in range(4):
            if active_lane and i == active_lane - 1:
                status.append(emoji.emojize(":green_circle:"))
            else:
                status.append(emoji.emojize(":red_circle:"))
        
        print("\n" + "       ".join(lanes))
        print("  ".join(status))
        print("-" * 50)

    def control_lights(self):
        """Main traffic light control loop"""
        try:
            while True:
                # Get current counts
                counts = self.read_counts()
                busiest_lane = counts.index(max(counts)) + 1
                
                # Calculate green duration (30s + 2s per vehicle)
                green_time = self.green_duration + (2 * max(counts))
                
                # Switch to busiest lane
                self.current_green = busiest_lane
                print(f"\nSwitching to Lane {busiest_lane} for {green_time}s")
                self.display_lanes(busiest_lane)
                
                # Countdown
                for remaining in range(green_time, 0, -1):
                    print(f"\rTime remaining: {remaining}s", end="")
                    if remaining <= 5:  # Yellow warning
                        print(" - YELLOW WARNING", end="")
                    time.sleep(1)
                
                # Switch all to red briefly
                print("\n\nTransitioning...")
                self.display_lanes(None)
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\nTraffic controller stopped")

if __name__ == "__main__":
    controller = TrafficController()
    controller.control_lights()