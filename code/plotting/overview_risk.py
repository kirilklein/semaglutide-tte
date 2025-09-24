import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta
background_color = "#d9e8e5"

plt.rcParams['figure.facecolor'] = background_color
plt.rcParams['axes.facecolor'] = background_color
# Risk range
x = np.linspace(0, 1, 500)

# Example Beta distributions (alpha, beta)
distributions = [
    beta(5.1, 2.1),   # skewed towards high risk
    beta(1.9, 2.2),   # U-shaped
    beta(5.9, 5.7),   # peaked in the middle
]

colors = ["#A0C4FF", "#FFD6A5", "#FFADAD"]

plt.figure(figsize=(6,4))

for dist, color in zip(distributions, colors):
    y = dist.pdf(x)
    plt.plot(x, y, color=color, linewidth=4, alpha=0.9)  # translucent lines

# Style adjustments
# plt.xlabel("Risk", fontsize=14, fontweight="bold")
plt.xticks([])  # remove ticks
plt.yticks([])  # remove ticks
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
# The bottom spine (x-axis) is visible by default, but we ensure it.
ax.spines['bottom'].set_visible(True)

# Add an arrow to the end of the x-axis
ax.annotate('', xy=(1.02, 0), xycoords='axes fraction', xytext=(1, 0), textcoords='axes fraction',
            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8))

# plt.show()
plt.savefig("outputs/figs/publication_figure.png", bbox_inches="tight", dpi=200)