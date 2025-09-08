# ParseDAT Bedrock

A command line utility that reads a Minecraft Bedrock `level.dat` file (Little-Endian NBT) and outputs the data as JSON.

## Usage

```bash
parsedat-bedrock /path/to/level.dat --out world.json --pretty
parsedat-bedrock /path/to/level.dat --stdout
parsedat-bedrock /path/to/level.dat --preserve-types --pretty
```

## Features

* Automatically detect compression algorithm: gzip, zlib, or uncompressed
* Parse NBT tags (0..12): `End`, `Byte`, `Short`, `Int`, `Long`, `Float`, `Double`,
  `Byte_Array`, `String`, `List`, `Compound`, `Int_Array`, `Long_Array`
* Emits clean JSON values (default)
* Emits typed JSON if --preserve-types flag is used
* Validates tag 0 termination (where applicable)
* No external dependencies

## Notes

This script assumes the input file is Bedrock-style NBTLE, opposed to Java’s Big-Endian NBT.

## Author

[DJ Stomp](https://github.com/DJStompZone)


## License

MIT License. See the [LICENSE](LICENSE) file for more details.
