import asyncio
import sys
from pawnstack.log import get_logger

# Initialize a logger for this module
logger = get_logger("pawnstack.asyncio.helper")


async def shutdown_async_tasks(loop=None, tasks=None, exit_on_shutdown=True, exit_code=0):
    """
    Shutdown all pending async tasks and close the loop gracefully.

    Args:
        loop (asyncio.AbstractEventLoop): The event loop to use. If None, the current running loop will be used.
        tasks (List[asyncio.Task]): List of tasks to cancel. If None, all pending tasks in the loop will be cancelled.
        exit_on_shutdown (bool): If True, the system will exit after shutdown.
        exit_code (int): Exit code to return when exiting the system (default is 0).
    """
    if loop is None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.warning("No running event loop found.")
            return

    if tasks is None:
        tasks = [task for task in asyncio.all_tasks(loop) if isinstance(task, asyncio.Task)]

    logger.info(f"Initiating graceful shutdown. Found {len(tasks)} pending task(s) to cancel.")

    if tasks:
        for task in tasks:
            if not task.done() and not task.cancelled():
                try:
                    task_name = task.get_coro().__name__
                except AttributeError:
                    task_name = str(task)
                logger.info(f"Cancelling task: {task_name}")
                task.cancel()

        # Wait for all tasks to be cancelled
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("All tasks cancelled.")

    logger.info("Event loop closed gracefully.")

    if exit_on_shutdown:
        logger.info(f"Exiting the system after graceful shutdown with exit code {exit_code}.")
        sys.exit(exit_code)
