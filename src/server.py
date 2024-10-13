# Being Updated Not For Use

import json
import re
import os
from urllib.parse import urlparse
from DrissionPage import ChromiumPage, ChromiumOptions
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Dict
import argparse
from cloudflare import CloudflareBypasser

# Check if running in Docker mode
DOCKER_MODE = os.getenv("DOCKERMODE", "false").lower() == "true"

# Chromium options arguments
arguments = [
    "-no-first-run",
    "-force-color-profile=srgb",
    "-metrics-recording-only",
    "-password-store=basic",
    "-use-mock-keychain",
    "-export-tagged-pdf",
    "-no-default-browser-check",
    "-disable-background-mode",
    "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
    "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
    "-deny-permission-prompts",
    "-disable-gpu",
    "-accept-lang=en-US",
    "-incognito"
]

browser_path = "/usr/bin/google-chrome"
app = FastAPI()

class CookieResponse(BaseModel):
    cookies: Dict[str, str]
    user_agent: str

def is_safe_url(url: str) -> bool:
    parsed_url = urlparse(url)
    ip_pattern = re.compile(
        r"^(127\.0\.0\.1|localhost|0\.0\.0\.0|::1|10\.\d+\.\d+\.\d+|172\.1[6-9]\.\d+\.\d+|172\.2[0-9]\.\d+\.\d+|172\.3[0-1]\.\d+\.\d+|192\.168\.\d+\.\d+)$"
    )
    hostname = parsed_url.hostname
    if (hostname and ip_pattern.match(hostname)) or parsed_url.scheme == "file":
        return False
    return True

def bypass_cloudflare(url: str, retries: int, log: bool) -> ChromiumPage:
    from pyvirtualdisplay import Display

    if DOCKER_MODE:
        # Start Xvfb for Docker
        display = Display(visible=0, size=(1920, 1080))
        display.start()

        options = ChromiumOptions()
        options.set_argument("--auto-open-devtools-for-tabs", "true")
        options.set_argument("--remote-debugging-port=9222")
        options.set_argument("--no-sandbox")  # Necessary for Docker
        options.set_argument("--disable-gpu")  # Optional, helps in some cases
        options.set_paths(browser_path=browser_path).headless(False)
    else:
        options = ChromiumOptions()
        options.set_argument("--auto-open-devtools-for-tabs", "true")
        options.set_paths(browser_path=browser_path).headless(False)

    driver = ChromiumPage(addr_or_opts=options)
    try:
        driver.get(url)
        cf_bypasser = CloudflareBypasser(driver, retries, log)
        cf_bypasser.bypass()

        cookies = driver.cookies()
        return cookies
    except Exception as e:
        driver.quit()
        if DOCKER_MODE:
            display.stop()
        raise e

@app.get("/cookies", response_model=CookieResponse)
async def get_cookies(url: str, retries: int = 5):
    if not is_safe_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    driver = None
    try:
        cookies = bypass_cloudflare(url, retries, log)
        cookies_dict = [{cookie['name']: cookie['value']} for cookie in cookies]

        # # Extract User Agent
        # user_agent = driver.page.driver.execute_script("return navigator.userAgent;")
        
        return CookieResponse(cookies=cookies_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if driver:
            driver.quit()

@app.get("/html")
async def get_html(url: str, retries: int = 5):
    if not is_safe_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    try:
        driver = bypass_cloudflare(url, retries, log)
        html = driver.html
        cookies_json = json.dumps(driver.cookies(as_dict=True))

        response = Response(content=html, media_type="text/html")
        response.headers["cookies"] = cookies_json
        response.headers["user_agent"] = driver.user_agent
        driver.quit()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloudflare bypass api")

    parser.add_argument("--nolog", action="store_true", help="Disable logging")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    args = parser.parse_args()
    if args.headless and not DOCKER_MODE:
        from pyvirtualdisplay import Display

        display = Display(visible=0, size=(1920, 1080))
        display.start()
    if args.nolog:
        log = False
    else:
        log = True
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
