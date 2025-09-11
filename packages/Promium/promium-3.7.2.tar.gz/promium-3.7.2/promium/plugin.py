import datetime
import io
import logging
import os
from _pytest.config import Config
from _pytest.runner import CallInfo
from typing import NamedTuple

import allure
import pytest
import urllib3
from selenium.common.exceptions import WebDriverException
from urllib3 import PoolManager

from promium.common import upload_screenshot
from promium.device_config import CHROME_DESKTOP_1920_1080, DesktopDevice
from promium.exceptions import BrowserConsoleException, PromiumException
from promium.logger import Logger
from promium.test_case import create_driver


log = logging.getLogger(__name__)


class FailInfoSelenium(NamedTuple):
    test_type: str
    url: str
    screenshot: str
    test_case: str
    run_command: str
    txid: str


class FailInfoRequest(NamedTuple):
    test_type: str
    url: str
    test_case: str
    status_code: str
    run_command: str
    txid: str


DEFAULT_HEADERS = {
    "Accept-Encoding": "gzip, deflate",
    "Accept": "*/*",
    "Connection": "keep-alive",
}


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--capturelog",
        dest="logger",
        default=None,
        action="store_true",
        help="Show log messages for each failed test",
    )
    parser.addoption(
        "--fail-debug-info",
        action="store_true",
        help="Show screenshot and test case urls for each failed test",
    )
    parser.addoption(
        "--duration-time", action="store_true", help="Show the very slow test"
    )
    parser.addoption(
        "--allure-report", action="store_true", help="Generate allure report"
    )
    parser.addoption(
        "--highlight", action="store_true", help="Highlighting elements"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Enable headless mode for Chrome browser only",
    )
    parser.addoption("--chrome", action="store_true", help="Use chrome browser")
    parser.addoption(
        "--firefox", action="store_true", help="Use firefox browser"
    )
    parser.addoption("--opera", action="store_true", help="Use opera browser")
    parser.addoption(
        "--repeat",
        action="store",
        default=1,
        type=int,
        metavar="repeat",
        help="Number of times to repeat each test. Mostly for debug purposes",
    )
    parser.addoption(
        "--check-console",
        action="store_true",
        help="Check browser console js and other errors",
    )
    parser.addoption(
        "-R",
        "--replace-headless",
        action="store",
        help=(
            """ When selenium tests running in Chrome Headless mode,
            the Headless browser can recognized as a bot,
            so we change the agent's username to a real one.
            By default user agent contains something like
            "HeadlessChrome/86.0.4240.75", but we need "Chrome/86.0.4240.75"
            You need to specify the Chrome version. """
        ),
    )


@pytest.fixture
def request_init(request: pytest.FixtureRequest) -> PoolManager:
    def _get_fail_debug(request: pytest.FixtureRequest) -> FailInfoRequest:
        """Failed test report generator"""
        if hasattr(request.config, "get_failed_test_command"):
            run_command = request.config.get_failed_test_command(request)
        else:
            run_command = "Please, add run command in your fixture."

        session = request.cls.session
        if session and not hasattr(session, "status_code"):
            session.status_code = None

        return FailInfoRequest(
            test_type="request",
            url=(session.url, [None])[0],
            test_case=(request.cls.test_case_url, [None])[0],
            status_code=(session.status_code, [None])[0],
            run_command=(run_command, [None])[0],
            txid=(request.cls.xrequestid, [None])[0],
        )

    session = urllib3.PoolManager(
        cert_reqs=False,
        timeout=15,
        headers=DEFAULT_HEADERS,
    )
    session.url = (
        "Use self.get_response(url) for request tests or "
        "util methods for api tests!"
    )
    request.cls.session = session
    request.config.get_fail_debug = _get_fail_debug
    request.config.assertion_errors = request.cls.assertion_errors = []
    yield session
    request.cls.xrequestid = None


@pytest.fixture
def driver_init(request: pytest.FixtureRequest) -> FailInfoSelenium:
    def _get_screenshot_png() -> bytes | str:
        try:
            return driver.get_screenshot_as_png()
        except Exception as e:
            log.error(f"[PROMIUM] Have problem with make screenshot: {e}")
            return "Error"

    def _get_fail_debug(request: pytest.FixtureRequest) -> FailInfoSelenium:
        """Failed test report generator"""
        driver = request.config.driver

        alerts = 0
        try:
            while driver.switch_to.alert:
                alert = driver.switch_to.alert
                alerts += 1
                alert.dismiss()
        except Exception:
            if alerts != 0:
                pass
        try:
            url = driver.current_url
        except Exception as e:
            url = str(e)
        screenshot = upload_screenshot(driver)

        if hasattr(request.config, "get_failed_test_command"):
            run_command = request.config.get_failed_test_command(request)
        else:
            run_command = "Please, add run command in your fixture."

        return FailInfoSelenium(
            test_type="selenium",
            url=(url, [None])[0],
            screenshot=(screenshot, [None])[0],
            test_case=(request.cls.test_case_url, [None])[0],
            run_command=(run_command, [None])[0],
            txid=(request.cls.xrequestid, [None])[0],
        )

    def _is_skipped_error(request: pytest.FixtureRequest, error: str) -> bool:
        for msg in request.cls.excluded_browser_console_errors:
            if msg["msg"] in error and msg["comment"]:
                return True
        return False

    def _check_console_errors(request: pytest.FixtureRequest) -> list:
        driver = request.config
        if hasattr(driver, "console_errors"):
            if driver.console_errors:
                browser_console_errors = driver.console_errors
                if hasattr(request.cls, "excluded_browser_console_errors"):
                    if request.cls.excluded_browser_console_errors:
                        try:
                            return list(
                                filter(
                                    lambda err: not _is_skipped_error(
                                        request, err
                                    ),
                                    browser_console_errors,
                                )
                            )
                        except Exception as e:
                            raise PromiumException(
                                "Please check your excluded errors list. "
                                f"Original exception is: {e}"
                            )
                return browser_console_errors
        return []

    mark = request.node.get_closest_marker("device")
    device = mark.args[0] if mark else CHROME_DESKTOP_1920_1080
    replacement_version = request.config.getoption("--replace-headless")
    if hasattr(device, "user_agent") and replacement_version:
        if not device.user_agent and "chrome" in os.environ.get("SE_DRIVER"):
            user_agent = (
                f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                f"(KHTML, like Gecko) "
                f"Chrome/{replacement_version} Safari/537.36"
            )
            device = DesktopDevice(1920, 1080, user_agent)

    request.cls.device = device
    if hasattr(request.config, "proxy_server"):
        proxy_server = request.config.proxy_server
    else:
        proxy_server = None
    browser_options = getattr(request.config, "browser_options", None)
    driver = create_driver(
        device,
        proxy_server=proxy_server,
        browser_options=browser_options,
    )
    driver.xrequestid = request.cls.xrequestid
    request.cls.driver = request.config.driver = driver
    request.config.get_fail_debug = _get_fail_debug
    request.config.get_screenshot_png = _get_screenshot_png
    request.config.check_console_errors = _check_console_errors
    request.config.assertion_errors = request.cls.assertion_errors = []
    request.config.console_errors = driver.console_errors = []
    yield driver
    driver.xrequestid = request.cls.xrequestid = None
    request.config.console_errors = driver.console_errors = []
    try:
        driver.close()
        driver.quit()
    except WebDriverException as e:
        log.error(f"[PROMIUM] Original webdriver exception: {e}")


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if metafunc.config.option.repeat > 1:
        metafunc.fixturenames.append("repeat")
        metafunc.parametrize("repeat", range(metafunc.config.option.repeat))


@pytest.fixture(autouse=True)
def logger(request: pytest.FixtureRequest) -> logging.Logger:
    return logging.getLogger()


def color_msg(msg: str, color: str = "bold red") -> str:
    if os.getenv("PROMIUM_ASSERTION_PANEL_MONO_COLOR", False):  # noqa: PLW1508
        return msg
    return f"[{color}]{msg}[/{color}]"


@pytest.mark.trylast
def pytest_runtest_call(item: pytest.Item) -> None:
    separator = "-" * 46
    if PANEL_WIDTH := os.getenv("PROMIUM_ASSERTION_PANEL_WIDTH"):
        from rich.console import Console  # noqa: PLC0415
        from rich.panel import Panel  # noqa: PLC0415
        from rich.text import Text  # noqa: PLC0415

        try:
            terminal_width = os.get_terminal_size().columns
        except Exception:
            terminal_width = 120

        try:
            PANEL_WIDTH = int(PANEL_WIDTH)
            if PANEL_WIDTH < 0 or terminal_width < PANEL_WIDTH:
                PANEL_WIDTH = terminal_width
        except Exception:
            PANEL_WIDTH = terminal_width
    if os.getenv("PROMIUM_ASSERTION_PANEL_MONO_COLOR", False):  # noqa: PLW1508
        border_style = "none"
    else:
        border_style = "red"

    if hasattr(item.config, "assertion_errors"):
        if item.config.assertion_errors:
            if PANEL_WIDTH:
                string_io = io.StringIO()
                console = Console(
                    file=string_io,
                    force_terminal=True,
                    width=PANEL_WIDTH - 5,
                )
                for error_text in item.config.assertion_errors:
                    rich_panel = Panel(
                        Text(error_text.strip(), justify="left"),
                        title=color_msg("Soft Assertion Error"),
                        border_style=border_style,
                        padding=(1, 2),
                    )
                    console.print(rich_panel)
                rich_output = string_io.getvalue()
                raise AssertionError(f"\n{rich_output}")
            else:  # noqa: RET506
                assertion_errors_list = f"{separator}\n".join(
                    item.config.assertion_errors
                )
                msg = f"\n{separator}\n{assertion_errors_list}{separator}\n"
                raise AssertionError(msg)

    if item.config.getoption("--check-console"):
        if hasattr(item.config, "check_console_errors"):
            if console_errors := item.config.check_console_errors(item):
                if PANEL_WIDTH:
                    string_io = io.StringIO()
                    console = Console(
                        file=string_io,
                        force_terminal=True,
                        width=PANEL_WIDTH - 5,
                    )
                    for error_text in console_errors:
                        rich_panel = Panel(
                            Text(error_text.strip(), justify="left"),
                            title=color_msg("Browser console js errors found"),
                            border_style=border_style,
                            padding=(1, 2),
                        )
                        console.print(rich_panel)
                    rich_output = string_io.getvalue()
                    raise BrowserConsoleException(f"\n{rich_output}")
                else:  # noqa: RET506
                    console_errors_list = f"{separator}\n".join(console_errors)
                    msg = (
                        f"Browser console js errors found:"
                        f"\n{separator}\n{console_errors_list}{separator}\n"
                    )
                    raise BrowserConsoleException(msg)


@pytest.mark.tryfirst
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item: pytest.Item, call: CallInfo) -> None:
    """pytest failed test report generator"""
    outcome = yield
    report = outcome.get_result()
    when = report.when
    item.config.path_to_test = f'{item.location[0]} -k "{item.name}"'

    if when == "call" and not report.passed:
        if item.config.getoption("--fail-debug-info"):
            fail_info = "Fail info not found."
            try:
                if hasattr(item.config, "get_fail_debug"):
                    fail_debug = item.config.get_fail_debug(item)
                    if fail_debug.test_type == "selenium":
                        fail_info = (
                            f"\nURL: {fail_debug.url}"
                            f"\nTEST CASE: {fail_debug.test_case}"
                            f"\nSCREENSHOT: {fail_debug.screenshot}"
                            f"\nRUN_COMMAND: {fail_debug.run_command}"
                            f"\nTXID: {fail_debug.txid}"
                        )
                        if item.config.getoption("--allure-report"):
                            allure.attach(
                                item.config.get_screenshot_png(),
                                name="SCREENSHOT",
                                attachment_type=allure.attachment_type.PNG,
                            )

                    elif fail_debug.test_type == "request":
                        fail_info = (
                            f"\nURL: {fail_debug.url}"
                            f"\nTEST_CASE: {fail_debug.test_case}"
                            f"\nSTATUS_CODE: {fail_debug.status_code}"
                            f"\nRUN_COMMAND: {fail_debug.run_command}"
                            f"\nTXID: {fail_debug.txid}"
                        )
                    if item.config.getoption("--allure-report"):
                        if fail_debug.test_case:
                            for url in fail_debug.test_case.split():
                                allure.dynamic.link(url=url, name="TestCase")
                        allure.attach(
                            fail_debug.url,
                            name="URL",
                            attachment_type=allure.attachment_type.URI_LIST,
                        )
                        allure.attach(
                            f"""<button onclick="navigator.clipboard.writeText(
                            '{fail_debug.run_command.replace('"', "&quot;")}');
                            this.textContent='Copied';">Copy</button> <br>
                            <div style="font-family: monospace,serif;
                            font-size: 14px;">{fail_debug.run_command}</div>""",
                            name="RUN COMMAND",
                            attachment_type=allure.attachment_type.HTML,
                        )

            except WebDriverException as e:
                fail_info = f"\nWebdriver instance must have crushed: {e.msg}"
            finally:
                longrepr = getattr(report, "longrepr", None)
                if hasattr(longrepr, "addsection"):
                    longrepr.sections.insert(
                        0, (f"Captured stdout {when}", fail_info, "-")
                    )

        if item.config.getoption("--duration-time"):
            duration = call.stop - call.start
            if duration > 120:
                report.sections.append((
                    f"Captured stdout {when}",
                    (
                        "\n\n!!!!! The very slow test. "
                        "Duration time is {} !!!!!\n\n"
                    ).format(
                        datetime.datetime.fromtimestamp(duration).strftime(
                            "%M min %S sec"
                        )
                    ),
                ))


def pytest_configure(config: Config) -> None:
    os.environ["PYTHONWARNINGS"] = (
        "ignore:An HTTPS request has been made, "
        "ignore:A true SSLContext object is not available, "
        "ignore:Unverified HTTPS request is being made"
    )

    if config.getoption("--headless"):
        os.environ["HEADLESS"] = "Enabled"
    if config.getoption("--highlight"):
        os.environ["HIGHLIGHT"] = "Enabled"
    if config.getoption("--capturelog"):
        config.pluginmanager.register(Logger(), "logger")
    if config.getoption("--check-console"):
        os.environ["CHECK_CONSOLE"] = "Enabled"
    if not getattr(config, "lastfailed_file", None):
        config.lastfailed_file = "lastfailed"
