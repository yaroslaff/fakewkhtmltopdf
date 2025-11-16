#!/usr/bin/env python3
"""Command-line interface that simulates wkhtmltopdf using plutoprint."""

import argparse
import sys
import os
import logging
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

try:
    import plutoprint
except ImportError:
    print("Error: plutoprint is not installed. Please install it with: pip install plutoprint", file=sys.stderr)
    sys.exit(1)


def setup_logger():
    """Set up logger to write to ~/.wkhtmltopdf.log"""
    log_file = Path.home() / '.wkhtmltopdf.log'
    
    # Create logger
    logger = logging.getLogger('fakewkhtmltopdf')
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create file handler
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger


def parse_args():
    """Parse command-line arguments compatible with wkhtmltopdf."""
    parser = argparse.ArgumentParser(
        description='Simulate wkhtmltopdf using plutoprint',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  fakewkhtmltopdf input.html output.pdf
  fakewkhtmltopdf --page-size A4 --orientation Portrait input.html output.pdf
  fakewkhtmltopdf --margin-top 20mm --margin-bottom 20mm input.html output.pdf
        '''
    )
    
    # Input and output (positional arguments like wkhtmltopdf)
    parser.add_argument('input', nargs='?', help='Input HTML file or URL')
    parser.add_argument('output', nargs='?', help='Output PDF file')
    
    # Page options
    parser.add_argument('--page-size', '--page-size', dest='page_size',
                       choices=['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9',
                                'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10',
                                'C5E', 'Comm10E', 'DLE', 'Executive', 'Folio', 'Ledger',
                                'Legal', 'Letter', 'Tabloid'],
                       default='A4', help='Set paper size (default: A4)')
    parser.add_argument('--orientation', choices=['Portrait', 'Landscape'],
                       default='Portrait', help='Set orientation (default: Portrait)')
    
    # Margin options
    parser.add_argument('--margin-top', dest='margin_top', default='10mm',
                       help='Set the page top margin (default: 10mm)')
    parser.add_argument('--margin-right', dest='margin_right', default='10mm',
                       help='Set the page right margin (default: 10mm)')
    parser.add_argument('--margin-bottom', dest='margin_bottom', default='10mm',
                       help='Set the page bottom margin (default: 10mm)')
    parser.add_argument('--margin-left', dest='margin_left', default='10mm',
                       help='Set the page left margin (default: 10mm)')
    
    # Other common options
    parser.add_argument('--zoom', type=float, default=1.0,
                       help='Zoom factor (default: 1.0)')
    parser.add_argument('--dpi', type=int, default=96,
                       help='Change the dpi explicitly (default: 96)')
    parser.add_argument('--disable-smart-shrinking', dest='enable_smart_shrinking',
                       action='store_false', default=True,
                       help='Disable the intelligent shrinking strategy')
    parser.add_argument('--enable-smart-shrinking', dest='enable_smart_shrinking',
                       action='store_true', default=True,
                       help='Enable the intelligent shrinking strategy (default)')
    parser.add_argument('--no-images', dest='load_images', action='store_false',
                       default=True, help='Do not load or print images')
    parser.add_argument('--images', dest='load_images', action='store_true',
                       default=True, help='Load or print images (default)')
    parser.add_argument('--disable-javascript', dest='enable_javascript',
                       action='store_false', default=True,
                       help='Do not allow web pages to run javascript')
    parser.add_argument('--enable-javascript', dest='enable_javascript',
                       action='store_true', default=True,
                       help='Allow web pages to run javascript (default)')
    parser.add_argument('--no-stop-slow-scripts', dest='stop_slow_scripts',
                       action='store_false', default=True,
                       help='Do not stop slow running javascripts')
    parser.add_argument('--stop-slow-scripts', dest='stop_slow_scripts',
                       action='store_true', default=True,
                       help='Stop slow running javascripts (default)')
    parser.add_argument('--encoding', default='utf-8',
                       help='Set the default text encoding (default: utf-8)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Be less verbose')
    parser.add_argument('--debug-javascript', dest='debug_javascript',
                       action='store_true', help='Show javascript debugging output')
    parser.add_argument('--title', help='The title of the generated pdf file')
    parser.add_argument('--grayscale', action='store_true',
                       help='PDF will be generated in grayscale')
    parser.add_argument('--lowquality', action='store_true',
                       help='Generates lower quality pdf/ps')
    parser.add_argument('--print-media-type', dest='print_media_type',
                       action='store_true', default=False,
                       help='Use print media-type instead of screen')
    parser.add_argument('--no-print-media-type', dest='print_media_type',
                       action='store_false', default=False,
                       help='Do not use print media-type (default)')
    
    # Viewport and window size
    parser.add_argument('--viewport-size', dest='viewport_size',
                       help='Set viewport size if you have custom scrollbars or css attribute e.g. "1024x768"')
    parser.add_argument('--window-status', dest='window_status',
                       help='Wait until window.status is equal to this string before rendering page')
    
    # Header and footer
    parser.add_argument('--header-left', dest='header_left',
                       help='Left aligned header text')
    parser.add_argument('--header-center', dest='header_center',
                       help='Centered header text')
    parser.add_argument('--header-right', dest='header_right',
                       help='Right aligned header text')
    parser.add_argument('--header-spacing', dest='header_spacing', type=float,
                       help='Spacing between header and content in mm')
    parser.add_argument('--header-line', dest='header_line', action='store_true',
                       help='Display line above the header')
    parser.add_argument('--footer-left', dest='footer_left',
                       help='Left aligned footer text')
    parser.add_argument('--footer-center', dest='footer_center',
                       help='Centered footer text')
    parser.add_argument('--footer-right', dest='footer_right',
                       help='Right aligned footer text')
    parser.add_argument('--footer-spacing', dest='footer_spacing', type=float,
                       help='Spacing between footer and content in mm')
    parser.add_argument('--footer-line', dest='footer_line', action='store_true',
                       help='Display line above the footer')
    
    # TOC (Table of Contents) - basic support
    parser.add_argument('--toc', action='store_true',
                       help='Insert a table of contents in the generated pdf')
    parser.add_argument('--toc-depth', dest='toc_depth', type=int, default=3,
                       help='For the TOC, specify the depth of the toc (default: 3)')
    
    # Cover page
    parser.add_argument('--cover', help='Use a HTML page as cover')
    
    # Outline options
    parser.add_argument('--outline', action='store_true', default=True,
                       help='Put an outline into the pdf (default)')
    parser.add_argument('--no-outline', dest='outline', action='store_false',
                       help='Do not put an outline into the pdf')
    parser.add_argument('--outline-depth', dest='outline_depth', type=int, default=4,
                       help='Set the depth of the outline (default: 4)')
    
    # Cookie and authentication
    parser.add_argument('--cookie', action='append', dest='cookies',
                       help='Set an additional cookie (repeatable), value should be url encoded.')
    parser.add_argument('--custom-header', action='append', dest='custom_headers',
                       help='Set an additional HTTP header (repeatable)')
    parser.add_argument('--custom-header-propagation', dest='custom_header_propagation',
                       action='store_true', default=False,
                       help='Add HTTP headers defined by --custom-header for each resource request.')
    parser.add_argument('--no-custom-header-propagation', dest='custom_header_propagation',
                       action='store_false', default=False,
                       help='Do not add HTTP headers for each resource request (default)')
    
    # User agent
    parser.add_argument('--user-style-sheet', dest='user_style_sheet',
                       help='Specify a user style sheet, to load with every page')
    
    # Additional options
    parser.add_argument('--allow', action='append', dest='allowed_paths',
                       help='Allow the file or files from the specified folder to be loaded')
    parser.add_argument('--disable-local-file-access', dest='allow_local_file_access',
                       action='store_false', default=True,
                       help='Do not allowed conversion of a local file to read in other local files')
    parser.add_argument('--enable-local-file-access', dest='allow_local_file_access',
                       action='store_true', default=True,
                       help='Allowed conversion of a local file to read in other local files (default)')
    
    return parser.parse_args()


def parse_size(size_str):
    """Parse size string (e.g., '10mm', '1in', '20px') to pixels or mm."""
    if not size_str:
        return None
    
    size_str = size_str.strip().lower()
    
    # Try to extract number and unit
    if size_str.endswith('mm'):
        return float(size_str[:-2])
    elif size_str.endswith('cm'):
        return float(size_str[:-2]) * 10
    elif size_str.endswith('in'):
        return float(size_str[:-2]) * 25.4
    elif size_str.endswith('px'):
        return float(size_str[:-2]) * 0.264583  # Convert px to mm (assuming 96dpi)
    else:
        # Try to parse as number (assume mm)
        try:
            return float(size_str)
        except ValueError:
            return None


def is_url(path):
    """Check if the input is a URL."""
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def read_input(input_path):
    """Read input from file or URL."""
    if is_url(input_path):
        import urllib.request
        with urllib.request.urlopen(input_path) as response:
            return response.read().decode('utf-8')
    else:
        input_file = Path(input_path)
        if not input_file.exists():
            print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
            sys.exit(1)
        return input_file.read_text(encoding='utf-8')


def build_plutoprint_options(args):
    """Build options dictionary for plutoprint from parsed arguments."""
    options = {}
    
    # Page size and orientation
    options['page_size'] = args.page_size
    options['orientation'] = args.orientation.lower()
    
    # Margins
    options['margin_top'] = parse_size(args.margin_top) or 10
    options['margin_right'] = parse_size(args.margin_right) or 10
    options['margin_bottom'] = parse_size(args.margin_bottom) or 10
    options['margin_left'] = parse_size(args.margin_left) or 10
    
    # Zoom and DPI
    if args.zoom != 1.0:
        options['zoom'] = args.zoom
    if args.dpi != 96:
        options['dpi'] = args.dpi
    
    # Other options that plutoprint might support
    if hasattr(plutoprint, 'PDF') and hasattr(plutoprint.PDF, '__init__'):
        # Try to pass additional options if plutoprint supports them
        if args.grayscale:
            options['grayscale'] = True
        if args.lowquality:
            options['quality'] = 'low'
        if args.title:
            options['title'] = args.title
    
    return options


def main():
    """Main entry point for the CLI."""
    # Set up logger
    logger = setup_logger()
    
    # Log full command line (sys.argv)
    timestamp = datetime.now().isoformat()
    logger.info(f"=== {timestamp} ===")
    logger.info(f"Full command line: {' '.join(sys.argv)}")
    
    args = parse_args()
    
    # Check if input and output are provided
    if not args.input:
        print("Error: Input file or URL is required.", file=sys.stderr)
        print("Usage: fakewkhtmltopdf [options] <input> <output>", file=sys.stderr)
        sys.exit(1)
    
    if not args.output:
        print("Error: Output PDF file is required.", file=sys.stderr)
        print("Usage: fakewkhtmltopdf [options] <input> <output>", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"Converting {args.input} to {args.output}...", file=sys.stderr)
    
    try:
        # Build options for plutoprint
        options = build_plutoprint_options(args)
        
        # Log parsed options and plutoprint options
        logger.info(f"Input: {args.input}")
        logger.info(f"Output: {args.output}")
        
        # Log command-line arguments (filter out None values and internal argparse attributes)
        cmd_args = {k: v for k, v in vars(args).items() 
                   if v is not None and not k.startswith('_')}
        logger.info(f"Command-line options: {cmd_args}")
        logger.info(f"Plutoprint options: {options}")
        
        # Generate PDF using plutoprint
        # plutoprint uses Book class: Book() -> load_html() or load_url() -> write_to_pdf()
        try:
            if hasattr(plutoprint, 'Book'):
                # Use the Book class (correct plutoprint API)
                book = plutoprint.Book()
                
                # Track which options were actually applied
                applied_options = []
                
                # Apply options if supported
                # Note: plutoprint Book may have different option names
                # We'll try to set common options if the Book class supports them
                if hasattr(book, 'set_page_size') and args.page_size:
                    try:
                        book.set_page_size(args.page_size)
                        applied_options.append(f"set_page_size({args.page_size})")
                    except (AttributeError, TypeError):
                        pass
                
                if hasattr(book, 'set_orientation') and args.orientation:
                    try:
                        book.set_orientation(args.orientation.lower())
                        applied_options.append(f"set_orientation({args.orientation.lower()})")
                    except (AttributeError, TypeError):
                        pass
                
                if applied_options:
                    logger.info(f"Applied to Book object: {', '.join(applied_options)}")
                
                # Load content - use load_url for URLs, load_html for file content
                if is_url(args.input):
                    logger.info(f"Loading URL: {args.input}")
                    book.load_url(args.input)
                else:
                    # Read HTML content from file
                    logger.info(f"Loading HTML file: {args.input}")
                    html_content = read_input(args.input)
                    book.load_html(html_content)
                
                # Write to PDF
                logger.info(f"Writing PDF to: {args.output}")
                book.write_to_pdf(args.output)
                
            elif hasattr(plutoprint, 'PDF'):
                # Fallback: Try PDF class if it exists
                pdf_class = plutoprint.PDF
                html_content = read_input(args.input)
                try:
                    pdf = pdf_class(html_content, **options)
                    pdf.write(args.output)
                except (TypeError, ValueError):
                    pdf = pdf_class(**options)
                    if hasattr(pdf, 'add_html'):
                        pdf.add_html(html_content)
                    pdf.write(args.output)
                    
            elif hasattr(plutoprint, 'pdf_from_html'):
                # Fallback: Function-based API
                html_content = read_input(args.input)
                plutoprint.pdf_from_html(html_content, args.output, **options)
            elif hasattr(plutoprint, 'convert'):
                # Fallback: Convert function
                html_content = read_input(args.input)
                plutoprint.convert(html_content, args.output, **options)
            elif hasattr(plutoprint, 'html_to_pdf'):
                # Fallback: html_to_pdf function
                html_content = read_input(args.input)
                plutoprint.html_to_pdf(html_content, args.output, **options)
            else:
                raise AttributeError("plutoprint module does not have Book, PDF, or conversion functions")
                
        except Exception as api_error:
            print(f"Error using plutoprint API: {str(api_error)}", file=sys.stderr)
            print("Please check plutoprint documentation for the correct API usage.", file=sys.stderr)
            if args.debug_javascript:
                import traceback
                traceback.print_exc()
            raise
        
        if not args.quiet:
            print(f"Successfully created {args.output}", file=sys.stderr)
        
        logger.info(f"Success: PDF created at {args.output}")
        logger.info("")  # Empty line for readability
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg, file=sys.stderr)
        logger.error(f"Failed: {error_msg}")
        if args.debug_javascript:
            import traceback
            traceback.print_exc()
            logger.error(f"Traceback: {traceback.format_exc()}")
        logger.info("")  # Empty line for readability
        sys.exit(1)


if __name__ == '__main__':
    main()

