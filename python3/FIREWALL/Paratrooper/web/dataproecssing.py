def dataprocessor():
    try:
        logger.info("Dataprocessor() data received: %s", str(bi.datain))

        # Check if the received input matches known command mappings
        shasum = str(bi.datain).strip()
        if shasum in command_map:
            command = command_map[shasum]

            if command == "DESTROY_HEADQUARTERS":
                logger.info("I SEE THE LIGHT")
                if int(bi.DET) > 2:
                    detcord()
                    logger.info("Destroy the HeadQuarters, INCOMING")
                else:
                    bi.DET += 1
            elif command == "SEND_CLIENT_DB":
                logger.info("Sending Client Database information to named pipe")
                logger.debug("Client DB: %s", str(bi.clientdb))
            elif command == "SEND_BAD_GUY_DB":
                logger.info("Sending Bad Guy Database information to named pipe")
                bi.dataout = str(bi.baddb)
            elif command == "SEND_THREADLIST":
                logger.info("Sending Threadlist information to named pipe")
                bi.dataout = str(bi.threadlist)
            elif command == "SEND_INIT_DAY":
                logger.info("Sending Current Day information to named pipe")
                bi.dataout = str(bi.initday)
            elif command == "SEND_REV_PORTS":
                logger.info("Sending Reverse Listener Ports information to named pipe")
                bi.dataout = str(bi.revports)
            elif command == "SEND_SHELLED":
                logger.info("Sending Shelled information to named pipe")
                bi.dataout = str(bi.shelled)
            elif command == "SEND_IPSET_MSF":
                logger.info("Sending ipset msfshelled group to named pipe")
                bi.dataout = str(bi.ipsetmsflist)
            elif command == "UPDATE_CLIENT_DB":
                logger.info("Updating the client database")
                banner()
                DBHandler().open_clientdb()
                DBHandler().save_clientdb()
            elif command == "ENABLE_SNIFFER":
                logger.info("Enabling the sniffer module")
                bi.enablesniffer = True
            elif command == "DISABLE_SNIFFER":
                logger.info("Disabling the sniffer module")
                bi.enablesniffer = False
            elif command == "ENABLE_SERVER":
                logger.info("Enabling the Paratrooper Server")
                IptBuilder().flush_fw()
                IptBuilder().basic_fw()
            elif command == "DISABLE_SERVER":
                logger.info("Disabling the Paratrooper Server")
                IptBuilder().flush_fw()
            elif command == "ENABLE_DEBUG":
                logger.info("Enabling STDOUT Debugger Information")
                AdminCmds().enablediag()
            elif command == "DISABLE_DEBUG":
                logger.info("Disabling STDOUT Debugger Information")
                AdminCmds().disablediag()
        else:
            # Attempt to evaluate the input as a dictionary command
            try:
                bi.datad = ast.literal_eval(bi.datain)
                if isinstance(bi.datad, dict) and 'RUNCMD' in bi.datad:
                    banner()  # Clear the screen, show banner + cmd output
                    sendcommands(bi.datad['RUNCMD'].strip())
            except Exception as failed_to_process:
                logger.error("dataprocessor() failed: %s", failed_to_process)

    except Exception as e:
        logger.critical("dataprocessor() encountered an error: %s", e)
