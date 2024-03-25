"""
NOM : Li
PRÉNOM : Min-Tchun
SECTION : B1-INFO
MATRICULE : 000590125
"""
from pixel import Pixel


class Image(object):
    def __init__(self, width: int, height: int, pixels):
        """
        Initialise la classe Image.

        Le constructeur prend en paramètre width, height représentant la dimension de l'image, ainsi qu'une liste de
        taille width * height comprenant des instances de la classe Pixel et représentant une image.

        Une exception est lancée lorsque les éléments de la liste pixels ne sont pas de classe Pixel ou lorsqu'il y a
        trop/pas assez de pixels par rapport au format de l'image.
        """
        self.w = width
        self.h = height
        self.img = pixels
        if self.w * self.h != len(self.img):
            raise ValueError("La quantité de pixels introduite ne correspond pas au format de l'image.")
        for i in pixels:
            if not isinstance(i, Pixel):
                raise ValueError("Les éléments de la liste ne sont pas de type Pixel.")

    def __getitem__(self, pos: tuple[int, int]):
        """
        Surcharge l'opérateur [] en lecture
        Lance une erreur si pos n'est pas une position valide dans l'image.
        """
        x = pos[0]
        y = pos[1]
        if not (x <= self.w and y <= self.h):
            raise IndexError("Il n'y a pas assez de pixels pour remplir l'image.")
        return self.img[y * self.w + x]

    def __setitem__(self, pos: tuple[int, int], pix):
        """
        Surcharge l'opérateur [] en écriture.
        Lance une erreur si pos n'est pas une position valide dans l'image.
        """
        x = pos[0]
        y = pos[1]
        if x < self.w or y < self.h:
            self.img[x + y * self.w] = pix
        else:
            raise IndexError("La position n'est pas valide.")

    def __eq__(self, other):
        """
        Surcharge l'opérateur d'égalité.
        """
        return self.img == other.img

    def get_width(self):
        """
        Retourne la largeur de l'image.
        """
        return self.w

    def get_height(self):
        """
        Retourne la hauteur de l'image.
        """
        return self.h

    def get_pixels(self):
        """
        Retourne une liste de pixel de taille width * height.
        """
        return self.img

