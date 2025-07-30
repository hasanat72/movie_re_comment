import streamlit as st
import imdb

def get_movie_reviews(movie_title):
    """
    Fetches user reviews for a given movie title using the imdbpy library.
    """
    ia = imdb.IMDb()
    reviews_list = []

    try:
        # Search for the movie
        movies = ia.search_movie(movie_title)
        if not movies:
            st.error(f"No movie found for the title: {movie_title}")
            return []

        movie = movies[0]
        ia.update(movie, 'reviews')

        if 'reviews' not in movie:
            st.warning(f"No reviews found for {movie['title']}.")
            return []

        for review in movie['reviews']:
            review_text = review.get('content', 'N/A')
            rating = review.get('rating')
            reviews_list.append({'review_text': review_text, 'rating': rating})

    except Exception as e:
        st.error(f"An error occurred while fetching reviews: {e}")
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
st.title('🎬 IMDb Movie Review Finder')
st.write("Enter the title of a movie to see its positive and negative reviews.")
movie_title = st.text_input('Movie Title', 'The Dark Knight')

if st.button('Search for Reviews'):
    if movie_title:
        with st.spinner('Searching for reviews... this may take a moment.'):
            reviews = get_movie_reviews(movie_title)
        
        if reviews:
            filter_and_display_reviews(reviews)
