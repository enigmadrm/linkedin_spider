import asyncio
import os
from dotenv import load_dotenv
import pandas as pd
from pyppeteer import launch
from pyppeteer.errors import TimeoutError as PyppeteerTimeoutError

# Load environment variables
load_dotenv('.env')
openai_api_key = os.environ.get('OPENAI_API_KEY')
vector_store_name = os.environ.get('VECTOR_STORE_NAME')
linkedin_username = os.environ.get('LINKEDIN_USERNAME')
linkedin_password = os.environ.get('LINKEDIN_PASSWORD')
chrome_path = os.environ.get('CHROME_PATH')
profile_dir = os.environ.get('PROFILE_DIR')


async def login_to_linkedin(page, username, password):
    """
    Login to LinkedIn

    :param page: Pyppeteer page object
    :param username: LinkedIn username
    :param password: LinkedIn password
    :return: None
    """
    await page.goto("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")
    await page.waitForSelector('#password')
    await page.waitFor(1000)
    if await page.querySelector('#username'):
        await page.type('#username', username)
    await page.waitForSelector('#password')
    await page.waitFor(1000)
    await page.type('#password', password)
    await page.waitForSelector('form.login__form')
    await page.waitFor(1000)
    await page.click('form.login__form button[type=submit]')
    await page.waitForNavigation({'timeout': 240000})


async def congratulate_job_changes(page):
    """
    Clicks on all the 'congrats on starting your new role' buttons on the LinkedIn job changes page.

    :param page: Pyppeteer page object
    :return: None
    """
    await page.goto("https://www.linkedin.com/mynetwork/catch-up/job_changes/")
    await page.waitForSelector('button[data-control-name="job_change_congratulate"]', {'timeout': 60000})

    buttons = await page.querySelectorAll('button[data-control-name="job_change_congratulate"]')

    for button in buttons:
        await button.click()
        await page.waitFor(1000)  # Adjust this delay as necessary to mimic human interaction and avoid detection


async def main():
    global linkedin_username, linkedin_password, chrome_path, profile_dir

    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.setViewport({'width': 1280, 'height': 800})

    # Log in to LinkedIn
    await login_to_linkedin(page, linkedin_username, linkedin_password)

    # Call the congratulate_job_changes function
    await congratulate_job_changes(page)

    await browser.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
