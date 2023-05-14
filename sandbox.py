from bs4 import BeautifulSoup

from datetime import date 

my_dict = dict()
my_dict["tee_times"] = list()
for _ in range(3):
    my_dict["tee_times"].append({"test": "value"})

print(my_dict)

# Open the HTML file
with open("sample.html", "r") as f:
    html = f.read()

# Create a BeautifulSoup object
soup = BeautifulSoup(html, "html.parser")

body_content = soup.find(id="bodyContent")
rows = body_content.findAll("div", class_="row")

tee_time_list = []
for row in rows:
    tee_time_dict = {}

    tee_time_div = row.find(class_="timeDiv timeDisplay")
    tee_time = tee_time_div.find("span").text

    price = ""
    price_span = row.find(class_="teeTimePrice")
    price_div_h3 = row.find(class_="detailAuctionRow")
    price_h3 = row.find(class_="priceDiv")

    if price_span is not None:
        price = price_span.text
    elif price_div_h3 is not None:
        price_div_h3 = price_div_h3.find("h3")
        price = price_div_h3.text
    else:
        price_h3 = price_h3.find("h3")
        price = price_h3.text

    p_tags = row.findAll("p")
    course = p_tags[0].text
    player_slots = p_tags[1].text

    tee_time_dict["tee_time"] = tee_time
    tee_time_dict["price"] = price
    tee_time_dict["course"] = course
    tee_time_dict["player_slots"] = player_slots

    tee_time_list.append(tee_time_dict)

print(tee_time_list)

