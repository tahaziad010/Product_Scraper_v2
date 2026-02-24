import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import tkinter as tk
from tkinter import messagebox

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

def get_rating(star_class):
    ratings = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
    for key in ratings:
        if key in star_class:
            return ratings[key]
    return 0

def scrape_books(min_rating, max_price, max_pages, output_file):
    books = []
    page = 1
    while page <= max_pages:
        url = BASE_URL.format(page)
        response = requests.get(url)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("article", class_="product_pod")
        for item in items:
            title = item.h3.a["title"]
            price_text = item.find("p", class_="price_color").text.strip()
            price_clean = re.sub(r"[^\d.]", "", price_text)
            price = float(price_clean)
            rating_class = item.find("p", class_="star-rating")["class"]
            rating = get_rating(rating_class)
            if rating >= min_rating and price <= max_price:
                books.append({"Title": title, "Price (£)": price, "Rating": rating})
        page += 1
        time.sleep(1)
    df = pd.DataFrame(books)
    df.to_csv(output_file, index=False)
    messagebox.showinfo("Done", f"Scraped {len(books)} books!\nSaved to {output_file}")

def run_scraper():
    min_rating_text = rating_entry.get().strip()
    max_price_text = price_entry.get().strip()
    pages_text = pages_entry.get().strip()
    output_file = output_entry.get().strip()

    if not min_rating_text or not max_price_text or not pages_text:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    if not min_rating_text.isdigit():
        messagebox.showerror("Error", "Minimum Rating must be an integer between 1 and 5.")
        return
    if not pages_text.isdigit():
        messagebox.showerror("Error", "Number of Pages must be an integer.")
        return

    try:
        min_rating = int(min_rating_text)
        max_price = float(max_price_text)
        pages = int(pages_text)
    except ValueError:
        messagebox.showerror("Error", "Price must be a valid number.")
        return

    if not output_file:
        output_file = "books.csv"

    scrape_books(min_rating, max_price, pages, output_file)

# ===== GUI Setup =====
root = tk.Tk()
root.title("Book Scraper GUI")
root.geometry("450x350")

# Labels + Examples
tk.Label(root, text="Minimum Rating (1-5) — int").pack()
rating_entry = tk.Entry(root)
rating_entry.pack()

tk.Label(root, text="Maximum Price — float").pack()
price_entry = tk.Entry(root)
price_entry.pack()

tk.Label(root, text="Number of Pages — int (max 50)").pack()
pages_entry = tk.Entry(root)
pages_entry.pack()

tk.Label(root, text="Output File Name — str ending with .csv").pack()
output_entry = tk.Entry(root)
output_entry.pack()

tk.Button(root, text="Start Scraping", command=run_scraper).pack(pady=20)

root.mainloop()