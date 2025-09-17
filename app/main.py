import asyncio, os
from app.logger import logger
from app.parser import parse_cdr_line
from app.db import engine, AsyncSessionLocal
from app.models import AvayaCDR, Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

NET_ADDR = os.getenv('NET_SOCKET_ADDR', '0.0.0.0')
NET_PORT = int(os.getenv('NET_SOCKET_PORT', '9000'))

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info('peername')
    logger.info(f'Client connected: {peer}')
    try:
        while not reader.at_eof():
            data = await reader.readline()
            if not data:
                break
            line = data.decode(errors='ignore').strip()
            if not line:
                continue
            parsed = parse_cdr_line(line)
            if not parsed:
                logger.warning(f'Could not parse line: {line}')
                continue
            start_str, duration, calling, called, code = parsed
            # insert into DB
            try:
                async with AsyncSessionLocal() as session:  # type: AsyncSession
                    stmt = insert(AvayaCDR).values(
                        date=start_str,
                        duration=duration,
                        calling_number=calling,
                        called_number=called,
                        call_code=code)
                    await session.execute(stmt)
                    await session.commit()
            except Exception as e:
                logger.error(f'DB insert failed: {e} | line={line}')
    except Exception as e:
        logger.exception('Error while handling client')
    finally:
        writer.close()
        await writer.wait_closed()
        logger.info(f'Client disconnected: {peer}')

async def init_db():
    # create tables if not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    # await init_db()
    server = await asyncio.start_server(handle_client, NET_ADDR, NET_PORT)
    addr = server.sockets[0].getsockname()
    logger.info(f'Avaya collector server started on {addr[0]}:{addr[1]}')
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Shutting down')        
