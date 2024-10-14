def fifohandler():
    try:
        # Create the named pipes (FIFO)
        makefifo(bi.fifoinfile)
        makefifo(bi.fifooutfile)

        if bi.fifoup:
            bi.datain = None
            logger.info("Entering fifohandler()")
            logger.debug("Input FIFO file: %s", bi.fifoinfile)

            while True:
                try:
                    logger.debug("Opening FIFO: %s", bi.fifoinfile)
                    with open(bi.fifoinfile, 'r') as fifo:
                        logger.debug("FIFO opened successfully")

                        while True:
                            bi.datain = fifo.read()
                            logger.debug("Data received from FIFO: %s", bi.datain)

                            if len(bi.datain) == 0:
                                logger.debug("No data in FIFO, breaking read loop")
                                break
                            else:
                                logger.debug("Offloading data to dataprocessor()")
                                dataprocessor()  # Process the received data
                                bi.datain = None  # Reset the input data
                                bi.dataout = None  # Reset the output data
                                break
                except Exception as fifo_error:
                    logger.error("Error handling FIFO: %s", fifo_error)
                    break
    except Exception as general_error:
        logger.critical("Failed to handle FIFOs: %s", general_error)
    finally:
        logger.info("Exiting fifohandler()")
