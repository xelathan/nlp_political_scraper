import json
from playwright.async_api import async_playwright
import requests
from pymongo import MongoClient
import asyncio
import certifi
import os

script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)
uri = config['mongodb_connection_string']
mongo_client = MongoClient(uri, w=1, tlsCAFile=certifi.where())
db = mongo_client['NLP-Cross-Cutting-Exposure']
visited_articles = set()
PAGE_RETRIES = 5

async def intercept_request(route, request, interception_complete, request_url, request_headers):
    print("interception")
    # Log the URL of the intercepted request
    request_url[0] = request.url
    request_headers[0] = request.headers
    interception_complete.set()
    await route.continue_()


async def intercept_users_request(route, request, interception_complete, request_headers):
    print("interception")
    # Log the URL of the intercepted request
    request_headers[0] = request.headers
    interception_complete.set()
    await route.continue_()


async def get_users(request_url, request_header, users):
    i = 0
    while True:
        try:
            data = {
                "sort_by": "best",
                "offset": 25 * i,
                "count": 25,
                "message_id": None,
                "depth": 15,
                "child_count": 15
            }

            response = requests.post(request_url, json=data, headers=request_header)
            if response.status_code == 200:
                r_json = response.json()
                if len(r_json['conversation']['comments']) == 0:
                    break
                users_in_convo = r_json['conversation']['users']
                for user_id, user in users_in_convo.items():
                    if not (user_id in users):
                        print(user['id'])
                        users[user_id] = {
                            "id": user['id'],
                            "display_name": user['display_name'],
                            "image_id": user['image_id'],
                            "user_name": user['user_name'],
                            "reputation": user['reputation']
                        }
                i += 1
                await asyncio.sleep(0.5)
            else:
                break
        except Exception as e:
            print(e)
            i += 1
            if i >= 50:
                break


async def get_comments_from_users(users, request_headers):
    user_ids_remove = []
    for user_id, user_data in users.items():
        i = 0
        while True:
            try:
                url = f'https://api-2-0.spot.im/v1.0.0/profile/user/{user_id}/activity?offset={i * 8}&count=8'
                response = requests.get(url, headers=request_headers)
                if response.status_code == 200:
                    r_json = response.json()
                    if not (r_json['items'] is None):
                        if len(r_json['items']) == 0:
                            break
                        users[user_id]['items'] = r_json['items']
                        i += 1
                        await asyncio.sleep(0.5)
                    else:
                        user_ids_remove.append(user_id)
                        break
                    await asyncio.sleep(0.5)
                else:
                    break
            except Exception as e:
                print(e)
                i += 1
                if i >= 200:
                    break

    for remove in user_ids_remove:
        users.pop(remove)


# Write array to MongoDB
def write_to_mongodb(_collection, _array, id_field):
    try:
        ids = [item[id_field] for item in _array]
        duplicate_docs = _collection.find({id_field: {'$in': ids}})
        duplicate_urls = set(dupe_doc[id_field] for dupe_doc in duplicate_docs)
        docs_to_insert = [item for item in _array if item[id_field] not in duplicate_urls]
        if docs_to_insert:
            _collection.insert_many(docs_to_insert)
    except Exception as e:
        print(e)


# Navigate to page
async def navigate_to_page(page, link):
    for i in range(0, PAGE_RETRIES):
        try:
            await page.goto(link, timeout=15000, wait_until="domcontentloaded")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            await asyncio.sleep(1)


async def navigate_to_article(page, link):
    for i in range(0, PAGE_RETRIES):
        try:
            await page.goto(link, timeout=15000, wait_until="domcontentloaded")
            comments_button = await page.wait_for_selector(
                '.link.caas-button.noborder.caas-tooltip.flickrComment.caas-comment.top')
            await comments_button.click()
            await asyncio.sleep(15)
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            await asyncio.sleep(1)

    return False


# Scrolls down to generate more articles
async def generate_more_articles(page, link):
    duration = 30
    for i in range(duration):
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
        await asyncio.sleep(1)


# Scrape Yahoo News section
async def scrape_section(link, p, section_users):
    browser = await create_new_browser(p)
    page = await create_new_page(browser)

    await navigate_to_page(page, link)
    await generate_more_articles(page, link)

    stream_items = await page.query_selector_all('.stream-item')
    for stream_item in stream_items:
        article_link = await stream_item.query_selector('a')
        article_link = await article_link.get_attribute('href')
        if 'news.yahoo.com' not in article_link and "https://" not in article_link:
            print(article_link)
            article_link = 'https://news.yahoo.com' + article_link
        if article_link not in visited_articles and article_link.__contains__(
                '.html') and 'news.yahoo.com' in article_link:
            visited_articles.add(article_link)
            article_page = await create_new_page(browser)

            interception_complete = asyncio.Event()
            interception_complete_two = asyncio.Event()
            users = {}

            request_url = ['e']
            request_headers = ['e']

            request_users_header = ['e']
            await article_page.route("https://api-2-0.spot.im/v1.0.0/conversation/read",
                                     handler=lambda route, request: asyncio.create_task(intercept_request(route,
                                                                                                          request,
                                                                            interception_complete, request_url, request_headers)))

            await article_page.route("https://api-2-0.spot.im/v1.0.0/profile/user/*/activity?offset=*",
                                     handler=lambda route, request: asyncio.create_task(intercept_users_request(route,
                                                                                                          request,
                                                                                                          interception_complete_two,
                                                                                                          request_users_header)))

            if await navigate_to_article(article_page, article_link):
                await interception_complete.wait()
                try:
                    await get_users(request_url[0], request_headers[0], users)

                    iframe_locator = article_page.frame_locator('iframe[id^="jacSandbox_"]')
                    profile_locator = 'button[data-spot-im-class="user-info-username"]'
                    profile_buttons = iframe_locator.locator(profile_locator).first
                    if profile_buttons:
                        await profile_buttons.click()
                        await interception_complete_two.wait()
                        await article_page.close()
                        await get_comments_from_users(users, request_users_header[0])

                        for user_id, user_data in users:
                            section_users.append(user_data)
                    else:
                        await article_page.close()
                except Exception as e:
                    print(e)
                    await article_page.close()
            else:
                await article_page.close()
            print("finished article")

    await page.close()
    await browser.close()
    print("finished section")


# Create new page given browser
async def create_new_page(browser):
    page = await browser.new_page(ignore_https_errors=True,
                                  user_agent="Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_10_3; en-US) "
                                             "Gecko/20100101 Firefox/55.8",
                                  bypass_csp=True,
                                  java_script_enabled=True,
                                  service_workers="block",
                                  reduced_motion="reduce", strict_selectors=False)
    page.set_default_timeout(15000)
    return page


# Create new browser
async def create_new_browser(p):
    browser = await p.firefox.launch(headless=True)
    return browser


async def process_link(link, p):
    section_users = []

    try:
        await scrape_section(link, p, section_users)
    except Exception as e:
        print(e)

    # Write to MongoDB
    collection_articles = db['Users']
    if section_users.__len__() > 0:
        write_to_mongodb(collection_articles, section_users, "url")


# Run the job
async def job():
    async with async_playwright() as p:
        await process_link("https://www.yahoo.com/news/tagged/360", p)

        # tasks = [asyncio.create_task(process_link(link, p)) for link in links]
        # await asyncio.gather(*tasks)

        visited_articles.clear()


if __name__ == '__main__':
    asyncio.run(job())
