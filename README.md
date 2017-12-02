
# edulent-asm

## Introduction

This is an assembler for the 8-bit Edulent educational microprocessor architecture.
## Usage

To compile a file to a binary,
```
$ python3 asm.py -o output.bin input.asm
```

To compile to effectively a hexdump of the binary,
```
$ python3 asm.py -x output.hex input.asm
```

## Contributing

The file `TODO.md` lists some features that still need to be implemented.
Perhaps the most important is referencing or writing a detailed description of
the instruction set.

## Bugs

This assembler is still awaiting a proper test suite, so there are almost
certainly some bugs still lurking. Feel free to report or fix them! Please use
the Github issue tracker to report bugs.

## License

edulent-asm: Assembler for the 8-bit Edulent educational CPU architecture.
Copyright (C) 2017 Zack Marvel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
