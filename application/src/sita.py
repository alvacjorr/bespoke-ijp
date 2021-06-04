import serial

# f = open('sita2.txt')

# textl = f.readline()

# if f[2]

s = serial.Serial("COM8", 57600)

filename = "data.txt"

f = open("data.txt", "w")

while True:
    l = s.readline()
    l = l.decode("utf-8")
    f.write(l)
    if l[1] == "D":
        print(l)
        temp = l[7:10]
        temp = int(temp)
        temp = temp / 10
        tension = l[4:7]
        tension = int(tension)
        tension = tension / 10
        print(temp)
        print(tension)
