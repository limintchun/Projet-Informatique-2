CC = g++
SRC = main.cpp encoding.cpp image.cpp pixel.cpp

FLAGS = -Werror -Wextra -Wpedantic -O2

all: 
	$(CC) $(SRC) $(FLAGS) -o ulbmp

clean:
	rm -rf *.o ulbmp
