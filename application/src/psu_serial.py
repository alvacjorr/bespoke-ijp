import serial
from contextlib import suppress
class GPD_43038:
    def __init__(self,port):
        """class to control a GWINSTEK GPD-43038"""

        
        self.instrument = serial.Serial(port, baudrate=115200, timeout= 0.0002)
        print("Connected to power supply:")
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
        if message in self.async_query_buffer:
            return
        self.async_query_buffer.append(message)
        self.write(message)


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

    def sanitize_reply_buffer(self): #occasionally the input buffer gets corrupted. this function fixes it
        for i in self.async_reply_buffer:

            if not i.endswith('\n'):
            
                i = self.async_reply_buffer.index(i)
                #print(self.async_reply_buffer)
                #print('we not good')
                temp = self.async_reply_buffer
            #with suppress(IndexError):
                if i+1 == len(temp):
                    print('boom')
                    #return 'SANFAIL'
                if i < len(temp):
                    print(i)
                    print(len(temp))
                    print(temp)
                    print(temp[i])
                    print(temp[i+1])
                    temp[i] = temp[i] + temp[i+1]
                    temp.pop(i+1)
                    self.async_reply_buffer = temp


            #print(self.async_reply_buffer)


        


    def get_async_response(self,message): #async checks if a query has been answered
        #print("_____________________________")
        #print("at start:")
        #print(self.async_reply_buffer)
        #print(self.async_query_buffer)
        
        #print(message)
        index = self.async_query_buffer.index(message)

        #print ('popping index ' + str(index))
        b = True
        try:
            response = self.async_reply_buffer.pop(index)
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
        #print(self.async_reply_buffer)
        #print(self.async_query_buffer)

        return response





    


    def write(self, message):
        self.instrument.write(message.encode())
        
        

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
        return float(reply[:-3])

    def get(self,cmd,ch,async_mode):
        comString = cmd + str(ch) + "?\n"
        if async_mode == 'QUERY':
            self.query_async(comString)
            return
        if async_mode == 'REPLY':
            try:
                return self.truncate_float_reply(self.get_async_response(comString))
            except ValueError:
                return 'EMPTY'



class PSU_DUMMY:
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
