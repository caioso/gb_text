./scripts/rgbpre.py -i main.z80 -o build/main.pre.z80 -I ./inc &&
rgbasm -o build/main.o build/main.pre.z80 -Weverything -Werror &&
rgblink -o build/main.gbc -m build/main.map -n build/main.sym build/main.o &&
rgbfix -v -p 0x00 build/main.gbc