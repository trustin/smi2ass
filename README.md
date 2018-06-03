# smi2ass

`smi2ass` is a command-line tool that converts SAMI to SSA/ASS (SubStation Alpha).

[Download the executable](https://github.com/trustin/smi2ass/releases) and run it with `.smi` file paths:

```
$ smi2ass my_subtitles.smi
```

`smi2ass` will convert the specified `.smi` files into `.ass` files. It will also generate multiple `.ass` files
if the `.smi` file contains the subtitles of multiple languages.

```
$ ls my_subtitles.*
my_subtitles.eng.ass
my_subtitles.kor.ass
```

## Supported tags

`smi2ass` supports `<p>`, `<br>`, `<b>`. `<i>`, `<u>`, `<s>`, `<font>` and `<rt>` (Ruby tags).

## Fixing a bad SAMI file

`smi2ass` will not output anything if the conversion went OK. It prints the problematic SAMI fragment if it failed the conversion,
so you can find the location of the problem in your `.smi` file, fix it and run again:

```
$ smi2ass my_bad_subtitles.smi
Failed to extract time code: <sync star=1234>
```

## Credits

The conversion script was initially forked from https://github.com/hojel/service.subtitles.gomtv/tree/3a7342961e140eaf8250659b0ac6158ce5e6bc5c/resources/lib. Since then, [@trustin](https://github.com/trustin) made the following changes:

- Added Ruby tag support
- Improved the preservation of white spaces
- Packaged into a single executable
- Updated Python from 2 to 3
- Updated BeautifulSoup from 3 to 4
- Miscellaneous cleanup
