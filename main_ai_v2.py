import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_community.chat_message_histories import SQLChatMessageHistory


os.environ["GROQ_API_KEY"] = "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"

class AssistantAI:
    def __init__(self, instructions, llm, db_path, tools) -> None:
        self.instructions = instructions
        self.llm = llm
        self.db_path = db_path
        self.tools = tools
        self.tool_names = [tool.name for tool in self.tools]
        pass

    def call_chat(self, input, user_id):

        # adicionar no chat promptTemplate tools
        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.instructions,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        runnable = prompt | self.llm
        # PROBLEMA NAS TOOLS E NO ERRO TypeError: Object of type HumanMessage is not JSON serializable

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

        with_message_history = RunnableWithMessageHistory(
            agent_executor,
            lambda: SQLChatMessageHistory(session_id=user_id, connection=self.db_path),
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        return with_message_history.invoke(
            {
                "input": input,
                "tool_names": self.tool_names,
                "tools": self.tools
            },
            config={"configurable": {"session_id": user_id}},
        )
