import asyncio
import aio_pika

from config import RABBITMQ_CORE_USER, RABBITMQ_CORE_PASS

async def start_consuming():
    # Create a connection to RabbitMQ
    connection = await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_CORE_USER}:{RABBITMQ_CORE_PASS}@biokeeper_mq/basic_vhost",
    )

    # Create a channel
    channel = await connection.channel()

    # Declare a queue
    queue = await channel.declare_queue('core.new_user', passive=True)

    # Define a callback function to handle incoming messages
    async def callback(message):
        async with message.process():
            with open('/testfolder/file.txt', 'a') as file:
                file.write('Message:')
                file.write(message.body.decode() + '\n')
            print(message.body)

    # Start consuming messages from the queue
    await queue.consume(callback)

    # Wait for incoming messages
    while True:
        await asyncio.sleep(1)


# asyncio.run(start_consuming())