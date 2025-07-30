import streamlit as st
import requests
from bs4 import BeautifulSoup

def get_google_reviews(movie_title):
    """
    Searches Google for movie reviews and scrapes the snippets.
    """
    search_query = f"{movie_title} movie reviews"
    search_url = f"https://www.google.com/search?q={search_query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    reviews_list = []

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Google's class names can be obfuscated and change often.
        # This selector looks for the containers that typically hold search results.
        # We will then look for text snippets within these containers.
        review_containers = soup.find_all('div', class_='g')

        for container in review_containers:
            # Try to find a snippet of text that looks like a review
            snippet_element = container.find('div', {'data-sncf': '1'})
            if snippet_element:
                snippet_text = snippet_element.get_text(strip=True)
                if len(snippet_text) > 50: # Filter out short, irrelevant text
                    reviews_list.append(snippet_text)

        # If the first selector doesn't work, try a fallback
        if not reviews_list:
             for container in soup.find_all("div", class_="VwiC3b"):
                review_text = container.get_text(strip=True)
                if len(review_text) > 50:
                    reviews_list.append(review_text)


    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Google search results: {e}")
    except Exception as e:
        st.error(f"An error occurred while parsing reviews: {e}")
        
    return reviews_list

# --- Streamlit App Interface ---
st.title('🎬 Google Movie Review Finder')
st.write("Enter the title of a movie to see review snippets from Google.")
movie_title = st.text_input('Movie Title', 'Inception')

if st.button('Search for Reviews'):
    if movie_title:
        with st.spinner('Searching Google for reviews...'):
            reviews = get_google_reviews(movie_title)

        if reviews:
            st.header("Review Snippets Found on Google")
            for i, review in enumerate(reviews[:5]): # Display up to 5 reviews
                st.write(f"**Review {i+1}:**")
                st.write(f"> {review}")
                st.write("---")
        else:
            st.error("Could not find any review snippets on Google. Please try a different movie title.")
