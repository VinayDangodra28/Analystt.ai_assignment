from selenium import webdriver
import requests
import re


PATH = "chromedriver_linux64/chromedriver"
options = webdriver.ChromeOptions()
options.add_argument('--headless')

# create a new Chrome session

inner_driver = webdriver.Chrome(PATH)

def get_url(url:str, page:int):
    final_url = url+"&page="+str(page)
    return final_url

def get_details(url:str,page:int):
    new_driver = webdriver.Chrome(PATH, options=options)
    final_url = get_url(page=page, url=url)
    print(final_url)
    new_driver.get(final_url)
    products = new_driver.find_elements_by_xpath("//div[@class='a-section']/div")
    products_data = []
    i=1
    try:
      for product in products:
        one_product_data = {}
        try:
            product_url_tag = product.find_element_by_xpath(".//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']")
            one_product_data['url']=product_url_tag.get_attribute("href")
        except:
            try:
              product_url_tag = product.find_element_by_xpath(".//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style']")
              one_product_data['url']=product_url_tag.get_attribute("href")
            except:
              one_product_data['url']=""
              print("product url not found")



          # for product name
        try:
            product_name_tag = product.find_element_by_xpath(".//span[@class='a-size-medium a-color-base a-text-normal']")
            one_product_data["name"] = product_name_tag.text
        except:
            one_product_data["name"] = ""
            print("product name not found")

          # for product price
        try:
            product_price_tag = product.find_element_by_xpath(".//span[@class='a-price-whole']")
            one_product_data["price"] = product_price_tag.text
        except:
            one_product_data["price"] = ""
            print("product price not found")

          # for product rating
        try:
            product_rating_tag = product.find_element_by_xpath(".//span[@class='a-size-base']")
            one_product_data["rating"] = product_rating_tag.text
        except:
            one_product_data["rating"] = ""
            print("product rating not found")

          # for product number of ratings
        try:
            product_number_of_ratings = product.find_element_by_xpath(".//span[@class='a-size-base s-underline-text']")
          #   print(product_number_of_ratings.text)
            one_product_data["number_of_rating"] = product_number_of_ratings.text
        except:
            one_product_data["number_of_rating"] = ""
            print("number of ratings not found")
        products_data.append(one_product_data)

          # getting inner page data
        try:
          inner_details = get_inner_details(one_product_data['url'])
          try:
            one_product_data["description"] = inner_details["description"]
          except:
            one_product_data["description"] = ""
          try:
            one_product_data["asin"] = inner_details["asin"]
          except:
            one_product_data["asin"] = ""
          try: 
            one_product_data["product_description"] = inner_details["product_description"]
          except:
            one_product_data["product_description"] = ""
          try:
            one_product_data["manufacturer"] = inner_details["manufacturer"]
          except:
             one_product_data["manufacturer"] = ""
        except:
          one_product_data["description"] = ""
          one_product_data["asin"] = ""
          one_product_data["product_description"] = ""
          one_product_data["manufacturer"] = ""

        i+=1
    except:
      new_driver.quit()
      return products_data
    new_driver.quit()
    return products_data

def get_inner_details(raw_url):
        try:
          url_suffix = re.findall('url=(.*)', raw_url)[0]
          url = "https://www.amazon.in"+url_suffix
          url = url.replace("%2F", "/")
          url = url.replace("%3F", "?")
          print(url)
        except:
           url = raw_url
        inner_details = {}
        # going inside the page
        try:
            inner_driver = webdriver.Chrome(PATH, options=options)
            inner_driver.get(url)
            # for description
            try:
                product_description_tag = inner_driver.find_element_by_xpath(".//ul[@class='a-unordered-list a-vertical a-spacing-mini']")
                items = product_description_tag.find_elements_by_tag_name('li')
                product_description = ""
                for item in items:
                  desc_item = item.find_element_by_xpath(".//span[@class='a-list-item']")
                  product_description += desc_item.text
                  product_description += "\n"
                if product_description != "":
                  inner_details["description"] = product_description
                else:
                    inner_details["description"] = ""
                    print("description not found")
            except:
              inner_details["description"] = ""
              print("description not found")

            # for asin
            pattern = re.compile(r'dp/(.*?)/')
            match = pattern.search(url)
            if match:
                asin = match.group(1)
                inner_details["asin"] = asin
            else:
               inner_details["asin"] = ""
               print("asin not found")
            
            # for product description
            try:
                product_productDescription_OuterTag = inner_driver.find_element_by_id("productDescription")
                product_productDescription_tag = product_productDescription_OuterTag.find_element_by_tag_name('span')
                inner_details["product_description"] = product_productDescription_tag.text
            except:
               inner_details["product_description"] = ""
               print("product description not found")

            # for manufacturer name
            try:
               product_manufacturer_outerHTML = inner_driver.find_element_by_name("a-cardui-deck-autoname-1-card0")
               product_manufacturer_tag = product_manufacturer_outerHTML.find_element_by_xpath(".//span[@class='a-size-medium a-text-bold']")
               inner_details["manufacturer"] = product_manufacturer_tag.text
            except:
               inner_details["manufacturer"] = ""
               print("manufacturer not found")

        except:
          inner_driver.quit()
          return inner_details
          print("not able to enter")


        inner_driver.quit()
        return inner_details


def run(url):
    driver = webdriver.Chrome(PATH, options=options)
    driver.get(url)
    pages = driver.find_element_by_xpath(".//span[@class='s-pagination-item s-pagination-disabled']")
    number_of_pages = int(pages.text)
    driver.quit()
    print(number_of_pages)
    i=0
    final_data = []
    try:
      while(i<=number_of_pages):
         i+=1
         a = get_details(url=url, page=i)
         print(f"page {i} done")
         for j in a:
            final_data.append(j)
    except:
      print("error")
      return final_data
    return final_data

if __name__ == "__main__":
  data = run(url="https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1")
  print(data)
  import csv 

  with open('bags.csv', 'w', newline='') as csvfile: 
    writer = csv.writer(csvfile, delimiter=',') 

    writer.writerow(["url", "name", "price", "rating", "number_of_rating", "description", "asin", "product_description", "manufacturer"]) 

    for item in data: 
      writer.writerow([item["url"], item["name"], item["price"], item["rating"], item["number_of_rating"], item["description"], item["asin"], item["product_description"], item["manufacturer"]])

