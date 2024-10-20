# newsfeedai

## Project Description
**newsfeedai** is an application that allows users to receive a tailored news feed based on their preferences. By leveraging NewsAPI for fetching the latest news and OpenAI models for understanding user preferences and classifying articles, the app ensures a personalized news consumption experience.

## Features
- **Customized News Feed:** Users can select categories, countries, and languages for news, and specify preferences for topics they want to see more or less of.
- **LLM-Driven User Preferences:** The app uses an AI language model to interpret user-specified preferences, enabling nuanced topic inclusions and exclusions.
- **Ban List Management:** Users can ban specific news agencies to exclude their content from the feed.
- **Filtered News Display:** News articles are categorized and displayed based on user selections, with options for viewing all articles or specific categories.

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/newsfeedai.git
cd newsfeedai
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Create a `.env` file and add your API keys:
```
NEWSAPI_KEY=your_newsapi_key
AIMLAPI_KEY=your_openai_key
```

4. Run the application:
```
streamlit run app.py
```

## How It Works
- **Input Preferences:** Users input their preferences using the sidebar (e.g., "latest AI developments" or "exclude politics").
- **Parse User Preferences:** The app sends user preferences to the LLM for parsing, generating lists of topics to include or exclude.
- **Fetch News:** News is fetched using the NewsAPI based on user preferences, country, and language selection.
- **Filter News:** Articles are further filtered by:
  - Banned news agencies.
  - Relevance to user preferences (checked using LLM).
  - Cleanliness of the content (e.g., articles not marked as removed).
- **Display News:** The news is displayed in the Streamlit app, grouped by categories and tailored topics.

## Code Structure
- **app.py:** Main file containing the Streamlit application logic and UI components.
- **fetch_articles_topk()**: Fetches top headlines based on the selected country, category, and language.
- **fetch_articles_all()**: Fetches a wider range of articles based on user-specified search topics.
- **llm_check_topic_in_text()**: Uses the LLM to classify whether a given article matches any specified topic.
- **display_news()**: Displays the filtered articles in the Streamlit interface, grouped by categories.
- **manage_banned_agencies()**: Allows users to add or remove news agencies from a ban list.
- **llm_parse_user_preference()**: Interprets user input to determine which topics to include or exclude using an LLM.
- **render_additional_filters()**: Handles UI for selecting language, countries, and user input for preferences.

## Example Usage
To filter for news about AI developments and exclude political content:
1. Enter "AI developments" as a preference.
2. Choose "Exclude" for "Politics."
3. Select "United States" as the country and "English" as the language.
4. Click "Submit" to see the tailored feed.

## Technologies Used
- **Streamlit:** For creating an interactive web interface.
- **NewsAPI:** For fetching news articles.
- **OpenAI API:** For language model-based processing of user preferences.
- **Python Libraries:** `pydantic` for structured data validation, `dotenv` for environment variable management.

## Future Improvements
- **Add More News Sources:** Extend the app to support additional news APIs.
- **User Authentication:** Allow users to save their preferences and access them across sessions.
- **Enhanced Topic Classification:** Use more advanced LLM models for improved classification and topic understanding.
- **From Web to Native Platforms:** Cross-platform application

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/syedsalman137/newsfeedai/blob/main/LICENSE) file for details.

## Contact
For any questions or suggestions, please open an issue or contact the project maintainer at [salmangithub137@gmail.com].
