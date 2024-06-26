import streamlit as st
import json
from llama_index.core import Document, VectorStoreIndex, ServiceContext
from llama_index.llms.openai import OpenAI

# Access the API keys from environment variables
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Display images in the sidebar with specific dimensions
st.sidebar.image("images/logo2.png", use_column_width=False, width=150)


# Define the chatbot function
def show_chatbot():
    st.header("Chat with Amazon Seller Central Assistant 💬")

    if "messages" not in st.session_state.keys():  # Initialize the chat message history
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Ask me a question about Selling on Amazon!",
            }
        ]

    @st.cache_resource(show_spinner=False)
    def my_load_data():
        with st.spinner(text="Documents are loading, please wait!..."):

            # Open Our dataset stored in json file
            with open("data/rag_dataset.json", "r", encoding="utf-8") as file:
                rag_dataset = json.load(file)

            # Create a list of Document objects
            documents_list = [
                Document(
                    text=doc["content"],
                    metadata={
                        "source_id": doc["source_id"],
                        "topic": doc["topic"],
                        "url": doc["url"],
                        "title": doc["title"],
                        "sub_title": doc["sub_title"],
                    },
                )
                for doc in rag_dataset
            ]

            # Service context tanimla
            service_context = ServiceContext.from_defaults(
                llm=OpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.5,
                    system_prompt="""You are a knowledgeable learning assistant. 
                                    Your users are asking questions about selling products on Amazon 
                                    and some documents are provided for you about selling products on amazon.com 
                                    You will be shown the user's question, and the relevant information from the amazon seller central informative materials. 
                                    Answer the user's question using only this information. 
                                    If you don't know the answer, just say you don't know. 
                                    Use three sentences maximum and be concise in your response.""",
                )
            )

            # Create a VectorStoreIndex from the list of documents
            index = VectorStoreIndex.from_documents(
                documents_list, service_context=service_context
            )
            return index

    index = my_load_data()

    # Create the chat engine
    chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=False)

    if prompt := st.chat_input(
        "Your question"
    ):  # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:  # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_engine.chat(prompt)
                st.write(response.response)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(
                    message
                )  # Add response to message history


# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chatbot", "Introduction"])

if page == "Chatbot":
    show_chatbot()
else:
    import presentation

    presentation.show_presentation()
