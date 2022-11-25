import vxi11_server as Vxi11
import sys
import os
import signal
import time
import logging

sys.path.append(os.path.abspath('..'))

#
# A simple instrument server.
#
# creates an InstrumentServer with the name INSTR
# adds a device handler with the name inst1
# this instrument simply responds with the current time when queried by
# a vxi11 client.
#
# 'TIME' may not be a legal vxi11 instrument name, but seems to work well.
# allowing some introspection on a device you havent used (and didnt document)
# in some time.
#


def signal_handler(signal, frame):
    logger.info('Handling Ctrl+C!')
    instr_server.close()
    sys.exit(0)


class U2049Bridge(Vxi11.InstrumentDevice, Vxi11.Instrument):

    def device_init(self):
        self.idn = 'VXI11', 'U2049XABridge', '1234', '567'
        self.result = 'empty'
        self.terminalInstrument = Vxi11.Instrument("TCPIP::10.86.134.71::INSTR")
        return

    def device_write(self, opaque_data, flags, io_timeout):
        error = Vxi11.Error.NO_ERROR

        #opaque_data is a bytes array, so decode it correctly
        bytesSeq=opaque_data.decode("ascii")
        print('\n@@incoming cmd:',repr(bytesSeq), '\n')
        # remove the tailing '\r\n'
        cmd = bytesSeq.strip('\r\n')

        if 'ERR?' in cmd: 
            #self.terminalInstrument.write(cmd)
            #self.result = self.terminalInstrument.read()
            self.result = '+0, No error'
        elif '?' in cmd:
            self.terminalInstrument.write(cmd)
            self.result = self.terminalInstrument.read()
        elif 'trig1:sour' in cmd.lower():
            self.terminalInstrument.write('TRIG:SOUR IMM')
        else:
            self.terminalInstrument.write(cmd)
        # dict(incomeCmd, outputCmd)
        print('\n@@Return result:', repr(self.result), '\n')


        '''
        if cmd == '*IDN?':
            mfg, model, sn, fw = self.idn
            self.result = "{},{},{},{}".format(mfg, model, sn, fw)
        elif cmd  == '*DEVICE_LIST?':
            devs = self.device_list
            self.result = ''
            isFirst = True
            for dev in devs:
                if isFirst:
                    self.result = '{}'.format(dev)
                    isFirst = False
                else:
                    self.result = '{}, {}'.format(self.result, dev)
        else:
            self.result = 'invalid'
        '''
        logger.info("%s: device_write(): %s %s", self.name(), cmd , self.result)
        return error
    
    def device_read(self, request_size, term_char, flags, io_timeout):
        error = Vxi11.Error.NO_ERROR
        reason = Vxi11.ReadRespReason.END

        #device-read returns opaque_data so encode it correctly
        opaque_data = self.result.encode("ascii")
        
        return error, reason, opaque_data


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to exit')
    logger.info('starting time_device')
    
    # create a server, attach a device, and start a thread to listen for requests
    instr_server = Vxi11.InstrumentServer(U2049Bridge)
    #name = 'TIME'
    #name = 'inst1'
    #instr_server.add_device_handler(U2049Bridge, 'inst0')
    instr_server.listen()

    # sleep (or do foreground work) while the Instrument threads do their job
    while True:
        time.sleep(1)

        
