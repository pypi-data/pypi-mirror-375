import asyncio
import turbobt


async def main():
    async with turbobt.Bittensor() as bittensor:
        while True:
            try:
                block = await bittensor.head.get()
                print(block.number)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(repr(e))
            finally:
                await asyncio.sleep(5)

asyncio.run(main())
