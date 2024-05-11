"""
NOM : Li
PRENOM : Min-Tchun
SECTION : B1-INFO
MATRICULE : 000590125
"""
from image import Image
from pixel import Pixel


class Encoder(object):
    def __init__(self, img, version=1, **kwargs):
        """
        Initialise la classe Encoder

        Le constructeur prend en paramètre une image à encoder, la version (mise par défaut à 1) et **kwargs (ceci
        permet de récupérer la profondeur ainsi que le RLE).
        """
        self.img = img
        self.version = version
        self.bbp = kwargs.get("depth", 1)
        self.rle = kwargs.get("rle", False)

        if self.version > 4:
            raise ValueError("Cette standardisation n'existe pas.")
        elif self.bbp not in [1, 2, 4, 8, 24]:
            raise ValueError("La profondeur doit être des multiples et diviseurs de 4.")
        elif self.bbp > 8 and self.rle:
            raise ValueError(
                "Vous ne pouvez pas encoder avec le RLE si la profondeur est supérieur à 8 bits par pixel.")

    def save_to(self, path):
        """
        Encode l'image reçue et l'enregistre au format ULBMP avec la version, définie en paramètre du
        constructeur, dans le fichier dont le chemin est donné en paramètre.
        """
        height = self.img.get_height()
        width = self.img.get_width()
        pixels = self.img.get_pixels()
        list_pixels = []

        # Convertit les données de type int en type byte
        for pixel in pixels:
            list_pixels.append((int.to_bytes(pixel.get_red(), byteorder='little'),
                                int.to_bytes(pixel.get_green(), byteorder='little'),
                                int.to_bytes(pixel.get_blue(), byteorder='little')))

        padding = list(set(list_pixels))  # Supprime les doublons
        grouped_pixels = [b''.join(element) for element in list_pixels]
        result = [b''.join(element) for element in padding]
        padding = b''.join(
            result)  # Join 3 fois les éléments de grouped_pixels pour pouvoir écrire le padding dans le fichier
        header = self.get_header(width, height, self.version, self.bbp, self.rle, padding)
        file = open(path, mode='wb')
        file.write(header)

        if self.version == 1:  # Phase 1
            bpixels = b''.join(bytes([pixel.get_red(), pixel.get_blue(), pixel.get_green()]) for pixel in pixels)
            file.write(bpixels)
        elif self.version == 2 or (self.rle and self.bbp >= 8):  # Phase 3
            count = 1
            for i in range(len(pixels) - 1):
                current = pixels[i]
                next_pixel = pixels[i + 1]

                if current == next_pixel:
                    count += 1
                    if count == 255:
                        count = 0
                else:
                    file.write(count.to_bytes(1, byteorder='little'))
                    file.write(bytes([current.get_red(), current.get_green(), current.get_blue()]))

            last_pixel = pixels[-1]
            while count > 0:
                chunk_count = min(count, 255)
                file.write(chunk_count.to_bytes(1, byteorder='little'))
                file.write(bytes([last_pixel.get_red(), last_pixel.get_green(), last_pixel.get_blue()]))
                count -= chunk_count
        elif self.version == 3:  # PHase 4
            for i in result:
                file.write(i)

            color_to_index = {color: index for index, color in enumerate(result)}

            indices = []
            for pixel in grouped_pixels:  # Parcourt la liste de pixels et trouver les indices correspondants dans la
                # palette
                indices.append(color_to_index[pixel])

            bit_string = ''.join(str(bit) for bit in indices)

            if len(bit_string) != 8:  # Convertit les bits en int en fonction de la profondeur
                shift = 8 - len(bit_string)
            shifter = '0' * shift
            shifted_bit_string = bit_string + shifter
            decimal_value = int(shifted_bit_string, 2)
            hex_value = bytes([decimal_value])
            file.write(hex_value)
        else:  # Phase 5
            black = Pixel(0, 0, 0)  # P'
            previous_pixel = black
            blocks = []
            small_bloc = '00'
            inter_bloc = '01'
            big_bloc_R = '1000'
            big_bloc_G = '1001'
            big_bloc_B = '1010'
            new_bloc = b'\xff'
            for i in pixels:
                delta_colors = Encoder.delta_colors(previous_pixel, i)

                # ULBMP_SMALL_DIFF
                if Encoder.is_small_difference(delta_colors[0], delta_colors[1], delta_colors[2]):
                    converted_value = ''
                    if delta_colors[0] < 0 or delta_colors[1] < 0 or delta_colors[2] < 0:
                        converted_value = (delta_colors[0] + 2, delta_colors[1] + 2, delta_colors[2] + 2)
                    else:
                        converted_value = (delta_colors[0], delta_colors[1], delta_colors[2])

                    DR = Encoder.int_to_binary(converted_value[0], 2)
                    DG = Encoder.int_to_binary(converted_value[1], 2)
                    DB = Encoder.int_to_binary(converted_value[2], 2)
                    # Assemble le bloc
                    binary_string = int(small_bloc + DR + DG + DB, 2).to_bytes(1, 'little')
                    blocks.append(binary_string)

                # ULBMP_INTERMEDIATE_DIFF
                elif Encoder.is_intermediate_difference(delta_colors[0] - delta_colors[1],
                                                        delta_colors[0] - delta_colors[1],
                                                        delta_colors[-1] - delta_colors[1]):
                    converted_value = ''
                    if delta_colors[0] < 0 or delta_colors[1] < 0 or delta_colors[2] < 0:
                        converted_value = (delta_colors[1] + 32, delta_colors[0] - delta_colors[1] + 8,
                                           delta_colors[-1] - delta_colors[1] + 8)
                    else:
                        converted_value = (
                            delta_colors[1], delta_colors[0] - delta_colors[1], delta_colors[-1] - delta_colors[1])

                    encoded_DG = Encoder.int_to_binary(converted_value[0], 6)
                    encoded_DR = Encoder.int_to_binary(converted_value[1], 4)
                    encoded_DB = Encoder.int_to_binary(converted_value[-1], 4)
                    # Assemble le bloc
                    binary_string = int(inter_bloc + encoded_DG, 2).to_bytes(1, 'little')
                    last_binary = int(encoded_DR + encoded_DB, 2).to_bytes(1, 'little')
                    blocks.append(binary_string)
                    blocks.append(last_binary)

                # ULBMP_BIG_DIFF Bloc R
                elif Encoder.is_big_difference_R(delta_colors[0], delta_colors[1] - delta_colors[0],
                                                 delta_colors[-1] - delta_colors[0]):

                    converted_value = (delta_colors[0] + 128, delta_colors[1] - delta_colors[0] + 32,
                                       delta_colors[-1] - delta_colors[0] + 32)
                    encoded_DG = Encoder.int_to_binary(converted_value[0], 8)
                    encoded_DR = Encoder.int_to_binary(converted_value[1], 6)
                    encoded_DB = Encoder.int_to_binary(converted_value[-1], 6)

                    # Assemble les blocs avec l'identificateur du type de différence
                    binary_strings = big_bloc_R + encoded_DG + encoded_DR + encoded_DB
                    byte = ''
                    for h in range(0, len(binary_strings), 8):
                        byte = binary_strings[h:h + 8]
                        binary_string = int(byte, 2).to_bytes(1, 'little')
                        blocks.append(binary_string)

                # ULBMP_BIG_DIFF Bloc G
                elif Encoder.is_big_difference_G(delta_colors[0] - delta_colors[1], delta_colors[1],
                                                 delta_colors[-1] - delta_colors[1]):
                    converted_value = (delta_colors[1] + 128, delta_colors[0] - delta_colors[1] + 32,
                                       delta_colors[-1] - delta_colors[1] + 32)

                    encoded_DG = Encoder.int_to_binary(converted_value[0], 8)
                    encoded_DR = Encoder.int_to_binary(converted_value[1], 6)
                    encoded_DB = Encoder.int_to_binary(converted_value[-1], 6)

                    binary_strings = big_bloc_G + encoded_DG + encoded_DR + encoded_DB
                    byte = ''
                    for h in range(0, len(binary_strings), 8):
                        byte = binary_strings[h:h + 8]
                        binary_string = int(byte, 2).to_bytes(1, 'little')
                        blocks.append(binary_string)


                # ULBMP_BIG_DIFF Bloc B
                elif Encoder.is_big_difference_B(delta_colors[0] - delta_colors[-1], delta_colors[-1],
                                                 delta_colors[1] - delta_colors[-1]):

                    converted_value = (
                        delta_colors[-1] + 128, delta_colors[0] - delta_colors[-1] + 32,
                        delta_colors[1] - delta_colors[-1] + 32)
                    encoded_DG = Encoder.int_to_binary(converted_value[0], 8)
                    encoded_DR = Encoder.int_to_binary(converted_value[1] - converted_value[1], 6)
                    encoded_DB = Encoder.int_to_binary(converted_value[-1] - converted_value[1], 6)

                    binary_strings = big_bloc_B + encoded_DG + encoded_DR + encoded_DB
                    byte = ''
                    for h in range(0, len(binary_strings), 8):
                        byte = binary_strings[h:h + 8]
                        binary_string = int(byte, 2).to_bytes(1, 'little')
                        blocks.append(binary_string)

                # ULBMP_NEW_PIXEL
                else:
                    red = i.get_red().to_bytes(1, 'little')
                    green = i.get_green().to_bytes(1, 'little')
                    blue = i.get_blue().to_bytes(1, 'little')
                    pixel = new_bloc + red + green + blue
                    blocks.append(pixel)

                previous_pixel = i  # Modifie P'
            for i in blocks:
                file.write(i)

    @staticmethod
    def get_header(width: int, height: int, version: int, bbp: int, rle: bool, padding, size=12):
        """
        Prend en paramètre, la largeur et la hauteur de l'image, la version d'encodage, la taille du header,
        la profondeur, une palette de couleurs et une valeur booléenne pour déterminer s'il faut encoder en RLE.
        Le paramètre size est mis par défaut à 12 car seul lors de la phase 4, la taille du header peut varier.

        Retourne un header en fonction des paramètres.
        """
        if version == 1 or version == 2 or version == 4:
            res = (b'ULBMP' + version.to_bytes(1, byteorder='little') + size.to_bytes(2, 'little')
                   + width.to_bytes(2, byteorder='little') + height.to_bytes(2, byteorder='little'))
        else:
            size = len(padding) + 14
            if rle and bbp >= 8:
                rle = b"\x01"
            else:
                rle = b"\x00"
            res = b'ULBMP' + version.to_bytes(1, byteorder='little') + size.to_bytes(2, 'little') + width.to_bytes(2,
                                                                                                                   byteorder='little') + height.to_bytes(
                2, byteorder='little') + bbp.to_bytes(1, byteorder='little') + rle
        return res

    @staticmethod
    def delta_colors(color1: Pixel, color2: Pixel):
        """
        Calcule la différence des valeurs RGB de 2 pixels
        Renvoie un tuple (r,g,b)
        """
        DR, DG, DB = color2.get_red() - color1.get_red(), color2.get_green() - color1.get_green(), color2.get_blue() - color1.get_blue()
        return DR, DG, DB

    @staticmethod
    def is_small_difference(DR, DG, DB):
        """
        Vérifie si c'est un bloc de type SMALL_DIFF
        Retourne True si les valeurs RGB sont entre -2 et 2 non-compris, False sinon
        """
        SMALL_DIFF_RANGE = [-2, -1, 0, 1]
        return DR in SMALL_DIFF_RANGE and DG in SMALL_DIFF_RANGE and DB in SMALL_DIFF_RANGE

    @staticmethod
    def is_intermediate_difference(DG, Drg, Dbg):
        """
        Vérifie si c'est un bloc de type INTERMEDIATE_DIFF
        Retourne True si les valeurs RGB sont entre  -32 et 32 non-compris, -8 et 8 non-compris, sinon False
        """
        INTERMEDIATE_DIFF_RANGE = range(-32, 32)
        INTERMEDIATE_RELATIVE_DIFF_RANGE = range(-8, 8)
        return DG in INTERMEDIATE_DIFF_RANGE and Drg in INTERMEDIATE_RELATIVE_DIFF_RANGE and Dbg in INTERMEDIATE_RELATIVE_DIFF_RANGE

    @staticmethod
    def is_big_difference_R(R, G, B):
        """
        Vérifie si c'est un bloc de type BIG_DIFF R
        Retourne True si les valeurs RGB sont entre  -128 et 128 non-compris, -32 et 32 non-compris, sinon False
        """
        BIG_DIFF_RANGE = range(-128, 128)
        BIG_RELATIVE_DIFF_RANGE = range(-32, 32)
        return R in BIG_DIFF_RANGE and max(R, G,
                                           B) == R and G in BIG_RELATIVE_DIFF_RANGE and B in BIG_RELATIVE_DIFF_RANGE

    @staticmethod
    def is_big_difference_G(R, G, B):
        """
        Vérifie si c'est un bloc de type BIG_DIFF G
        Retourne True si les valeurs RGB sont entre  -128 et 128 non-compris, -32 et 32 non-compris, sinon False
        """
        BIG_DIFF_RANGE = range(-128, 128)
        BIG_RELATIVE_DIFF_RANGE = range(-32, 32)
        return R in BIG_RELATIVE_DIFF_RANGE and max(R, G,
                                                    B) == G and G in BIG_DIFF_RANGE and B in BIG_RELATIVE_DIFF_RANGE

    @staticmethod
    def is_big_difference_B(R, G, B):
        """
        Vérifie si c'est un bloc de type BIG_DIFF B
        Retourne True si les valeurs RGB sont entre  -128 et 128 non-compris, -32 et 32 non-compris, sinon False
        """
        BIG_DIFF_RANGE = range(-128, 128)
        BIG_RELATIVE_DIFF_RANGE = range(-32, 32)
        return R in BIG_RELATIVE_DIFF_RANGE and G in BIG_RELATIVE_DIFF_RANGE and B in BIG_DIFF_RANGE

    @staticmethod
    def int_to_binary(num, num_bits):
        """
        Convertit un entier en chaine de caractère sous forme binaire
        """
        binary = ""
        for i in range(num_bits - 1, -1, -1):
            # Effectuer un décalage vers la droite pour récupérer le bit de poids faible
            bit = (num >> i) & 1
            # Ajouter le bit à la chaîne binaire
            binary += str(bit)
        return binary


class Decoder(object):
    """
    Initialise la classe Decoder.

    La classe consiste en une unique méthode statique load_from(path: str) -> Image qui charge l'image encodée dans le
    fichier dont le chemin est donné en paramètre et renvoie cette image.
    """

    @staticmethod
    def load_from(path):
        """
        Prend en paramtre une image encodée dans le fichier dont le chemin est donné en paramètre.
        Renvoie cette image.
        """
        file = open(path, mode='rb')
        data = file.read()
        size = int.from_bytes(data[6:8], byteorder='little')
        header = data[0:size]
        version = int.from_bytes(data[5:6], byteorder='little')
        bbp = data[12]
        rle = Decoder.decode_rle(data[13:14])
        padding = data[14:size]
        converted_padding = [padding[i:i + 3] for i in range(0, len(padding), 3)]
        height = int.from_bytes(data[10:12], byteorder='little')
        width = int.from_bytes(data[8:10], byteorder='little')
        pixels = data[size:]

        if header != Decoder.decode_header(height, width, version, bbp, rle, padding, size):
            raise Exception("Le fichier ne peut pas être lu.")

        elif version.to_bytes(1, 'little') == b'\x01':  # Phase 1
            img = [(int.from_bytes(pixels[i:i + 1]), int.from_bytes(pixels[i + 1:i + 2]),
                    int.from_bytes(pixels[i + 2:i + 3]))
                   for
                   i in range(0, len(pixels), 3)]
            img = [Pixel.get_pixel(p) for p in img]

        elif version.to_bytes(1, 'little') == b'\x02':  # Phase 3
            img = [(int.from_bytes(pixels[i:i + 1]), int.from_bytes(pixels[i + 1:i + 2]),
                    int.from_bytes(pixels[i + 2:i + 3]), int.from_bytes(pixels[i + 3: i + 4]))
                   for i in range(0, len(pixels), 4)]
            img = [Pixel.get_pixel(p) for p in img]

        elif version.to_bytes(1, 'little') == b'\x03':  # Phase 4
            if rle:
                repet = []
                idx = []
                for i in range(0, len(pixels), 2):
                    repet.append(pixels[i])
                    idx.append(pixels[i + 1])
                repeted_pxl = [converted_padding[idx] * repet[idx] for idx in idx]
                pixels_list = []

                # Boucle sur chaque ligne de pixels
                for row in repeted_pxl:
                    for i in range(0, len(row), 3):
                        r, g, b = row[i:i + 3]
                        pixels_list.append((r, g, b))
                img = [Pixel.get_pixel(p) for p in pixels_list]

            else:
                int_value = int.from_bytes(pixels, byteorder='little')
                binary_string = Decoder.hex_to_binary(hex(int_value)[2:])

                # Diviser la chaîne binaire en pixels
                pixels = Decoder.split_into_pixels(binary_string, bbp)

                # Convertir chaque groupe en entier
                str_img = [converted_padding[i] for i in pixels]
                if len(str_img) != (width * height):
                    str_img = str_img[:width * height]
                converted_img = [(pixel[0], pixel[1], pixel[2]) for pixel in str_img]
                img = [Pixel.get_pixel(p) for p in converted_img]

        else:  # Phase 5
            previous = Pixel(0, 0, 0)
            blocs = []
            binary_pixels = Decoder.bytes_to_binary(pixels)
            img = []
            count = 0

            for i in range(0, len(binary_pixels), 8):  # Sépare binary_pixels en bytes
                byte_chunk = binary_pixels[i:i + 8]
                blocs.append(byte_chunk)

            while len(img) < width * height:  # Comme ma fonction Decoder.split_into_pixels(bytes, bbp) retourne une
                # liste pour la
                # phase 4, j'ai fait des manipulations un peu bizarre, j'ai pas trouvé plus optimale désolé
                if blocs[count].startswith('00'):  # SMALL DIFF
                    converted_value = Decoder.split_into_pixels(blocs[count], 2)
                    delta = Encoder.delta_colors(Pixel(previous.get_red(), previous.get_green(), previous.get_blue()),
                                                 Pixel(converted_value[1], converted_value[2], converted_value[3]))
                    if not Encoder.is_small_difference(delta[0], delta[1], delta[2]):
                        diff_colors = [converted_value[1] - 2, converted_value[2] - 2, converted_value[3] - 2]
                    else:
                        diff_colors = [converted_value[1], converted_value[2], converted_value[3]]
                    result = [diff_colors[0] + previous.get_red(), diff_colors[1] + previous.get_green(),
                              diff_colors[2] + previous.get_blue()]
                    previous = Pixel(result[0], result[1], result[2])

                    img.append(result)
                    count += 1

                elif blocs[count].startswith('01'):  # INTERMEDIATE DIFF
                    bloc = blocs[count] + blocs[count + 1]
                    DG = Decoder.split_into_pixels(bloc[2:8], 6)
                    DR = Decoder.split_into_pixels(bloc[8:12], 4)
                    DB = Decoder.split_into_pixels(bloc[12:16], 4)

                    delta = Encoder.delta_colors(Pixel(previous.get_red(), previous.get_green(), previous.get_blue()),
                                                 Pixel(DR[0], DG[0], DB[0]))
                    if not Encoder.is_intermediate_difference(delta[0] - delta[1], delta[1], delta[-1] - delta[1]):
                        diff_colors = [DR[0] - 8, DG[0] - 32, DB[0] - 8]
                    else:
                        diff_colors = [DR[0], DG[0], DB[0]]
                    result = [diff_colors[0] + diff_colors[1] + previous.get_red(),
                              diff_colors[1] + previous.get_green(),
                              diff_colors[2] + diff_colors[1] + previous.get_blue()]
                    previous = Pixel(result[0], result[1], result[2])
                    img.append(result)
                    count += 2

                elif blocs[count].startswith('1000'):  # BIG DIFF R
                    bloc = blocs[count] + blocs[count + 1] + blocs[count + 2]
                    DR = Decoder.split_into_pixels(bloc[4:12], 8)
                    DG = Decoder.split_into_pixels(bloc[12:16], 6)
                    DB = Decoder.split_into_pixels(bloc[16:], 6)
                    delta = Encoder.delta_colors(Pixel(previous.get_red(), previous.get_green(), previous.get_blue()),
                                                 Pixel(DR[0], DG[0], DB[0]))
                    if not Encoder.is_big_difference_R(delta[0], delta[1], delta[2]):
                        diff_colors = [DR[0] - 128, DG[0] - 32, DB[0] - 32]
                    else:
                        diff_colors = [DR[0], DG[0], DB[0]]
                    result = [diff_colors[0] + previous.get_red(), diff_colors[1] + diff_colors[0] + previous.get_green(), diff_colors[2] + diff_colors[0] + previous.get_blue()]
                    previous = Pixel(DR[0], DG[0], DB[0])
                    img.append(result)
                    count += 3

                elif blocs[count].startswith('1001'):  # BIG DIFF G
                    bloc = blocs[count] + blocs[count + 1] + blocs[count + 2]
                    DR = Decoder.split_into_pixels(bloc[12:16], 6)
                    DG = Decoder.split_into_pixels(bloc[4:12], 8)
                    DB = Decoder.split_into_pixels(bloc[16:], 6)
                    delta = Encoder.delta_colors(Pixel(previous.get_red(), previous.get_green(), previous.get_blue()),
                                                 Pixel(DR[0], DG[0], DB[0]))
                    if not Encoder.is_big_difference_G(delta[0], delta[1], delta[2]):
                        diff_colors = [DR[0] - 32, DG[0] - 128, DB[0] - 32]
                    else:
                        diff_colors = [DR[0], DG[0], DB[0]]
                    result = [diff_colors[0] + diff_colors[1] + previous.get_red(), diff_colors[1] + previous.get_green(), diff_colors[2] + diff_colors[1] + previous.get_blue()]
                    previous = Pixel(DR[0], DG[0], DB[0])
                    img.append(result)
                    count += 3

                elif blocs[count].startswith('1010'):  # BIG DIFF B
                    bloc = blocs[count] + blocs[count + 1] + blocs[count + 2]
                    DR = ''.join(
                        map(str, Decoder.split_into_pixels(bloc[12:18], 6)))  # Comme 6 n'est pas un multiple n'est pas
                    # un multiple de 4, conversin de chaque élément de la liste ça évite d'avoir une couleur de type [int, int]
                    DG = ''.join(map(str, Decoder.split_into_pixels(bloc[18:24], 6)))
                    DB = Decoder.split_into_pixels(bloc[4:12], 8)
                    delta = Encoder.delta_colors(Pixel(previous.get_red(), previous.get_green(), previous.get_blue()),
                                                 Pixel(int(DR), int(DG), DB[0]))
                    if not Encoder.is_big_difference_R(delta[0], delta[1], delta[-1]):
                        diff_colors = [int(DR) - 32, int(DG) - 32, DB[0] - 128]
                    else:
                        diff_colors = [int(DR), int(DG), DB[0]]
                    result = [diff_colors[0] + diff_colors[2] + previous.get_red(),
                              diff_colors[1] + diff_colors[2] + previous.get_green(),
                              diff_colors[2] + previous.get_blue()]
                    previous = Pixel(result[0], result[1], result[2])
                    img.append(result)
                    count += 3
            res = []
            for i in img:
                res.append(Pixel(i[0], i[1], i[2]))
            img = res

        return Image(width, height, img)

    @staticmethod
    def decode_rle(byte: bytes):
        """
        Retourne une valeur booléenne en fonction du byte déterminant l'utilisation du RLE.
        """
        if byte == b'\x00':
            return False
        else:
            return True

    @staticmethod
    def decode_header(width, height, version, bbp
                      , rle, padding, size):
        """
        Retourne un header décodé en fonction des paramètres données
        """
        if version == 1 or version == 2 or version == 4:
            res = b'ULBMP' + version.to_bytes(1, byteorder='little') + size.to_bytes(2, 'little') + width.to_bytes(2,
                                                                                                                   byteorder='little') + height.to_bytes(
                2, byteorder='little')
        else:
            if rle and bbp >= 8:
                rle = b"\x01"
            else:
                rle = b"\x00"
            res = b'ULBMP' + version.to_bytes(1, byteorder='little') + size.to_bytes(2, 'little') + height.to_bytes(2,
                                                                                                                    byteorder='little') + width.to_bytes(
                2, byteorder='little') + bbp.to_bytes(1, byteorder='little') + rle + padding
        return res

    @staticmethod
    def hex_to_binary(hex_value):
        """
        Convertit un string représenté en hexadécimal en binaire
        """
        hex_bytes = bytes.fromhex(hex_value)
        binary_string = ""
        for byte in hex_bytes:
            for i in range(7, -1, -1):
                bit = (byte >> i) & 1
                binary_string += str(bit)
        return binary_string

    @staticmethod
    def bytes_to_binary(byte_string):
        """
        Convertit une chaine d'octet en chaine de caractères en représentation binaire
        """
        # Conversion des octets en représentation binaire
        binary_string = ''
        for byte in byte_string:
            # Utilisation du masking pour obtenir chaque bit du byte
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                # Ajout du bit à la chaîne binaire
                binary_string += str(bit)
        return binary_string

    @staticmethod
    def split_into_pixels(binary_string, bbp):
        """
        Sépare les pixels en représentation binaire en fonction de la profondeur bbp
        """
        pixels = []
        for i in range(0, len(binary_string), bbp):
            pixel_bits = binary_string[i:i + bbp]
            pixels.append(int(pixel_bits, 2))
        return pixels
