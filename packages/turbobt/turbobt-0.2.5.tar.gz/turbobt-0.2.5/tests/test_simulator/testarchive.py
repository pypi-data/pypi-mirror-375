import asyncio

import turbobt

async def main():
    bittensor = turbobt.Bittensor("archive")
    current_block_number = (await bittensor.head.get()).number
    print(current_block_number)
    async with bittensor.block(int(current_block_number*0.01)):
        subnet = bittensor.subnet(12)
        neurons = await subnet.list_neurons()
    for neuron in neurons:
        print(neuron.stake, neuron.axon_info, neuron.active, neuron.axon_info.ip, neuron)

asyncio.run(main())
