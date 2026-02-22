import asyncpg

async def PostgresHandler(config):
    #global db_pool
    return await asyncpg.create_pool(**config)
