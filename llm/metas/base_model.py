from abc import ABCMeta, abstractmethod
from langchain import OpenAI, SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
import os
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import OpenAI, LLMChain
from langchain.utilities import GoogleSearchAPIWrapper


class BaseLangchainModel(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def get_result(self, question):
        pass


class SQLChainModel(BaseLangchainModel):
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_PORT = os.getenv('DB_PORT')

    def __init__(self):
        db = SQLDatabase.from_uri(
            f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}',
        )

        # setup llm
        llm = ChatOpenAI(temperature=0, model_name="gpt-4")

        # Create db chain
        self.prompt_query = """
                        Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.

                        Make sure to include the unit of measurement from the 'UNIT_NAME' column and 'DATE' column in your final answer with korean.
                        Ignore 'UNIT_NAME' if it is None.
                        Find the one-word keyword in the question.

                        Follow these steps:

                        1. Use the identified keyword to formulate a PostgreSQL query. Your query should find rows where the keyword appears in the 'STAT_NAME' column using the LIKE operator with % as wildcards. If specific dates are provided in the question, include them in your query using the = operator to obtain values for each individual date. Limit the row count to 100.
                        2. In the SQL results, identify the oldest date as the "Comparison Date" and the latest date as the "Reference Date". Calculate the difference by subtracting the value at the Comparison Date from that at the Reference Date. If the result is positive, it means the value has increased from the Comparison Date to the Reference Date. If the result is negative, it indicates a decrease.
                        3. Summarize the answer based on the SQL results with Korean. 

                        Here is the format to follow:

                        Question: Question here
                        SQLQuery: SQL Query to run
                        SQLResult: Result of the SQLQuery
                        Answer: Final answer here

                        {question}
                """
        # Setup the database chain
        self.db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True, use_query_checker=True)

    def get_result(self, question):
        query = self.prompt_query.format(question=question)
        result = self.db_chain.run(query)
        return result


class ChatMemoryModel(BaseLangchainModel):
    redis_broker_url = os.getenv('CELERY_BROKER_URL')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    google_cse_id = os.getenv('GOOGLE_CSE_ID')

    def __init__(self, session_id):
        search = GoogleSearchAPIWrapper(google_api_key=self.google_api_key, google_cse_id=self.google_cse_id)
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to answer questions about current events",
            )
        ]

        prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
        suffix = """Begin!"

        {chat_history}
        Question: {input}
        {agent_scratchpad}
        """

        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        message_history = RedisChatMessageHistory(
            url=self.redis_broker_url, ttl=600, session_id=f"{session_id}"
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history", chat_memory=message_history
        )

        llm_chain = LLMChain(llm=OpenAI(temperature=0, model_name='gpt-4'), prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, memory=memory
        )

    def get_result(self, question):
        result = self.agent_chain.run(input=question)
        return result
