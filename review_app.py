
import streamlit as st
import requests
from bs4 import BeautifulSoup

def search_movie_url(movie_title):
    """
    Searches for a movie on IMDb and retrieves its URL.
    """
    base_url = "https://www.imdb.com/find"
    search_query = movie_title.replace(" ", "+")
    search_url = f"{base_url}?q={search_query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find('a', href=lambda href: href and '/title/tt' in href)
        if result:
            movie_path = result.get('href')
            return f"https://www.imdb.com{movie_path}"
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching for movie: {e}")
    return None

def scrape_movie_reviews(movie_url):
    """
    Scrapes user reviews and ratings from a given IMDb movie page URL.
    """
    reviews_url = f"{movie_url.split('?')[0]}reviews"
    reviews_list = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(reviews_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # This selector targets the main container for each review
        review_containers = soup.find_all('div', class_='review-container')

        for container in review_containers:
            review_text = "N/A"
            rating = None

            review_text_element = container.find('div', class_='text')
            if review_text_element:
                review_text = review_text_element.get_text(strip=True)

            rating_element = container.find('span', class_='rating-other-user-rating')
            if rating_element and rating_element.find('span'):
                rating = float(rating_element.find('span').get_text(strip=True))

            reviews_list.append({'review_text': review_text, 'rating': rating})

    except requests.exceptions.RequestException as e:
        st.error(f"Error scraping reviews: {e}")
    return reviews_list
    
def filter_and_display_reviews(review_list):
    """
    Filters and displays positive and negative reviews.
    """
    positive_reviews = [r['review_text'] for r in review_list if r['rating'] is not None and r['rating'] >= 7]
    negative_reviews = [r['review_text'] for r in review_list if r['rating'] is not None and r['rating'] <= 4]

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
    if movie_title:
        with st.spinner('Searching for the movie...'):
            movie_url = search_movie_url(movie_title)

        if movie_url:
            st.success(f"Found movie page: {movie_url.split('?')[0]}")
            with st.spinner('Scraping reviews... this may take a moment.'):
                reviews = scrape_movie_reviews(movie_url)

            if reviews:
                filter_and_display_reviews(reviews)
            else:
                st.error("Could not scrape reviews. The IMDb page structure may have changed, or there might be no reviews available.")
        else:
            st.error(f"Could not find a movie with the title: '{movie_title}'")
