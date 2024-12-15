import argparse
import asyncio
import logging
from aiopath import AsyncPath
from aioshutil import copyfile


async def read_folder(path: AsyncPath, output: AsyncPath) -> None:
    try:
        async for item in path.iterdir():
            if await item.is_dir():
                await read_folder(item, output)
            elif await item.is_file():
                await copy_file(item, output)
    except Exception as e:
        logging.error(f"Error reading folder {path}: {e}")


async def copy_file(file: AsyncPath, output: AsyncPath) -> None:
    try:
        extension_name = file.suffix[1:]
        extension_folder = output / extension_name
        await extension_folder.mkdir(exist_ok=True, parents=True)
        await copyfile(file, extension_folder / file.name)
        logging.info(f"Copied {file} to {extension_folder / file.name}")
    except Exception as e:
        logging.error(f"Error copying file {file}: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="Async file sorter by extension.")
    parser.add_argument("source", type=str, help="Path to the source folder")
    parser.add_argument("output", type=str, help="Path to the output folder")
    args = parser.parse_args()

    source = AsyncPath(args.source)
    output = AsyncPath(args.output)

    asyncio.run(read_folder(source, output))
