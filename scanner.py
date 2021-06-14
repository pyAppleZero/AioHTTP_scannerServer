from aiohttp import web
import socket
import threading
import syslog

routes = web.RouteTableDef()

def tcpConnect(ip, port_number, openPorts):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.settimeout(0.3)
    try:
        connection.connect((ip, port_number))
        openPorts.append(port_number)
        connection.close()
        openedPortStr = 'Port:'+str(port_number)+'open'
        syslog.syslog(syslog.LOG_INFO, openedPortStr)
    except:
        closedPortStr = 'Port:'+str(port_number)+'closed'
        syslog.syslog(syslog.LOG_INFO, closedPortStr)
        pass

def scan_ports(host_ip, portMin, portMax, openPorts):
    forScan = portMax - portMin + 1
    threads = []
    for i in range(forScan):
        thread = threading.Thread(target=tcpConnect, args=(host_ip, i, openPorts))
        threads.append(thread)
    for i in range(forScan):
        threads[i].start()
    for i in range(forScan):
        threads[i].join()

@routes.get('/scan/{ip}/{begin_port}/{end_port}')
async def handler(request):
    try:
        ip = request.match_info["ip"]
        dotCounter = 0
        for i in ip:
            if i == '.': dotCounter = dotCounter+1
        if dotCounter == 3:
            try:
                portMin = int(request.match_info["begin_port"])
            except Exception:
                syslog.syslog("Error: arguement type error")
                return web.json_response({"error": 'arguement type error'})
            if portMin < 0: portMin = 0; syslog.syslog('Warning: Negative port number!')

            try:
                portMax = int(request.match_info["end_port"])
            except Exception:
                syslog.syslog("Error: arguement type error")
                return web.json_response({"error": 'type error'})
            if (portMax < portMin) or (portMax < 0) or (portMax > 65535): portMax = 65535; syslog.syslog('Warning: Maximum port corrected!')

            logStr = 'New Request: '+ip+'|Ports: '+str(portMin)+'-'+str(portMax)
            syslog.syslog(syslog.LOG_INFO, logStr)

        else:
            syslog.syslog("Error: wrong IP type")
            return web.json_response({"error": 'ip'})
        
        openPorts = []
        scan_ports(ip, portMin, portMax, openPorts)
        return web.json_response({"port": str(openPorts), "state": "open"})

    except Exception:
        syslog.syslog("Error: Common error")
        pass

@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        status = response.status
        if status == 200:
            return response
    except web.HTTPNotFound as error_404:
        status = error_404.status
        syslog.syslog('Code 404: Not Found')
    return web.json_response({'error': status})

async def scanApp() -> web.Application:
    app = web.Application(middlewares=[error_middleware])
    app.add_routes(routes)
    return app

web.run_app(scanApp())
