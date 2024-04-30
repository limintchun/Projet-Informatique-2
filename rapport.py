import matplotlib.pyplot as plt
import numpy as np


x = np.linspace(-5, 5, 100)
plt.plot(x, np.sin(x))

plt.ylabel('fonction sinus')
plt.xlabel("l'axe des abcisses")
plt.show()

plt.savefig('sinus.png')
