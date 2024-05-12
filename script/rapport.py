import matplotlib.pyplot as plt
import numpy as np

names = ['1.0', 'RLE', 'bbp = 1', 'bbp = 2', 'bbp = 4', 'bbp = 8', 'bbp = 24', 'Delta']  # nom des barres

values = [518.8, 19, 21, 43, 84, 179,1200, 87]

# 360 * 480 * 3 = 518400 = 518 Mb
plt.bar(names, values)  # Tracer

plt.title('Taux de compression')
plt.xlabel("Méthode d'encodage")
plt.ylabel('Stockage (kO)')

plt.savefig('graph')
plt.show()
