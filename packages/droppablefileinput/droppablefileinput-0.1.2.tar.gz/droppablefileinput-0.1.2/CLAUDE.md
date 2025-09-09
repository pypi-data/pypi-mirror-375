# DroppableFileInput Django Widget

## Project Overview
This is a custom Django form widget that enhances file upload functionality with drag-and-drop support. It provides client-side validation for file size and type, along with a modern, user-friendly interface.

## Key Features
- **Drag and Drop**: Users can drag files directly onto the upload area
- **File Validation**: Client-side validation for file size and type before upload
- **Auto-submit**: Optional automatic form submission when a file is selected
- **Internationalization**: Full i18n support with English and German translations
- **Customizable**: Flexible styling options and configurable error messages

## Technical Architecture

### Widget Structure
- `DroppableFileInput` extends Django's `ClearableFileInput`
- JavaScript handles drag/drop events and client-side validation
- CSS provides responsive styling with visual feedback

### Key Files
- `droppablefileinput/widgets.py` - Main widget class with server-side validation
- `droppablefileinput/static/droppablefileinput/js/droppable_file_input.js` - Client-side logic
- `droppablefileinput/static/droppablefileinput/css/droppable_file_input.css` - Styling
- `droppablefileinput/templates/widgets/droppable_file_input.html` - Widget template

## Development Setup

### Environment
```bash
# Create virtual environment with Python 3.11+
uv venv
source .venv/bin/activate

# Install all dependencies including dev
uv sync --all-extras
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_widgets.py
```

### Important Test Notes
- Tests use `StaticLiveServerTestCase` with Playwright for browser testing
- `conftest.py` sets `DJANGO_ALLOW_ASYNC_UNSAFE=true` to handle Django/Playwright async context issues
- This is a known limitation when using Playwright's sync_api with Django's test framework

## Validation Logic

### File Size Validation
- Supports formats: "100" (bytes), "10K", "5M", "2G"
- Case-insensitive parsing
- Both client-side (JavaScript) and server-side (Python) validation

### File Type Validation
- Comma-separated MIME types (e.g., "image/png,image/jpeg")
- Validates against file's content_type attribute
- Client-side uses file.type, server-side uses uploaded file object

## Internationalization

### Adding New Languages
1. Create message files:
   ```bash
   cd droppablefileinput
   uv run django-admin makemessages -l <language_code>
   ```

2. Edit the .po file in `droppablefileinput/locale/<language_code>/LC_MESSAGES/django.po`

3. Compile messages:
   ```bash
   uv run django-admin compilemessages
   ```

### Current Translations
- English (en) - Base language
- German (de) - Complete translation

## Release Process

### Version Bump
1. Update version in `pyproject.toml`
2. Update classifiers if Python version support changes
3. Run tests with all supported Python versions

### Build and Publish
```bash
# Build the package
uv build

# Run tests one more time
uv run pytest

# Commit and push
git add -A
git commit -m "Release vX.Y.Z - Description"
git push origin main

# Create and push tag
git tag -a vX.Y.Z -m "Version X.Y.Z - Description"
git push origin vX.Y.Z

# Publish to PyPI
UV_PUBLISH_TOKEN=$(grep -A2 "\[pypi\]" ~/.pypirc | grep "password" | cut -d'=' -f2 | xargs) uv publish

# Create GitHub release
gh release create vX.Y.Z --title "vX.Y.Z - Title" --notes "Release notes..."
```

## Widget Options

### Constructor Parameters
- `auto_submit` (bool): Submit form automatically on file selection
- `max_file_size` (str): Maximum file size (e.g., "10M", "1K")
- `allowed_types` (str): Comma-separated MIME types
- `icon_url` (str): Custom icon URL (defaults to included SVG)
- `icon_width/height` (int): Icon dimensions (default 32x32)
- `drop_text` (str): Main instruction text
- `link_text` (str): Link text in instruction
- `description_text` (str): Additional description
- `instructions` (str): Custom instructions below main text
- `max_size_error_message` (str): Custom file size error
- `invalid_file_type_error_message` (str): Custom file type error

## Example Usage

### Basic Usage
```python
from django import forms
from droppablefileinput.widgets import DroppableFileInput

class UploadForm(forms.Form):
    file = forms.FileField(widget=DroppableFileInput())
```

### Advanced Configuration
```python
class UploadForm(forms.Form):
    file = forms.FileField(
        widget=DroppableFileInput(
            auto_submit=True,
            max_file_size="10M",
            allowed_types="image/png,image/jpeg,application/pdf",
            instructions="Only images and PDFs under 10MB",
            max_size_error_message="File too large! Maximum is 10MB.",
            icon_url="/static/custom-icon.svg",
            icon_width=64,
            icon_height=64,
        )
    )
```

## CSS Customization

The widget uses these main CSS classes:
- `.droppable-file-input-container` - Main container
- `.droppable-file-input-card` - Card wrapper
- `.droppable-file-input-card-body` - Inner content area
- `.droppable-file-input-label` - Label for the file input
- `.droppable-file-input-icon` - File upload icon
- `.droppable-file-input-alert` - Error message container
- `.dragging` - Applied when file is dragged over

## JavaScript Events

The widget handles these events:
- `dragenter`, `dragover` - Visual feedback when dragging
- `dragleave`, `drop` - Handle file drop
- `change` - File selection via click
- Form submission prevention during file processing

## Known Limitations

1. **Async Context in Tests**: Django's `StaticLiveServerTestCase` has issues with Playwright's async context. We use `DJANGO_ALLOW_ASYNC_UNSAFE=true` as a workaround.

2. **Browser Compatibility**: Drag and drop requires modern browser support. Older browsers fall back to standard file input.

3. **Multiple Files**: Currently only supports single file selection. Multiple file support could be added in future versions.

## Future Improvements

- [ ] Multiple file selection support
- [ ] Progress bar for file uploads
- [ ] Image preview for image files
- [ ] Chunked upload support for large files
- [ ] More language translations
- [ ] Accessibility improvements (ARIA labels)
- [ ] TypeScript version of JavaScript code

## Development Tips

1. **Testing Changes**: Always test both drag-and-drop and click-to-select methods
2. **Browser Testing**: Test in multiple browsers, especially Safari and Firefox
3. **Mobile Testing**: Ensure touch events work properly on mobile devices
4. **Translation Keys**: Keep translation keys consistent and descriptive
5. **Error Messages**: Make error messages user-friendly and actionable

## Dependencies

- Django >= 4.0
- Python >= 3.11
- No JavaScript framework dependencies (vanilla JS)

## Security Considerations

1. **Client-side validation** is for UX only - always validate on the server
2. **File type validation** should check actual content, not just extension
3. **File size limits** should be enforced at multiple levels (client, Django, web server)
4. **CSRF protection** is handled by Django's form framework

## Debugging Tips

1. **JavaScript errors**: Check browser console for client-side issues
2. **File validation**: Use browser dev tools to inspect file object properties
3. **Drag events**: Some browsers have quirks with drag event propagation
4. **Django integration**: Ensure widget is properly registered in INSTALLED_APPS

## Performance Notes

- CSS and JS files are minified in production
- Icon is inline SVG to reduce HTTP requests
- Validation is performed client-side first to reduce server load
- No external dependencies keeps bundle size minimal