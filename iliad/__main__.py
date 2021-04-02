import asyncio
import configparser

import iliad


async def main():
    cp = configparser.ConfigParser()
    cp.read("config.ini")

    user = await iliad.get(cp["iliad"]["user"], cp["iliad"]["pass"])
    print(user)

    # with open("saved", 'w') as f:
    #     f.write(user.html)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
