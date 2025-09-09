/**
 * DroppableFileInput - Enhanced file input widget with drag-and-drop support
 * Provides accessible, secure file upload functionality with validation
 */
class DroppableFileInput {
  constructor(element) {
    this.dropArea = element;
    this.fileInput = element.querySelector('input[type="file"]');
    this.fileInfo = element.querySelector(".droppablefileinput__label");
    this.spinner = element.querySelector(".droppablefileinput__spinner");
    this.instructions = element.querySelector(".droppablefileinput__instructions");
    this.icon = element.querySelector(".droppablefileinput__icon");
    this.errorContainer = element.querySelector(".droppablefileinput__error");
    this.clearButton = element.querySelector(".droppablefileinput__clear");
    this.filePreview = element.querySelector(".droppablefileinput__preview");
    
    // Parse configuration from data attributes
    this.config = {
      autoSubmit: this.fileInput.dataset.autoSubmit === "True",
      maxFileSize: this.parseMaxSize(this.fileInput.dataset.maxFileSize),
      allowedTypes: this.fileInput.dataset.allowedTypes ? 
        this.fileInput.dataset.allowedTypes.split(",").map(t => t.trim()) : [],
      maxSizeErrorMessage: this.fileInput.dataset.maxSizeErrorMessage,
      invalidFileTypeErrorMessage: this.fileInput.dataset.invalidFileTypeErrorMessage
    };
    
    // Track drag state for proper highlighting
    this.dragCounter = 0;
    
    // Bind methods to maintain context
    this.handleDrop = this.handleDrop.bind(this);
    this.handleDragEnter = this.handleDragEnter.bind(this);
    this.handleDragLeave = this.handleDragLeave.bind(this);
    this.handleDragOver = this.handleDragOver.bind(this);
    this.handleClick = this.handleClick.bind(this);
    this.handleFileSelect = this.handleFileSelect.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.clearSelection = this.clearSelection.bind(this);
    
    this.init();
  }
  
  init() {
    // Add ARIA attributes for accessibility
    this.dropArea.setAttribute("role", "button");
    this.dropArea.setAttribute("tabindex", "0");
    this.dropArea.setAttribute("aria-label", "Click or press Enter to select a file, or drag and drop a file here");
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Hide file input visually but keep it accessible
    this.fileInput.setAttribute("aria-hidden", "true");
    this.fileInput.style.position = "absolute";
    this.fileInput.style.left = "-9999px";
  }
  
  setupEventListeners() {
    // Drag and drop events
    this.dropArea.addEventListener("drop", this.handleDrop);
    this.dropArea.addEventListener("dragenter", this.handleDragEnter);
    this.dropArea.addEventListener("dragleave", this.handleDragLeave);
    this.dropArea.addEventListener("dragover", this.handleDragOver);
    
    // Click and keyboard events
    this.dropArea.addEventListener("click", this.handleClick);
    this.dropArea.addEventListener("keydown", this.handleKeyDown);
    
    // File input change event
    this.fileInput.addEventListener("change", this.handleFileSelect);
    
    // Clear button event
    if (this.clearButton) {
      this.clearButton.addEventListener("click", this.clearSelection);
    }
  }
  
  destroy() {
    // Remove all event listeners to prevent memory leaks
    this.dropArea.removeEventListener("drop", this.handleDrop);
    this.dropArea.removeEventListener("dragenter", this.handleDragEnter);
    this.dropArea.removeEventListener("dragleave", this.handleDragLeave);
    this.dropArea.removeEventListener("dragover", this.handleDragOver);
    this.dropArea.removeEventListener("click", this.handleClick);
    this.dropArea.removeEventListener("keydown", this.handleKeyDown);
    this.fileInput.removeEventListener("change", this.handleFileSelect);
    
    if (this.clearButton) {
      this.clearButton.removeEventListener("click", this.clearSelection);
    }
  }
  
  handleDragEnter(e) {
    e.preventDefault();
    e.stopPropagation();
    this.dragCounter++;
    this.highlight();
  }
  
  handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    this.dragCounter--;
    if (this.dragCounter === 0) {
      this.unhighlight();
    }
  }
  
  handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    this.dragCounter = 0;
    this.unhighlight();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      this.handleFiles(files);
    }
  }
  
  handleClick(e) {
    // Prevent triggering if clicking on clear button
    if (e.target.closest(".droppablefileinput__clear")) {
      return;
    }
    this.fileInput.click();
  }
  
  handleKeyDown(e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      this.fileInput.click();
    }
  }
  
  handleFileSelect(e) {
    if (e.target.files.length > 0) {
      this.handleFiles(e.target.files);
    }
  }
  
  highlight() {
    this.dropArea.classList.add("droppablefileinput__highlight");
    this.dropArea.setAttribute("aria-describedby", "drop-active");
  }
  
  unhighlight() {
    this.dropArea.classList.remove("droppablefileinput__highlight");
    this.dropArea.removeAttribute("aria-describedby");
  }
  
  parseMaxSize(sizeStr) {
    if (!sizeStr) return Infinity;
    
    const match = sizeStr.match(/^(\d+)([KMG]?)$/i);
    if (!match) return Infinity;
    
    const value = parseInt(match[1], 10);
    const unit = match[2].toUpperCase();
    
    switch (unit) {
      case "K": return value * 1024;
      case "M": return value * 1024 * 1024;
      case "G": return value * 1024 * 1024 * 1024;
      default: return value;
    }
  }
  
  formatFileSize(bytes) {
    if (bytes < 1024) return `${bytes} bytes`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  }
  
  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
  
  showError(message) {
    if (this.errorContainer) {
      this.errorContainer.textContent = message;
      this.errorContainer.style.display = "block";
      this.errorContainer.setAttribute("role", "alert");
      this.errorContainer.setAttribute("aria-live", "assertive");
    } else {
      // Fallback to console error instead of alert
      console.error("DroppableFileInput:", message);
    }
  }
  
  hideError() {
    if (this.errorContainer) {
      this.errorContainer.textContent = "";
      this.errorContainer.style.display = "none";
      this.errorContainer.removeAttribute("role");
      this.errorContainer.removeAttribute("aria-live");
    }
  }
  
  showFilePreview(file) {
    if (!this.filePreview) return;
    
    // Clear previous preview
    this.filePreview.innerHTML = "";
    
    // Show image preview for image files
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = document.createElement("img");
        img.src = e.target.result;
        img.alt = `Preview of ${this.escapeHtml(file.name)}`;
        img.className = "droppablefileinput__preview-image";
        this.filePreview.appendChild(img);
      };
      reader.readAsDataURL(file);
    }
  }
  
  validateFile(file) {
    // Check file size
    if (file.size > this.config.maxFileSize) {
      this.showError(this.config.maxSizeErrorMessage);
      return false;
    }
    
    // Check file type
    if (this.config.allowedTypes.length > 0 && !this.config.allowedTypes.includes(file.type)) {
      this.showError(this.config.invalidFileTypeErrorMessage);
      return false;
    }
    
    return true;
  }
  
  handleFiles(files) {
    const file = files[0]; // Currently only supporting single file
    
    // Clear any previous errors
    this.hideError();
    
    // Validate file
    if (!this.validateFile(file)) {
      return;
    }
    
    // Create a new FileList containing only the valid file
    const dt = new DataTransfer();
    dt.items.add(file);
    this.fileInput.files = dt.files;
    
    // Show file details
    this.showFileDetails(file);
    
    // Show preview if applicable
    this.showFilePreview(file);
    
    // Auto-submit if configured
    if (this.config.autoSubmit && this.fileInput.form) {
      this.submitForm();
    }
  }
  
  showFileDetails(file) {
    // Hide initial UI elements
    if (this.icon) this.icon.style.display = "none";
    if (this.instructions) this.instructions.style.display = "none";
    
    // Show file information (safely escaped)
    const fileName = this.escapeHtml(file.name);
    const fileSize = this.formatFileSize(file.size);
    
    this.fileInfo.textContent = `${file.name} (${fileSize})`;
    
    // Show clear button if available
    if (this.clearButton) {
      this.clearButton.style.display = "inline-block";
    }
    
    // Announce to screen readers
    this.dropArea.setAttribute("aria-label", `Selected file: ${file.name}, size: ${fileSize}. Press Enter to change selection.`);
  }
  
  clearSelection(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    // Clear file input
    this.fileInput.value = "";
    
    // Reset UI
    if (this.icon) this.icon.style.display = "";
    if (this.instructions) this.instructions.style.display = "";
    this.fileInfo.textContent = this.fileInfo.dataset.originalText || "Drag the file here or click choose file to upload.";
    
    // Hide clear button
    if (this.clearButton) {
      this.clearButton.style.display = "none";
    }
    
    // Clear preview
    if (this.filePreview) {
      this.filePreview.innerHTML = "";
    }
    
    // Clear errors
    this.hideError();
    
    // Reset aria label
    this.dropArea.setAttribute("aria-label", "Click or press Enter to select a file, or drag and drop a file here");
  }
  
  submitForm() {
    // Verify CSRF token exists
    const form = this.fileInput.form;
    const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]');
    
    if (!csrfToken) {
      console.error("CSRF token not found. Form submission blocked for security.");
      return;
    }
    
    // Show loading state
    if (this.spinner) {
      this.spinner.style.display = "inline-block";
    }
    
    // Submit the form
    form.submit();
  }
}

// Initialize all DroppableFileInput widgets when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  const widgets = document.querySelectorAll(".droppablefileinput__card");
  
  widgets.forEach(widget => {
    // Store instance on element for later access/cleanup
    widget._droppableFileInput = new DroppableFileInput(widget);
  });
  
  // Clean up on page unload to prevent memory leaks
  window.addEventListener("beforeunload", () => {
    widgets.forEach(widget => {
      if (widget._droppableFileInput) {
        widget._droppableFileInput.destroy();
      }
    });
  });
});