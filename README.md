# 💬 AI AI Bremen

## FastAPI client
### How to run it on your own machine
1. Install the requirements
   ```
   $ pip install -r requirements_fast_api.txt
   ```
2. Set env variables
   ```
   OPENAI_API_KEY="your_open_ai_api_key"
   DB_TOKEN="database_usage_token"
   ```
3. Run the app
   ```
   $ python start_fast_api.py
   ```
4. Visit [http://localhost:8000/docs](http://localhost:4342/docs)

## Streamlit app
### Link
- https://bremen.streamlit.app/
### Magic Link including your own API key
- https://bremen.streamlit.app/?api_key=<your_open_ai_api_key>

### How to run it on your own machine

1. Install the requirements
   ```
   $ pip install -r requirements.txt
   ```

2. Run the app
   ```
   $ streamlit run streamlit_app.py
   ```
