import os

# Set DJANGO_ALLOW_ASYNC_UNSAFE for tests to avoid async context issues
# This is needed for Django's StaticLiveServerTestCase when used with Playwright
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
