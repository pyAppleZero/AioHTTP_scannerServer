# AioHTTP_scannerServer
aiohttp server with multithreaded requests port scanner
JSON response format

Usage: GET /scan/<ip>/<begin_port>/<end_port>
Answer: {"port": "str(list)", "state": "open"}
