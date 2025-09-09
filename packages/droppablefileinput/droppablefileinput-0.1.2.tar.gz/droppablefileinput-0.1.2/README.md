# droppablefileinput


[![Release](https://img.shields.io/github/v/release/blackbox-innovation/django-droppablefileinput)](https://img.shields.io/github/v/release/blackbox-innovation/django-droppablefileinput)
[![Build status](https://img.shields.io/github/actions/workflow/status/blackbox-innovation/django-droppablefileinput/main.yml?branch=main)](https://github.com/blackbox-innovation/django-droppablefileinput/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/blackbox-innovation/django-droppablefileinput/branch/main/graph/badge.svg)](https://codecov.io/gh/blackbox-innovation/django-droppablefileinput)
[![Commit activity](https://img.shields.io/github/commit-activity/m/blackbox-innovation/django-droppablefileinput)](https://img.shields.io/github/commit-activity/m/blackbox-innovation/django-droppablefileinput)
[![License](https://img.shields.io/github/license/blackbox-innovation/django-droppablefileinput)](https://img.shields.io/github/license/blackbox-innovation/django-droppablefileinput)


DroppableFileInput is a custom Django widget that enhances the usability of file input forms by allowing users to drag and drop files. This widget utilizes JavaScript to provide interactive feedback, such as highlighting the drop area when a file is dragged over and displaying file details on the page. This uses no external JavaScript dependencies, all functionality is brought by this package.


- **Github repository**: <https://github.com/blackbox-innovation/django-droppablefileinput/>
- **Documentation**: <https://blackbox-innovation.github.io/droppablefileinput/>

## Features

- **Drag and Drop**: Easy file uploading by dragging files into the drop area.
- **Interactive Feedback**: Highlights the drop area during a drag operation and shows file details once a file is selected.
- **Size Validation**: Validates the file size on the client side before submitting to the server.
- **Type Validation**: Ensures that only allowed file types can be uploaded.
- **Auto Submit**: Optionally auto-submits the form once a file is selected.

## Installation

To install DroppableFileInput, you can download it directly from GitHub or use pip:
```python
pip install git+https://github.com/blackbox-innovation/django-droppablefileinput.git
```


Setup
-----
After installation, add `droppablefileinput` to your `INSTALLED_APPS` in your Django settings:


```python
INSTALLED_APPS = [
...
'droppablefileinput',
...
]
```


Ensure you have Django's static file handling set up, as this widget relies on associated CSS and JavaScript files.


Usage
-----
To use the `DroppableFileInput` in your Django forms, import the widget and use it in a form field:


```python
from django import forms
from droppablefileinput.widgets import DroppableFileInput
class UploadForm(forms.Form):
file = forms.FileField(widget=DroppableFileInput())
```


In your templates, make sure to include the form's media:


```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Upload File</title>
    {{ form.media }}
  </head>
  <body>
    <form method="post" enctype="multipart/form-data">
      {% csrf_token %} {{ form.as_p }}
      <button type="submit">Upload</button>
    </form>
  </body>
</html>


```
Customization
-------------


The `DroppableFileInput` widget can be customized with the following parameters:
- `auto_submit`: Whether to auto-submit the form upon file selection.
- `max_file_size`: Maximum file size allowed for upload.
- `allowed_types`: List of allowed file MIME types.
- `icon_url`: URL to the icon image to display in the drop area.
- `icon_width`: Width of the icon image.
- `icon_height`: Height of the icon image.

Example:


```python
class UploadForm(forms.Form):
    file = forms.FileField(widget=DroppableFileInput(
    auto_submit=True,
    max_file_size="10M",
    allowed_types="image/jpeg,image/png",
    icon_url=static('images/custom-icon.svg'),
    icon_width=40,
    icon_height=40
))
```



Contributing
------------
Contributions are welcome! If you would like to contribute to this project, please follow these steps:
1. Fork the repository on GitHub.
2. Clone your forked repository to your local machine.
3. Create a new branch for your feature or fix.
4. Make changes and test.
5. Submit a pull request with a clear description of the changes and any relevant issue numbers.

License
-------
Distributed under the MIT License. See `LICENSE` file for more information.


Support
-------
If you have any issues or feature requests, please file an issue on the GitHub repository issue tracker.