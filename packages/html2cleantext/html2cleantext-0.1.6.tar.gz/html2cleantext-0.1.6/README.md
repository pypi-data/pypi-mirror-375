# html2cleantext

Convert HTML to clean, structured Markdown or plain text. Perfect for extracting readable content from web pages with robust boilerplate removal and language-aware processing.

## Features

- 🧹 **Smart Cleaning**: Automatically removes navigation, footers, ads, and other boilerplate
- 📝 **Flexible Output**: Convert to Markdown or plain text
- 🌍 **Language-Aware**: Special support for Bengali and English with automatic language detection
- 🔗 **Link Control**: Choose to keep or remove links and images
- 🚀 **Multiple Input Sources**: Process HTML strings, files, or URLs
- ⚡ **CLI & Python API**: Use from command line or integrate into your Python projects
- 📦 **Minimal Dependencies**: Modern, lightweight dependency stack

## Installation

```bash
pip install html2cleantext
```

Or install from source:

```bash
git clone https://github.com/Shawn-Imran/html2cleantext.git
cd html2cleantext
pip install -e .
```

## Quick Start

### Python API

```python
import html2cleantext

# From HTML string
html = "<h1>Hello World</h1><p>This is a test with a <a href='https://example.com'>link</a>.</p>"
markdown = html2cleantext.to_markdown(html)  # Output: ... [link](https://example.com) ...
text = html2cleantext.to_text(html, keep_links=True)  # Output: ... link [Link:https://example.com] ...

# From file
markdown = html2cleantext.to_markdown("page.html")

# From URL
markdown = html2cleantext.to_markdown("https://example.com")

# With options
clean_text = html2cleantext.to_text(
    html,
    keep_links=True,  # Use [Link:URL] format in plain text
    keep_images=False,
    remove_boilerplate=True
)
```

### Command Line Interface

```bash
# Convert to Markdown (default, links as [text](URL))
html2cleantext input.html

# Convert to plain text (links as [Link:URL])
html2cleantext input.html --mode text --keep-links

# From URL
html2cleantext https://example.com --output clean.md

# Remove links and images
html2cleantext input.html --no-links --no-images

# Keep all content (no boilerplate removal)
html2cleantext input.html --no-remove_boilerplate
```

## API Reference

### Core Functions

#### `to_markdown(html_input, **options)`

Convert HTML to clean Markdown format.

**Parameters:**
- `html_input` (str|Path): HTML string, file path, or URL
- `keep_links` (bool): Preserve links (default: True)
- `keep_images` (bool): Preserve images (default: True)
- `remove_boilerplate` (bool): Remove boilerplate content (default: True)
- `normalize_lang` (bool): Apply language normalization (default: True)
- `language` (str, optional): Language code for normalization (auto-detected if None)

**Returns:** Clean Markdown text (str)

#### `to_text(html_input, **options)`

Convert HTML to clean plain text format.

**Parameters:**
- Same as `to_markdown()` but with different defaults:
- `keep_links` (bool): Default False
- `keep_images` (bool): Default False

**Returns:** Clean plain text (str)

### CLI Options

```
positional arguments:
  input                 HTML input: file path, URL, or raw HTML string

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --mode {markdown,text}, -m {markdown,text}
                        Output format (default: markdown)
  --output OUTPUT, -o OUTPUT
                        Output file path (default: stdout)
  --keep-links          Preserve links in the output
  --no-links            Remove links from the output
  --keep-images         Preserve images in the output
  --no-images           Remove images from the output
  --remove_boilerplate   Remove navigation, footers, and boilerplate content
  --no-remove_boilerplate
                        Keep all content including navigation and footers
  --language LANGUAGE, -l LANGUAGE
                        Language code for normalization
  --no-normalize        Skip language-specific normalization
  --verbose, -v         Enable verbose logging
```

## Link Output Format

- **Markdown output**: Links are converted to standard Markdown format `[text](URL)` for compatibility with Markdown renderers.
- **Plain text and CLI output**: Links are converted to `[Link:URL]` format (e.g., `My Link [Link:https://example.com]`) for easy parsing and clear distinction from other text.

---

## Examples

### Basic Usage

```python
import html2cleantext

# Simple HTML to Markdown
html = """
<html>
<head><title>Test Page</title></head>
<body>
    <nav>Navigation menu</nav>
    <main>
        <h1>Main Title</h1>
        <p>This is the main content with a <a href=\"https://example.com\">link</a>.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
    </main>
    <footer>Footer content</footer>
</body>
</html>
"""

result_md = html2cleantext.to_markdown(html)
print(result_md)
# Output:
# Main Title
#
# This is the main content with a [link](https://example.com).
#
# * Item 1
# * Item 2

result_txt = html2cleantext.to_text(html, keep_links=True)
print(result_txt)
# Output:
# Main Title
#
# This is the main content with a link [Link:https://example.com].
#
# Item 1
# Item 2
```

### Command Line Examples

```bash
# Basic conversion (Markdown, links as [text](URL))
html2cleantext index.html > clean.md

# Plain text with links as [Link:URL]
html2cleantext index.html --mode text --keep-links > clean.txt
```

## Language Support

html2cleantext provides enhanced support for:

- **English**: Smart quote normalization, punctuation cleanup
- **Bengali**: Unicode normalization, punctuation handling
- **Auto-detection**: Automatically detects language when not specified

Additional languages can be easily added by extending the normalization functions.

## Architecture

The package follows a clean pipeline architecture:

1. **Input Processing**: Handles HTML strings, files, or URLs
2. **HTML Parsing**: Uses BeautifulSoup with lxml parser
3. **Cleaning**: Removes scripts, styles, and unwanted attributes
4. **Boilerplate Removal**: Strips navigation, footers, ads using readability-lxml or manual rules
5. **Language Detection**: Auto-detects content language
6. **Conversion**: Converts to Markdown using markdownify or extracts plain text
7. **Normalization**: Applies language-specific text cleanup
8. **Output**: Returns clean text or writes to file

## Dependencies

- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser
- `markdownify` - HTML to Markdown conversion
- `readability-lxml` - Content extraction and boilerplate removal
- `langdetect` - Language detection
- `requests` - HTTP requests for URL fetching

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

```bash
git clone https://github.com/Shawn-Imran/html2cleantext.git
cd html2cleantext
pip install -e .[dev]  # Install with development dependencies
# OR
pip install -e .  # Install package only
pip install -r requirements-dev.txt  # Install dev dependencies separately
```

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v0.1.0
- Initial release
- Core HTML to Markdown/text conversion
- Boilerplate removal using readability-lxml
- Language-aware normalization for Bengali and English
- Command-line interface
- Support for HTML strings, files, and URLs
