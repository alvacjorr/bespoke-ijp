import pyvisa

def main():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())

    my_instrument = rm.open_resource('USB::0x0699::0x0349::C013148::INSTR')
    print(my_instrument.query('*IDN?'))
    #print(my_instrument.query('OUTP1?'))
    #my_instrument.write('*TRG')

if __name__ == '__main__':
    main()