class Opcode:
    ADD = 1
    MUL = 2
    INP = 3
    OUT = 4
    JIT = 5
    JIF = 6
    LT = 7
    EQ = 8
    HALT = 99
    
class Mode:
    POS = 0
    IMM = 1

OP_FNS = {
    Opcode.LT: lambda a, b: 1 if a < b else 0,
    Opcode.EQ: lambda a, b: 1 if a == b else 0,
    Opcode.ADD: lambda a, b: a + b,
    Opcode.MUL: lambda a, b: a * b,
}

def parse(instr):
    """
    >>> parse(2)
    (2, 0, 0, 0)
    >>> parse(1002)
    (2, 0, 1, 0)
    >>> parse(11199)
    (99, 1, 1, 1)
    """
    instr = '{:05}'.format(instr)
    return (int(instr[3:]), int(instr[2]), int(instr[1]), int(instr[0]))

def read(mem, mode, loc):
    if mode == Mode.IMM:
        return loc
    else:
        return mem[loc]
    
async def execute_at(ip, memory, input, output):
    instr = memory[ip]
    op, m_a, m_b, m_dst = parse(instr)
    if op == Opcode.HALT:
        return -1
    elif op == Opcode.INP:
        dst = memory[ip+1]
        memory[dst] = await input()
        return ip + 2
    elif op == Opcode.OUT:
        src = memory[ip+1]
        output(read(memory, m_a, src))
        return ip + 2
    elif op == Opcode.JIT:
        src_a, src_b = memory[ip+1:ip+3]
        if read(memory, m_a, src_a) > 0:
            return read(memory, m_b, src_b)
        return ip + 3
    elif op == Opcode.JIF:
        src_a, src_b = memory[ip+1:ip+3]
        if read(memory, m_a, src_a) == 0:
            return read(memory, m_b, src_b)
        return ip + 3
    elif op in OP_FNS:
        op_fn = OP_FNS[op]
        src_a, src_b, dst = memory[ip+1:ip+4]
        memory[dst] = op_fn(read(memory, m_a, src_a), 
                            read(memory, m_b, src_b))
        return ip + 4
    else:
        raise Exception('Invalid opcode: {}'.format(op))
        
async def default_input():
    return int(input('I> '))

def default_output(o):
    print('O>', o)
    
async def execute(program, ip=0, input=default_input, output=default_output):
    """
    >>> execute([1,0,0,0,99])
    [2, 0, 0, 0, 99]
    >>> execute([1,1,1,4,99,5,6,0,99])
    [30, 1, 1, 4, 2, 5, 6, 0, 99]
    >>> execute([1002,4,3,4,33])
    [1002, 4, 3, 4, 99]
    """
    memory = program[:]
    while 0 <= ip < len(memory):
        ip = await execute_at(ip, memory, input, output)
    return memory, ip

def parse_program(program_txt):
    return [int(l) for l in program_txt.split(',')]
