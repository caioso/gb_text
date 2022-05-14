rgbasm -o main.o main.z80
rgblink -o main.gbc -m main.map -n main.sym main.o
rgbfix -v -p 0x00 main.gbc