from django import forms
from django.shortcuts import render

from droppablefileinput.widgets import DroppableFileInput


class UploadFileForm(forms.Form):
    file = forms.FileField(
        widget=DroppableFileInput(
            instructions="Only PNG files are allowed and the maximum file size is 1KB",
            auto_submit=True,
            allowed_types="image/png",
            max_file_size="1K",
        )
    )


def home(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES["file"]
            file_name = uploaded_file.name
            file_size = uploaded_file.size
            # Handle the uploaded file here for demonstration purposes
            return render(request, "home.html", {"form": form, "file_name": file_name, "file_size": file_size})
    else:
        form = UploadFileForm()
    return render(request, "home.html", {"form": form})
