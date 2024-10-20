import streamlit as st
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize News API client
newsapi_key = os.getenv('NEWSAPI_KEY')
api = NewsApiClient(api_key='XXXXXXXXXXXXXXXXXXXXXXX')

# Country and language mappings
country_mapping = {
    "United Arab Emirates": "ae", "Argentina": "ar", "Austria": "at", "Australia": "au", "Belgium": "be",
    "Bulgaria": "bg", "Brazil": "br", "Canada": "ca", "Switzerland": "ch", "China": "cn", "Colombia": "co",
    "Cuba": "cu", "Czech Republic": "cz", "Germany": "de", "Egypt": "eg", "France": "fr", "United Kingdom": "gb",
    "Greece": "gr", "Hong Kong": "hk", "Hungary": "hu", "Indonesia": "id", "Ireland": "ie", "Israel": "il",
    "India": "in", "Italy": "it", "Japan": "jp", "South Korea": "kr", "Lithuania": "lt", "Latvia": "lv",
    "Morocco": "ma", "Mexico": "mx", "Malaysia": "my", "Nigeria": "ng", "Netherlands": "nl", "Norway": "no",
    "New Zealand": "nz", "Philippines": "ph", "Poland": "pl", "Portugal": "pt", "Romania": "ro", "Serbia": "rs",
    "Russia": "ru", "Saudi Arabia": "sa", "Sweden": "se", "Singapore": "sg", "Slovenia": "si", "Slovakia": "sk",
    "Thailand": "th", "Turkey": "tr", "Taiwan": "tw", "Ukraine": "ua", "United States": "us", "Venezuela": "ve",
    "South Africa": "za"
}

language_mapping = {
    "Arabic": "ar", "German": "de", "English": "en", "Spanish": "es", "French": "fr", "Hebrew": "he",
    "Italian": "it", "Dutch": "nl", "Norwegian": "no", "Portuguese": "pt", "Russian": "ru", "Swedish": "sv",
    "Urdu": "ud", "Chinese": "zh"
}

# Function to display news items
def display_news(news_items):
    st.title("Newsfeed")

    if not news_items:
        st.info("No relevant news to display.")
        return

    for item in news_items:
        st.subheader(item['title'])
        st.write(item['description'])
        st.markdown(f"[Read more]({item['url']})")
        st.image(item.get('urlToImage', ''))
        st.write(f"Published at: {item['publishedAt']}")
        st.markdown("---")

# Function to render category filters using checkboxes in columns
def render_category_filters(categories):
    st.sidebar.subheader("Categories")
    num_columns = 3
    columns = st.sidebar.columns(num_columns)
    selected_categories = []

    for index, category in enumerate(categories):
        col = columns[index % num_columns]
        if col.checkbox(category, key=f"{category}_checkbox"):
            selected_categories.append(category.lower())

    return selected_categories

# Function to render additional filters: language, country, and user preferences
def render_additional_filters():
    # Language selection
    st.sidebar.subheader("Select Language")
    language_full = st.sidebar.selectbox(
        "Language",
        options=list(language_mapping.keys()),
        index=list(language_mapping.keys()).index("English")
    )
    language_code = language_mapping[language_full]

    # Country selection
    st.sidebar.subheader("Select Countries")
    country_full_list = st.sidebar.multiselect(
        "Countries",
        options=list(country_mapping.keys())
    )
    country_codes = [country_mapping[country] for country in country_full_list]

    # Text input for user preferences
    st.sidebar.subheader("User Preferences")
    user_preference = st.sidebar.text_input(
        "Enter your news preferences (e.g., 'latest AI developments', 'global economy trends')",
        placeholder="Type your preferences..."
    )

    return language_code, country_codes, user_preference

# Function to manage banned news agencies
def manage_banned_agencies():
    st.sidebar.subheader("Banned News Agencies")

    if 'banned_agencies' not in st.session_state:
        st.session_state.banned_agencies = []

    new_agency = st.sidebar.text_input("Enter news agency to ban", key="new_agency")
    if st.sidebar.button("Add to Ban List", key="add_agency"):
        if new_agency and new_agency not in st.session_state.banned_agencies:
            st.session_state.banned_agencies.append(new_agency)
            st.sidebar.success(f"Added '{new_agency}' to banned list.")
        else:
            st.sidebar.warning("Agency already in the banned list or input is empty.")

    if st.session_state.banned_agencies:
        st.sidebar.write("Banned Agencies:")
        for agency in st.session_state.banned_agencies:
            cols = st.sidebar.columns([4, 1])
            cols[0].write(agency)
            if cols[1].button("❌", key=f"remove_{agency}"):
                st.session_state.banned_agencies.remove(agency)
                st.sidebar.info(f"Removed '{agency}' from banned list.")

# Function to fetch news using NewsAPI
def fetch_news(language, country, category, user_preference, banned_agencies):
    try:
        response = api.get_top_headlines(
            q=user_preference,
            language=language,
            country=country if country else None,
            category=category if category else None,
            page_size=20
        )
        articles = response.get('articles', [])
        # Filter out articles from banned agencies
        articles = [
            article for article in articles
            if article['source']['name'] not in banned_agencies
        ]
        return articles
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

# Main function for the app
def main():
    categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]

    selected_categories = render_category_filters(categories)
    language_code, country_codes, user_preference = render_additional_filters()

    manage_banned_agencies()

    # Get the first country or use None
    selected_country = country_codes[0] if country_codes else None
    selected_category = selected_categories[0] if selected_categories else None

    # Fetch news based on the selected filters
    filtered_news = fetch_news(
        language_code,
        selected_country,
        selected_category,
        user_preference,
        st.session_state.banned_agencies
    )

    display_news(filtered_news)

if __name__ == "__main__":
    main()
