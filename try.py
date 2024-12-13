import pickle
import streamlit as st
import requests

# Load data
def load_data():
    movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
    return movies, similarity

# API Functions
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def fetch_movie_details(movie_id):
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
        'release_year': movie_data.get('release_date', '')[:4],
        'vote_count': movie_data.get('vote_count', 0),
        'overview': movie_data.get('overview', 'No overview available.'),
        'genres': [genre['name'] for genre in movie_data.get('genres', [])],
        'runtime': movie_data.get('runtime', 'N/A'),
        'language': movie_data.get('original_language', 'N/A').upper(),
        'tagline': movie_data.get('tagline', ''),
        'status': movie_data.get('status', 'N/A')
    }






# Recommendation Function
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        
        for i in distances[1:21]:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_names.append(movies.iloc[i[0]].title)
            recommended_movie_posters.append(fetch_poster(movie_id))
            
        return recommended_movie_names, recommended_movie_posters
    except Exception as e:
        st.error(f"Error in recommend function: {e}")
        return [], []






def display_movie_details(movie_title, movie_poster, movie_details):

        st.markdown("""
            <div style="
                background-color: #ffffff;
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.1);
                margin: 1rem 0;
                border: 1px solid #eee;
            ">
        """, unsafe_allow_html=True)
        
        # Movie title
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="font-size: 2.2rem; color: #2c3e50;">{movie_title}</h2>
                <div style="color: #666; font-style: italic; margin-top: 0.5rem;">{movie_details['tagline']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Create columns for poster and details
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Poster
            st.image(movie_poster, use_column_width=True)
            
            # Movie Info
            st.markdown(f"""
                <div style="
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 10px;
                    margin-top: 1rem;
                ">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem; font-size: 1.1rem;">Movie Info</h4>
                    <div style="font-size: 0.9rem;">
                        <p><strong>Runtime:</strong> {movie_details['runtime']} min</p>
                        <p><strong>Language:</strong> {movie_details['language']}</p>
                        <p><strong>Status:</strong> {movie_details['status']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Rating and Year
            st.markdown(f"""
                <div style="
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 1.5rem;
                ">
                    <div style="
                        background: #f8f9fa;
                        padding: 0.8rem 1.2rem;
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                    ">
                        <span style="color: #ffc107; font-size: 1.2rem; margin-right: 0.5rem;">★</span>
                        <span style="font-weight: 600;">{movie_details['rating']}/10</span>
                        <span style="color: #6c757d; margin-left: 0.5rem;">({movie_details['vote_count']} votes)</span>
                    </div>
                    <div style="
                        background: #f8f9fa;
                        padding: 0.8rem 1.2rem;
                        border-radius: 10px;
                    ">
                        <span style="margin-right: 0.5rem;">📅</span>
                        <span style="font-weight: 600;">{movie_details['release_year']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Overview
            st.markdown(f"""
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: #2c3e50; margin-bottom: 0.5rem; font-size: 1.1rem;">Overview</h4>
                    <p style="color: #444; line-height: 1.6;">{movie_details['overview']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Genres
            st.markdown("""
                <h4 style="color: #2c3e50; margin-bottom: 0.5rem; font-size: 1.1rem;">Genres</h4>
            """, unsafe_allow_html=True)
            
            genre_html = "".join([f"""
                <span style="
                    display: inline-block;
                    background: #e9ecef;
                    padding: 0.4rem 0.8rem;
                    border-radius: 15px;
                    font-size: 0.9rem;
                    margin: 0.2rem;
                    color: #495057;
                ">{genre}</span>
            """ for genre in movie_details['genres']])
            
            st.markdown(f"""
                <div style="
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.5rem;
                    margin-bottom: 1.5rem;
                ">
                    {genre_html}
                </div>
            """, unsafe_allow_html=True)
            
            # Cast Section
            st.markdown("<h4 style='color: #2c3e50; margin-bottom: 0.5rem; font-size: 1.1rem;'>Top Cast</h4>", unsafe_allow_html=True)
            
            cast_html = "".join([f"""
                <span style="
                    display: inline-block;
                    background: #f8f9fa;
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    margin: 0.3rem;
                ">{cast_member}</span>
            """ for cast_member in movie_details['cast']])
            
            st.markdown(f"""
                <div style="
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.5rem;
                    margin-top: 0.5rem;
                ">
                    {cast_html}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add spacing before recommendations









def display_recommended_movies(recommended_names, recommended_posters, prefix='rec'):
    st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
    
    for row in range(4):  # 4 rows
        cols = st.columns(5)  # 5 columns
        start_idx = row * 5
        
        for i, col in enumerate(cols):
            idx = start_idx + i
            if idx < len(recommended_names):
                with col:
                    # Create clickable poster
                    poster_html = f"""
                    <div class="poster-container" 
                         onclick="handleClick('{recommended_names[idx]}')" 
                         style="cursor: pointer;">
                        <img src="{recommended_posters[idx]}" class="poster-img">
                    </div>
                    """
                    st.markdown(poster_html, unsafe_allow_html=True)
                    
                    # Display movie title as button
                    if st.button(
                        recommended_names[idx],
                        key=f"{prefix}_movie_{idx}",
                        help=f"Click to see details for {recommended_names[idx]}",
                    ):
                        handle_movie_click(recommended_names[idx])

    st.markdown('</div>', unsafe_allow_html=True)

def handle_movie_click(movie_title):
    try:
        # Get movie details
        movie_id = movies[movies['title'] == movie_title]['movie_id'].iloc[0]
        movie_details = fetch_movie_details(movie_id)
        movie_poster = fetch_poster(movie_id)
        
        # Update session state
        st.session_state.selected_movie = {
            'title': movie_title,
            'poster': movie_poster,
            'id': movie_id,
            'details': movie_details
        }
        
        # Get new recommendations
        new_names, new_posters = recommend(movie_title)
        st.session_state.recommendations = {
            'names': new_names,
            'posters': new_posters
        }
        
        # Force rerun to update the UI
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"Error handling movie click: {e}")

def search_movie(query):
    query = query.strip().lower()
    movie_titles = movies['title'].str.lower()
    matched_movies = movies[movie_titles.str.contains(query, na=False)]
    return matched_movies

# Main App
def main():
    st.markdown(
        """
        <style>
        /* Add background image styling */
        .stApp {
            background-image: url('https://st5.depositphotos.com/1234320/72924/i/450/depositphotos_729249552-stock-photo-soft-blurred-gradient-pastel-colors.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        

        .poster-img {
            width: 100%;
            height: auto;
            max-height: 225px;  /* Adjusted height */
            object-fit: cover;
            border-radius: 6px;
            display: block;
        }

        /* Detail poster specific styles */
        .detail-poster {
            max-width: 200px;  /* Slightly larger for detail view */
        }

        /* Movie grid layout */
        .movie-row {
            margin-bottom: 1rem;
            display: flex;
            gap: 0.5rem;
            justify-content: center;
        }

        .recommendation-section {
            padding: 0.5rem 0;
        }

        /* Button styles */
        .stButton > button {
            font-size: 0.8rem !important;
            padding: 0.3rem 0.5rem !important;
            height: auto !important;
            min-height: 0 !important;
            width: 100% !important;
            white-space: normal !important;
            word-wrap: break-word !important;
        }

        /* Movie stats and cast styles */
        .movie-stats {
            display: flex;
            gap: 1rem;
            margin: 1rem 0;
        }

        .stat-item {
            background: #f8f9fa;
            padding: 0.4rem 0.8rem;
            border-radius: 15px;
            font-size: 0.9rem;
        }

        .cast-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }

        .cast-member {
            background: #f8f9fa;
            padding: 0.3rem 0.6rem;
            border-radius: 15px;
            font-size: 0.8rem;
        }

        

        /* Detail poster specific styles */
        .detail-poster {
            max-width: 200px;
            margin: 0 auto;
        }

        /* Movie stats styling */
        .movie-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin: 1rem 0;
        }

        .stat-item {
            background: white;
            padding: 0.6rem 1rem;
            border-radius: 20px;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .rating-star {
            color: #ffc107;
            font-size: 1.2rem;
        }

        /* Cast section styling */
        .cast-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .cast-member {
            background: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="header"><h1>Personalized Movie Recommendation System</h1></div>', unsafe_allow_html=True)
    
    # Load data
    global movies, similarity
    movies, similarity = load_data()
    
    # Search section
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    with st.container():
        selected_movie = st.text_input(
            "Enter a Movie",
            key="movie_search",
            label_visibility="visible"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            search_button = st.button('Search')
    
    # Handle search and display
    if search_button and selected_movie:
        matched_movies = search_movie(selected_movie)
        
        if matched_movies.empty:
            st.warning("Movie not found! Please check the spelling or try another movie.")
        else:
            matched_movie = matched_movies.iloc[0]
            handle_movie_click(matched_movie['title'])
    
    # Always display selected movie details if available
    if st.session_state.get('selected_movie'):
        movie = st.session_state.selected_movie
        
        display_movie_details(movie['title'], movie['poster'], movie['details'])
            
            # Display recommendations if available
        if st.session_state.get('recommendations'):
                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
                st.subheader("You Might Also Like")
                display_recommended_movies(
                    st.session_state.recommendations['names'],
                    st.session_state.recommendations['posters'],
                    prefix=f"rec_{movie['id']}"
                )
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
