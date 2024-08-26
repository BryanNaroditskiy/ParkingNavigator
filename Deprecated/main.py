import tkinter as tk
import random

class ParkingLotVisualization:

    def __init__(self, rows, spots_per_row):
        self.root = tk.Tk()
        self.root.title("Complex Parking Lot Visualization")

        self.cell_size = 30
        self.rows = rows
        self.spots_per_row = spots_per_row

        # Initialize parking lot with all spots as open (0)
        self.parking_data = [[0 for _ in range(spots_per_row * 2)] for _ in range(rows)]

        self.canvas_width = self.cell_size * (2 * spots_per_row + 1)
        self.canvas_height = self.cell_size * (2 * rows + 1)

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack(pady=20)

        self.draw_parking_lot()

    def draw_parking_lot(self):
        # Draw Parking Spots
        for i in range(self.rows):
            for j in range(self.spots_per_row * 2):
                x1 = j * self.cell_size
                y1 = (i * 2 + 1) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "red" if self.parking_data[i][j] == 1 else "green"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def fill_random_spots(self, fill_percentage=0.5):
        total_spots = self.rows * self.spots_per_row * 2
        spots_to_fill = int(total_spots * fill_percentage)

        while spots_to_fill > 0:
            i = random.randint(0, self.rows - 1)
            j = random.randint(0, self.spots_per_row * 2 - 1)

            if self.parking_data[i][j] == 0:
                self.parking_data[i][j] = 1
                spots_to_fill -= 1

        # Redraw parking lot with filled spots
        self.draw_parking_lot()

    def run(self):
        self.root.mainloop()

# Example usage: Creates a parking lot with 5 rows and 10 parking spots in each row.
parking = ParkingLotVisualization(5, 10)
parking.fill_random_spots(fill_percentage=0.7)
parking.run()
