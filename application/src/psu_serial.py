import serial
class GPD_4303S:
    """Class to control a GW INSTEK GPD-4303S power supply
    """    
    def __init__(self,port):
        """Initialise the PSU by connecting it, as well as creating a buffer for async communications.

        :param port: The COM/tty port the PSU is attached to
        :type port: string
        """

        
        self.instrument = serial.Serial(port, baudrate=115200, timeout= 0.002)
        print("Connected to power supply.")
        self.async_query_buffer = [] #create an empty lis
        self.async_reply_buffer = []
        #self.identify()




        
    def async_waiting(self):
        if not (self.async_query_buffer):
            print('no pending')
            return False
        else:
            print('pending task')
            return True

    def async_waiting_number(self):
        return len(self.async_query_buffer)


    def query(self, message): #takes a port and a message for that port and returns the response given 
        if not self.async_waiting():
            self.instrument.reset_input_buffer()
            self.write(message)
            msg =  self.instrument.readline()
            #print(msg)
            return msg.decode('utf-8')
        else:
            return 'comm locked'

    def query_async(self,message): #asynchronously gets a query and returns a unique ID
        #print('Querying: ' + message)
        if message in self.async_query_buffer:
            #print(message + ' already in buffer')
            #print(self.async_query_buffer)
            return
        self.async_query_buffer.append(message)
        self.write(message)
        #print(message + ' added to buffer')
        #print(self.async_query_buffer)


        return self.async_query_buffer.index(message)

    def poll_async(self):
        going = True
        while going:
            msg = self.instrument.readline()
            msg = msg.decode('utf-8')
            
            if not msg:
                going = False
            else:
                self.async_reply_buffer.append(msg)
                return self.sanitize_reply_buffer()

    def sanitize_reply_buffer(self):
        """Occasionally the reply buffer gets corrupted, ususally from the poller thinking there is a newline when in fact there is not.

        :return: Status of cleaning
        :rtype: string
        """        
        for i in self.async_reply_buffer:

            if not i.endswith('\n'):
            
                i = self.async_reply_buffer.index(i)
                temp = self.async_reply_buffer
            #with suppress(IndexError):
                if i+1 == len(temp):
                    return 'SANFAIL'
                if i < len(temp):
                    #print(i)
                    #print(len(temp))
                    #print(temp)
                    #print(temp[i])
                    #print(temp[i+1])
                    temp[i] = temp[i] + temp[i+1]
                    temp.pop(i+1)
                    self.async_reply_buffer = temp


            #print(self.async_reply_buffer)


        


    def get_async_response(self,message):
        """Check if a particular message has received an async response yet.

        :param message: Message we are looking for a reply to
        :type message: string
        :return: Response from the PSU
        :rtype: string
        """        
        index = self.async_query_buffer.index(message)
        #print('**********')
        #print ('requesting ' + message + ' at index ' + str(index))
        b = True
        try:
            response = self.async_reply_buffer[index]
            if response.endswith('\n'):
                response = self.async_reply_buffer.pop(index)
            else:
                b = False
                response = 'EMPTY'
        except IndexError: 
            #print('response not available yet!!')
            response = 'EMPTY'
            b = False
        if b:    
            #print('got reply:')
            #print(response)
            query = self.async_query_buffer.pop(index)
            #print('for query:')
            #print(query)
        #print('Buffers:')
        #print(self.async_reply_buffer)
        #print(self.async_query_buffer)
        #print('_________________')

        return response





    


    def write(self, message):
        """Write a message to the PSU

        :param message: Message to send
        :type message: String
        """        
        self.instrument.write(message.encode())
        
        

    def identify(self):
        """Print the ID of the PSU
        """
        print(self.query("*IDN?\n"))

    def turn_on(self):
        """Turn on all outputs on the PSU
        """
        self.write("OUT1\n")

    def turn_off(self):
        """Turn off all outputs on the PSU
        """
        self.write("OUT0\n")

    def set_voltage(self, v, ch):
        """Sets the voltage on a selected channel on the PSU

        :param v: voltage in Volts
        :type v: float
        :param ch: Channel to set
        :type ch: int (1,2,3,4)
        """        
        self.write("VSET" + str(ch) + ":" + str(v) + "\n")

    def set_current(self, i, ch):
        """Sets the current on a selected channel on the PSU

        :param i: current in Amps
        :type i: float
        :param ch: Channel to set
        :type ch: int (1,2,3,4)
        """
        self.write("ISET" + str(ch) + ":" + str(i) + "\n")

    def get_set_voltage(self, ch):
        reply =  self.query("VSET" + str(ch) + "?" + "\n")
        reply = reply[:-3] #truncate units V, CR and LF off the end
        return float(reply)

    def get_set_current(self, ch):
        reply = self.query("ISET" + str(ch) + "?" + "\n") #this will give a string for example "2.200A"
        reply = reply[:-3] #truncate units A off the end
        return float(reply) #and return it as a float

    def get_out_voltage(self, ch):
        reply = self.query("VOUT" + str(ch) + "?\n")
        reply = reply[:-3]
        return float(reply)

    def get_out_current(self, ch):
        reply = self.query("IOUT" + str(ch) + "?\n")
        return self.truncate_float_reply(reply)

    def get_out_current_a(self, ch):
        self.query_async("IOUT" + str(ch) + "?\n")

    def get_out_current_r(self,ch):
        r = self.get_async_response("IOUT" + str(ch) + "?\n")
        return self.truncate_float_reply(r)

    def truncate_float_reply(self,reply):
        """Truncate the last three letters of a reply and convert the remainder to float. For example, "0.002A\\r\\n" to "0.002"

        :param reply: Voltage or current data from the PSU
        :type reply: string
        :return: The voltage or current
        :rtype: float
        """
        return float(reply[:-3])

    def get(self,cmd,ch,async_mode):
        """Generic method to retrieve data from the PSU asynchronously.

        :param cmd: The first section of the command, e.g. VOUT
        :type cmd: String
        :param ch: Channel
        :type ch: int
        :param async_mode: Denotes whether to send a query or check for a reply.
        :type async_mode: string 'QUERY' or 'REPLY'
        :return: The reponse to the query, if available
        :rtype: String or None
        """
        comString = cmd + str(ch) + "?\n"
        if async_mode == 'QUERY':
            self.query_async(comString)
            return
        if async_mode == 'REPLY':
            try:
                return self.truncate_float_reply(self.get_async_response(comString))
            except ValueError:
                #print('a')
                return 'EMPTY'

    def get_custom(self,msg,async_mode):
        """Generic method to retrieve data from the PSU asynchronously with a custom msg.

        """
        comString = msg
        if async_mode == 'QUERY':
            self.query_async(comString)
            return
        if async_mode == 'NOREPLY':
            self.write(comString)
            return
        if async_mode == 'REPLY':
            try:
                return self.truncate_float_reply(self.get_async_response(comString))
            except ValueError:
                return 'EMPTY'



class PSU_DUMMY:
    """Dummy PSU class for when a realy PSU is not available.
    """
    def __init__(self,port):
        """dummy GPD-43038"""

        
        print("Connected to dummy power supply.")



    def query(self, message): #takes a port and a message for that port and returns the response given 

        self.write(message)
        msg =  self.instrument.readline()
        #print(msg)
        return msg.decode('utf-8')

    def write(self, message):
        print(message)
        
        

    def identify(self):
        print(self.query("*IDN?\n"))

    def turn_on(self):
        self.write("OUT1\n")

    def turn_off(self):
        self.write("OUT0\n")

    def set_voltage(self, v, ch):
        self.write("VSET" + str(ch) + ":" + str(v) + "\n")

    def set_current(self, i, ch):
        self.write("ISET" + str(ch) + ":" + str(i) + "\n")
