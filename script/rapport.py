import matplotlib.pyplot as plt
import numpy as np

names = ['1.0', '2.0', '3.0', '4.0'] # nom des barres

values = [518.8 , 10, 100, 1000]

# 360 * 480 * 3 = 518400 = 518 Mb
plt.bar(names, values) # Tracer

plt.title('Taux de compression')
plt.xlabel('Version de ULBMP')
plt.ylabel('Stockage (Mb)')

plt.show()