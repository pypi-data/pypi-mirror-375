import turbobt
import pprint
import scalecodec
import bittensor_wallet
import pytest

from turbobt.substrate._hashers import HASHERS


async def main2():
    async with turbobt.Bittensor() as bt:
        # v = await bt.subtensor.rpc(
        #     "SubtensorModule.get_yuma3_on",
        #     {
        #         "netuid": 12,
        #     }
        # )
        v2 = await bt.subtensor.state.getStorage("SubtensorModule.Yuma3On", 2)
        sub = await bt.subtensor.state.subscribeStorage(["System.Events"])
        async for event in sub:
            print(event)
        #     pallet, storage_function = bt.subtensor["System", "Events"]
        #     param_types = storage_function.get_params_type_string()
        #     param_hashers = storage_function.get_param_hashers()

        #     key_type_string = []

        #     for param_hasher, param_type in zip(param_hashers, param_types):
        #         try:
        #             hasher = HASHERS[param_hasher]
        #         except KeyError:
        #             raise NotImplementedError(param_hasher)

        #         key_type_string.append(f"[u8; {hasher.hash_length}]")
        #         key_type_string.append(param_type)

        #     key_type = bt.subtensor._registry.create_scale_object(
        #         f"({', '.join(key_type_string)})",
        #     )
        #     value_type = bt.subtensor._registry.create_scale_object(
        #         storage_function.get_value_type_string(),
        #     )
        #     prefix = bt.subtensor.state._storage_key(
        #         pallet,
        #         storage_function,
        #         [],
        #     )

        #     results = (
        #         (
        #             bytearray.fromhex(key.removeprefix(prefix)),
        #             bytearray.fromhex(value[2:]),
        #         )
        #         for key, value in event["changes"]
        #     )
        #     results = (
        #         (
        #             key_type.decode(
        #                 scalecodec.ScaleBytes(key),
        #             ),
        #             value_type.decode(
        #                 scalecodec.ScaleBytes(value),
        #             ),
        #         )
        #         for key, value in results
        #     )
        #     results = (
        #         v
        #         for key, value in results
        #         for v in value
        #     )
        #     for value in results:
        #         # pprint.pprint(value)
        #         if value["event_id"] in (
        #             "ExtrinsicSuccess",
        #             "ExtrinsicFailed",
        #         ):
        #             continue
        #         print(value["event_id"], value["event"]["attributes"])
        #     # print(list(results))

        # b = await bt.block(5858264).get()
        # print(await b.get_timestamp())
        # block_hash = await bt.subtensor.chain.getBlockHash(5858264)
        # block = await bt.subtensor.chain.getBlock(block_hash)
        # extrinsics = block["block"]["extrinsics"]
        # calls = [f'{e["call"]["call_module"]}_{e["call"]["call_function"]}' for e in extrinsics]
        # extrinsics = [
        #     extrinsic["call"]
        #     for extrinsic in extrinsics
        #     if extrinsic["call"]["call_module"] == "Multisig" and extrinsic["call"]["call_function"] == "as_multi"
        # ]

        # try:
        #     pprint.pprint(extrinsics[0])
        # except IndexError:
        #     pass
        # calls = [c for c in calls if c not in ("set_weights", "commit_crv3_weights", "add_stake_limit", "set_commitment")]
        # print(calls)
        events = await bt.subtensor.system.Events.get(
            block_hash="0x0e96a0ed9eddf4b401c5e4234c36c41834ffb82c606fd0d92bf68c99f0b8122c",
        )
        # events = await bt.subtensor.state.getStorage(
        #     "System.Events",
        #     # block_hash=block_hash,
        # )
        value = await bt.subtensor.state.getStorage(
            "SubtensorModule.NetworkRateLimit",
            # block_hash=block_hash,
        )

        # assert value == 2628000
        print(value)

        e = await bt.subtensor.admin_utils.sudo_set_network_rate_limit(
            2000,
            wallet=bittensor_wallet.Wallet("alice", "default"),
        )
        await e.wait_for_finalization()


async def main():
    # wallet = bittensor_wallet.Wallet("luxor-validator", "default")
    wallet = bittensor_wallet.Wallet("alice", "default")

    async with turbobt.Bittensor(
        # "local",
        wallet=wallet,
    ) as bt:
        v = await bt.subnets.count()
        await bt.subnets[0].neurons.register(wallet.hotkey)
        await bt.batch(
            bt.subnets[0].neurons["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"].remove_stake(10_000_000_000),
            bt.subnets[0].neurons["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"].add_stake(100_000_000_000),
            # bt.subnets[0].neurons["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"].remove_stake(10_000_000_000),
            # bt.subnets.register(),
        )
        async with bt.transaction():
            await bt.subnets[0].neurons["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"].remove_stake(10_000_000_000)
            await bt.subnets[0].neurons["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"].add_stake(100_000_000_000)

        return

        # await bt.subnets[0].neurons["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"].add_stake(321_000_000_000)
        await bt.subnets[0].neurons["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"].remove_stake(100_000_000_000)
        return

        subnet = bt.subnet(1)

        try:
            await subnet.neurons.register(wallet.hotkey)
        except turbobt.subtensor.exceptions.HotKeyAlreadyRegisteredInSubNet:
            pass

        # 128 -> OK
        extrinsic = await subnet.commitments.set(b"0" * 128)
        await extrinsic.wait_for_finalization()

        # 129 -> Not OK (doesn't even fire request as runtime/scale can't encode)
        with pytest.raises(
            ValueError,
            match="Value 'Raw129' not present in type_mapping of this enum",
        ):
            await subnet.commitments.set(b"0" * 129)

        # Fill up the buffer (3100 bytes)
        extrinsics = [
            await subnet.commitments.set(b"0" * 128)
            for i in range(23)
        ]
        await asyncio.gather(
            *[extrinsic.wait_for_finalization() for extrinsic in extrinsics]
        )

        with pytest.raises(
            turbobt.substrate.exceptions.SubstrateException,
            match="Space Limit Exceeded for the current interval",
        ):
            extrinsic = await subnet.commitments.set(b"0" * 128)
            await extrinsic.wait_for_finalization()
        # for i in range(31):
        #     extrinsic = await subnet.commitments.set(b"0" * 128)
        #     await extrinsic.wait_for_finalization()

        # extrinsic = await subnet.commitments.set(b"0" * 128)
        # await extrinsic.wait_for_finalization()

        return
        

    # async with turbobt.Bittensor(wallet=wallet) as bt:
    async with turbobt.Bittensor("ws://54.83.169.218:9946", wallet=wallet) as bt:
        # set_stake_threshold
        # subnet = bt.subnet(388)
        # block = await bt.head.get()
        # timestamp = await block.get_timestamp()
        # bt.subnets.count()
        subnet = bt.subnet(2)
        # ex = await bt.subtensor.admin_utils.sudo_set_stake_threshold(wallet)
        # await ex.wait_for_finalization()
        validators = await subnet.neurons.validators()
        # weights = await subnet.weights.fetch()
        commitments = await subnet.commitments.fetch()
        # neurons = await subnet.list_neurons()

        # await subnet.neurons.serve(
        #     ip="192.168.0.2",
        #     port=8000,
        # )

        # neuron = await subnet.get_neuron(wallet.hotkey.ss58_address)

        # print(neurons)

        # await bt.subtensor.admin_utils.sudo_set_commit_reveal_weights_enabled(
        #     netuid=subnet.netuid,
        #     enabled=True,
        #     wallet=wallet,
        # )

        # await subnet.weights.commit({
        #     0: 1.0,
        #     # 1: 0.8,
        # })

        for i in range(10):
            weights = await subnet.weights.fetch_pending()
            print(weights)
            # neuron = await bt.subtensor.neuron_info.get_neuron(
            #     netuid=2,
            #     uid=0,
            # )

            # print(neuron["weights"])

            await asyncio.sleep(0.1)


import asyncio

asyncio.run(main())