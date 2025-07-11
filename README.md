# 🧠 FlashMind AI

Turn your notes into knowledge: Flashcards & Q&A powered by AI.

FlashMind AI is a Streamlit application that leverages Google's Gemini-1.5-Flash model to help users convert their study notes and documents into interactive flashcards and engage in a Q&A session. It supports various document formats (PDF, DOCX, TXT) and allows users to paste text directly. The application also provides an option to email generated flashcards for convenient offline access.

---


## ✨ Features

* **Document Upload**: Upload PDF, DOCX, or TXT files containing your notes.
* **Text Input**: Paste text directly into the application.
* **AI-Powered Flashcard Generation**: Automatically generates interactive flashcards (Question & Answer pairs) from your uploaded or pasted content.
* **Interactive Flashcards**: Click to flip flashcards and reveal answers, enhancing the learning experience.
* **Intelligent Q&A Chatbot**: Engage in a conversational chat with the AI to ask questions and gain deeper insights into your study material.
* **Dynamic Subject Titling**: The AI automatically infers and displays a subject title for your uploaded/pasted content.
* **Email Flashcards**: Send generated flashcards to any email address for easy access and review.
* **Responsive Design**: Adapts to different screen sizes for optimal viewing on both desktop and mobile.
* **Customizable Theme**: Features a visually appealing interface with dynamic background images and custom CSS.

---

### 👨‍💻 App UI
#### 🔃 Multiple background image functionality
The background image dynamically changes each time the user reloads the app, to give an interactive feel to it  

### 📱 Extra responsiveness to hide unnecesary elements when viewed on mobile. (hide-on-mobile) 

### 📱 UI for Email sending Utility with SendGrid
---
<img width="1200" alt="Screenshot 2025-07-11 130431" src="https://github.com/user-attachments/assets/87510da4-99a0-4ba8-ad7e-3d2c9a7b0de9" />

<img width="970" height="716" alt="Screenshot 2025-07-11 134415" src="https://github.com/user-attachments/assets/ddd3935b-b849-429d-9bbd-a764f30918ad" />

---



In the image folder, the background images (i.e., `image(image_number).jpg`) are fed into the `app.py` with base64 to encode the image. Randint is used to cycle throught the images, so that it can display a different image each time the app is run:

```python
image_number = random.randint(1, 6)
BACKGROUND_IMAGE_PATH = f"images/image{image_number}.jpg"
encoded_background_image = get_base64_image(BACKGROUND_IMAGE_PATH)
```
---

### Why Flashmind AI? 🤔

* **Boost Productivity:** ⚡🚀 Get instant Q&A with an interrcative feel, to make the user have the flashcard experience.

* **Learn & Grow:** 🌱🎓 The AI can be prompted to generate etailed explanations help you understand underlying concepts within your subject text.

* **Reliable Assistance:** ✅🛡️ Powered by a robust AI model and guided by expert prompt engineering techniques (Chain of Thought, Guardrails, Few-Shot learning).

* **Fast Email utility feature:** 📦🌐 Users can mail their flashcards to themselves for later use.

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.8+**
* **pip** (Python package installer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/bigm-o/Flash_mind.git](https://github.com/bigm-o/Flash_mind.git)
    cd Flash_mind
    ```

2.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### API Keys Configuration

FlashMind AI uses Google Gemini API for AI functionalities and SendGrid for email services. You need to configure your API keys securely.

1.  **Create a `.streamlit` directory** in the root of your project if it doesn't already exist.
    ```bash
    mkdir .streamlit
    ```

2.  **Create a `secrets.toml` file** inside the `.streamlit` directory.

3.  **Add your API keys to `secrets.toml`:**

    ```toml
    # .streamlit/secrets.toml

    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
    SENDGRID_API_KEY = "YOUR_SENDGRID_API_KEY_HERE"
    SENDER_EMAIL = "your_verified_sender_email@example.com"
    ```
    * Replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual Google Gemini API Key.
    * Replace `"YOUR_SENDGRID_API_KEY_HERE"` with your actual SendGrid API Key.
    * Replace `"your_verified_sender_email@example.com"` with an email address you have verified with SendGrid.

    **Note:** You can obtain a Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey). For SendGrid, register at [SendGrid](https://sendgrid.com/) and follow their instructions to get an API Key and verify a sender identity.

---

## 💻 Usage

1.  **Run the Streamlit application:**

    ```bash
    streamlit run src/app.py
    ```

    This command will open the application in your default web browser.

2.  **Choose your input method:**
    * **Upload Document**: Click "Upload Document" and select a PDF, DOCX, or TXT file from your computer.
    * **Paste Text**: Click "Paste Text" and paste your notes directly into the provided text area.

3.  **Interact with the AI:**
    * After uploading or pasting, the AI will process your content and provide an initial response.
    * **Generate Flashcards**: Click the "Generate flashcards for the notes" button (for the initial content) or "Generate Flashcards for this response" (for subsequent AI responses) to create interactive flashcards.
    * **Engage in Q&A**: Use the chat input box at the bottom to ask the AI questions about your notes or the generated content.
    * **Email Flashcards**: After generating flashcards, a "📧 Email Flashcards" button will appear. Click it, enter the recipient's email address, and send your flashcards.

---

## 📂 Project Structure

```
Flash Mind Ai/
├── .streamlit/
│   └── config.toml  
│   └── secrets.toml         # Securely stores your Gemini API Key
├── images/
│   ├── image1              
│   ├── image2
│   ├── image3           
│   ├── image4
│   ├── image5
│   ├── image6
├── src/
│   ├── app.py               # The main Streamlit application
│   ├── prompt.txt           # Contains the AI's core instructions/prompt
├── requirements.txt         # Lists Python dependencies
└── README.md                # This file
```

## 🛠️ Technologies Used

* **Python**
* **Streamlit**: For creating the interactive web application.
* **Google Gemini API (gemini-1.5-flash)**: For AI-powered text processing, Q&A, and flashcard generation.
* **python-docx**: For extracting text from `.docx` files.
* **PyPDF2**: For extracting text from `.pdf` files.
* **SendGrid**: For sending emails with generated flashcards.
* **HTML/CSS/JavaScript**: For custom UI components and interactive elements (like flip cards).

---

Made by BigMO (Mo-Dev)
