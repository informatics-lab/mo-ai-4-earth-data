from azure.storage.blob.aio import BlobServiceClient
import os
import aiohttp
import uuid
import base64
import logging

CHUNKSIZE = 10 * 1024 ** 2  # 10MB


HEADERS = {
    "x-api-key": os.environ['APIKEY']
}

async def write_lotus_url_data_to_blob(url, name, metadata={}):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            await write_to_blob(response.content, name)

def _id(i, name):
    id = (uuid.uuid4().hex + str(i) + str(hash(name))).encode('utf-8')
    b64_encoded = base64.b64encode(id[:16])
    return b64_encoded.decode("utf-8")

async def write_to_blob(stream, name, metadata={}):    
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["BLOB_CONN_STR"])
    async with blob_service_client:
        # Instantiate a new ContainerClient
        container_client = blob_service_client.get_container_client(os.environ["CONTAINER_NAME"])
        
        # Instantiate a new BlobClient
        blob_client = container_client.get_blob_client(name)

        # [START upload_a_blob in CHUNKSIZE chunks ]
        blocks = []
        chunk_num = 0
        async for data in chunk_stream(stream):
            chunk_id = _id(chunk_num, name)
            logging.info(f"Chunk `{chunk_id}` len {len(data)} to blob name: {name}")
            await blob_client.stage_block(block_id=chunk_id, data=data, length=len(data))
            blocks.append(chunk_id)
            chunk_num+=1
        
        blob = await blob_client.commit_block_list(block_list=blocks, metadata=metadata)
         # [END upload_a_blob]

        logging.info(f'Blob {name} uploaded in {chunk_num} parts')

async def chunk_stream(stream):
    chunk = True
    while chunk:
        chunk = await stream.read(CHUNKSIZE)
        if chunk:
            yield chunk