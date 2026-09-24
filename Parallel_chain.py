import json

from langchain_groq import ChatGroq
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

from pydantic import BaseModel, Field


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Models
# --------------------------------------------------

model1 = ChatGroq(
    model="openai/gpt-oss-20b"
)

model2 = ChatGroq(
    model="openai/gpt-oss-20b"
)


# --------------------------------------------------
# Pydantic Models for Quiz
# --------------------------------------------------

class Question(BaseModel):

    question: str = Field(
        description="The quiz question"
    )

    options: list[str] = Field(
        description="Exactly 4 answer options"
    )

    correct_answer: int = Field(
        description="Index of the correct option: 0, 1, 2 or 3"
    )


class Quiz(BaseModel):

    questions: list[Question] = Field(
        description="Exactly 5 multiple-choice questions"
    )


# --------------------------------------------------
# Notes Prompt
# --------------------------------------------------

prompt1 = PromptTemplate(

    template="""
Generate short, clear and exam-friendly notes
from the following study material.

Use the following structure:

# Topic

Give a short introduction to the topic.

## Key Points

Explain the important concepts using bullet points.

## Advantages and Disadvantages

Create a Markdown table with exactly these columns:

| Advantages | Disadvantages |
|------------|---------------|

Put the relevant advantages in the left column
and disadvantages in the right column.

## Important Concepts

Explain important concepts briefly.

## Applications

List important applications if they are present
in the study material.

Rules:

- Keep the notes simple and easy to revise.
- Use only information from the provided study material.
- Do not add unrelated information.
- Use Markdown formatting.
- The Advantages and Disadvantages section MUST contain a table.

Study Material:

{text}
""",

    input_variables=["text"]
)


# --------------------------------------------------
# Question Answer Prompt
# --------------------------------------------------

prompt2 = PromptTemplate(

    template="""
Generate exactly 5 short question-and-answer pairs
from the following study material.

Use this exact format:

Q1. Question

Answer:
Answer text here.

Q2. Question

Answer:
Answer text here.

Q3. Question

Answer:
Answer text here.

Q4. Question

Answer:
Answer text here.

Q5. Question

Answer:
Answer text here.

Rules:

- The question and answer MUST be on separate lines.
- Leave one blank line between each question and answer.
- Keep answers short and useful for exam preparation.
- Use only information from the provided study material.
- Do not add extra questions.

Study Material:

{text}
""",

    input_variables=["text"]
)


# --------------------------------------------------
# Quiz Prompt
# --------------------------------------------------

prompt3 = PromptTemplate(

    template="""
Create exactly 5 multiple-choice questions
from the following study material.

Return ONLY valid JSON.

Use exactly this format:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option 1",
                "Option 2",
                "Option 3",
                "Option 4"
            ],
            "correct_answer": 0
        }}
    ]
}}

Rules:

- Create exactly 5 questions.
- Each question must have exactly 4 options.
- Only one option must be correct.
- correct_answer must be 0, 1, 2, or 3.
- 0 means the first option.
- 1 means the second option.
- 2 means the third option.
- 3 means the fourth option.
- Questions must be based only on the provided study material.
- Do not add markdown.
- Do not add ```json.
- Return only JSON.

Study Material:

{text}
""",

    input_variables=["text"]
)


# --------------------------------------------------
# Output Parser
# --------------------------------------------------

parser = StrOutputParser()


# --------------------------------------------------
# Quiz JSON Parser
# --------------------------------------------------

def parse_quiz(response):

    content = response.content.strip()

    # Remove markdown code fences if the model adds them
    if content.startswith("```"):

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()

    data = json.loads(content)

    return Quiz(**data)


# --------------------------------------------------
# Parallel Chain
# --------------------------------------------------

parallel_chain = RunnableParallel({

    "notes":
        prompt1
        | model1
        | parser,

    "question_answers":
        prompt2
        | model2
        | parser,

    "quiz":
        prompt3
        | model2
        | parse_quiz
})