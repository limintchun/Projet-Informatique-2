"""
NOM : Li
PRÉNOM : Min-Tchun
SECTION : B1-INFO
MATRICULE : 000590125
"""


class Pixel(object):
    """
    Initialise la classe Pixel.

    La classe Pixel représente, comme son nom l’indique, un pixel et doit contenir trois entiers entre 0 et 255 :
    l’intensité des canaux rouge, vert et bleu. Ce type doit être immuable : les valeurs RGB ne peuvent pas être
    modifiées, mais elles doivent pouvoir être récupérées. Deux instances de Pixel peuvent être comparées par
    l’opérateur ==.
    """

    def __init__(self, r, g, b):
        """
        Prend en paramètre une valeur R, une valeur G et une valeur B.
        Initialise la classe Pixel.
        """
        self.red = r
        self.green = g
        self.blue = b
        if self.red < 0 or self.green < 0 or self.blue < 0:
            raise ValueError("Les valeurs RGB ne peuvent pas êter négatives.")
        self.pixel = (self.red, self.green, self.blue)

    def get_blue(self):
        """
        Retourne la valeur d'intensité de bleu du pixel.
        """
        return self.blue

    def get_green(self):
        """
        Retourne la valeur d'intensité de vert du pixel.
        """
        return self.green

    def get_red(self):
        """
        Retourne la valeur d'intensité de rouge du pixel.
        """
        return self.red

    def __eq__(self, other):
        """
        Retourne une valeur booléene. True si les pixels sont identiques, False sinon.
        """
        return self.pixel == other.pixel

    def __len__(self):
        """
        Retourne la longueur du pixel
        """
        return len(self.pixel)

    @staticmethod
    def get_pixel(pixels):
        """
        Prend en paramètres un tuple RGB.
        Retourne un objet de type Pixel
        """
        return Pixel(pixels[0], pixels[1], pixels[2])

