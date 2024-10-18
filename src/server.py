import os
import re
import json
import argparse
from typing import Dict
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cloudflare import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions
from pyvirtualdisplay import Display

# Initialize FastAPI application
app = FastAPI()

# Chromium browser path
BROWSER_PATH = "/usr/bin/google-chrome"

# Default Chromium options
CHROMIUM_OPTIONS = [
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

class CookieResponse(BaseModel):
    """Model for returning cookie information."""
    cookies: Dict[str, str]
    user_agent: str


def is_safe_url(url: str) -> bool:
    """Check if the provided URL is safe."""
    parsed_url = urlparse(url)
    ip_pattern = re.compile(
        r"^(127\.0\.0\.1|localhost|0\.0\.0\.0|::1|10\.\d+\.\d+\.\d+|172\.1[6-9]\.\d+\.\d+|"
        r"172\.2[0-9]\.\d+\.\d+|172\.3[0-1]\.\d+\.\d+|192\.168\.\d+\.\d+)$"
    )
    
    hostname = parsed_url.hostname
    if (hostname and ip_pattern.match(hostname)) or parsed_url.scheme == "file":
        return False
    return True


def bypass_cloudflare(url: str, retries: int, log: bool) -> Dict[str, str]:
    """Bypass Cloudflare protection for the specified URL."""
    options = ChromiumOptions()
    
    # Set additional Chromium options
    for arg in CHROMIUM_OPTIONS:
        options.set_argument(arg)

    options.set_paths(browser_path=BROWSER_PATH).headless(True)  # Set headless mode to True
    driver = ChromiumPage(addr_or_opts=options)

    try:
        driver.get(url)
        cf_bypasser = CloudflareBypasser(driver, retries, log)
        cf_bypasser.bypass()

        # Retrieve cookies from the browser
        cookies = driver.cookies()
        return cookies
    except Exception as e:
        driver.quit()
        raise e


@app.get("/cookies", response_model=CookieResponse)
async def get_cookies(url: str, retries: int = 5):
    """Endpoint to retrieve cookies from a specified URL."""
    if not is_safe_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    try:
        cookies = bypass_cloudflare(url, retries, log)
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        # Extract User Agent (currently not implemented)
        # user_agent = driver.page.driver.execute_script("return navigator.userAgent;")

        return CookieResponse(cookies=cookies_dict, user_agent="User-Agent placeholder")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloudflare Bypass API")

    parser.add_argument("--nolog", action="store_true", help="Disable logging")

    args = parser.parse_args()
    log = not args.nolog

    # Start the application
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Not for use, WIP