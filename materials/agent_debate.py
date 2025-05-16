import asyncio
import platform
from typing import Any
import fire
from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team

class SpeakAloud(Action):
    """Action: Speak out aloud in a debate (quarrel)"""
    PROMPT_TEMPLATE: str = """
    ## BACKGROUND
    Suppose you are {name}, you are in a debate with {opponent_name}.
    ## DEBATE HISTORY
    Previous rounds:
    {context}
    ## YOUR TURN
    Now it's your turn, you should closely respond to your opponent's latest argument, state your position, defend your arguments, and attack your opponent's arguments,
    craft a strong and emotional response in 80 words, in {name}'s rhetoric and viewpoints, your will argue:
    """
    name: str = "SpeakAloud"
    async def run(self, context: str, name: str, opponent_name: str):
        prompt = self.PROMPT_TEMPLATE.format(context=context, name=name, opponent_name=opponent_name)
        # logger.info(prompt)
        rsp = await self._aask(prompt)
        return rsp
    
class Debator(Role):
    name: str = ""
    profile: str = ""
    opponent_name: str = ""

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.set_actions([SpeakAloud])
        self._watch([UserRequirement, SpeakAloud])

    ## 0.7.2 及以上版本可以不用重写 _observe
    # async def _observe(self) -> int:
    #     await super()._observe()
    #     # accept messages sent (from opponent) to self, disregard own messages from the last round
    #     self.rc.news = [msg for msg in self.rc.news if msg.send_to == {self.name}]
    #     return len(self.rc.news)

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo  # An instance of SpeakAloud
        memories = self.get_memories()
        context = "\n".join(f"{msg.sent_from}: {msg.content}" for msg in memories)
        print(context)
        rsp = await todo.run(context=context, name=self.name, opponent_name=self.opponent_name)
        msg = Message(
            content=rsp,
            role=self.profile,
            cause_by=type(todo),
            sent_from=self.name,
            send_to=self.opponent_name,
        )
        self.rc.memory.add(msg)
        return msg

# 声明异步函数


async def debate(idea: str, investment: float = 3.0, n_round: int = 5):
    """Run a team of presidents and watch they quarrel. :)"""
    Biden = Debator(name="Biden", profile="Democrat", opponent_name="Trump")
    Trump = Debator(name="Trump", profile="Republican", opponent_name="Biden")
    team = Team()
    team.hire([Biden, Trump])
    team.invest(investment)
    team.run_project(idea, send_to="Biden")  # send debate topic to Biden and let him speak first
    # 这里是异步的第三层创建：它并不是真正的异步任务，而是提供真正的多个异步任务的入口以及资源管理；内部会管理多个异步任务
    await team.run(n_round=n_round) # 协程对象
    # 假设 run 方法是如下的写法，那么这样写是“顺序的”，一人说完另一人说。每一轮其实是两个 await 顺序执行。虽然用了 async 和 await，但并发度是 1 个一个执行，不高效。
    """
    class Team:
        async def run(self, n_round):
            for i in range(n_round):
                print(f"Round {i+1}")
                await self.debators[0].respond()
                await self.debators[1].respond()
    """
    # 但是如果 run 的写法如下, 
    # 这里每轮调用了两个 debator 的 respond()，并发执行。
    # asyncio.gather() 是并发等待多个协程的方式。
    # 即使有 10 个 Debator，它们都可以一起运行。
    """
    class Team:
        async def run(self, n_round):
            for i in range(n_round):
                print(f"Round {i+1}")
                tasks = [debator.respond() for debator in self.debators]
                results = await asyncio.gather(*tasks)
                # 分析结果、打印输出等
    """



def main(idea: str, investment: float = 3.0, n_round: int = 10):
    """
    :param idea: Debate topic, such as "Topic: The U.S. should commit more in climate change fighting" or "Trump: Climate change is a hoax"
    :param investment: contribute a certain dollar amount to watch the debate
    :param n_round: maximum rounds of the debate
    :return:
    """
    if platform.system() == "Windows":
        # print('windows')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # print('linux')

    """
    我有一个问题：
    asyncio.run 启动的事件管理对象，只传入了一个异步方法，debate，且 debate 中内部只有一个 await team.run 方法，
    当程序执行到 await 时，该异步方法 debate 是事件管理器，或者说主线程 main 中的唯一一个协程。这种写法的意义在哪里。
    答案是：“取决于 team.run() 是否启动了多个并发协程或 I/O 操作”。这个结构是非常常见的 异步执行架构基础模式(这是 Python asyncio 的标准启动模式)
    """

    # 开启异步调度的两个方法：
    # 1. asyncio.run() 是 asyncio 的事件循环的入口点
    # 2. 要有一个  asynvc 异步函数作为  async 世界的 main()；
    # 那么此时如下代码就是上述两个展开异步的关键组件； 共同完成 异步 的第一层 + 第二层创建
    asyncio.run(debate(idea, investment, n_round)) # 协程调度入口
    





if __name__ == "__main__":
    # main 是整个程序的入口
    fire.Fire(main("Topic: The U.S. should commit more in climate change fighting"))
