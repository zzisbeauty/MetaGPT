import asyncio

from metagpt.context import Context
from metagpt.roles.product_manager import ProductManager
from metagpt.logs import logger


async def main():
    msg = "Write a PRD with Snack Game"
    context = Context()
    role = ProductManager(context=context)
    while msg:
        msg = await role.run(msg)
        logger.info(str(msg))


if __name__ == "__main__":
    asyncio.run(main())