import streamlit as st
from newsapi import NewsApiClient
import os
from typing import Optional
from datetime import datetime, timedelta

from openai import OpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

ONE_WEEK = timedelta(days=7)

newsapi_key = st.secrets["NEWSAPI_KEY"]
openai_key = st.secrets["AIMLAPI_KEY"]

openai_url = "https://api.aimlapi.com/v1"

newsapi_client = NewsApiClient(api_key=newsapi_key)
openai_client = OpenAI(api_key=openai_key, base_url=openai_url)

class NewsPreferences(BaseModel):
    include: list[str] = Field(description="List of topics the user wants to include in their news search.")
    exclude: list[str] = Field(description="List of topics the user wants to exclude from their news search.")

class TopicClassifier(BaseModel):
    belongs: bool = Field(description="Yes or No | True or False")
    category: Optional[str] = Field(description="Topic which it belongs to")

news_preference_parser = JsonOutputParser(pydantic_object=NewsPreferences)
news_preference_system_prompt = (
    "You are a helpful assistant that understands user preferences for news. "
    "Your job is to parse the user's input into two lists: "
    "1. A list of topics the user wants to include in their news search. "
    "2. A list of topics the user wants to exclude from their news search. "
    "Output the response as a JSON object with two keys: 'include' and 'exclude'."
)

topic_classifier_parser = JsonOutputParser(pydantic_object=TopicClassifier)
topic_classifier_system_prompt = (
    "You are a classifier that helps determine if an article belongs to a specific topic. "
    "The user will provide a headline and summary of an article, as well as a list of topics. "
    "Your task is to analyze the headline and summary and determine if the article is relevant "
    "to any of the provided topics. Output the response as a JSON object with two keys: "
    "{belongs: True|False, category: category|None}"
)


# Country and language mappings
# country_mapping = {
#     "United Arab Emirates": "ae", "Argentina": "ar", "Austria": "at", "Australia": "au", "Belgium": "be",
#     "Bulgaria": "bg", "Brazil": "br", "Canada": "ca", "Switzerland": "ch", "China": "cn", "Colombia": "co",
#     "Cuba": "cu", "Czech Republic": "cz", "Germany": "de", "Egypt": "eg", "France": "fr", "United Kingdom": "gb",
#     "Greece": "gr", "Hong Kong": "hk", "Hungary": "hu", "Indonesia": "id", "Ireland": "ie", "Israel": "il",
#     "India": "in", "Italy": "it", "Japan": "jp", "South Korea": "kr", "Lithuania": "lt", "Latvia": "lv",
#     "Morocco": "ma", "Mexico": "mx", "Malaysia": "my", "Nigeria": "ng", "Netherlands": "nl", "Norway": "no",
#     "New Zealand": "nz", "Philippines": "ph", "Poland": "pl", "Portugal": "pt", "Romania": "ro", "Serbia": "rs",
#     "Russia": "ru", "Saudi Arabia": "sa", "Sweden": "se", "Singapore": "sg", "Slovenia": "si", "Slovakia": "sk",
#     "Thailand": "th", "Turkey": "tr", "Taiwan": "tw", "Ukraine": "ua", "United States": "us", "Venezuela": "ve",
#     "South Africa": "za"
# }

country_mapping = {
    "United States": "us",
}

# language_mapping = {
#     "Arabic": "ar", "German": "de", "English": "en", "Spanish": "es", "French": "fr", "Hebrew": "he",
#     "Italian": "it", "Dutch": "nl", "Norwegian": "no", "Portuguese": "pt", "Russian": "ru", "Swedish": "sv",
#     "Urdu": "ud", "Chinese": "zh"
# }

language_mapping = {
    "English": "en",
}

country_mapping = {k: v for k, v in sorted(country_mapping.items())}
language_mapping = {k: v for k, v in sorted(language_mapping.items())}

# Function to display news items grouped by category
def display_news(news_items, selected_categories, llm_topics):
    st.title("Newsfeed")

    if not news_items:
        st.info("No relevant news to display.")
        return

    # Grouping and displaying news by category if selected categories exist
    if llm_topics:
        for category in llm_topics:
            category_news = [item for item in news_items if (item.get('category', '').lower() == category.lower())]

            if category_news:
                st.markdown(f"---\n## {category.title()}\n---")
                for item in category_news:
                    render_article(item)
        news_items = [item for item in news_items if (item.get('category', '').lower() not in [x.lower() for x in llm_topics])]

    if selected_categories:
        # Iterate over selected categories and display news under each category
        for category in selected_categories:
            category_news = [item for item in news_items if item.get('category', '').lower() == category]
            if category_news:
                st.markdown(f"---\n## {category.capitalize()}\n---")
                for item in category_news:
                    render_article(item)
    else:
        # If no specific category is selected, display all news in one section
        st.markdown(f"---\n## Trending\n---")
        for item in news_items:
            render_article(item)

def render_article(item):
    st.subheader(item['title'])
    st.write(item['description'])
    st.markdown(f"[Read more]({item['url']})")
    url2image = item.get('urlToImage', '')
    if url2image:
        st.image(url2image)
    st.write(f"Published at: {item['publishedAt']}")
    st.markdown("---")

# Function to render category filters using checkboxes in columns
def render_category_filters(categories):
    st.sidebar.subheader("Categories")
    num_columns = 2
    columns = st.sidebar.columns(num_columns)
    selected_categories = []

    for index, category in enumerate(categories):
        col = columns[index % num_columns]
        if col.checkbox(category, key=f"{category}_checkbox"):
            selected_categories.append(category.lower())

    return selected_categories

# Function to render additional filters: language, country, and user preferences
def render_additional_filters():
    st.sidebar.subheader("Select Language")
    language_full = st.sidebar.selectbox(
        "Language",
        options=list(language_mapping.keys()),
        index=list(language_mapping.keys()).index("English")
    )
    language_code = language_mapping[language_full]

    st.sidebar.subheader("Select Countries")
    country_full_list = st.sidebar.multiselect(
        "Countries",
        options=list(country_mapping.keys())
    )
    country_codes = [country_mapping[country] for country in country_full_list]

    # Manage user preferences input with Submit/Edit functionality
    st.sidebar.subheader("User Preferences")
    
    # Initialize session state for user preferences if not already set
    if 'user_preference' not in st.session_state:
        st.session_state.user_preference = ""
    if 'preference_input_enabled' not in st.session_state:
        st.session_state.preference_input_enabled = True
    if 'preference_button_label' not in st.session_state:
        st.session_state.preference_button_label = "Submit"

    # Display the text input and button
    user_preference = st.sidebar.text_input(
        "Enter your news preferences (e.g., 'latest AI developments', 'global economy trends')",
        value=st.session_state.user_preference,
        disabled=not st.session_state.preference_input_enabled,
        placeholder="Type your preferences..."
    )

    # Display the Submit/Edit button
    if st.sidebar.button(st.session_state.preference_button_label):
        if st.session_state.preference_input_enabled:
            # If the input was enabled and user clicked Submit, disable input
            st.session_state.user_preference = user_preference
            st.session_state.preference_input_enabled = False
            st.session_state.preference_button_label = "Edit"
        else:
            # If the input was disabled and user clicked Edit, enable input
            st.session_state.preference_input_enabled = True
            st.session_state.preference_button_label = "Submit"

    return language_code, country_codes, st.session_state.user_preference


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

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_articles_topk(
    q=None,
    language=None,
    country=None,
    category=None,
    page_size=20
):
    response = newsapi_client.get_top_headlines(
                    q=q,
                    language=language,
                    country=country,
                    category=category,
                    page_size=page_size
                )
    return response.get('articles', [])

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_articles_all(
        q,
        language=None,
        page_size=20
):
    if not q:
        st.error("some error in user preference logic")
    response = newsapi_client.get_everything(
        q=q,
        language=language,
        from_param=(datetime.now() - ONE_WEEK),
        page_size=page_size
    )
    return response.get('articles', [])

@st.cache_data(ttl=3600, show_spinner=False)
def llm_check_topic_in_text(topics, headline, summary):
    user_prompt = (
        f"Headline: {headline}\n"
        f"Summary: {summary}\n"
        f"Topics: {', '.join(topics)}\n"
        "Does the article belong to any of these topics?"
    )

    # Request completion from the LLM using the user's input.
    completion = openai_client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": topic_classifier_system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,  # Lower temperature for more consistent responses.
        max_tokens=50,
    )

    # Extract the LLM's response.
    response_content = completion.choices[0].message.content

    parsed_response = {}
    try:
        parsed_response = topic_classifier_parser.parse(response_content)
        print("Parsed Response:", parsed_response)
    except Exception as e:
        print(f"Error parsing response: {e}")
    
    return parsed_response.get("belongs", False)

def llm_based_filter(articles, filter_out_topics):
    articles = [
        article for article in articles
        if not llm_check_topic_in_text(
            filter_out_topics,
            headline=article["title"],
            summary=article["description"]
        )
    ]
    return articles

def is_clean(article):
    if article["title"].lower() == "[removed]":
        return False
    return True

def fetch_news(
        language,
        countries,
        categories,
        llm_search_topics=None,
        banned_agencies=None,
        llm_ban_topics=None
    ):
    try:
        if not countries:
            countries = [None]
        if not categories:
            categories = [None]
        articles = []
        for country in countries:
            for category in categories:
                temp_articles = fetch_articles_topk(
                    q=None,
                    language=language,
                    country=country,
                    category=category,
                    page_size=20
                )
                for temp_article in temp_articles:
                    temp_article['category'] = category if category is not None else ""
                articles.extend(temp_articles)

        if llm_search_topics:
            for topic in llm_search_topics:
                temp_articles = fetch_articles_all(
                    q=topic,
                    language=language,
                    page_size=20
                )
                for temp_article in temp_articles:
                    temp_article['category'] = topic  # Tag each article with its category
                articles.extend(temp_articles)


        if banned_agencies:
            articles = [
                article for article in articles
                if article['source']['name'] not in banned_agencies
            ]
        
        articles = [
            article for article in articles
            if is_clean(article)
        ]

        if llm_ban_topics:
            articles = llm_based_filter(articles, llm_ban_topics)

        return articles
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []
    
# Function to parse user preferences using an LLM
def llm_parse_user_preference(user_preference):
    """
    This function takes the user's input preferences and uses an LLM to determine
    topics to search for and topics to exclude.
    
    Args:
        user_preference (str): The user's input describing their news preferences.

    Returns:
        tuple: A tuple containing a list of search topics and a list of ban topics.
    """

    if not user_preference:
        return [], []
    
    completion = openai_client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": news_preference_system_prompt},
            {"role": "user", "content": user_preference},
        ],
        temperature=0.3,
        max_tokens=150,
    )
    response_content = completion.choices[0].message.content
    parsed_response  = {}
    try:
        parsed_response = news_preference_parser.parse(response_content)
        print("Parsed Response:", parsed_response)
    except Exception as e:
        print(f"Error parsing response: {e}")
    
    llm_search_topics = parsed_response.get("include", [])
    llm_ban_topics = parsed_response.get("exclude", [])
    return llm_search_topics, llm_ban_topics

def main():
    categories = ["general", "business", "health", "science", "sports", "technology", "entertainment"]

    selected_categories = render_category_filters(categories)
    language_code, country_codes, user_preference = render_additional_filters()

    manage_banned_agencies()

    llm_search_topics, llm_ban_topics = llm_parse_user_preference(user_preference)

    filtered_news = fetch_news(
        language_code,
        country_codes,
        selected_categories,
        llm_search_topics,
        st.session_state.banned_agencies,
        llm_ban_topics,
    )

    display_news(filtered_news, selected_categories, llm_search_topics)

if __name__ == "__main__":
    main()
