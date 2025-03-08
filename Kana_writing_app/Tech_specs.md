
## Detailed Technical Specifications for LLM Integration

### Initialization (Starting the App)
When the app opens, it performs the following steps:
1. Sends a `GET` request to `localhost:5000/api/groups/:id/raw`.
2. Receives a JSON response containing a list of Japanese vocabulary words paired with their English translations.
3. Stores these vocabulary pairs in the app’s memory for future sentence generation.

---

### Application States (Detailed Flow)
The application transitions clearly through three distinct user-interaction states:

#### 1. Setup State
- Initially, the user sees only a single interactive button labeled **"Generate Sentence"**.
- Clicking this button triggers the app to communicate with the Sentence Generator LLM.
- The Sentence Generator LLM uses the previously stored vocabulary to create an appropriate beginner-level English sentence.
- Once the sentence is generated, the app smoothly transitions into the **Practice State**.

#### 2. Practice State
- The generated English sentence is clearly displayed to the user.
- An image upload field appears beneath the English sentence, prompting users to submit a photo of their handwritten Japanese translation.
- A button labeled **"Submit for Review"** is available.
- After the user uploads their image and clicks the "Submit for Review" button, the image is sent to the Grading System for evaluation.
- Upon submission, the app advances into the **Review State**.

#### 3. Review State
- The generated English sentence remains clearly displayed on the screen.
- The image upload interface is removed to focus the user on their evaluation results.
- Detailed feedback from the Grading System is provided, including:
  - **Transcription**: The exact Japanese text recognized from the uploaded image.
  - **Translation**: A literal English translation of the transcribed Japanese text.
  - **Grade**: An accuracy-based letter grade (S being the highest, followed by A, B, etc.).
  - **Feedback**: Clear, specific recommendations for improving accuracy and translation quality.
- A "Next Question" button appears, prompting users to generate a new sentence and restart practice.

---

### Sentence Generator LLM Prompt Instructions
- Generate a clear, beginner-friendly English sentence utilizing the provided vocabulary word: `{{word}}`.
- Ensure grammar simplicity suitable for learners at the JLPT N5 proficiency level.
- Utilize descriptive, beginner-level vocabulary specifically:
  - Simple objects (examples: book, car, ramen, sushi).
  - Common actions (examples: drink, eat, meet).
  - Frequently used time-related expressions (examples: tomorrow, today, yesterday).

---

### Grading System LLM Workflow
When evaluating an uploaded image, follow these detailed steps:
1. **Transcription Step**: Utilize MangaOCR technology to accurately recognize and transcribe Japanese text from the submitted image.
2. **Translation Step**: Pass this transcription through an LLM tasked with creating a direct and literal English translation.
3. **Scoring Step**: Employ a separate LLM to evaluate translation accuracy against the original generated English sentence, assigning a letter-grade (S, A, B, etc.) based on performance.
4. **Feedback Generation Step**: Provide detailed, actionable feedback highlighting areas of accuracy or suggesting specific improvements.
5. Deliver the comprehensive evaluation—including transcription, translation, assigned grade, and feedback—to the frontend application to display clearly for user review.
