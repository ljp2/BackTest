import matplotlib.pyplot as plt

def update_elements(event):
    if event.xdata is not None and event.ydata is not None:
        # Update the position of the horizontal line
        hline.set_ydata(event.ydata)

        # Update the position of the label
        label.set_text(f'Cursor Position: x={max_x:.2f}, y={event.ydata:.2f}')
        label.set_position((max_x, event.ydata + 0.1))

        fig.canvas.draw_idle()

# Sample data
x_values = [1, 2, 3, 4, 5]
y_values = [2, 3, 5, 7, 11]

fig, ax = plt.subplots()
scatter = ax.scatter(x_values, y_values)

# Set the initial position of the label in data coordinates
max_x = max(x_values)
max_y = max(y_values)
label = ax.text(max_x, min(max_y, min(y_values)), '', ha='right', va='bottom', transform=ax.transData)

# Add a horizontal line
hline, = ax.plot([min(x_values), max_x], [y_values[0], y_values[0]], linestyle='--', color='gray')

fig.canvas.mpl_connect('motion_notify_event', update_elements)

plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Cursor Position Label and Horizontal Line')

plt.show()
