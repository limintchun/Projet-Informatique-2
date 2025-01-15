#ifndef IMAGE_H
#define IMAGE_H

#include "pixel.h"

#include <vector>

class Image {
private:
    int width, height;
    int size;
    std::vector<Pixel>pixels; 
public:
    // constructeur
    Image(int width, int height, std::vector<Pixel> pixels); 

    // créer un destructeuer ?
    bool sameList(const std::vector<Pixel>& pix, const std::vector<Pixel>& other)const; 
    const Pixel& getPixel(int x, int y);
    bool operator==(const Image& image) const;

    Pixel& operator[](int idx[2]);
    const Pixel& operator[](int idx) const;

    int getHeight();
    int getWidth();
    std::vector<Pixel>getPixel();
};

#endif // !IMAGE_H
