#ifndef ENCODING_H
#define ENCODING_H

#include <string>

#include "image.h"

class Encoder {
private:
    Image image;

public:
    Encoder(Image image);
    void save_to(std::string path);
};


class Decoder {
public:
    Image load_from(std::string path);
};

#endif // ENCODING_H
