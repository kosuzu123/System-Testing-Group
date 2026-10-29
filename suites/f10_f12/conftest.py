"""Independent sessions and scenario-level evidence. No results are fabricated."""
import importlib.metadata,json,os,platform,secrets,time,tempfile
from datetime import datetime,timezone
from pathlib import Path
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pages import Shop

def pytest_addoption(parser):
    parser.addoption("--base-url",default="https://opencart.abstracta.us/")
    parser.addoption("--headed",action="store_true")
    parser.addoption("--evidence-dir",default="artifacts/latest")

def pytest_configure(config):
    config._output=Path(config.getoption("--evidence-dir")).resolve()
    config._output.mkdir(parents=True,exist_ok=True)
    config._results,config._started={},time.time()
    config._env=dict(python=platform.python_version(),os=platform.platform(),architecture=platform.machine(),selenium=importlib.metadata.version("selenium"),pytest=pytest.__version__,base_url=config.getoption("--base-url"),started_utc=datetime.now(timezone.utc).isoformat())

def new_driver(config):
    options=Options()
    if not config.getoption("--headed"):options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1100")
    options.add_argument("--no-first-run")
    options.add_argument("--user-data-dir="+tempfile.mkdtemp(prefix="a3-chrome-"))
    if os.getenv("CHROME_BINARY"):options.binary_location=os.environ["CHROME_BINARY"]
    service=Service(executable_path=os.environ["CHROMEDRIVER"]) if os.getenv("CHROMEDRIVER") else Service()
    driver=webdriver.Chrome(service=service,options=options)
    driver.set_page_load_timeout(40)
    driver.implicitly_wait(0)
    caps=driver.capabilities
    config._env.update(browser=caps.get("browserName"),browser_version=caps.get("browserVersion"),driver_version=caps.get("chrome",{}).get("chromedriverVersion","").split(" ")[0])
    return driver

@pytest.fixture(scope="session")
def account(pytestconfig):
    email,password=os.getenv("TEST_EMAIL"),os.getenv("TEST_PASSWORD")
    if bool(email)!=bool(password):pytest.fail("Supply both TEST_EMAIL and TEST_PASSWORD, or neither.")
    if email:return email,password
    email,password="kunyu.a3."+secrets.token_hex(6)+"@example.com","A3!"+secrets.token_hex(10)
    driver=new_driver(pytestconfig)
    try:Shop(driver,pytestconfig.getoption("--base-url")).register(email,password)
    finally:driver.quit()
    return email,password  # No credentials in logs or shared report.

@pytest.fixture
def shop(request,pytestconfig):
    driver=new_driver(pytestconfig)
    page=Shop(driver,pytestconfig.getoption("--base-url"),pytestconfig._output,request.node.get_closest_marker("scenario").args[0])
    request.node._shop=page
    try:yield page
    finally:driver.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item,call):
    result=yield
    report=result.get_result()
    marker=item.get_closest_marker("scenario")
    if not marker:return
    sid=marker.args[0]
    entry=item.config._results.setdefault(sid,dict(scenario=sid,phases=[],evidence=[]))
    phase=dict(when=report.when,outcome=report.outcome,seconds=round(report.duration,3))
    if report.failed or report.skipped:phase["detail"]=str(report.longrepr)
    entry["phases"].append(phase)
    page=getattr(item,"_shop",None) or getattr(item,"_api",None)
    if page and report.when=="call":
        try:page.capture("final" if report.passed else "failure")
        except Exception:pass
        entry["evidence"]=list(page.evidence)
    if report.failed:
        entry["status"]="FAIL" if report.when=="call" and call.excinfo and call.excinfo.errisinstance(AssertionError) else "ERROR"
    elif report.skipped:entry["status"]="BLOCKED"
    elif report.when=="call":entry["status"]="PASS"

def pytest_sessionfinish(session,exitstatus):
    c=session.config
    c._env.update(requests=importlib.metadata.version("requests"),beautifulsoup4=importlib.metadata.version("beautifulsoup4"))
    payload=dict(environment=c._env,duration_seconds=round(time.time()-c._started,2),exit_code=int(exitstatus),results=sorted(c._results.values(),key=lambda x:x["scenario"]))
    (c._output/"results.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    (c._output/"environment.json").write_text(json.dumps(c._env,indent=2),encoding="utf-8")


@pytest.fixture(scope="session")
def http_account(pytestconfig):
    from http_client import ApiShop
    email,password="kunyu.a3."+secrets.token_hex(6)+"@example.com","A3!"+secrets.token_hex(10)
    api=ApiShop(pytestconfig.getoption("--base-url"),pytestconfig._output,"setup")
    api.register(email,password)
    return email,password

@pytest.fixture
def api(request,pytestconfig):
    from http_client import ApiShop
    page=ApiShop(pytestconfig.getoption("--base-url"),pytestconfig._output,request.node.get_closest_marker("scenario").args[0])
    request.node._api=page
    yield page
    page.session.close()
