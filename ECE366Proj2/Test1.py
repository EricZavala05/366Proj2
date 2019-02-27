import numpy as np
import array as ar


def hexdecode(char):
    return {
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
    c=0
    for term in hexterms:
    #select only the last 8 characters in each line
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
        #instruction count [total, r, i, j]
        self.count = [0]*6
      
    def execute(self):
        bottom = len(self.code.tolist())
        while self.pc < bottom :
            command= self.code[self.pc]
            types = command>>26
            if command == 268500991:
                self.count[0]+=1
                self.count[3]+=1
                break
            elif types==0:
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
            self.count[0]+=1
        self.result()

    def rshift(self, val, n): return val>>n if val >= 0 else (val+0x100000000)>> n
    
    def rtype(self,command):
        self.count[1]+=1
        #extract values from command
        rs = 0x1f & (command >> 21)
        rt = 0x1f & (command >> 16)
        rd = 0x1f & (command >> 11)
        sh = 0x1f & (command >> 6)
        func = 0x3f & command 
        if func == 0x00:#sll
            self.reg[rd] = self.reg[rt] << sh
        elif func == 0x02:#srl
            self.reg[rd] = self.rshift(self.reg[rt], sh)
        elif func == 0x03:#sra
            self.reg[rd] = self.reg[rt] >> sh
        elif func == 0x20:#add
            self.reg[rd]=self.reg[rs]+self.reg[rt]
	    #todo error handling
        elif func == 0x21:#addu
            self.reg[rd]=self.reg[rs]+self.reg[rt]
            self.count[1]-=1
            self.count[5]+=1
        elif func == 0x22:#sub
            self.reg[rd]=self.reg[rs]-self.reg[rt]
        elif func == 0x23:#subu
            self.reg[rd]=self.reg[rs]-self.reg[rt]
            self.count[1]-=1
            self.count[5]+=1
        elif func == 0x24:#and
            self.reg[rd]=self.reg[rs]&self.reg[rt]
        elif func == 0x25:#or
            self.reg[rd]=self.reg[rs]|self.reg[rt]
        elif func == 0x26:#xor
            self.reg[rd]=self.reg[rs]^self.reg[rt]
        elif func == 0x27:#nor
            self.reg[rd]= ~(self.reg[rs]|self.reg[rt])
        elif func == 0x2a:#slt
            self.count[1]-=1
            self.count[5]+=1
            if self.reg[rs] < self.reg[rt]:
                self.reg[rd] = 1
            else:
                self.reg[rd] = 0
        elif func == 0x2b:#sltu
            self.count[1]-=1
            self.count[5]+=1
            if self.reg[rs] < self.reg[rt]:
                self.reg[rd] = 1
            else:
                self.reg[rd] = 0
        
    def itype(self,command):
        #extract values from command
        opcode= 0x3f & (command >> 26)
        rs = 0x1f & (command >> 21)
        rt = 0x1f & (command >> 16)
        imm = np.int16(0xffff & command)    #check this 
        if opcode == 4:#beq
            if self.reg[rs] == self.reg[rt]:
                self.pc += imm
                self.count[3] += 1
        if opcode == 5:#bne 
            if self.reg[rs] != self.reg[rt]:
                self.pc += imm
                self.count[3] += 1
        if opcode == 6: #andi
            imm = (0xffff & command)            #check this
            self.reg[rt] = self.reg[rs] & imm
            self.count[1] += 1
        if opcode == 0xd: #ori
            imm = (0xffff & command)            #check this
            self.reg[rt] = self.reg[rs] | imm
            self.count[1] += 1
        if opcode == 8:#addi 
            self.reg[rt]= self.reg[rs] + imm
            self.count[1] += 1
        if opcode == 0xf:#addi 
            self.reg[rt]= imm << 16
            self.count[1] += 1
        if opcode ==0x2b:#sw
            self.mem[(self.reg[rs]+imm-self.offset)>>2] = self.reg[rt]
            self.count[4] += 1
        if opcode ==0x23:#lw
             self.reg[rt] = self.mem[(self.reg[rs]+imm-self.offset)>>2]
             self.count[4] += 1

    def jtype(self,command):
        self.count[2]+=1
        #extract values from command
        addr = 0x3ffffff & (command >> 21)
        opcode = 0x3f & (command >> 26) 
        if opcode == 2:
            self.pc = (((self.pc<<2)&0xf0000000)| addr<<2) >> 2

    def result(self):
        print('Registers:')
        i = 0
        for thing in self.reg:
            print(str(i) + ': ' + str(hex(thing & 0xffffffff)))
            i += 1
        c=0
        self.pc *= 4
        print('PC: ' + str(self.pc))
        print('Memory: Hex  Decimal')
        while c < 0x14:
            print(str(format(self.offset+(c*4),'0x'))+':  '+hex(self.mem[c]&0xffffffff)+'   '+str(self.mem[c]))
            c+=1
        print('Total instructions run: '+str(self.count[0]))
        print('ALU instructions: '+str(self.count[1]))
        print('Jump Instructions: '+str(self.count[2]))
        print('Branch Instructions: '+str(self.count[3]))
        print('Memory Instructions: '+str(self.count[4]))
        print('Other Instructions: '+str(self.count[5]))
        
#end mipsMachine class
infile = open("in.txt", 'r')
mipshex = infile.read()
binary = hextobin(mipshex)
outfile = open('out.txt','w')
#to check my work
for instruction in binary:
    outfile.write(format(instruction, '032b')+'\n')
outfile.close()

order66 = mipsMachine(binary)

order66.execute()
