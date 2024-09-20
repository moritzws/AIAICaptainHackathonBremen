import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬HanseGPT Assistant")
st.write()

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management

# https://your_app.streamlit.app/?api_key=1
if st.query_params.get("api_key"):
    openai_api_key = st.query_params["api_key"]
else:
    openai_api_key = st.secrets["openapi_key"]

if not openai_api_key:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Dropdown menu for role selection
    roles = ["Verwaltung", "Filiale", "Presse", "Rechtsabteilung"]
    selected_role = st.selectbox("Wo bei Rossman arbeitest du", roles)

    # Define locations for each role
    locations = {
        "Verwaltung": [51.9607, 7.6261],  # Münster (Rossmann headquarters)
        "Filiale": [52.3759, 9.7320],  # Hannover (example city with Rossmann stores)
        "Presse": [52.5200, 13.4050],  # Berlin (capital city, likely location for press office)
        "Rechtsabteilung": [50.1109, 8.6821]  # Frankfurt (financial hub, possible location for legal department)
    }

    # Initialize session state for selected role if not exists
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = roles[0]

    # Update session state when a new role is selected
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role

    # Get the coordinates for the selected role
    selected_location = locations[st.session_state.selected_role]

    # Create a map centered on the selected location
    st.write(
        f"Standort für {st.session_state.selected_role}: Latitude {selected_location[0]}, Longitude {selected_location[1]}")

    col1, col2 = st.columns(2)

    client = OpenAI(api_key=openai_api_key)

    # Sidebar for chat input and messages
    with col1:
        with st.container(height=320):
            # Create a session state variable to store the chat messages. This ensures that the
            # messages persist across reruns.
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Display the existing chat messages via `st.chat_message`.
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Create a chat input field to allow the user to enter a message. This will display
            # automatically at the bottom of the page.
            if prompt := st.chat_input("Wo klemmt's?"):
                # Store and display the current prompt.
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generate a response using the OpenAI API.
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )

                # Stream the response to the chat using `st.write_stream`, then store it in 
                # session state.
                with st.chat_message("assistant"):
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})

    with col2:
        with st.container(height=320):
            st.map(
                data=[{"lat": selected_location[0], "lon": selected_location[1]}],
                zoom=10,
            )
