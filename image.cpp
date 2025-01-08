#include "image.h"
#include "pixel.h"
#include <iostream>

Image::Image(int w, int h, std::vector<Pixel>pixels): width(w), height(h), size(w *h), pixels(pixels){
    if (width * height != size) {
        std::cerr << "La quantité de pixels introduite ne correspond pas au format de l'image" << std::endl;
    }
}

bool Image::sameList(const std::vector<Pixel>& pix, const std::vector<Pixel>& other) const{
    if (pix.size() != other.size()) {
        return false;
    }

    for (size_t i = 0; i < pix.size(); i++) {
        if (pix[i] != other[i]) {
            return false;
        }
    }
    return true;
}

bool Image::operator==(const Image& image) const {
    return sameList(pixels, image.pixels) && width == image.width && height == image.height;
}

const Pixel& Image::getPixel(int x, int y){
    int idx = y * width +x;
    return pixels[idx];
}

Pixel& Image::operator[](int idx[2]) {
    int x = idx[0];
    int y = idx[1];
    if ( x >= width && y >= height) {
        std:: cerr << "Il n'y a pas assez de pixels pour remplir l'image" << std::endl;
        exit(1);
    }
    return pixels[y * width + x];
}

const Pixel& Image::operator[](size_t idx) const{
    if (idx >= size) {
        std::cerr << "La position n'est pas valide" << std::endl;
        exit(1);
    }
    return pixels[idx];
}

