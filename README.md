# AioHTTP_scannerServer
aiohttp server with multithreaded requests port scanner
JSON response format

Because of using syslog python module, works on linux only. But if delete logging functions, it will be run on windows.

Usage: GET /scan/<ip>/<begin_port>/<end_port>
Answer: {"port": "str(list)", "state": "open"}
