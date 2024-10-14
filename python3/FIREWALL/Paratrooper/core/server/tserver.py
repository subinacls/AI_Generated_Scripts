def tserver():
    """
    Initializes the threaded TCP server and joins all threads in the bi.threadlist.
    Thread safety is ensured with thread locks.
    """
    try:
        logger.log('Entering: tserver()', 'info')

        # Start the Threaded TCP Server
        server_address = ('localhost', 65432)  # Example server address
        server = ThreadedTCPServer(server_address, ThreadedTCPRequestHandler)

        # Start the server in a separate thread
        server_thread = threading.Thread(target=server.mytcpserver)
        server_thread.daemon = True  # Allow the thread to exit when main program exits
        server_thread.start()

        # Add the server thread to bi.threadlist and ensure thread safety
        with lock:
            bi.threadlist.append(server_thread)

        # Join and monitor each thread in the bi.threadlist to prevent runaway memory consumption
        with lock:
            for t in bi.threadlist:
                t.join()

        logger.log('Exiting: tserver()', 'info')

    except Exception as tcpserverfail:
        logger.log(f"tserver() - TCP Server initialization failed: {tcpserverfail}", 'error')
        logger.log('Exiting: tserver()', 'info')
        return 0  # Return 0 on failure to indicate the server did not start
