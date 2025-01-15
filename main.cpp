#include <iostream>
#include "pixel.h"
#include "image.h"
#include "encoding.h"

// test pixel 
int main() {
    Pixel pixel(1, 2, 3);
    Pixel pix(3, 2, 1);

    bool up= pixel == pix;
    bool azer = pixel != pix;
    std::cout << "red = " << pixel.getRed(pixel) << std::endl;
    std::cout << "greed = " << pixel.getGreen(pixel) << std::endl;
    std::cout << "blue = " << pixel.getBlue(pixel) << std::endl;

    std::cout << "pixel == pix ?" << up<< std::endl;
    std::cout << "pixel != pix ?" << azer << std::endl;


    std::vector<Pixel>vec = {pixel, pix};
    Image image(1, 2, vec);
    
    for (long unsigned int i = 0; i < vec.size(); i++) {
        std::cout << vec[i].getRed(vec[i]) << std::endl;
    }
    std::cout << image.getWidth() << std::endl;
    std::cout << image.getHeight() << std::endl;
    // std::cout << image.getPixel() << std::endl;
    return 0;
}
