# 活水 PDF 转换器 (Huoshui PDF Converter)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://github.com/modelcontextprotocol/spec)
[![PyPI version](https://badge.fury.io/py/huoshui-pdf-converter.svg)](https://pypi.org/project/huoshui-pdf-converter/)

A high-quality, cross-platform PDF ↔ Markdown converter implemented as an MCP (Model Context Protocol) server. Supports bidirectional conversion with full Unicode/CJK character support.

## Features

### Core Capabilities

- **PDF → Markdown**: Extract text and images with layout preservation
- **Markdown → PDF**: Generate beautiful PDFs with multiple rendering engines
- **Unicode Support**: Full support for Chinese, Japanese, Korean, and other Unicode characters
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **MCP Integration**: Use with Claude Desktop or any MCP-compatible client

### Technical Features

- **Pure Python**: No external system dependencies required
- **Automatic Font Detection**: Finds and uses system Unicode fonts
- **Smart Engine Selection**: Automatically switches engines based on content
- **Comprehensive Error Handling**: Graceful degradation and detailed logging
- **Async Architecture**: Non-blocking operations for better performance

## Installation

### From MCP Registry (Recommended)

This server is available in the Model Context Protocol Registry. Install it using your MCP client.

mcp-name: io.github.huoshuiai42/huoshui-pdf-converter

### As a Python Package

```bash
pip install huoshui-pdf-converter
```

Or using `uv` (recommended):

```bash
uv pip install huoshui-pdf-converter
```

### As an MCP Server

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "huoshui-pdf-converter": {
      "command": "uvx",
      "args": ["huoshui-pdf-converter"],
      "env": {}
    }
  }
}
```

Or if you prefer to use a specific Python environment:

```json
{
  "mcpServers": {
    "huoshui-pdf-converter": {
      "command": "python",
      "args": ["-m", "huoshui_pdf_converter.server"],
      "env": {}
    }
  }
}
```

## Usage

### Command Line Interface

```bash
# Convert PDF to Markdown
huoshui-pdf pdf-to-md input.pdf output.md

# Convert Markdown to PDF
huoshui-pdf md-to-pdf input.md output.pdf

# With options
huoshui-pdf md-to-pdf input.md output.pdf --page-size A4 --margin 2cm --font-size 12
```

### As a Python Library

```python
import asyncio
from huoshui_pdf_converter import PDFToMarkdownConverter, MarkdownToPDFConverter

async def main():
    # PDF to Markdown
    pdf_converter = PDFToMarkdownConverter()
    result = await pdf_converter.convert(
        pdf_path="input.pdf",
        output_path="output.md",
        extract_images=True,
        preserve_formatting=True
    )

    # Markdown to PDF
    md_converter = MarkdownToPDFConverter()
    result = await md_converter.convert(
        markdown_path="input.md",
        output_path="output.pdf",
        page_size="A4",
        margin="2cm",
        font_size=12
    )

asyncio.run(main())
```

### MCP Tools

When used as an MCP server, the following tools are available:

1. **pdf_to_markdown**: Convert PDF files to Markdown

   ```json
   {
     "pdf_path": "path/to/input.pdf",
     "output_path": "path/to/output.md",
     "extract_images": true,
     "preserve_formatting": true
   }
   ```

2. **markdown_to_pdf**: Convert Markdown files to PDF

   ```json
   {
     "markdown_path": "path/to/input.md",
     "output_path": "path/to/output.pdf",
     "page_size": "A4",
     "margin": "2cm",
     "font_size": 12
   }
   ```

3. **list_supported_formats**: Get supported formats and engines
4. **validate_file**: Validate input files before conversion

## Supported Formats

### Input Formats

- **PDF**: All standard PDF files (PDF 1.0 - 1.7)
- **Markdown**: CommonMark and GitHub Flavored Markdown

### Output Options

- **Page Sizes**: A4, A3, Letter, Legal
- **Margins**: Customizable (e.g., "1cm", "0.5in")
- **Font Sizes**: Any size in points
- **Images**: PNG, JPEG extraction from PDFs

## Unicode and Font Support

The converter automatically detects and uses appropriate fonts for different languages:

- **macOS**: Arial Unicode, PingFang SC, STHeiti
- **Windows**: Microsoft YaHei, SimSun, Arial Unicode MS
- **Linux**: Noto Sans CJK, Source Han Sans, WenQuanYi

## Architecture

### Conversion Engines

**PDF → Markdown**

- PyMuPDF (MuPDF): High-quality text and image extraction

**Markdown → PDF**

- ReportLab: Best Unicode support, cross-platform compatibility
- xhtml2pdf: Good HTML/CSS rendering (fallback)
- fpdf2: Basic PDF generation (last resort)

### Engine Selection Logic

1. Detects CJK characters → Uses ReportLab
2. Complex formatting → Uses xhtml2pdf
3. Basic documents → Uses any available engine

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/huoshui-pdf-converter.git
cd huoshui-pdf-converter

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
python test_converter.py
```

### Project Structure

```
huoshui-pdf-converter/
├── huoshui_pdf_converter/
│   ├── __init__.py
│   ├── server.py           # MCP server implementation
│   ├── pdf_converter.py    # PDF to Markdown converter
│   └── markdown_converter.py # Markdown to PDF converter
├── pyproject.toml
├── README.md
├── LICENSE
└── test_converter.py
```

## Troubleshooting

### Common Issues

1. **Chinese characters not displaying**:

   - Ensure Arial Unicode or similar fonts are installed
   - The converter will automatically detect and use appropriate fonts

2. **Import errors**:

   - Install all dependencies: `pip install huoshui-pdf-converter[all]`

3. **MCP connection issues**:
   - Check Claude Desktop logs
   - Ensure Python is in your PATH

### Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) for Model Context Protocol support
- Uses [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for PDF parsing
- Uses [ReportLab](https://www.reportlab.com/) for PDF generation
- Inspired by the need for better PDF ↔ Markdown conversion tools

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/huoshui-pdf-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/huoshui-pdf-converter/discussions)
- **Email**: your.email@example.com
