from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from numpy import block

my_data = []

from datetime import date
import json
from pprint import pprint
import random
import threading
from typing import List
from bs4 import BeautifulSoup
import requests




user_agents = [
    "safari/5.0 (Windows NT 6.1; Win64; x64",
    'Mozilla/5.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
]

class keyword_tracker:

        def __init__(self, keyword: str) -> List:
            self.keyword = keyword.strip().replace(" ", "+")
            print("self.keyword", self.keyword)
            self.base_url = "https://www.amazon.com"
            self.headers = {'User-Agent':
                            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0"
                            random.choice(user_agents), 'From': 'my url'}
            print("self.headers", self.headers)
            global all_data
            self.all_data = {"Organic": [], "Sponsored": []}
            self.organic_counter = 0
            self.sponsored_counter = 0
            self.run()
            

        def run(self):

            URL = f"https://www.amazon.com/s?k={self.keyword}"

            webpage = requests.get(URL, headers=self.headers)

            soup = BeautifulSoup(webpage.content, "lxml")

            pages = [URL]
            try:
                page2 = None
                page3 = None
                page2exist = soup.find(
                    "span", attrs={"class": "s-pagination-strip"})

                if page2exist:
                    page2 = page2exist.find(
                        "a", attrs={"aria-label": "Go to page 2"})["href"]

                page3exist = soup.find(
                    "span", attrs={"class": "s-pagination-strip"})
                if page3exist:
                    page3 = page3exist.find(
                        "a", attrs={"aria-label": "Go to page 3"})["href"]

                if page2:
                    pages.append(str(self.base_url + str(page2)).strip())
                if page3:
                    pages.append(str(self.base_url + str(page3)).strip())

            except Exception as e:
                print("[41] def run()", e)
            print(pages)
            print()

            threads = []
            for idx, page in enumerate(pages):
                t = threading.Thread(
                    target=self.search_pages, args=[page, idx])
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

        def get_top_brands(self, soup):
            if not soup:
                return None
            asins = []
            try:
                for s in soup:
                    asin = s.parent.get("data-asin", None)
                    if not asin:
                        link = soup.find(
                            "a", attrs={"class": "a-link-normal _bXVsd_link_36_Co"})
                        if link:
                            if link.get("href", None):
                                asins = link.get("href").strip().split("lp_asins=")[
                                                    1].split("&")[0].split("%2C")
            except Exception as e:
                print(e)
            return asins

        def get_bottom_brands(self, soup):
            if not soup:
                return None
        
            asins = []
            try:
                for s in soup:
                    asin = s.parent.get("data-asin", None)
                    if not asin:
                        link = soup.find("a", attrs={
                                            "class": "a-spacing-none a-link-normal _bXVsd_mainImageLink_1UpRh _bXVsd_link_gJc5l _bXVsd_hidden_L-XDK"})
                        if link:
                            if link.get("href", None):
                                asins.append(
                                    *link.get("href").strip().split("lp_asins=")[1].split("&")[0].split("%2C"))
            except Exception as e:
                print(e)
            return asins

        def get_video_ads(self, soup):
            if not soup:
                return None
            asins = []
            try:
                for s in soup:
                    link = s.find("div", attrs={
                                    "class": "a-section sbv-video aok-relative sbv-vertical-center-within-parent"})
                    if link and link.find("a") and "lp_asins=" in link.find("a").get("href").strip():
                        asins.append(
                            *link.find("a").get("href").strip().split("lp_asins=")[1].split("&")[0].split("%2C"))
            except Exception as e:
                print(e)
            return asins

        def search_pages(self, page, idx):
            soup = BeautifulSoup(requests.get(
                page, headers=self.headers).content, "lxml")
            links = soup.find_all("a", attrs={
                'class': 'a-link-normal s-no-outline'})
            top_brands = self.get_top_brands(soup.find_all("div", attrs={
                "class": "celwidget pd_rd_w-sLTj8 content-id-amzn1.sym.53aae2ac-0129-49a5-9c09-6530a9e11786:amzn1.sym.53aae2ac-0129-49a5-9c09-6530a9e11786 pf_rd_p-53aae2ac-0129-49a5-9c09-6530a9e11786 pf_rd_r-SZR1CWN8N61S57Q5FSQW pd_rd_wg-1mV0R pd_rd_r-e6f0dbe5-5ffa-45ae-bc18-d0aee9174fff c-f"
            }))
            bottom_brands = self.get_bottom_brands(soup.find_all("div", attrs={
                                                    "class": "celwidget pd_rd_w-2XDdr content-id-amzn1.sym.85014337-b4b1-4f3c-85f8-828d3b814280:amzn1.sym.85014337-b4b1-4f3c-85f8-828d3b814280 pf_rd_p-85014337-b4b1-4f3c-85f8-828d3b814280 pf_rd_r-182C8EY4Z98M4WCY4WP5 pd_rd_wg-5nAKj pd_rd_r-39c4e05c-4ece-48cc-8265-7065234a86da c-f"}))

            video_ads = self.get_video_ads(soup.find_all('span', {'data-component-type':'sbv-video-single-product'}))

            links_list = []
            for link in links:
                sponsored = False
                best_seller = False
                discount = None
                prime = False
                limited_deal = False
                editorial_pick = False

                if "spons" in str(link.get("href")):
                    sponsored = True

                is_best_seller = soup.find(
                    "span", attrs={"class": "a-badge-text"})
                if is_best_seller and "Best Seller" in is_best_seller.text:
                    best_seller = True

                is_discounted = soup.find("a", attrs={
                                            "class": "a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
                if is_discounted:
                    discount = is_discounted.find(
                        "span", attrs={"class": "a-size-extra-large s-color-discount s-light-weight-text"})
                    if discount:
                        discount = discount.text.strip()

                is_prime = soup.find(
                    "i", attrs={"class": "a-icon a-icon-prime a-icon-small"})
                if is_prime:
                    prime = True

                is_limited_deal = soup.find(
                    "span", attrs={"class": "a-size-base a-color-price"})
                if is_limited_deal and "order soon." in is_limited_deal.text:
                    limited_deal = is_limited_deal.text

                is_editorial_pick = soup.find(
                    "span", attrs={"class": "a-badge-text"})
                if is_editorial_pick and "Editors' pick" in is_editorial_pick.text:
                    editorial_pick = True

                links_list.append({
                    "link": link.get('href'),
                    "best_seller": best_seller,
                    "sponsored": sponsored,
                    "discount": discount,
                    "prime": prime,
                    "limited_deal": limited_deal,
                    "editorial_pick": editorial_pick,
                    "top_brands": top_brands,
                    "bottom_brands": bottom_brands,
                    "video_ads": video_ads
                })

            org = 0
            spons = 0
            for l in links_list:
                if l["sponsored"] and l["prime"]:
                    spons += 1
                else:
                    org += 1
            print("org", org, "spons", spons)
            threads = []
            for link in links_list:

                counter = None
                if link["sponsored"]:
                    counter = self.sponsored_counter
                    self.sponsored_counter += 1
                else:
                    counter = self.organic_counter
                    self.organic_counter += 1

                soup = BeautifulSoup(requests.get(
                    self.base_url + link["link"], headers=self.headers).content, "lxml")
                t = threading.Thread(target=self.get_data, args=[
                                        soup, counter, link, idx])
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

        def get_title(self, soup):

            try:

                title = soup.find("span", attrs={"id": 'productTitle'})

                title_value = title.string

                title_string = title_value.strip()

            except AttributeError:
                title_string = ""

            return title_string

        def get_price(self, soup):
            price = None
            try:
                tag = soup.find(
                    "span", attrs={
                        "class": "a-price a-text-price a-size-medium apexPriceToPay"
                    })
                if tag:
                    price = tag.span.text.strip()
                else:
                    tag = soup.find("span", attrs={
                        "class": "price_inside_buybox"
                    })
                    if tag:
                        price = tag.text.strip()
            except Exception:
                price = None
            return price

        def get_stars(self, soup):

            try:
                rating = soup.find(
                    "i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()

            except AttributeError:

                try:
                    rating = soup.find(
                        "span", attrs={'class': 'a-icon-alt'}).string.strip()
                except:
                    rating = ""

            return rating

        def get_rating(self, soup):
            try:
                review_count = soup.find(
                    "span", attrs={'id': 'acrCustomerReviewText'}).string.split("out")[0].strip()

            except AttributeError:
                review_count = ""

            return review_count

        def get_availability(self, soup):
            try:
                available = soup.find("div", attrs={'id': 'availability'})
                available = available.find("span").string.strip()

            except AttributeError:
                available = "Not Available"

            return available

        def get_asin(self, soup):
            try:
                ASIN = None
                is_ASIN = soup.find_all(
                    "th", attrs={'class': 'a-color-secondary a-size-base prodDetSectionEntry'})
                for val in is_ASIN:
                    if val.string.strip() == "ASIN":
                        ASIN = val.parent.td.string

                if not ASIN:
                    is_ASIN = soup.find(
                        "div", attrs={"id": "detailBullets_feature_div"})
                    if is_ASIN:
                        is_ASIN = is_ASIN.find_all("li")
                        for val in is_ASIN:
                            selector = val.span.select("span")
                            if "ASIN" in val.span.span.string.strip():
                                ASIN = selector[1].string.strip()
            except Exception as e:
                ASIN = None

            return ASIN

        def get_image(self, soup):
            try:
                img = soup.find("img", attrs={"id": "landingImage"})["src"]
            except Exception as e:
                img = None
            return img

        def is_amazon_choice(self, soup):
            try:
                choice = False
                is_amzn_choice = soup.find(
                    "div", attrs={"class": "ac-badge-wrapper"})
                if is_amzn_choice:
                    choice = True

            except:
                choice = False

            return choice

        def get_coupon(self, soup):
            try:
                coupon = None
                tag = soup.find(
                    "span", attrs={"class": "apl_m_font apl_message"})
                if tag:
                    coupon = coupon.span.string
                if not coupon:
                    tag = soup.find(
                        "span", attrs={"class": "promoPriceBlockMessage"})
                    coupon = tag.div.find(
                        "span", attrs={"class": "a-color-success"}).span.text.strip()
            except:
                coupon = None

            return coupon

        def get_delivery(self, soup):
            try:
                delivery = None
                tag = soup.find("div", attrs={
                                "id": "mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"})

                try:
                    if "different delivery location" in tag.span.string:
                        delivery = str(tag.span.string).strip()
                except:
                    if tag.span.span.string:
                        delivery = str(tag.span.span.string).strip()

            except Exception:
                delivery = None
            return delivery

        def get_date(self):
            return date.today().strftime("%d/%m/%y")

        def get_tag(self, soup):

            tag = None
            is_tag = soup.find('span', {'class':'a-badge-label-inner a-text-ellipsis'})
            print(is_tag)
            try:
                if is_tag:
                    tag = is_tag.find(
                        'span', {'class': 'a-badge-text'}).text,

            except Exception as e:
                tag = None
            return tag

        def get_list_price(self, soup):
            list_price = None
            try:
                list_price = soup.find('span', {'class':'a-price-whole'}).text
            except:
                list_price = 0
            return list_price

        def get_discount(self, soup, link):
            if link["discount"]:
                return link["discount"]

            discount = None
            try:
                tag = soup.find(
                    "td", attrs={"class": "a-span12 a-color-price a-size-base"})
                if tag:
                    discount = tag.span.text.strip()
            except:
                discount = None
            return discount

        def get_best_seller(self, soup, link):
            if link["best_seller"]:
                return True
            tag = soup.find("div", attrs={"class": "zg-badge-wrapper"})
            if tag:
                return True
            return False

        def get_data(self, new_soup, idx, link, page):
            data = {

                "Rank": idx + 1,
                "Keyword": self.keyword,
                "Url": self.base_url + link["link"],
                "Sponsored": link["sponsored"],
                "Best_Seller": self.get_best_seller(new_soup, link),
                "ASIN": self.get_asin(new_soup),
                "Title": self.get_title(new_soup),
                "Original_Price": self.get_price(new_soup),
                "Stars": self.get_stars(new_soup),
                "List_Price": self.get_list_price(new_soup),
                "Rating": self.get_rating(new_soup),
                "Availability": self.get_availability(new_soup),
                "Image": self.get_image(new_soup),
                "AmazonsChoice": self.is_amazon_choice(new_soup),
                "Coupon": self.get_coupon(new_soup),
                "Delivery": self.get_delivery(new_soup),
                "TimeStamp": self.get_date(),
                "Discount": self.get_discount(new_soup, link),
                "Result_Type": "Sponsored" if link["sponsored"] else "Organic",
                "Prime": link["prime"],
                "best_seller": link['best_seller'],
                "limited_deal": link['limited_deal'],
                "editorial_pick": link['editorial_pick'],
                "top_brands": link['top_brands'],
                "bottom_brands": link['bottom_brands'],
                "video_ads": link["video_ads"]

            }
            # print(data)
            my_data.append(data)
            print()
            print()
          


            if link["sponsored"]:
                self.all_data["Sponsored"].append(data)
            else:
                self.all_data["Organic"].append(data)
          
            print('<====This is my dta ======> ', my_data)
            return
        

def index(request):
    # for i in range(1):

    dt = keyword_tracker("1 year old boy gifts")
    # dt.get_data(new_soup, 1, link, page)

    #print("----------------",(len(dt.all_data["Sponsored"]), len(dt.all_data["Organic"])))
    # import pandas as pd
    # df = pd.DataFrame(dt.all_data["Organic"])
    #df = pd.DataFrame(dt.all_data["Sponsored"])
    # df
    print('<====This is my dta ======> ', my_data)

    # return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, 'polls/index.html', {'my_data': my_data})
    
                
            # i += 1  
        

    