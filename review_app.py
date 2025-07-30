import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_movie_url(movie_title):
    """
    Searches for a movie on IMDb and retrieves its URL.

    Args:
        movie_title (str): The title of the movie to search for.

    Returns:
        str: The full IMDb URL for the movie, or None if not found.
    """
    base_url = "https://www.imdb.com/find"
    search_query = movie_title.replace(" ", "+")
    search_url = f"{base_url}?q={search_query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        first_result_link = soup.find('a', href=lambda href: href and '/title/tt' in href)

        if first_result_link:
            movie_path = first_result_link.get('href')
            full_movie_url = f"https://www.imdb.com{movie_path}"
            return full_movie_url
        else:
            return None

    except requests.exceptions.RequestException:
        return None

def scrape_movie_reviews(movie_url):
    """
    Scrapes user reviews and ratings from a given IMDb movie page URL using Selenium.

    Args:
        movie_url (str): The full IMDb URL of the movie page.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'review_text' and 'rating'.
              Returns an empty list if no reviews are found or an error occurs.
    """
    reviews_url = f"{movie_url.split('?')[0]}reviews"
    reviews_list = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(reviews_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.lister-item-content"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        review_containers = soup.find_all('div', class_='lister-item-content')

        for container in review_containers:
            review_text_element = container.find('div', class_='text show-more__control')
            review_text = review_text_element.get_text(strip=True) if review_text_element else "N/A"

            rating_element = container.find('span', class_='rating-other-user-rating')
            rating = None
            if rating_element:
                rating_span = rating_element.find('span')
                if rating_span:
                    rating_text = rating_span.get_text(strip=True)
                    if rating_text:
                        rating = float(rating_text)

            reviews_list.append({'review_text': review_text, 'rating': rating})

    except Exception:
        return []
    finally:
        driver.quit()

    return reviews_list

def filter_and_display_reviews(review_list):
    """
    Filters scraped reviews into positive and negative categories and displays them.

    Args:
        review_list (list): A list of review dictionaries, each with 'review_text' and 'rating'.
    """
    positive_reviews = []
    negative_reviews = []

    for review in review_list:
        if review['rating'] is not None:
            if review['rating'] >= 7:
                positive_reviews.append(review['review_text'])
            elif review['rating'] <= 4:
                negative_reviews.append(review['review_text'])
    
    st.write("---")
    st.header("Positive Reviews")
    if positive_reviews:
        for i, review in enumerate(positive_reviews[:5]):
            st.write(f"{i+1}. {review}")
    else:
        st.write("No positive reviews found.")

    st.write("---")
    st.header("Negative Reviews")
    if negative_reviews:
        for i, review in enumerate(negative_reviews[:5]):
            st.write(f"{i+1}. {review}")
    else:
        st.write("No negative reviews found.")


# --- Streamlit App Interface ---

st.title('🎬 IMDb Movie Review Scraper')

st.write("Enter the title of a movie to see its positive and negative reviews.")

movie_title = st.text_input('Movie Title', 'The Dark Knight')

if st.button('Search for Reviews'):
    with st.spinner('Searching for the movie...'):
        movie_url = search_movie_url(movie_title)

    if movie_url:
        st.success(f"Found movie: {movie_url}")
        with st.spinner('Scraping reviews... this may take a moment.'):
            reviews = scrape_movie_reviews(movie_url)
        
        if reviews:
            filter_and_display_reviews(reviews)
        else:
            st.error("Could not scrape reviews for this movie. The website structure may have changed, or the reviews page may not be accessible.")
    else:
        st.error(f"Could not find a movie with the title: '{movie_title}'")
