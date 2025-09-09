import asyncio

import bittensor_wallet
import pytest

import turbobt


async def main():
    wallet = bittensor_wallet.Wallet("alice", "default")

    async with turbobt.Bittensor(
        "local",
        wallet=wallet,
    ) as bt:
        subnet = bt.subnet(1)

        try:
            await subnet.neurons.register(wallet.hotkey)
        except turbobt.subtensor.exceptions.HotKeyAlreadyRegisteredInSubNet:
            pass

        # 128 -> OK
        extrinsic = await subnet.commitments.set(b"01" * 256)
        await extrinsic.wait_for_finalization()

        v = await subnet.commitments.get(wallet.hotkey.ss58_address)
        assert v == "0"

        # # 129 -> Not OK (doesn't even fire request as runtime/scale can't encode)
        # with pytest.raises(
        #     ValueError,
        #     # match="Value 'Raw129' not present in type_mapping of this enum",
        # ):
        #     await subnet.commitments.set(b"0" * 513)

        # Fill up the buffer (3100 bytes)
        extrinsics = [
            await subnet.commitments.set(b"0" * 512)
            for i in range(5)
        ]
        await asyncio.gather(
            *[extrinsic.wait_for_finalization() for extrinsic in extrinsics]
        )

        # Bang!
        with pytest.raises(
            turbobt.substrate.exceptions.SubstrateException,
            match="Space Limit Exceeded for the current interval",
        ):
            extrinsic = await subnet.commitments.set(b"0" * 512)
            await extrinsic.wait_for_finalization()


asyncio.run(main())