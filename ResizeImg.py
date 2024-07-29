import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.animation import FuncAnimation

def create_colormap():
    colors = [
        (0.0,   'darkblue'),    # Dark blue from 0 to 1
        (0.1,   'mediumblue'),  # Transition from dark blue to medium blue (1 to 25)
        (0.2,   'blue'),        # Transition from medium blue to blue (26 to 50)
        (0.3,   'deepskyblue'), # Transition from blue to deep sky blue (51 to 75)
        (0.4,   'cyan'),        # Transition from deep sky blue to cyan (76 to 100)
        (0.5,   'lime'),        # Transition from cyan to lime (101 to 125)
        (0.6,   'yellow'),      # Transition from lime to yellow (126 to 150)
        (0.7,   'gold'),        # Transition from yellow to gold (151 to 175)
        (0.8,   'orange'),      # Transition from gold to orange (176 to 200)
        (0.9,   'darkorange'),  # Transition from orange to dark orange (201 to 225)
        (1.0,   'darkred')      # Transition from dark orange to dark red (226 to 255)
    ]
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=256)
    return cmap
# Initialize pressure data with random values
def randomize_pressure_data():
    return np.random.randint(0, 256, size=(15, 5))

# Define custom labels for each cell
def get_custom_labels():
    rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    cols = ['1', '2', '3', '4', '5', '6', '7', '8']
    custom_labels = []

    for i in range(8):
        row_labels = []
        for j in range(8):
            if j < len(cols) and i < len(rows):
                row_labels.append(rows[i] + cols[j])
            else:
                row_labels.append('')
        custom_labels.append(row_labels)

    return custom_labels

# Create the initial graph without footprint mask
def create_graph(pressure_data, custom_labels, cmap):
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(pressure_data, cmap=cmap, vmin=0, vmax=255)

    # Add text labels to each cell based on custom_labels
    text_labels = []
    for i in range(8):
        for j in range(8):
            label = custom_labels[i][j]
            if label:
                text = ax.text(j, i, label, ha='center', va='center', fontsize=10, color='black', weight='bold', zorder=10)
                text_labels.append(text)

    ax.set_xticks([])
    ax.set_yticks([])

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Pressure Intensity')
    ax.set_title('Pressure Heatmap')

    return fig, ax, im, text_labels

# Update the heatmap with new data
def update(frame, pressure_data, im, text_labels):
    # Generate new random pressure data
    pressure_data = np.random.randint(0, 256, size=(8, 8))

    im.set_data(pressure_data)
    # Ensure the data stays within the valid range [0, 255] for colour heatmap
    im.set_clim(vmin=0, vmax=255)

    # Update text labels (if they change with new data)
    for text in text_labels:
        text.set_zorder(10)

    return [im] + text_labels

if __name__ == "__main__":
    cmap = create_colormap()
    pressure_data = randomize_pressure_data()
    custom_labels = get_custom_labels()

    fig, ax, im, text_labels = create_graph(pressure_data, custom_labels, cmap)
    
    # to animate
    ani = FuncAnimation(fig, update, frames=200, interval=100, blit=True, 
                        fargs=(pressure_data, im, text_labels))

    plt.show()
