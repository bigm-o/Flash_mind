import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import io
import base64
import random
from docx import Document # For .docx files
from PyPDF2 import PdfReader # For .pdf files
import streamlit.components.v1 as components
import json

# Import SendGrid libraries
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

from streamlit_extras.stylable_container import stylable_container

# --- Gemini API Configuration ---
gemini_api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_key")

st.set_page_config(page_title="🧠 FlashMind AI", layout="centered")

st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
)

# --- Image Encoding Function (keep for background) ---
def get_base64_image(image_path):
    """Encodes a local image file to a base64 string for CSS background."""
    try:
        # Determine MIME type based on file extension
        if image_path.lower().endswith(('.png')):
            mime_type = "image/png"
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            mime_type = "image/jpeg"
        elif image_path.lower().endswith(('.gif')):
            mime_type = "image/gif"
        else:
            mime_type = "image/jpeg"
            st.warning(f"Unknown image type for {image_path}. Defaulting to image/jpeg.")

        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        st.error(f"Background image not found at: {image_path}. Please ensure the file exists.")
        return ""
    except Exception as e:
        st.error(f"Error encoding background image: {e}")
        return ""

# --- Specify your local background image path ---
image_number = random.randint(1, 6)
BACKGROUND_IMAGE_PATH = f"images/image{image_number}.jpg"
encoded_background_image = get_base64_image(BACKGROUND_IMAGE_PATH)

st.markdown(f"""
<style>
    /* Google Fonts Import - MUST be at the top of the <style> block */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;700&display=swap');

    /* Overall App Background and Font */
    html, body {{
        font-family: 'Poppins', sans-serif;
        background-color: #f0f2f6; /* Fallback background color */
    }}

    /* Target Streamlit's main container for background image */
    [data-testid="stApp"] {{
        background-image: url("{encoded_background_image}"); /* Using Base64 encoded image */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #e0e0e0;
    }}
</style>
""", unsafe_allow_html=True)

# --- Function to load CSS from a file ---
def load_css(file_path):
    """Loads custom CSS from a specified file."""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: CSS file not found at '{file_path}'. Please ensure the file exists.")
    except Exception as e:
        st.error(f"Error loading CSS from '{file_path}': {e}")

# --- Load custom CSS for Styling ---
load_css("static/style.css")

st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center; text-align: center; font-size: 3rem;">
        <i class="fas fa-brain" style="color: #ffffff;"></i> </div>
    <br>
    <div class="hide-on-mobile" style="display: flex; align-items: center; justify-content: center; text-align: center; font-size: 3rem;">
        <strong>FLASHMIND AI</strong>
    </div>
    <div class="hide-on-large" style="display: flex; align-items: center; justify-content: center; text-align: center; font-size: 1.8rem;">
        <strong>FLASHMIND AI</strong>
    </div>
    <br>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="text-align: center; font-size: 1.5rem;">
        <span class="hide-on-mobile">Turn your notes into knowledge: Flashcards & Q&A powered by AI</span>
        <span class="hide-on-large" style="font-size: 1rem;">Turn your notes into knowledge: Flashcards & Q&A powered by AI</span>
        <br>
        <div style="text-align: center; margin-top: 30px; margin-bottom: 30px;">
            <a href="https://github.com/bigm-o/Flash_mind.git" target="_blank" class="simple-repo-button">
                <i class="fab fa-github"></i> View on GitHub
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# Check if API key is available from secrets/environment variables
if not gemini_api_key:
    st.error("Gemini API Key not found. Please ensure it's set in your `.streamlit/secrets.toml` file or as an environment variable.")
    st.stop()

try:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}. Please verify your API key's validity.")
    st.stop()

# --- Read the prompt from prompt.txt ---
try:
    with open("src/prompt.txt", "r") as f:
        system_instruction_prompt = f.read().strip()
except FileNotFoundError:
    st.error("Error: 'src/prompt.txt' not found. Please make sure the prompt file is in the 'src' directory.")
    st.stop()
except Exception as e:
    st.error(f"Error reading 'src/prompt.txt': {e}")
    st.stop()

# --- Functions for Document Text Extraction ---
def extract_text_from_pdf(file_bytes):
    """Extracts text from a PDF file."""
    text = ""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_docx(file_bytes):
    """Extracts text from a DOCX file."""
    text = ""
    try:
        document = Document(io.BytesIO(file_bytes))
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return None

def extract_text_from_txt(file_bytes):
    """Extracts text from a TXT file."""
    try:
        # Decode as UTF-8, with error handling for common issues
        return file_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        st.error(f"Error extracting text from TXT: {e}")
        return None

# --- Session State Initialization ---
if "app_state" not in st.session_state:
    st.session_state.app_state = "initial_input"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_text" not in st.session_state:
    st.session_state.document_text = None
if "subject_title" not in st.session_state:
    st.session_state.subject_title = None

if "first_chat_used" not in st.session_state:
    st.session_state.first_chat_used = False
if "flashcards_for_message_idx" not in st.session_state:
    st.session_state.flashcards_for_message_idx = -1 # Stores the index of the AI message for which flashcards are shown
if "initial_flashcards_generated" not in st.session_state:
    st.session_state.initial_flashcards_generated = False
if "show_email_form" not in st.session_state:
    st.session_state.show_email_form = False
if "generated_flashcards_data" not in st.session_state:
    st.session_state.generated_flashcards_data = [] # Store the generated flashcards

# --- Email Sending Utility (SendGrid Integration) ---
def send_flashcards_email(recipient_email, flashcards_data, subject_title="FlashMind AI Flashcards"):
    """
    Sends flashcards via email using SendGrid.
    Requires SENDGRID_API_KEY and SENDER_EMAIL to be set in .streamlit/secrets.toml
    """
    sendgrid_api_key = st.secrets.get("SENDGRID_API_KEY")
    sender_email = st.secrets.get("SENDER_EMAIL")

    if not sendgrid_api_key or not sender_email:
        st.error("Email sending is not configured. Please set SENDGRID_API_KEY and SENDER_EMAIL in your `.streamlit/secrets.toml` file.")
        return

    # Construct HTML email body
    email_body_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Poppins', sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }}
            h2 {{ color: #555; }}
            .flashcard-section {{ margin-bottom: 20px; border: 1px dashed #ccc; padding: 15px; border-radius: 5px; background-color: #fff; }}
            .question {{ font-weight: bold; color: #555; }}
            .answer {{ color: #008000; margin-top: 5px; }}
            .footer {{ margin-top: 30px; font-size: 0.9em; color: #777; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Your Flashcards on "{subject_title}" from FlashMind AI</h2>
            <p>Hello,</p>
            <p>Here are the flashcards you requested:</p>
    """

    for i, card in enumerate(flashcards_data):
        email_body_html += f"""
            <div class="flashcard-section">
                <p class="question"><strong>Q{i+1}:</strong> {card['question']}</p>
                <p class="answer"><strong>A{i+1}:</strong> {card['answer']}</p>
            </div>
        """
    
    email_body_html += f"""
            <p>Happy learning!</p>
            <p>Best regards,<br>The FlashMind AI Team</p>
            <div class="footer">
                <p>This email was sent from FlashMind AI. <a href="https://github.com/bigm-o/Flash_mind.git">Visit our GitHub!</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        sg = sendgrid.SendGridAPIClient(sendgrid_api_key)
        from_email = Email(sender_email)
        to_email = To(recipient_email)
        subject = f"Your Flashcards from FlashMind AI have arrived!!!"
        content = Content("text/html", email_body_html)
        
        message = Mail(from_email, to_email, subject, content)
        
        response = sg.client.mail.send.post(request_body=message.get())

        if response.status_code == 202:
            st.success(f"Flashcards sent successfully to **{recipient_email}**!")
        else:
            st.error(f"Failed to send email. Status Code: {response.status_code}")
            st.error(f"Response Body: {response.body}")
            st.error(f"Response Headers: {response.headers}")

    except Exception as e:
        st.error(f"An error occurred while sending the email: {e}")
        st.warning("Please ensure your SendGrid API Key and Sender Email are correctly configured and verified.")


# --- Flashcard Generation Function ---
def generate_flashcards(source_text, max_flashcards=15):
    st.markdown(
        """
            <p style="font-size:1.5rem; color: white; display: flex; align-items: center; justify-content: center; text-align: center;">Flashcards</p>
            <small style="font-size:1rem; color: #67f88e; display: flex; align-items: center; justify-content: center; text-align: center;">(Click Flashcards to Flip)</small>
        """,
        unsafe_allow_html=True
    )
    # Prompt the AI to generate Q&A pairs from the given text
    qa_prompt = f"""
    Generate question and answer flashcards based on the following text.
    Format each flashcard strictly as "Q: Your question here A: Your answer here".
    Ensure the questions cover key concepts and facts from the text.
    Do not include any introductory or concluding remarks, just the Q&A pairs.
    Each Q&A pair should be on a new line.
    {f"Generate a maximum of {max_flashcards} flashcards." if max_flashcards else ""}

    Text:
    ---
    {source_text}
    ---
    Flashcards:
    """
    
    try:
        with st.spinner("Generating flashcards..."):
            flashcard_response = model.generate_content(qa_prompt).text.strip()

        raw_qa_pairs = [pair.split("A:") for pair in flashcard_response.split("Q:") if "A:" in pair]
        
        if not raw_qa_pairs:
            st.info("No Q&A pairs could be generated from this text. Please ensure the text contains sufficient information.")
            return

        # Prepare flashcards in a structured format for JSON
        flashcards_data = []
        for j, qa in enumerate(raw_qa_pairs):
            if len(qa) == 2:
                question = qa[0].strip()
                answer = qa[1].strip()
                flashcards_data.append({"question": question, "answer": answer})
            else:
                st.warning(f"Could not parse Q&A pair: {qa}. Ensure the AI's output is correctly formatted as 'Q: Question A: Answer'.")

        if not flashcards_data:
            st.info("No valid flashcards could be parsed from the AI's response.")
            return

        # Store generated flashcards in session state
        st.session_state.generated_flashcards_data = flashcards_data

        # The CSS for the flipping effect
        css = """
        <style>
            .flashcard-container{
                padding-bottom: 2rem;
                align-items: center;
            }

            .flashcard {
                background-color: transparent;
                width: 350px;
                height: 200px;
                perspective: 1000px;
                margin: 20px auto;
                
            }

            .flashcard .front{
                width: 85%;
                height: 100%;
                border: 1px dashed white;
                border-radius: 15px;
                position: absolute;
                backface-visibility: hidden;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.4rem;
                background: rgba(0, 0, 0, 0.1);
                color: white;
            }

            .flashcard .back {
                transform: rotateY(180deg);
                color: #67f88e;
                width: 85%;
                height: 100%;
                border: 1px dashed #67f88e;
                border-radius: 15px;
                position: absolute;
                backface-visibility: hidden;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.1rem;
                background: rgba(0, 0, 0, 0.1);
                color: #67f88e; /* Changed to match border color */
            }

            .flashcard {
                position: relative;
                transition: transform 0.6s;
                transform-style: preserve-3d;
                cursor: pointer;
            }

            .flashcard.flipped {
                transform: rotateY(180deg);
            }
            
            p {
                margin: 0;
                line-height: 1.4;
            }
        </style>
        """

        # The JavaScript for creating and flipping cards
        # inject flashcards_data directly as a JSON string
        js_script = f"""
        <script>
            const flashcardsData = {json.dumps(flashcards_data)}; // Inject Python list as JSON
            const container = document.getElementById('flashcards-container');

            flashcardsData.forEach(card => {{
                const cardContainer = document.createElement('div');
                cardContainer.className = 'flashcard-container';

                const flashcard = document.createElement('div');
                flashcard.className = 'flashcard';
                flashcard.onclick = function() {{
                    this.classList.toggle('flipped');
                }};

                const front = document.createElement('div');
                front.className = 'front';
                front.innerHTML = `<p>${{card.question}}</p>`;

                const back = document.createElement('div');
                back.className = 'back';
                back.innerHTML = `<p>${{card.answer}}</p>`;

                flashcard.appendChild(front);
                flashcard.appendChild(back);
                cardContainer.appendChild(flashcard);
                container.appendChild(cardContainer);
            }});
        </script>
        """

        # Combine HTML structure, CSS, and JavaScript
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Flashcards</title>
            {css}
        </head>
        <body>
            <div id="flashcards-container">
                </div>
            {js_script}
        </body>
        </html>
        """

        # Render the custom HTML component
        estimated_height = len(flashcards_data) * 200 
        components.html(html_content, height=estimated_height, scrolling=False)

        st.markdown(
            """
                <small style="font-size:1rem; color: #67f88e; display: flex; align-items: center; justify-content: center; text-align: center;">(Click Flashcards to Flip)</small>
            """,
            unsafe_allow_html=True
        )
        # Add the "Email Flashcards" button
        st.markdown("---") # Separator
        if st.button("📧 Email My Flashcards", key="email_flashcards_button"):
            st.session_state.show_email_form = not st.session_state.show_email_form # Toggle form visibility
            st.rerun()

    except Exception as e:
        st.error(f"An error occurred while generating flashcards: {e}")
        st.warning("Please try again. If the issue persists, the provided text might be too complex or short for flashcard generation, or there's an API issue.")


# --- Main Application Logic ---

# Display chat messages
if st.session_state.app_state == "chatting" or len(st.session_state.messages) > 0:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            for part in message["parts"]:
                if "text" in part:
                    st.markdown(part["text"])
                elif "image" in part:
                    st.image(part["image"], caption="Uploaded Image", use_container_width=True)

            # Add "Generate Flashcards" button
            if message["role"] == "assistant":
                # For the very first AI response after document/text input
                if i == 0 and not st.session_state.initial_flashcards_generated:
                    if st.button("Generate flashcards for the notes", key=f"generate_flashcards_initial_{i}"):
                        st.session_state.flashcards_for_message_idx = i # Store index to show flashcards later
                        st.session_state.initial_flashcards_generated = True # Mark as generated
                        st.rerun()
                # For all subsequent AI responses
                elif i > 0: # This means it's not the first AI message
                    if st.button(f"Generate Flashcards for this response", key=f"generate_flashcards_{i}"):
                        st.session_state.flashcards_for_message_idx = i
                        st.rerun()

    # Display flashcards if a button has been clicked
    if st.session_state.flashcards_for_message_idx != -1:
        target_message_idx = st.session_state.flashcards_for_message_idx
        
        # Logic for initial notes flashcards
        if target_message_idx == 0 and st.session_state.initial_flashcards_generated:
            # Generate flashcards from the full document text for the initial request
            if st.session_state.document_text:
                generate_flashcards(st.session_state.document_text, max_flashcards=15)
            else:
                st.error("Document text not available for initial flashcard generation.")
        # Logic for subsequent response-specific flashcards
        elif target_message_idx > 0 and target_message_idx < len(st.session_state.messages):
            target_message = st.session_state.messages[target_message_idx]
            if target_message["role"] == "assistant" and "text" in target_message["parts"][0]:
                generate_flashcards(target_message["parts"][0]["text"])
            else:
                st.warning("Selected message is not an AI response or contains no text for flashcard generation.")
        else:
            # Reset if message no longer exists or index is out of bounds
            st.session_state.flashcards_for_message_idx = -1
            st.warning("Could not find the associated AI response for flashcards.")

    # Email input form (appears when show_email_form is True)
    if st.session_state.show_email_form and st.session_state.generated_flashcards_data:
        st.markdown("---") # Separator
        st.subheader("Send Flashcards via Email")
        with st.form("email_flashcards_form"):
            user_email = st.text_input("Enter your email address:", key="email_input")
            submit_email = st.form_submit_button("Send Email")

            if submit_email:
                if user_email and "@" in user_email and "." in user_email: # Simple email validation
                    send_flashcards_email(user_email, st.session_state.generated_flashcards_data, st.session_state.subject_title)
                    st.session_state.show_email_form = False # Hide form after submission
                    st.rerun()
                else:
                    st.error("Please enter a valid email address.")
    elif st.session_state.show_email_form and not st.session_state.generated_flashcards_data:
        st.warning("No flashcards have been generated to send via email yet.")
        if st.button("Close Email Form", key="close_empty_email_form"):
            st.session_state.show_email_form = False
            st.rerun()


# Initial input options (Upload Document / Paste Text)
if st.session_state.app_state == "initial_input":

    col1, col2 = st.columns(2)

    with col1:

        with stylable_container(
            key="upload_doc_box_style",
            css_styles="""
                {
                    border: 2px dashed #007bff;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 150px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    background-color: rgba(255, 255, 255, 0.1);
                    position: relative; /* Needed for positioning the hidden button */
                }
                /* Style the paragraph text within the container (not the button label) */
                p {
                    font-weight: bold;
                }
            """
        ):
            
            if st.button("Upload Document", key="hidden_upload_trigger"):
                st.session_state.app_state = "uploading_document"
                st.rerun()
            st.markdown("<p></p>", unsafe_allow_html=True)


    with col2:
        with stylable_container(
            key="paste_text_box_style",
            css_styles="""
                {
                    border: 2px dashed #007bff;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 150px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    background-color: rgba(255, 255, 255, 0.1);
                    position: relative;
                }
                p {
                    font-weight: bold;
                }
            """
        ):
            if st.button("Paste Text", key="hidden_paste_trigger"):
                st.session_state.app_state = "pasting_text"
                st.rerun()
            st.markdown("<p></p>", unsafe_allow_html=True)


# Display file uploader if "Upload Document" was clicked
elif st.session_state.app_state == "uploading_document":
    st.subheader("Upload your document:")
    uploaded_document = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
        key="document_uploader_actual",
        label_visibility="visible"
    )
    if uploaded_document:
        st.session_state.app_state = "processing"
        st.session_state.uploaded_file_obj = uploaded_document
        st.rerun()
    else:
        st.info("Please upload a document to proceed.")
        if st.button("Go Back", key="go_back_from_upload"):
            st.session_state.app_state = "initial_input"
            st.rerun()


# Processing uploaded document
elif st.session_state.app_state == "processing" and st.session_state.uploaded_file_obj:
    uploaded_document = st.session_state.uploaded_file_obj
    file_extension = uploaded_document.name.split('.')[-1].lower()
    extracted_text = None

    with st.spinner(f"Processing {uploaded_document.name}..."):
        file_bytes = uploaded_document.getvalue()

        if file_extension == "pdf":
            extracted_text = extract_text_from_pdf(file_bytes)
        elif file_extension == "docx":
            extracted_text = extract_text_from_docx(file_bytes)
        elif file_extension == "txt":
            extracted_text = extract_text_from_txt(file_bytes)
        else:
            st.error("Unsupported file type.")
            st.session_state.app_state = "initial_input"
            st.rerun()

    if extracted_text:
        st.session_state.document_text = extracted_text
        st.success(f"Successfully processed '{uploaded_document.name}'.")

        subject_prompt = f"""
        Analyze the following document text and provide a concise, general subject title (e.g., "Photosynthesis", "World War II", "Python Programming Basics").
        Document:
        ---
        {extracted_text[:2000]}
        ---
        Subject Title:
        """
        try:
            subject_response = model.generate_content(subject_prompt).text.strip()
            st.session_state.subject_title = subject_response
        except Exception as e:
            st.warning(f"Could not infer subject title: {e}. Proceeding without a specific title.")
            st.session_state.subject_title = "your document"

        st.session_state.messages = []
        st.session_state.flashcards_for_message_idx = -1
        st.session_state.initial_flashcards_generated = False # Reset for new document
        initial_ai_response = f"Oh, I see you want to learn about **{st.session_state.subject_title}**. What would you like to know about this subject matter?"
        st.session_state.messages.append({"role": "assistant", "parts": [{"text": initial_ai_response}]})
        st.session_state.app_state = "chatting"
        st.rerun()

# Input for pasting text
elif st.session_state.app_state == "pasting_text":
    st.subheader("Paste your subject text below:")
    pasted_text = st.text_area(
        "",
        height=200,
        max_chars=100000,
        key="pasted_text_input"
    )
    col1, col2 = st.columns(2)

    with col1:
        go_back_txt = st.button("Go Back", key="go_back_from_paste")
        
    with col2:
        submit_pasted_text = st.button("Submit Text", key="submit_pasted_text")

    if submit_pasted_text and pasted_text:
        st.session_state.document_text = pasted_text
        st.success("Text successfully pasted and loaded.")

        subject_prompt = f"""
        Analyze the following text and provide a concise, general subject title (e.g., "Photosynthesis", "World War II", "Python Programming Basics").
        Text:
        ---
        {pasted_text[:2000]}
        ---
        Subject Title:
        """
        try:
            subject_response = model.generate_content(subject_prompt).text.strip()
            st.session_state.subject_title = subject_response
        except Exception as e:
            st.warning(f"Could not infer subject title: {e}. Proceeding without a specific title.")
            st.session_state.subject_title = "your text"

        st.session_state.messages = []
        st.session_state.flashcards_for_message_idx = -1
        st.session_state.initial_flashcards_generated = False # Reset for new text
        initial_ai_response = f"Oh, I see you want to learn about **{st.session_state.subject_title}**. What would you like to know about this subject matter?"
        st.session_state.messages.append({"role": "assistant", "parts": [{"text": initial_ai_response}]})
        st.session_state.app_state = "chatting"
        st.rerun()
    elif submit_pasted_text and not pasted_text:
        st.warning("Please paste some text before submitting.")
    
    if go_back_txt:
        st.session_state.app_state = "initial_input"
        st.rerun()

# Chat input for questions/commands (only visible in 'chatting' state)
elif st.session_state.app_state == "chatting":
    st.markdown("""
        <style>
            .stChatInputContainer {
                display: flex !important;
            }
        </style>
    """, unsafe_allow_html=True)

    prompt_input = st.chat_input(
        f"What would you like to know about {st.session_state.subject_title}?...",
        key="main_chat_input"
    )

    if prompt_input:
        user_text = prompt_input
        user_message_parts = [{"text": user_text}]

        st.session_state.first_chat_used = True
        st.session_state.flashcards_for_message_idx = -1 # Reset flashcards when user sends new message
        st.session_state.show_email_form = False # Hide email form when user sends new message

        st.session_state.messages.append({"role": "user", "parts": user_message_parts})
        with st.chat_message("user"):
            st.markdown(user_text)

        gemini_messages_for_api = []

        gemini_messages_for_api.append({"role": "user", "parts": [{"text": system_instruction_prompt}]})
        gemini_messages_for_api.append({"role": "model", "parts": [{"text": "Hello! I'm FlashMind AI. How can I help you learn from your document?"}]})

        gemini_messages_for_api.append({"role": "user", "parts": [{"text": f"Here is the document for analysis:\n\n---\n{st.session_state.document_text}\n---"}]})
        gemini_messages_for_api.append({"role": "model", "parts": [{"text": f"I have processed the document about **{st.session_state.subject_title}**. What would you like to do?"}]})

        for msg in st.session_state.messages:
            is_initial_system_prompt = (msg["role"] == "user" and msg["parts"][0]["text"] == system_instruction_prompt)
            is_initial_ai_greeting = (msg["role"] == "assistant" and msg["parts"][0]["text"].startswith("Hello! I'm FlashMind AI."))
            is_document_context = (msg["role"] == "user" and msg["parts"][0]["text"].startswith("Here is the document for analysis:"))
            is_document_processed_ai_response = (msg["role"] == "model" and msg["parts"][0]["text"].startswith("I have processed the document about"))

            if not (is_initial_system_prompt or is_initial_ai_greeting or is_document_context or is_document_processed_ai_response):
                role_for_gemini = "user" if msg["role"] == "user" else "model"
                parts_for_gemini = []
                for part in msg["parts"]:
                    if "text" in part:
                        parts_for_gemini.append({"text": str(part["text"])})
                    elif "image" in part:
                        parts_for_gemini.append(part["image"])
                gemini_messages_for_api.append({"role": role_for_gemini, "parts": parts_for_gemini})

        try:
            stream = model.generate_content(
                gemini_messages_for_api,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=2048
                )
            )

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response_content = ""
                for chunk in stream:
                    if chunk.text:
                        full_response_content += chunk.text
                        message_placeholder.markdown(full_response_content + "▌")
                message_placeholder.markdown(full_response_content)

            st.session_state.messages.append({"role": "assistant", "parts": [{"text": full_response_content}]})
            st.rerun()

        except Exception as e:
            st.error(f"An error occurred while generating response: {e}")
            st.warning("Please try again. If the issue persists, verify your API key or the model's availability.")
