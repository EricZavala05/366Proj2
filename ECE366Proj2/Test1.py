import numpy as np
import array as ar


def hexdecode(char):
    return{
        '0':0,
        '1':1,
        '2':2,
        '3':3,
        '4':4,
        '5':5,
        '6':6,
        '7':7,
        '8':8,
        '9':9,
        'a':10,
        'b':11,
        'c':12,
        'd':13,
        'e':14,
        'f':15,
        }[char]

def hextobin(hexitem):
    binary =ar.array('I',[0])
    hexterms = hexitem.split('\n')
    #print(hexterms)
    c=0
    for term in hexterms:
        hexterms[c] = term[-8:]
        c+=1  
    k=0
    for term in hexterms:
        c = 0
        for char in term:
            num = hexdecode(char)
            binary[k] += num * 16**(7-c)
            c+=1
        binary.append(0)
        k+=1    
    if binary[k]==0:
        binary.pop()
    return binary



class mipsMachine:
    def __init__(self, arra):
        self.reg = np.int32([0]*32)
        self.mem = np.int32([0]*0x4c)
        self.code = arra
        self.pc = 0
        self.offset = 0x2000
      
    def execute(self):
        bottom = len(self.code.tolist())
        while self.pc < bottom :
            command= self.code[self.pc]
            types = command>>26
            if types==0:
                #r-type
                self.rtype(command)
            elif types > 3:
                #i-type
                self.itype(command)
            else:
                self.jtype(command)
                #j-type
            self.pc += 1
            self.reg[0] = 0 #reg0 is always 0
        print('fell off bottom')
    def rtype(self,command):
        #extract values from command
        rs = 0x1f & (command >> 21)
        rt = 0x1f & (command >> 16)
        rd = 0x1f & (command >> 11)
        opcode = 0x3f & command 
##        print("execute r-type")
##        print(format(command,'032b'))
##        print(rs)
##        print(rt)
##        print(rd)
        if opcode == 0x20:#add
            self.reg[rd]=self.reg[rs]+self.reg[rt]
	    #todo error handling
        elif opcode == 0x21:#addu
            self.reg[rd]=self.reg[rs]+self.reg[rt]
        elif opcode == 0x22:#sub
            self.reg[rd]=self.reg[rs]-self.reg[rt]
            #error handling?
        elif opcode == 0x23:#subu
            self.reg[rd]=self.reg[rs]-self.reg[rt]
        elif opcode == 0x24:#and
            self.reg[rd]=self.reg[rs]&self.reg[rt]
        elif opcode == 0x25:#or
            self.reg[rd]=self.reg[rs]|self.reg[rt]
        elif opcode == 0x26:#xor
            self.reg[rd]=self.reg[rs]^self.reg[rt]
        elif opcode == 0x27:#nor
            self.reg[rd]= ~(self.reg[rs]|self.reg[rt])
        elif opcode == 0x2a:#slt
            if self.reg[rs] < self.reg[rt]:
                self.reg[rd] = 1
            else:
                self.reg[rd] = 0
        elif opcode == 0x2b:#sltu
            if self.reg[rs] < self.reg[rt]:
                self.reg[rd] = 1
            else:
                self.reg[rd] = 0

    def itype(self,command):
        #extract values from command
        opcode= 0x3f & (command >> 26)
        rs = 0x1f & (command >> 21)
        rt = 0x1f & (command >> 16)
        imm = np.int16(0xffff & command)
        #debug, yay!
##        print("execute i-type")
##        print(format(command,'032b'))
##        print('rs: '+str(rs)+' is 0x' +str(format(self.reg[rs],'08x')))
##        print('rt: '+str(rt)+' is ' +str(self.reg[rt]))
##        print(imm)
        if opcode == 4:#beq
            if self.reg[rs] == self.reg[rt]:
                self.pc += imm
        if opcode == 5:#bne
            if self.reg[rs] != self.reg[rt]:
                self.pc += imm
        if opcode == 8:#addi
            self.reg[rt]= self.reg[rs] + imm
        if opcode ==0x2b:#sw
            self.mem[(self.reg[rs]+imm-self.offset)>>2] = self.reg[rt]

    def jtype(self,command):
        #extract values from command
        addr = 0x3ffffff & (command >> 21)
        opcode = 0x3f & (command >> 26) 
##        print("execute j-type todo: check for weird opcodes")
##        print(format(command,'032b'))
        if opcode == 2:
            self.pc = (((self.pc<<2)&0xf0000000)| addr<<2) >> 2

    def result(self):
        print('Registers:')
        for thing in self.reg:
            print('0x'+str(format(thing,'0x')))
        c=0
        print('Memory:')
        while c < 0x14:
            print(str(format(self.offset+(c*4),'0x'))+':  '+str(self.mem[c]))
            c+=1

    
#end mipsMachine class
infile = open("in.txt", 'r')
mipshex = infile.read()
binary = hextobin(mipshex)
outfile = open('out.txt','w')
#to check my work
##for instruction in binary:
##    outfile.write(format(instruction, '032b')+'\n')
##outfile.close()
##print('doesn\'t crash 0')

order66 = mipsMachine(binary)
#execute order 66.
order66.execute()

order66.result()


