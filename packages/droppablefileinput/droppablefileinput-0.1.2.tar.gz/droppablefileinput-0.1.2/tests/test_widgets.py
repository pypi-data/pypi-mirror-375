from unittest.mock import Mock

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.forms import Form
from django.forms.fields import FileField
from django.test import TestCase, override_settings
from playwright.sync_api import sync_playwright

from droppablefileinput.widgets import DroppableFileInput


def assert_and_accept_dialog(dialog, expected_message):
    assert dialog.message == expected_message
    dialog.accept()


class TestDroppableFileInput(TestCase):
    def setUp(self):
        class TestForm(Form):
            file = FileField(
                widget=DroppableFileInput(
                    auto_submit=True,
                    max_file_size="10M",
                    allowed_types="image/png,image/jpeg",
                    icon_url="/static/droppablefileinput/images/test_icon.svg",
                    icon_width=48,
                    icon_height=48,
                )
            )

        self.form = TestForm()

    def test_widget_rendering(self):
        rendered = self.form.as_p()
        self.assertIn("Drag the file here or click", rendered)
        self.assertIn('data-auto-submit="True"', rendered)
        self.assertIn('data-max-file-size="10M"', rendered)
        self.assertIn('data-allowed-types="image/png,image/jpeg"', rendered)
        self.assertIn('src="/static/droppablefileinput/images/test_icon.svg"', rendered)
        self.assertIn('width="48"', rendered)
        self.assertIn('height="48"', rendered)

    def test_default_icon(self):
        widget = DroppableFileInput()
        context = widget.get_context("file", None, {"id": "file_id"})
        self.assertIn("/static/droppablefileinput/images/icon.svg", context["widget"]["icon_url"])
        self.assertEqual(context["widget"]["icon_width"], 32)
        self.assertEqual(context["widget"]["icon_height"], 32)

    def test_widget_attrs(self):
        widget = DroppableFileInput(attrs={"class": "custom-class", "accept": ".pdf"})
        rendered = widget.render("file", None, attrs={"id": "file_id"})
        self.assertIn('id="file_id"', rendered)

    def test_js_css_inclusion(self):
        widget = DroppableFileInput()
        media = str(widget.media)
        self.assertIn("droppablefileinput/css/droppable_file_input.css", media)
        self.assertIn("droppablefileinput/js/droppable_file_input.js", media)

    def test_template_context(self):
        widget = DroppableFileInput(auto_submit=True, max_file_size="20M", allowed_types="application/pdf")
        context = widget.get_context("file", None, {"id": "file_id"})
        self.assertEqual(context["widget"]["name"], "file")
        self.assertEqual(context["widget"]["auto_submit"], True)
        self.assertEqual(context["widget"]["max_file_size"], "20M")
        self.assertEqual(context["widget"]["allowed_types"], "application/pdf")


class TestDroppableFileInputStatic(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.page = self.browser.new_page()

    def tearDown(self):
        self.page.close()

    @override_settings(DEBUG=True)
    def test_invalid_file_type(self):
        self.page.goto(f"{self.live_server_url}/")
        input_selector = 'input[type="file"]'
        self.page.set_input_files(input_selector, {"name": "file.txt", "mimeType": "text/plain", "buffer": b"content"})

        # Handle the alert dialog
        self.page.on(
            "dialog",
            lambda dialog: assert_and_accept_dialog(dialog, "Invalid file type. Only image/png files are allowed."),
        )

        # Trigger the change event to simulate file upload
        self.page.evaluate("document.querySelector('input[type=\"file\"]').dispatchEvent(new Event('change'))")

    def test_file_size_limit(self):
        self.page.goto(f"{self.live_server_url}/")
        input_selector = 'input[type="file"]'
        self.page.set_input_files(input_selector, {"name": "file.png", "mimeType": "image/png", "buffer": b"a" * 1025})

        # Handle the alert dialog
        self.page.on(
            "dialog",
            lambda dialog: assert_and_accept_dialog(dialog, "The file is too large. The maximum file size is 1K."),
        )

        # Trigger the change event to simulate file upload
        self.page.evaluate("document.querySelector('input[type=\"file\"]').dispatchEvent(new Event('change'))")


class TestDroppableFileInputValidation(TestCase):
    def test_parse_max_size(self):
        widget = DroppableFileInput()

        # Test various size formats
        self.assertEqual(widget.parse_max_size("100"), 100)
        self.assertEqual(widget.parse_max_size("10K"), 10 * 1024)
        self.assertEqual(widget.parse_max_size("5M"), 5 * 1024 * 1024)
        self.assertEqual(widget.parse_max_size("2G"), 2 * 1024 * 1024 * 1024)

        # Test case insensitive
        self.assertEqual(widget.parse_max_size("10k"), 10 * 1024)
        self.assertEqual(widget.parse_max_size("5m"), 5 * 1024 * 1024)

        # Test invalid formats
        self.assertIsNone(widget.parse_max_size(""))
        self.assertIsNone(widget.parse_max_size(None))
        self.assertIsNone(widget.parse_max_size("10X"))
        self.assertIsNone(widget.parse_max_size("MB10"))

    def test_validate_file_size(self):
        widget = DroppableFileInput(max_file_size="1M")

        # Mock file object under limit
        small_file = Mock()
        small_file.size = 500 * 1024  # 500KB
        is_valid, error = widget.validate_file_size(small_file)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

        # Mock file object over limit
        large_file = Mock()
        large_file.size = 2 * 1024 * 1024  # 2MB
        is_valid, error = widget.validate_file_size(large_file)
        self.assertFalse(is_valid)
        self.assertIn("too large", error)

    def test_validate_file_type(self):
        widget = DroppableFileInput(allowed_types="image/png,image/jpeg")

        # Valid file type
        png_file = Mock()
        png_file.content_type = "image/png"
        is_valid, error = widget.validate_file_type(png_file)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

        # Invalid file type
        pdf_file = Mock()
        pdf_file.content_type = "application/pdf"
        is_valid, error = widget.validate_file_type(pdf_file)
        self.assertFalse(is_valid)
        self.assertIn("Invalid file type", error)

    def test_validate_combined(self):
        widget = DroppableFileInput(
            max_file_size="1M",
            allowed_types="image/png,image/jpeg"
        )

        # Valid file
        valid_file = Mock()
        valid_file.size = 500 * 1024
        valid_file.content_type = "image/png"
        is_valid, errors = widget.validate(valid_file)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Invalid file (both size and type)
        invalid_file = Mock()
        invalid_file.size = 2 * 1024 * 1024
        invalid_file.content_type = "application/pdf"
        is_valid, errors = widget.validate(invalid_file)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 2)
