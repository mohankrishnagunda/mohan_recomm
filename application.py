import pickle
import streamlit as st
import requests

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def fetch_movie_details(movie_id):
    # Base URL and API key
    base_url = "https://api.themoviedb.org/3"
    api_key = "8265bd1679663a7ea12ac168da84d2e8"
    
    # Fetch movie details
    movie_url = f"{base_url}/movie/{movie_id}?api_key={api_key}"
    movie_response = requests.get(movie_url)
    movie_data = movie_response.json()
    
    # Fetch cast
    cast_url = f"{base_url}/movie/{movie_id}/credits?api_key={api_key}"
    cast_response = requests.get(cast_url)
    cast_data = cast_response.json()
    
    # Get top 5 cast members
    top_cast = cast_data.get('cast', [])[:5]
    cast_names = [actor['name'] for actor in top_cast]
    
    return {
        'cast': cast_names,
        'rating': movie_data.get('vote_average', 'N/A'),
        'release_year': movie_data.get('release_date', '')[:4],  # Get just the year
        'vote_count': movie_data.get('vote_count', 0)
    }

def recommend(movie):
    try:
        # Get the index of the movie
        index = movies[movies['title'] == movie].index[0]
        
        # Get similarity scores and sort them
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        # Get top 20 recommendations
        recommended_movie_names = []
        recommended_movie_posters = []
        
        for i in distances[1:21]:  # Skip first movie (itself) and get next 20
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_names.append(movies.iloc[i[0]].title)
            recommended_movie_posters.append(fetch_poster(movie_id))
            
        return recommended_movie_names, recommended_movie_posters
    except Exception as e:
        st.error(f"Error in recommend function: {e}")
        return [], []


# Streamlit UI
st.markdown(
    """
    <style>
    .main-container {
        background-color: #f8f9fa;
        padding: 20px;
        font-family: 'Arial', sans-serif;
    }
    .header {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #343a40;
        margin-bottom: 20px;
    }
    .center-btn {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .poster-container {
        text-align: center;
        padding: 10px;
        transition: transform 0.3s ease;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 10px;
        height: 100%;
    }
    .poster-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .movie-title {
        font-weight: bold;
        font-size: 14px;
        margin: 10px 0;
        color: #495057;
        height: 40px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    .poster-img {
        width: 150px;
        height: 225px;
        border-radius: 8px;
        object-fit: cover;
    }
    .recommendation-section {
        margin-top: 30px;
    }
    .movie-row {
        margin-bottom: 30px;
    }
    .movie-details {
        margin-top: 20px;
        padding: 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .cast-section {
        margin: 15px 0;
    }
    .cast-list {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
    }
    .cast-member {
        background: #f8f9fa;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 14px;
    }
    .movie-stats {
        display: flex;
        gap: 20px;
        margin: 15px 0;
        flex-wrap: wrap;
    }
    .stat-item {
        background: #f8f9fa;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .rating-star {
        color: #ffc107;
    }
    .clickable-movie {
        cursor: pointer;
        width: 100%;
        border: none;
        background: none;
        padding: 0;
    }
    .clickable-movie:hover .poster-container {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .search-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        margin: 20px 0;
    }
    
    .stTextInput {
        width: 100%;
    }
    
    .search-button {
        display: flex;
        justify-content: center;
        margin-top: 10px;
    }
    
    .search-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .search-input {
        width: 100%;
        margin-bottom: 15px;
    }
    
    .search-button-container {
        width: 100%;
        display: flex;
        justify-content: center;
        margin-top: 10px;
    }
    
    .stButton > button {
        width: 200px;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<div class="header">Personalized Movie Recommendation System</div>', unsafe_allow_html=True)

# Load movie data and similarity matrix
movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

# Initialize session states if they don't exist
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

# If there's a movie in session state, display it
if st.session_state.selected_movie:
    movie = st.session_state.selected_movie
    st.subheader("Selected Movie")
    
    col1, col2 = st.columns([1, 2])
    
    # Display poster in the first column
    with col1:
        st.markdown(
            f"""
            <div class="poster-container">
                <img src="{movie['poster']}" class="poster-img">
                <div class="movie-title">{movie['title']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Display movie details in the second column
    with col2:
        st.markdown(
            f"""
            <div class="movie-stats">
                <div class="stat-item">
                    <span class="rating-star">★</span> {movie['details']['rating']}/10
                    <span style="color: #6c757d; margin-left: 5px;">
                        ({movie['details']['vote_count']} votes)
                    </span>
                </div>
                <div class="stat-item">
                    📅 {movie['details']['release_year']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<h4>Top Cast</h4>", unsafe_allow_html=True)
        cast_html = "".join([
            f'<span class="cast-member">{cast}</span>' 
            for cast in movie['details']['cast']
        ])
        st.markdown(f'<div class="cast-list">{cast_html}</div>', unsafe_allow_html=True)
    
    # Get new recommendations based on selected movie
    recommended_movie_names, recommended_movie_posters = recommend(movie['title'])

# Search bar for movie input
st.markdown('<div class="search-section">', unsafe_allow_html=True)
with st.container():
    selected_movie = st.text_input(
        "Enter a Movie",
        placeholder="Enter a movie name...",
        key="movie_search"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        search_button = st.button('Search')

if search_button:
    if selected_movie:  # Check if user has entered a movie
        try:
            # Strip and lowercase the input for case-insensitive matching
            selected_movie = selected_movie.strip().lower()
            movie_titles = movies['title'].str.lower()  # Lowercase the dataset movie titles

            # Find movies that contain the entered text
            matched_movies = movies[movie_titles.str.contains(selected_movie, na=False)]

            if matched_movies.empty:
                st.warning("Movie not found! Please check the spelling or try another movie.")
            else:
                # Use the first match for recommendations
                matched_movie = matched_movies.iloc[0]
                matched_movie_title = matched_movie['title']
                matched_movie_id = matched_movie['movie_id']

                # Fetch the poster for the selected movie
                selected_movie_poster = fetch_poster(matched_movie_id)

                # Display the selected movie
                st.subheader("Selected Movie")
                
                # Fetch additional movie details
                movie_details = fetch_movie_details(matched_movie_id)
                
                col1, col2 = st.columns([1, 2])
                
                # Display poster in the first column
                with col1:
                    st.markdown(
                        f"""
                        <div class="poster-container">
                            <img src="{selected_movie_poster}" class="poster-img">
                            <div class="movie-title">{matched_movie_title}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                
                # Display cast and movie stats in the second column
                with col2:
                    # Display movie stats
                    st.markdown(
                        f"""
                        <div class="movie-stats">
                            <div class="stat-item">
                                <span class="rating-star">★</span> {movie_details['rating']}/10
                                <span style="color: #6c757d; margin-left: 5px;">
                                    ({movie_details['vote_count']} votes)
                                </span>
                            </div>
                            <div class="stat-item">
                                📅 {movie_details['release_year']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Display cast section
                    st.markdown("<h4>Top Cast</h4>", unsafe_allow_html=True)
                    cast_html = "".join([
                        f'<span class="cast-member">{cast}</span>' 
                        for cast in movie_details['cast']
                    ])
                    st.markdown(f'<div class="cast-list">{cast_html}</div>', unsafe_allow_html=True)

                # Get recommendations
                recommended_movie_names, recommended_movie_posters = recommend(matched_movie_title)

                # Handle empty recommendations
                if not recommended_movie_names:
                    st.warning("No recommendations found for this movie. Please try another one.")
                else:
                    st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
                    st.subheader("Recommended Movies")
                    
                    # Display movies in rows with proper spacing
                    for row in range(4):  # 4 rows
                        st.markdown('<div class="movie-row">', unsafe_allow_html=True)
                        cols = st.columns(5)  # 5 columns per row
                        start_idx = row * 5
                        end_idx = start_idx + 5
                        
                        for i, col in enumerate(cols):
                            idx = start_idx + i
                            if idx < len(recommended_movie_names):
                                movie_id = movies[movies['title'] == recommended_movie_names[idx]]['movie_id'].iloc[0]
                                with col:
                                    # Display movie poster
                                    st.markdown(
                                        f"""
                                        <div class="poster-container">
                                            <img src="{recommended_movie_posters[idx]}" class="poster-img">
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                    
                                    # Make the title clickable using a button styled as text
                                    if st.button(
                                        recommended_movie_names[idx],
                                        key=f"movie_{idx}",
                                        help=f"Click to see recommendations for {recommended_movie_names[idx]}"
                                    ):
                                        try:
                                            # Get movie ID and fetch all required details
                                            movie_id = movies[movies['title'] == recommended_movie_names[idx]]['movie_id'].iloc[0]
                                            movie_details = fetch_movie_details(movie_id)
                                            movie_poster = fetch_poster(movie_id)
                                            
                                            # Get new recommendations
                                            new_names, new_posters = recommend(recommended_movie_names[idx])
                                            
                                            # Update session state with complete movie information
                                            st.session_state.selected_movie = {
                                                'title': recommended_movie_names[idx],
                                                'poster': movie_poster,
                                                'id': movie_id,
                                                'details': movie_details
                                            }
                                            
                                            # Store recommendations in session state
                                            st.session_state.recommendations = {
                                                'names': new_names,
                                                'posters': new_posters
                                            }
                                            
                                            # Force a rerun to update the UI
                                            st.experimental_rerun()
                                        except Exception as e:
                                            st.error(f"Error getting recommendations: {e}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a movie name to get recommendations.")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
