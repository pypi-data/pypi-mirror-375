import logging
from ..shared.base_playwright import BasePlaywrightComputer

logger = logging.getLogger(__name__)


class LocalPlaywrightBrowser(BasePlaywrightComputer):
    """Launches a local Chromium instance using Playwright."""

    def __init__(self, start_url: str, headless: bool = False):
        super().__init__()
        self.headless = headless
        self.start_url = start_url

    def _get_browser_and_page(self):
        """Create a Chromium browser and page using Playwright."""
        try:
            from playwright.sync_api import Browser, Page  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "Playwright is required for LocalPlaywrightBrowser. "
                "Install it with:\n\n"
                "   pip install 'playwright>=1.40'\n"
                "   python -m playwright install\n"
            ) from e

        width, height = self.get_dimensions()
        launch_args = [
            f"--window-size={width},{height}",
            "--disable-extensions",
            "--disable-file-system",
        ]
        browser: Browser = self._playwright.chromium.launch(
            chromium_sandbox=True,
            headless=self.headless,
            args=launch_args,
            env={"DISPLAY": ":0"},
        )

        context = browser.new_context()

        # Add event listeners for page creation and closure
        context.on("page", self._handle_new_page)

        page: Page = context.new_page()
        page.set_viewport_size({"width": width, "height": height})
        page.on("close", self._handle_page_close)
        page.goto(self.start_url)

        return browser, page

    def _handle_new_page(self, page):
        """Handle the creation of a new page."""
        logger.debug("New page created")
        self._page = page
        page.on("close", self._handle_page_close)

    def _handle_page_close(self, page):
        """Handle the closure of a page."""
        logger.debug("Page closed")
        if self._page == page:
            if self._browser.contexts[0].pages:
                self._page = self._browser.contexts[0].pages[-1]
            else:
                logger.debug("Warning: All pages have been closed.")
                self._page = None
