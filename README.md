# fakewkhtmltopdf

A Python package that simulates the `wkhtmltopdf` utility, accepting the same command-line options and arguments, but using [plutoprint](https://plutoprint.readthedocs.io/) under the hood for PDF generation.

## Installation

Install from a Git repository using `pipx`:

```bash
pipx install git+https://github.com/yourusername/fakewkhtmltopdf.git
```

Or install using `pip`:

```bash
pip install git+https://github.com/yourusername/fakewkhtmltopdf.git
```

## Usage

After installation, you can use `wkhtmltopdf` command just like the original utility:

```bash
# Basic usage
wkhtmltopdf input.html output.pdf

# With options
wkhtmltopdf --page-size A4 --orientation Portrait input.html output.pdf

# With margins
wkhtmltopdf --margin-top 20mm --margin-bottom 20mm input.html output.pdf

# From URL
wkhtmltopdf https://example.com/page.html output.pdf
```

## Supported Options

This package supports most common `wkhtmltopdf` options:

### Page Options
- `--page-size`: Set paper size (A4, Letter, etc.)
- `--orientation`: Set orientation (Portrait, Landscape)

### Margin Options
- `--margin-top`, `--margin-right`, `--margin-bottom`, `--margin-left`: Set page margins

### Other Options
- `--zoom`: Zoom factor
- `--dpi`: DPI setting
- `--grayscale`: Generate grayscale PDF
- `--title`: Set PDF title
- `--quiet`: Be less verbose
- And many more...

## How It Works

This package:
1. Parses command-line arguments using the same interface as `wkhtmltopdf`
2. Maps those options to `plutoprint` API calls
3. Generates the PDF using `plutoprint` instead of the actual `wkhtmltopdf` binary

## Requirements

- Python 3.7+
- plutoprint

## License

MIT

