from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()

# LLM
model1 = ChatGroq(
    model="openai/gpt-oss-20b"
)

# LLM
model2 = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# Prompt for notes
prompt1 = PromptTemplate(
    template='Generate short and simple notes from the following text \n {text}',
    input_variables=['text']
)

# Prompt for quiz
prompt2 = PromptTemplate(
    template = 'Generate 5 short question answers from the following text \n {text}',
    input_variables=['text']
)

# Prompt for final document
prompt3 = PromptTemplate(
    template = 'Merge the provided notes and quiz into a single document \n notes -> {notes} and quiz -> {quiz}',
    input_variables=['notes', 'quiz']
)

parser = StrOutputParser()

# Run notes and quiz in parallel
parallel_chain = RunnableParallel({
    'notes' : prompt1 | model1 | parser,
    'quiz' :prompt2 | model2 | parser
})

# Merge the results
merge_chain = prompt3 | model1 | parser

# Complete chain
study_material_chain = parallel_chain

final_chain = parallel_chain | merge_chain

