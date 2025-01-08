#ifndef PIXEL_H
#define PIXEL_H

class Pixel {
private:
    int red, green, blue;
public:
    // constructeur
    Pixel(int red, int green, int blue);

    // créer un destructeuer ?

    // Getter car les valeurs rgb sont immuables
    int getRed(Pixel pixel); 

    // Getter car les valeurs rgb sont immuables
    int getGreen(Pixel pixel);
    
    // Getter car les valeurs rgb sont immuables
    int getBlue(Pixel pixel);

    // overloading de l'opérateur ==
    bool operator==(const Pixel& pixel) const;

    bool operator!=(const Pixel& pixel) const;
};

#endif // !PIXEL_H
