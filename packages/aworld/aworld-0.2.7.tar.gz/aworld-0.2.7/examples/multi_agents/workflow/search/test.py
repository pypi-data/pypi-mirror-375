# coding: utf-8
# Copyright (c) 2025 inclusionAI.
import os
from typing import AsyncGenerator

from aworld.agents.llm_agent import Agent
from aworld.config.conf import AgentConfig
from aworld.core.agent.swarm import Swarm
from aworld.core.common import ActionModel, TaskItem, Observation
from aworld.core.event.base import Message, Constants, TopicType, AgentMessage
from aworld.output.base import StepOutput
from aworld.runner import Runners
from aworld.runners import HandlerFactory
from aworld.runners.handler.agent import AgentHandler
from examples.common.tools.common import Tools

# os.environ["LLM_MODEL_NAME"] = "YOUR_LLM_MODEL_NAME"
# os.environ["LLM_BASE_URL"] = "YOUR_LLM_BASE_URL"
# os.environ["LLM_API_KEY"] = "YOUR_LLM_API_KEY"

search_sys_prompt = "You are a helpful search agent."
search_prompt = """
    Please act as a search agent, constructing appropriate keywords and searach terms, using search toolkit to collect relevant information, including urls, webpage snapshots, etc.

    Here are the question: {task}

    pleas only use one action complete this task, at least results 6 pages.
    """

summary_sys_prompt = "You are a helpful general summary agent."

summary_prompt = """
Summarize the following text in one clear and concise paragraph, capturing the key ideas without missing critical points. 
Ensure the summary is easy to understand and avoids excessive detail.

Here are the content: 
{task}
"""


@HandlerFactory.register(name="replan")
class PlanHandler(AgentHandler):
    def is_valid_message(self, message: Message):
        if message.category != "replan":
            return False
        return True

    async def handle(self, message: Message) -> AsyncGenerator[Message, None]:
        if not self.is_valid_message(message):
            return

        content = message.payload
        # data is List[ActionModel]
        for action in content:
            if not isinstance(action, ActionModel):
                # error message, p2p
                yield Message(
                    category=Constants.OUTPUT,
                    payload=StepOutput.build_failed_output(name=f"{message.caller or self.name()}",
                                                           step_num=0,
                                                           data="action not a ActionModel.",
                                                           task_id=self.task_id),
                    sender=self.name(),
                    session_id=message.session_id,
                    headers=message.headers
                )
                msg = Message(
                    category=Constants.TASK,
                    payload=TaskItem(msg="action not a ActionModel.", data=content, stop=True),
                    sender=self.name(),
                    session_id=message.session_id,
                    topic=TopicType.ERROR,
                    headers=message.headers
                )
                yield msg
                return


        # 取第一个action
        action = content[0]
        # 基于action来决定是否需要重新plan
        need_replan = True
        swarm = message.context.swarm
        # 找到plan agent
        agent = swarm.find_agents_by_prefix("plan")
        if agent:
            agent = agent[0]

        # 做replan的输入
        con = None
        if need_replan:
            yield AgentMessage(session_id=message.session_id,
                               payload=con,
                               sender=self.name(),
                               receiver=agent.id(),
                               headers={'context': message.context})
        else:
            idx = next((i for i, x in enumerate(swarm.ordered_agents) if x == agent), -1)
            # 特殊处理！idx一定不是最后一个，还有reporting agent
            yield AgentMessage(session_id=message.session_id,
                               payload=con,
                               sender=self.name(),
                               receiver=self.swarm.ordered_agents[idx + 1].id(),
                               headers={'context': message.context})


# search and summary
if __name__ == "__main__":
    # need to set GOOGLE_API_KEY and GOOGLE_ENGINE_ID to use Google search.
    # os.environ['GOOGLE_API_KEY'] = ""
    # os.environ['GOOGLE_ENGINE_ID'] = ""

    agent_config = AgentConfig(
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_model_name=os.getenv("LLM_MODEL_NAME"),
        llm_base_url=os.getenv("LLM_BASE_URL"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_temperature=os.getenv("LLM_TEMPERATURE", 0.0)
    )

    a = Agent(
        conf=agent_config,
        name="rewrite_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
    )

    b = Agent(
        conf=agent_config,
        name="search_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        tool_names=[Tools.SEARCH_API.value]
    )

    c = Agent(
        conf=agent_config,
        name="plan_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        agent_names=[b.id()]
    )

    d = Agent(
        conf=agent_config,
        name="replan_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        event_handler_name="replan"
    )

    e = Agent(
        conf=agent_config,
        name="report_agent",
        system_prompt=summary_sys_prompt,
        agent_prompt=summary_prompt
    )
    # default is workflow swarm
    swarm = Swarm(a, b, c, d, e)

    prefix = ""
    # can special search google, wiki, duck go, or baidu. such as:
    # prefix = "search wiki: "
    res = Runners.sync_run(
        input=prefix + """What is an agent.""",
        swarm=swarm
    )
    print(res.answer)
