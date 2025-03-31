# Install required packages:
# pip install langchain langchain-openai

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class OpenAIConnector:
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the OpenAI connector with an API key and model.
        
        Args:
            api_key (str): Your OpenAI API key
            model (str): The OpenAI model to use (default: gpt-3.5-turbo)
        """
        self.llm = ChatOpenAI(
            api_key="", # Insert your OpenAI API key for it to work!
            model=model,
            temperature=0.7
        )

    def send_prompt(self, system: str, prompt: str) -> str:
        """
        Send a prompt to OpenAI and get a response.
        
        Args:
            prompt (str): The prompt to send
        
        Returns:
            str: The response from OpenAI
        """

        try:
            # Create a simple prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "{system}"),
                ("human", "{prompt}")
            ])
            
            # Chain the prompt template with the LLM
            chain = prompt_template | self.llm
            
            # Invoke the chain with the prompt
            response = chain.invoke({"system": system, "prompt": prompt})
            return response.content
        except Exception as e:
            return f"Error: {str(e)}"

