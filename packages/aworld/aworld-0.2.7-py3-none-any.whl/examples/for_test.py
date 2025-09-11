import json
from collections import OrderedDict

from aworld.core.exceptions import AWorldRuntimeException

from aworld.agents.loop_llm_agent import LoopableAgent

from aworld.core.agent.base import BaseAgent
from aworld.core.agent.swarm import TeamSwarm, GraphBuildType
from aworld.core.common import Observation, ActionModel, TaskItem
from aworld.core.context.base import Context
from aworld.core.event.base import Message, Constants, TopicType
from aworld.core.task import TaskResponse, Task
from aworld.output.outputs import DefaultOutputs
from aworld.utils.common import sync_exec
from aworld.utils.run_util import exec_tool
from examples.multi_agents.workflow.search.run import *
from examples.common.tools.common import Tools

agent_config = AgentConfig(
    llm_provider="openai",
    llm_model_name="gpt-4o",
    llm_temperature=1,
    llm_api_key="dummy",
    llm_base_url="http://localhost:34567",
)


def search_workflow_swarm():
    search = Agent(
        conf=agent_config,
        name="search_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        tool_names=[Tools.SEARCH_API.value]
    )

    summary = Agent(
        conf=agent_config,
        name="summary_agent",
        system_prompt=summary_sys_prompt,
        agent_prompt=summary_prompt
    )

    swarm = Swarm(search, summary, max_steps=1)

    prefix = ""
    # can special search google, wiki, duck go, or baidu. such as:
    # prefix = "search wiki: "
    res = Runners.sync_run(
        input=prefix + """What is an agent.""",
        swarm=swarm
    )
    print(res.answer)

def search_workflow_swarm_parallel():
    search1 = Agent(
        conf=agent_config,
        name="search_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        tool_names=[Tools.SEARCH_API.value]
    )

    search2 = Agent(
        conf=agent_config,
        name="search_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        tool_names=[Tools.SEARCH_API.value]
    )

    summary = Agent(
        conf=agent_config,
        name="summary_agent",
        system_prompt=summary_sys_prompt,
        agent_prompt=summary_prompt
    )

    swarm = Swarm((search1, summary), (search2, summary), max_steps=1)

    prefix = ""
    # can special search google, wiki, duck go, or baidu. such as:
    # prefix = "search wiki: "
    res = Runners.sync_run(
        input=prefix + """What is an agent.""",
        swarm=swarm
    )
    print(res.answer)

def search_hybrid_swarm():
    search = Agent(
        conf=agent_config,
        name="search_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        tool_names=[Tools.SEARCH_API.value]
    )

    summary = Agent(
        conf=agent_config,
        name="summary_agent",
        system_prompt=summary_sys_prompt,
        agent_prompt=summary_prompt
    )
    s1 = Swarm(search)
    s2 = Swarm(summary)
    # default is workflow swarm
    swarm = Swarm(s1, s2, summary, max_steps=1)

    task1 = Task(input="search baidu: what is an agent", agent=search)
    task2 = Task(input="search baidu: what is an agent", swarm=swarm)

    res = Runners.sync_run_task([task1, task2])
    print(res.keys(), res)

    # prefix = ""
    # # can special search google, wiki, duck go, or baidu. such as:
    # # prefix = "search wiki: "
    # res = Runners.sync_run(
    #     input=prefix + """What is an agent.""",
    #     swarm=swarm
    # )
    # print(res.answer)


def swarm_define(keep_build_type: bool = True):
    agent1 = Agent(name='agent1', conf=agent_config)
    agent2 = Agent(name='agent2', conf=agent_config)
    agent3 = Agent(name='agent3', conf=agent_config)
    agent4 = Agent(name='agent4', conf=agent_config)
    agent5 = Agent(name='agent5', conf=agent_config)
    agent6 = Agent(name='agent6', conf=agent_config)
    agent7 = Agent(name='agent7', conf=agent_config)
    agent8 = Agent(name='agent8', conf=agent_config)

    # hybrid swarm, 层级
    team_swarm1 = TeamSwarm(agent1, agent2, agent3)
    team_swarm2 = TeamSwarm(agent4, agent5, root_agent=agent6)
    swarm = Swarm(agent7, team_swarm1, team_swarm2, agent8)
    swarm.reset("")
    print(swarm.ordered_agents)

    # Workflow swarm
    swarm = Swarm((agent1, agent3), (agent2, agent3))
    swarm.reset("")
    print([agent.id() for agent in swarm.communicate_agent])

    # Handoff swarm
    swarm = Swarm((agent1, agent3), (agent1, agent2), (agent2, agent3))
    swarm.reset("")
    print(swarm)

    # Runners.run(input="")

    # swarm = Swarm(agent1, [(agent2, (agent4, [agent7, agent8])), (agent3, agent5)], agent6)
    # swarm.reset("")
    # print(swarm.ordered_agents)
    #
    # swarm = Swarm((agent1, agent2), (agent1, agent3), (agent1, agent4), (agent1, agent5),
    #               build_type=GraphBuildType.HANDOFF, keep_build_type=keep_build_type)
    # swarm.reset("")
    # print(swarm.build_type)



def only_tool():
    context = Context()
    outputs = DefaultOutputs()
    res: TaskResponse = sync_exec(exec_tool, "search_api", "baidu", {"query": "test"}, "", context, True, outputs)
    print(json.loads(res.answer))


def only_one_step():
    search = Agent(
        conf=agent_config,
        name="search_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        tool_names=[Tools.SEARCH_API.value],
        wait_tool_result=True
    )
    context = Context()
    context._task = Task()

    content = """baidu: What is an agent."""
    content = Observation(content=content)
    message = Message(payload=content, headers={"context": context})

    rule_agent = BaseAgent()

    action = [{"role": "user", "content": ""}, {"role": "assistant", "content": "{'tool': ''}"}]

    message = Message(payload=action, headers={"context": context})
    res = rule_agent.run(action)

    if isinstance(res.payload, str):
        print("finished: ", res.payload)
    else:
        info = res.payload[0].policy_info
        print("contain tool result: ", info)
        content = info


def topology():
    agent1 = Agent(name='agent1', conf=agent_config)
    agent2 = Agent(name='agent2', conf=agent_config)
    agent3 = Agent(name='agent3', conf=agent_config)
    agent4 = Agent(name='agent4', conf=agent_config)
    agent5 = Agent(name='agent5', conf=agent_config)
    agent6 = Agent(name='agent6', conf=agent_config)
    agent7 = Agent(name='agent7', conf=agent_config)
    agent8 = Agent(name='agent8', conf=agent_config)
    topo = [(agent1, agent2), (agent2, agent3), (agent1, agent3)]

    topo = [(agent1, agent2), (agent2, agent3), (agent4, agent3)]

    swarm = Swarm(topology=topo, root_agent=agent1, build_type=GraphBuildType.HANDOFF)
    swarm.reset()

    message = Message(session_id="abc", payload=ActionModel(agent_name=agent1.id(), policy_info="adsfasdfasdfasdffasd"))
    action = message.payload
    session_id = message.session_id
    agent_name = action.agent_name
    agent = swarm.agents.get(agent_name)
    if not agent:
        next_msg = Message(
            category=Constants.TASK,
            payload=TaskItem(
                msg=f"Can not find {action.agent_name} agent in ordered_agents: {swarm.ordered_agents}.",
                data=action,
                stop=True),
            sender="xxx",
            session_id=session_id,
            topic=TopicType.ERROR,
            headers=message.headers
        )
        print("error, ", next_msg)
        return

    receiver = None
    # loop agent type
    if isinstance(agent, LoopableAgent):
        agent.cur_run_times += 1
        if not agent.finished:
            receiver = agent.goto

    if receiver:
        next_msg = Message(
            category=Constants.AGENT,
            payload=Observation(content=action.policy_info),
            sender=agent.id(),
            session_id=session_id,
            receiver=receiver,
            headers=message.headers
        )
    else:
        agent_graph = swarm.agent_graph
        # next
        successor = agent_graph.successor.get(agent_name)
        if not successor:
            next_msg = Message(
                category=Constants.TASK,
                payload=action.policy_info,
                sender=agent.id(),
                session_id=session_id,
                topic=TopicType.FINISHED,
                headers=message.headers
            )
            print("finished, ", next_msg)
            return

        for k, _ in successor.items():
            predecessor = agent_graph.predecessor.get(k)
            if not predecessor:
                raise AWorldRuntimeException(f"{k} has no predecessor {agent_name}, may changed during iteration.")

            pre_finished = True
            for pre_k, _ in predecessor.items():
                if pre_k == agent_name:
                    continue
                # check all predecessor agent finished
                pre_finished = False
                print(f"{pre_k} not finished, will wait it.")

            if pre_finished:
                next_msg = Message(
                    category=Constants.AGENT,
                    payload=Observation(content=action.policy_info),
                    sender=agent.id(),
                    session_id=session_id,
                    receiver=k,
                    headers=message.headers
                )

    print(next_msg)

def for_test():
    agent1 = Agent(name='agent1', agent_id="aaa", conf=agent_config)
    agent2 = Agent(name='agent1', agent_id="aaa", conf=agent_config)
    swarm1 = Swarm(agent1, agent2)
    swarm2 = Swarm(agent1, agent2)

    print(swarm1.topology == swarm2.topology)

    print(type(swarm1) == type(swarm2))

    xx = [swarm1, swarm2]

    print(swarm1 in xx)
    #
    # if agent1 == agent2:
    #     print("xxxxxxxx")

    # print(all([True, True, True]))


if __name__ == '__main__':
    # only_tool()
    # search_workflow_swarm_parallel()
    # swarm_define()
    # hybrid_swarm()

    search_hybrid_swarm()

    # topology()

    # from dataclasses import dataclass
    # from dataclasses_json import dataclass_json
    #
    # @dataclass_json
    # @dataclass
    # class Book:
    #     title: str
    #     author: str
    #     xx: dict
    #
    #
    # book = Book("西游记", "吴承恩", {"ad": "1592"})
    #
    # book_json = book.to_json()
    # print(book_json)
    # # {"title": "西游记", "author": "吴承恩", "year": 1592}
    #
    # book_obj = Book.from_json(book_json)
    # print(book_obj)
    # # Book(title='西游记', author='吴承恩', year=1592)
    #
    #
    # Runners.run_task(Task())
