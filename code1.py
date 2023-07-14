from bs4 import BeautifulSoup
import requests
import time
import re




SPECIAL_CHARACTERS = ["\r", "\n", "\t", "\xa0"]
OPTIONS_NOT_FOUND = ["Wait for product to come back in stock", "Re-enter the product type and name"]

def make_soup(link):
	response = requests.get(link)
	soup = BeautifulSoup(response.content, "html.parser")
	all_element_list = get_all_elements(soup)
	return soup, all_element_list

def get_product_types(soup):
	links = soup.find(class_ = "rf-refurbished-categories-no-js")
	children = list(links.children)
	product_types_a_tags = []
	for child in children:
	  if('li' in str(child)):
	    product_types_a_tags.append(child)
	product_types = []
	for product_type in product_types_a_tags:
	  product_types.append(product_type.text)
	return product_types

def get_product_types_for_link(product_types):
	product_types_for_link = []
	for product in product_types:
	  product = product.replace(" ", "")
	  product = product.lower()
	  product_types_for_link.append(product)
	return product_types_for_link


global search

def get_all_elements(soup):
	lis = soup.find_all("li")
	all_element_list = []
	for li in lis:
	  x = li.findChildren()
	  for i in x:
	    if('<span class="as-price-previousprice">' in str(i)):
	      all_element_list.append(x)
	return all_element_list

def get_product_names(all_element_list):
	names = []
	for i in all_element_list:
	  for j in i:
	    if('a href' in str(j)):
	      text = remove_escape_characters(j.text)
	      names.append(text)
	      break
	return names

def get_current_prices(all_element_list):
	curr_prices = []
	for i in all_element_list:
	  for j in i:
	    if('div class="as-price-currentprice as-producttile-currentprice"' in str(j)):
	      text = remove_escape_characters(j.text)
	      curr_prices.append(text)
	return curr_prices

def get_money_saved(all_element_list):
	saved_prices = []
	for i in all_element_list:
	  for j in i:
	    if('span class="as-producttile-savingsprice"' in str(j)):
	      text = remove_escape_characters(j.text)
	      saved_prices.append(text)
	return saved_prices	

def get_links(all_element_list):
	pattern = 'a href="(.*)"'
	links = []
	for i in all_element_list:
	  for j in i:
	    if('a href' in str(j)):
	      text = re.findall(pattern, str(j))
	      text = text[0]
	      text = "apple.com" + text
	      links.append(text)
	      break
	return links

def remove_escape_characters(text):
    text = text.strip()
    for character in SPECIAL_CHARACTERS:
        text = text.replace(character, "")
    return text

def check_if_in_stock(search, link, repeat):
	global result, names
	soup, all_element_list = make_soup(link)	
	names = get_product_names(all_element_list)
	if(search not in names):
		if(repeat == True):
			result = 1
			return
		print("Your desired product is not available or does not exist - please ensure that the product you entered is in the product type you have selected and that the name is typed correctly")
		for i in range(len(OPTIONS_NOT_FOUND)):
			print(str(i + 1) + ". " + OPTIONS_NOT_FOUND[i])
		print()
		choice = input("Enter what you would like to do: ")

		if(choice == "Wait for product to come back in stock" or choice == "1"):
			result = 1
		else:
			result = 2
	else:
		result = 3

def check_result(search, link, repeat):
	if(result == 1):
		while(True):
			repeat = True
			check_if_in_stock(search, link, repeat)
			if(result == 3):
				check_result(search, link, repeat)
			time.sleep(60)
	elif(result == 2):
		main()
	elif(result == 3):
		print()
		print("Your product is in stock")
		soup, all_element_list = make_soup(link)
		current_prices = get_current_prices(all_element_list)
		saved_prices = get_money_saved(all_element_list)
		links = get_links(all_element_list)
		try:
			pos = names.index(search)
		except:
			pos = names.index(search)
		
		print("It is being sold for the price: ", str(current_prices[pos]), " and you are saving: ", saved_prices[pos])
		print("You can buy it from this link:\n", str(links[pos]))
		print()
		main()


def main():
	while(True):
		repeat = False
		link = "https://www.apple.com/shop/refurbished"
		response = requests.get(link)

		soup = BeautifulSoup(response.content, "html.parser")
		product_types = get_product_types(soup)
		product_types_for_link = get_product_types_for_link(product_types)
		product_types.append("Quit")
		print(product_types)

		print()
		print()
		print("REFURBISHED SCRAPER")
		for i in range(0, len(product_types)):
			print(str(i + 1) + ". " + product_types[i])

		print()

		option = input("Enter which product you are seraching for: ")
		option = option.lower()

		link = None

		if(option == product_types[-1].lower() or option == str(len(product_types))):
			exit()
		else:
			product_types.pop(-1)
		for i in range(len(product_types_for_link)):
			if(option == product_types[i].lower() or option == str(i+1) or option == product_types_for_link[i]):
				link = f"https://www.apple.com/shop/refurbished/{product_types_for_link[i]}"


		if(link == None):
			print("INVALID CHOICE")
			continue



		search = input("What item are you searching for: ")

		check_if_in_stock(search, link, repeat)

		check_result(search, link, repeat)

main()