import asyncio
import logging

logger = logging.getLogger(__name__)

notification_queue = asyncio.Queue()


async def periodic_balance_logger(balance_service, group_id: int):
    while True:
        try:
            balances = balance_service.compute_balances(group_id)
            logger.info(f"[ASYNC] Periodic balances for group {group_id}: {balances}")
        except Exception as e:
            logger.error(f"[ASYNC] Failed to compute balances: {e}")

        await asyncio.sleep(5)


async def simulate_notifications():
    while True:
        message = await notification_queue.get()
        logger.info(f"[ASYNC] Notification sent: {message}")
