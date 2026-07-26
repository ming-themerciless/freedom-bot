import asyncio

from application.actor_locks import ActorLockManager


def test_actor_name_variants_are_serialized():
    async def exercise():
        manager = ActorLockManager()
        first_entered = asyncio.Event()
        release_first = asyncio.Event()
        second_entered = asyncio.Event()

        async def first():
            async with manager.acquire(" Aria "):
                first_entered.set()
                await release_first.wait()

        async def second():
            await first_entered.wait()
            async with manager.acquire("ARIA"):
                second_entered.set()

        first_task = asyncio.create_task(first())
        second_task = asyncio.create_task(second())
        await first_entered.wait()
        await asyncio.sleep(0)

        assert not second_entered.is_set()

        release_first.set()
        await asyncio.gather(first_task, second_task)
        assert second_entered.is_set()

    asyncio.run(exercise())


def test_different_actors_can_run_concurrently():
    async def exercise():
        manager = ActorLockManager()
        first_entered = asyncio.Event()
        second_entered = asyncio.Event()
        release = asyncio.Event()

        async def enter(actor_name, entered):
            async with manager.acquire(actor_name):
                entered.set()
                await release.wait()

        first_task = asyncio.create_task(enter("Aria", first_entered))
        second_task = asyncio.create_task(enter("Borin", second_entered))
        await asyncio.gather(first_entered.wait(), second_entered.wait())

        assert first_entered.is_set()
        assert second_entered.is_set()

        release.set()
        await asyncio.gather(first_task, second_task)

    asyncio.run(exercise())
