# import aiofiles
import argparse
import asyncio

import aiofiles
from dotenv import load_dotenv
import json
import mimetypes
import os
import pandas as pd
import pyppeteer
from pyppeteer.errors import TimeoutError as PyppeteerTimeoutError
import requests

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
    await page.waitForNavigation()


async def scrape_company_posts(page, url, days_ago):
    """
    Scrape LinkedIn company posts

    :param page: Pyppeteer page object
    :param url: LinkedIn company URL
    :param days_ago: How many days ago to scrape for posts
    :return: List of posts
    """
    await page.goto(url)

    # Click to change sorting from Top to Recent
    await page.waitForSelector('div.sort-dropdown__dropdown button.artdeco-dropdown__trigger')
    await page.click('div.sort-dropdown__dropdown button.artdeco-dropdown__trigger')

    await page.waitForSelector('div.sort-dropdown__dropdown div.artdeco-dropdown__content button.artdeco-button--muted')
    await page.click('div.sort-dropdown__dropdown div.artdeco-dropdown__content button.artdeco-button--muted')

    # Wait for posts to load
    await page.waitFor(2000)
    await page.waitForSelector('.scaffold-finite-scroll__content > div')

    # Page down until no more posts are loaded
    while True:
        num_posts = await page.evaluate('''() => {
            return document.querySelectorAll('.scaffold-finite-scroll__content .feed-shared-update-v2').length
        }''')

        await page.evaluate('''() => window.scrollTo(0, document.body.scrollHeight)''')

        oldest_timestamp = await page.evaluate('''() => {
            let posts = document.querySelectorAll('.scaffold-finite-scroll__content .feed-shared-update-v2');
            let last_post = Array.from(posts).pop();
            let post_id = last_post.dataset.urn.match(/([0-9]{19})/).pop();
            return parseInt(BigInt(post_id).toString(2).slice(0, 41), 2);
        }''')
        post_age = (pd.Timestamp.now() - pd.to_datetime(oldest_timestamp, unit='ms')).days
        if -1 < days_ago < post_age:
            break

        try:
            await page.waitForFunction('''(num_posts) => {
                console.log('num_posts is ' + num_posts);
                return document.querySelectorAll('.scaffold-finite-scroll__content .feed-shared-update-v2').length > num_posts;
            }''', {'timeout': 5000}, str(num_posts))
        except PyppeteerTimeoutError:
            break

    # Extract posts
    posts = await page.evaluate('''() => {
        let posts = document.querySelectorAll('.scaffold-finite-scroll__content .feed-shared-update-v2');
        
        let results = [];
        for (let post of posts) {
            let post_id = post.dataset.urn.match(/([0-9]{19})/)
            post_id = post_id ? post_id.pop() : null;
            if (!post_id) continue;
            let timestamp = parseInt(BigInt(post_id).toString(2).slice(0, 41), 2);
            let textElement = post.querySelector('div.feed-shared-update-v2__description-wrapper.mr2 span[dir=ltr]');
            let text = textElement ? textElement.innerText : '';
            let is_repost = !!post.querySelector('.update-components-mini-update-v2');
            let repost_id = null;
            let repost_timestamp = null;
            let repost_actor_name = null;
            let repost_degree = null;
            let repost_text = null;
            if (is_repost) {
                let repost = post.querySelector('.update-components-mini-update-v2');
                repost_id = repost.querySelector('a.update-components-mini-update-v2__link-to-details-page').href.match(/([0-9]{19})/).pop();
                repost_timestamp = parseInt(BigInt(repost_id).toString(2).slice(0, 41), 2);
                repost_actor_name = repost.querySelector('.update-components-actor__name').innerText;
                let degree_element = repost.querySelector('.update-components-actor__supplementary-actor-info > span');
                repost_degree = degree_element ? degree_element.innerText : '';
                let commentary_element = repost.querySelector('.update-components-update-v2__commentary');
                repost_text = commentary_element ? commentary_element.innerText : '';
            }
            results.push({post_id, timestamp, text, is_repost, repost_id, repost_timestamp, repost_actor_name, 
                          repost_degree, repost_text});
        }
        
        return results;
    }''')

    posts = posts[::-1]

    return posts


async def scrape_user_posts(page, url, days_ago):
    """
    Scrape LinkedIn user posts

    :param page: Pyppeteer page object
    :param url: LinkedIn user URL
    :param days_ago: How many days ago to scrape for posts
    :return: List of posts
    """
    await page.goto(url)

    # Wait for posts to load
    await page.waitFor(2000)
    await page.waitForSelector('div.scaffold-finite-scroll__content > ul > li')

    # Page down until no more posts are loaded
    while True:
        num_posts = await page.evaluate('''() => {
            return document.querySelectorAll('.scaffold-finite-scroll__content .feed-shared-update-v2').length
        }''')

        await page.evaluate('''() => window.scrollTo(0, document.body.scrollHeight)''')

        oldest_timestamp = await page.evaluate('''() => {
            let posts = document.querySelectorAll('.scaffold-finite-scroll__content .feed-shared-update-v2');
            let last_post = Array.from(posts).pop();
            let post_id = last_post.dataset.urn.match(/([0-9]{19})/).pop();
            return parseInt(BigInt(post_id).toString(2).slice(0, 41), 2);
        }''')
        post_age = (pd.Timestamp.now() - pd.to_datetime(oldest_timestamp, unit='ms')).days
        if -1 < days_ago < post_age:
            break

        try:
            await page.waitForFunction('''(num_posts) => {
                console.log('num_posts is ' + num_posts);
                return document.querySelectorAll('.scaffold-finite-scroll__content .feed-shared-update-v2').length > num_posts;
            }''', {'timeout': 5000}, str(num_posts))
        except PyppeteerTimeoutError:
            break

    # Extract posts
    posts = await page.evaluate('''() => {
        let posts = document.querySelectorAll('div.scaffold-finite-scroll__content > ul > li .feed-shared-update-v2');

        let results = [];
        for (let post of posts) {
            let post_id = post.dataset.urn.match(/([0-9]{19})/).pop();
            let timestamp = parseInt(BigInt(post_id).toString(2).slice(0, 41), 2);
            let textElement = post.querySelector('div.feed-shared-update-v2__description-wrapper.mr2 span[dir=ltr]');
            let text = textElement ? textElement.innerText : '';
            let is_repost = !!post.querySelector('.update-components-mini-update-v2');
            let repost_id = null;
            let repost_timestamp = null;
            let repost_actor_name = null;
            let repost_degree = null;
            let repost_text = null;
            if (is_repost) {
                let repost = post.querySelector('.update-components-mini-update-v2');
                let repost_link = repost.querySelector('a.update-components-mini-update-v2__link-to-details-page');
                repost_id = repost_link ? repost.querySelector('a.update-components-mini-update-v2__link-to-details-page').href.match(/([0-9]{19})/).pop() : null;
                if (repost_id) {
                    repost_timestamp = parseInt(BigInt(repost_id).toString(2).slice(0, 41), 2);
                    repost_actor_name = repost.querySelector('.update-components-actor__name').innerText;
                    let degree_element = repost.querySelector('.update-components-actor__supplementary-actor-info > span');
                    repost_degree = degree_element ? degree_element.innerText : '';
                    let commentary_element = repost.querySelector('.update-components-update-v2__commentary');
                    repost_text = commentary_element ? commentary_element.innerText : '';
                }
            }
            results.push({post_id, timestamp, text, is_repost, repost_id, repost_timestamp, repost_actor_name, 
                          repost_degree, repost_text});
        }
        
        return results;
    }''')

    posts = posts[::-1]

    return posts


async def save_posts_to_json(filename, posts):
    """
    Save posts to a JSON file

    :param filename: The filename to save to
    :param posts: The posts to save
    :return: None
    """
    async with aiofiles.open(filename, 'w') as file:
        await file.write(json.dumps(posts, indent=4))


def check_and_create_vector_store(vector_store_name):
    """
    Check if a vector store exists and create it if it doesn't

    :param vector_store_name: The name of the vector store
    :return: The vector store id
    """
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json',
        'OpenAI-Beta': 'assistants=v2'
    }
    api_url = f"https://api.openai.com/v1/vector_stores"

    response = requests.get(f"{api_url}", headers=headers)

    if response.status_code == 200:
        vector_stores = response.json().get('data', [])

        # find the vector store by name
        vector_store = next((store for store in vector_stores if store['name'] == vector_store_name), None)

        if not vector_store:
            create_response = requests.post(api_url, headers=headers, json={"name": vector_store_name})
            if create_response.status_code == 200:
                print('Vector store created successfully')
                return create_response.json().get('id')
            else:
                print(f'Failed to create vector store, response code {create_response.status_code}, message:',
                      create_response.json().get('error').get('message'))
        else:
            print(f'Found vector store id {vector_store["id"]} for name {vector_store_name}')
            return vector_store['id']

    else:
        print('Failed to fetch vector stores', response.status_code, response.text)


def upload_to_vector_store(vector_store_id, json_filepath):
    """
    Upload a JSON file to an OpenAI vector store

    :param vector_store_id: The OpenAI vector store id
    :param json_filepath: The JSON file to upload
    :return: True if successful, False otherwise
    """
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'OpenAI-Beta': 'assistants=v2'
    }

    # extract the filename from the path
    json_file = os.path.basename(json_filepath)

    api_url_files = "https://api.openai.com/v1/files"

    # Delete the file if it already exists
    response = requests.get(api_url_files, headers=headers)
    for file in response.json().get('data', []):
        if file['filename'] == json_file:
            result = requests.delete(f"{api_url_files}/{file['id']}", headers=headers)
            if result.status_code != 200:
                print(
                    f'Failed to delete existing file {json_file}, response code {result.status_code}, message:',
                    result.json().get('error').get('message'))
                return False

    # Upload the file to OpenAI
    file_type = mimetypes.guess_type(json_filepath)
    files = {'file': (json_filepath, open(json_filepath, 'rb'), file_type)}
    data = {'purpose': 'assistants'}
    response = requests.post(api_url_files, headers=headers, files=files, data=data)

    if response.status_code != 200:
        print(f'Failed to upload file, response code {response.status_code}, message:',
              response.json().get('error').get('message'))
        return False

    file_id = response.json().get('id')

    # Then, use the returned file id to create a vector store file
    api_url_vector_store = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
    json_payload = {
        'file_id': file_id
    }

    response = requests.post(api_url_vector_store, headers=headers, json=json_payload)

    if response.status_code == 200:
        print(f'File uploaded to vector store id {vector_store_id} successfully')
    else:
        print(
            f'Failed to upload file to vector store id {vector_store_id}, response code {response.status_code}, message:',
            response.json().get('error').get('message'))
        return False

    return True


async def main():
    global vector_store_name, linkedin_password, linkedin_username, chrome_path, profile_dir

    parser = argparse.ArgumentParser(
        description='Scrape LinkedIn posts and export them to Excel and/or upload them to an OpenAI vector store')
    parser.add_argument("--url", help="The LinkedIn URL to spider")
    parser.add_argument("--json", help="The json filename to save to", default="output.json")
    parser.add_argument("--start",
                        help="If first run, how many days in the past should we scrape for posts? -1 for all",
                        default=-1, type=int)
    parser.add_argument('--increment',
                        help="Tag the output files with today's date so that you get incremental updates",
                        action='store_false', default=True)
    parser.add_argument('--excel', help="Export downloaded posts to an Excel file?", action='store_true', default=True)
    parser.add_argument("--openai", help="Upload downloaded posts to OpenAI vector storage?",
                        action='store_true',
                        default=False)
    parser.add_argument('--store', help="The OpenAI vector store name to upload to", default=vector_store_name)
    parser.add_argument('--username', help="The LinkedIn username", default=linkedin_username)
    parser.add_argument('--password', help="The LinkedIn password", default=linkedin_password)
    args = parser.parse_args()

    url = args.url or None

    linkedin_username = args.username
    linkedin_password = args.password

    # Determine json filename to store posts
    json_basefilepath = args.json if not url else url.split('/')[4] + '_posts'
    json_filepath = json_basefilepath
    if args.increment:
        json_filepath += f'_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}'
    json_filepath += '.json'

    # Load any existing posts from file if we're not doing an incremental update
    posts = []
    if not args.increment:
        if os.path.isfile(json_filepath):
            with open(json_filepath, 'r') as file:
                posts = json.load(file)

    days_ago = args.start

    # Scrape posts
    new_posts = []
    if url:
        last_post_timestamp = None
        if len(posts) > 0:
            last_post_timestamp = posts[-1]['timestamp']
        else:
            # find the most recent post from the json files in the current directory
            for file in os.listdir('.'):
                if file.endswith('.json') and file.startswith(json_basefilepath):
                    with open(file, 'r') as f:
                        json_posts = json.load(f)
                        post_timestamp = json_posts[-1]['timestamp']
                        if not last_post_timestamp:
                            last_post_timestamp = post_timestamp
                        if last_post_timestamp and post_timestamp > last_post_timestamp:
                            last_post_timestamp = post_timestamp

        # if we found a last_post_date, convert timestamp to days ago and use it
        if last_post_timestamp:
            days_ago = (pd.Timestamp.now() - pd.to_datetime(last_post_timestamp, unit='ms')).days

        params = {
            'headless': False,
        }
        if chrome_path is not None and len(chrome_path) > 0:
            params['executablePath'] = chrome_path
        if profile_dir is not None and len(profile_dir) > 0:
            params['userDataDir'] = profile_dir
        browser = await pyppeteer.launch(params)

        page = None
        pages = await browser.pages()
        if len(pages) > 0:
            # find the about:blank page by looking backward through the list
            for the_page in pages[::-1]:
                if the_page.url == 'about:blank':
                    page = the_page
                    break

        if not page:
            page = await browser.newPage()

        viewport = await page.evaluate('''() => {
            return {
                width: window.outerWidth,
                height: window.outerHeight
            }
        }''')
        await page.setViewport(viewport)
        await login_to_linkedin(page, linkedin_username, linkedin_password)

        if 'company' in url:
            new_posts = await scrape_company_posts(page, url, days_ago)
        else:
            new_posts = await scrape_user_posts(page, url, days_ago)

        # filter out any posts in new_posts that are older than last_post_date
        if last_post_timestamp:
            new_posts = [post for post in new_posts if post['timestamp'] > last_post_timestamp]

        await browser.close()

    # Merge new posts with existing posts and remove duplicates then save output
    if len(new_posts) > 0:
        if len(posts) > 0:
            old_post_ids = [post['post_id'] for post in posts]
            new_posts = [post for post in new_posts if post['post_id'] not in old_post_ids]
        posts += new_posts

        await save_posts_to_json(json_filepath, posts)

    # Export posts to Excel
    if args.excel:
        df = pd.DataFrame(posts,
                          columns=['post_id', 'timestamp', 'text', 'is_repost', 'repost_id', 'repost_timestamp',
                                   'repost_actor_name', 'repost_degree', 'repost_text'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['repost_timestamp'] = pd.to_datetime(df['repost_timestamp'], unit='ms')
        df.to_excel(json_filepath.replace('.json', '.xlsx'), index=False)

    # Upload to OpenAI vector store
    if args.openai:
        if args.store:
            vector_store_name = args.store
        vector_store_id = check_and_create_vector_store(vector_store_name)
        upload_to_vector_store(vector_store_id, json_filepath)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
