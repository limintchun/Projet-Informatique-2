#include "pixel.h"

Pixel::Pixel(int r, int g, int b) : red(r), green(g), blue(b) {}

int Pixel::getRed(Pixel pixel) {
    return pixel.red;
}
int Pixel::getGreen(Pixel pixel) {
    return pixel.green;
}

int Pixel::getBlue(Pixel pixel) {
    return pixel.blue;
}

bool Pixel::operator==(const Pixel& pixel) const {
    return red == pixel.red && green == pixel.green && blue == pixel.blue;
}

bool Pixel::operator!=(const Pixel & pixel) const {
    return red != pixel.red || green != pixel.green || blue != pixel.blue;
}

