import random
import copy
import math

class Node():
    def __init__(self,circuit):
        self.ports = list()
        circuit.append(self)
    
class Resistor():
    def __init__(self,portA,portB,value):
        self.portA = portA
        self.portB = portB
        self.value = value

        portA.ports.append(self)
        portB.ports.append(self)
        return

class Voltage():
    def __init__(self,portA,value):
        self.portA = portA
        #self.portB = portB
        self.value = value

        portA.ports.append(self)
        #portB.ports.append(self)
    
        
class Out():
    def __init__(self,portA):
        self.portA = portA
        self.value = "OUT" 
        portA.ports.append(self)
'''
G = Node()
N0 = Node()
N1 = Node()
N2 = Node()
N3 = Node()

R1 = Resistor(G,N1,2.0)
R2 = Resistor(N1,G,2)
R3 = Resistor(N1,N2,1)
R4 = Resistor(N0,N2,2)
R5 = Resistor(N2,N3,1)
R6 = Resistor(G,N3,2)

V1 = Voltage(N0,5)

O = Out(N3)
'''
def VD(circuit,r1,r2,portA,portB,node,debug = False):
    G = circuit[0]
    for a in portA.ports:
        if isinstance(a,Voltage):# or portA == G:
            for b in portB.ports:
                if isinstance(b,Voltage):# or portB== G:
                    total = r1.value+r2.value
                    volts = a.value*r1.value/total
                    volts += b.value*r2.value/total
                    if debug: print a.value,b.value,volts,r1.value,r2.value

                    portA.ports.remove(r1)
                    portB.ports.remove(r2)
                    node.ports.remove(r1)
                    node.ports.remove(r2)
                    
                    temp = Node(circuit)
                    Resistor(temp,node,(r1.value*r2.value)/(r1.value+r2.value))
                    Voltage(temp,volts)
                    return 1
    return 0

def Thevenin(circuit, debug = False):
    
    G = circuit[0]
    x = 1;
    while True:
        for z in circuit:
            if debug: print z
            for y in z.ports:
                if debug: print y,y.value
        if len(circuit) == 1:
            break
        if debug: print "Node:",x
        node = circuit[x]

        if len(node.ports) == 0:
            circuit.pop(x)
            if debug: print "NONE"
            continue

        if len(node.ports) == 1:
            if isinstance(node.ports[0],Voltage):
                if debug: print "POPPED"
                circuit.pop(x)
                #x = 0
                continue
        
        if len(node.ports) == 2:
            r1 = node.ports[0]
            r2 = node.ports[1]
            if isinstance(r1,Resistor) and isinstance(r2,Resistor):
                if r1.portA == node:
                    portA = r1.portB
                else:
                    portA = r1.portA

                if r2.portA == node:
                    portB = r2.portB
                else:
                    portB = r2.portA

                if portA != portB:
                    if debug: print "SERIES"
                    portA.ports.remove(r1)
                    portB.ports.remove(r2)
                    temp = Resistor(portA,portB,r1.value+r2.value)
                    circuit.pop(x)
                    x = 1
                    continue
        
        for ia in range(0,len(node.ports)):
            for ib in range(ia+1,len(node.ports)):
                r1 = node.ports[ia]
                r2 = node.ports[ib]
                
                if isinstance(r1,Resistor) and isinstance(r2,Resistor):

                    if r1.portA == node:
                        portA = r1.portB
                    else:
                        portA = r1.portA

                    if r2.portA == node:
                        portB = r2.portB
                    else:
                        portB = r2.portA

                    if portA == portB: 
                        if debug: print "PARALLEL"
                        portA.ports.remove(r1)
                        portB.ports.remove(r2)
                        node.ports.remove(r1)
                        node.ports.remove(r2)
                        Resistor(portA,node,(r1.value*r2.value)/(r1.value+r2.value))
                        x = 0
                        break
                    else:
                        if VD(circuit,r1,r2,portA,portB,node,debug):
                            if debug: print "VD"
                            x = 0
                            break
                                            
        if x < len(circuit)-1:
            x = x + 1
            continue
        else:
            break


'''
Thevenin(Circuit)

for x in Circuit:
    for y in x.ports:
        print y, y.value
'''

class pdac():

    def __init__(self,bits,volts):
        self.bits = bits
        self.volts = volts
    def output(self,value):
        if value >= 2**self.bits or value < 0:
            raise Exception('Value out of bounds')
        
        output = 0
        p2 = 1
        for z in range(0,self.bits):
            if value & p2 > 0:
                output+=p2
            p2=p2*2
        output = float(output)
        return self.volts*output/(2**(bits))

class r2r():


    def v(self,value):
        value = self.distribution(value)
        value = float(value)
        return value
    
    def __init__(self,bits,volts,distribution):
        self.distribution = distribution
        self.bits = bits
        
        self.circuit = list()
        self.rcontrol = list()

        G = Node(self.circuit)
        VNode = Node(self.circuit)
        V = Voltage(VNode,volts)
        V = Voltage(G,0)

        self.G = G
        self.VNode = VNode

        temp = Node(self.circuit)
      
        p2 = 1
        
        r = 10000
        r2 = 20000

        self.rcontrol.append(Resistor(VNode,temp,self.v(r2)))
        Resistor(G,temp,self.v(r2))
        for x in range(0,bits-1):
            temp2 = Node(self.circuit)
            self.rcontrol.append(Resistor(G,temp2,self.v(r2)))
            Resistor(temp,temp2,self.v(r))
            temp = temp2
        self.O = Out(temp)

        self.table = list()
        for x in range(0,bits):
            self.table.append(self.slowoutput(2**x))

    def output(self,value):

        if value >= 2**self.bits or value < 0:
            raise Exception('Value out of bounds')
        
        output = 0
        p2 = 1
        for z in range(0,self.bits):
            if value & p2 > 0:
                output+=self.table[z]
            p2=p2*2
        return output
        
    def slowoutput(self,value):
        
        if value >= 2**self.bits or value < 0:
            raise Exception('Value out of bounds')
        p2 = 1
        
        for x in range(0,self.bits):
            if value & p2 > 0:
                if self.rcontrol[x].portA != self.VNode:
                    self.rcontrol[x].portA.ports.remove(self.rcontrol[x])
                    self.rcontrol[x].portA = self.VNode
                    self.VNode.ports.append(self.rcontrol[x])
            else:
                if self.rcontrol[x].portA != self.G:
                    self.rcontrol[x].portA.ports.remove(self.rcontrol[x])
                    self.rcontrol[x].portA = self.G
                    self.G.ports.append(self.rcontrol[x])
            p2 = p2*2

        circuit = copy.deepcopy(self.circuit)
        #THIS DEEP COPY >:(
        Thevenin(circuit)
        '''
        for x in circuit:
            print x
            for y in x.ports:
                print y, y.value
        '''
        if len(circuit) == 2:
            return 0
        else:
            return circuit[2].ports[1].value

        
def perfect(value):
    return value


def normal(value):
    tolerance = 0.005
    x = random.gauss(value,value*tolerance/3)
    return x

def worst(value):
    tolerance = 0.005
    x = random.choice((-1,1))
    x = value*(tolerance*x+1)
    return x

class correction():

    def __init__(self,dac,bits,volts):
        self.dac = dac
        self.bits = bits
        self.table = list()
        self.pdac = pdac(bits,volts)
        for x in range(0,bits):
            self.table.append(dac.output(2**x))

    def output(self,value):

        if value >= 2**self.bits or value < 0:
            raise Exception('Value out of bounds')
        
        ideal = self.pdac.output(value)

        output = 0
        for z in range(self.bits-1,-1,-1):
            if self.table[z] <= (ideal-output):
                output+=self.table[z]

        diff = math.fabs(output-ideal)
        diff2 = math.fabs(self.dac.output(value)-ideal)
        if diff2<diff:
            output = self.dac.output(value)
        
        return output
        

bits = 18
volts = 5
dac1 = pdac(bits,volts)
dac2 = r2r(bits,volts,worst)
dac3 = r2r(bits,volts,normal)
dac4 = correction(dac2,bits,volts)

LSB = (5.0/(2**bits))

for x in range(0,bits):
    y1 = dac1.output(2**x)
    y2 = dac2.output(2**x)
    y3 = dac4.output(2**x)

    d1 = (y2-y1)/LSB
    d2 = (y3-y1)/LSB
    if math.fabs(d2)<math.fabs(d1):
        print "IMPROVED",
    elif math.fabs(d2)>math.fabs(d1):
        print "WORSE   ",
    else:
        print "SAME    ",
    print d1 , d2

print 


for x in range(0,15):
    tdac = r2r(bits,5,worst)
    s1 = tdac.output(0)
    greatest = 0
    for x in range(1,2**bits):
        s2 = tdac.output(x)
        DNL = (s2-s1)/LSB
        if math.fabs(DNL) > greatest:
            greatest = math.fabs(DNL)
            #print x, greatest
        s1 = s2
    print greatest,
    
    tdac = correction(tdac,bits,5)
    s1 = tdac.output(0)
    greatest = 0
    for x in range(1,2**bits):
        s2 = tdac.output(x)
        DNL = (s2-s1)/LSB
        if math.fabs(DNL) > greatest:
            greatest = math.fabs(DNL)
            #print x, greatest
        s1 = s2
    print greatest

    
