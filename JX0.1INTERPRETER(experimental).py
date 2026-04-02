# ==========================================
# JX0.1 Interpreter (Case-Insensitive)
# Sem input.detect
# ==========================================
# Autor: João Manoel Martins Silveira
# Base: JX v0.1 - Comandos e Funções
# ==========================================

import time
import threading
import queue

# ==================== GLOBALS ====================
variables = {}
loops = {}
stop_flags = {}
_input = ""
input_queue = []
current_loop_id = None
running = True
command_history = []

# ==================== HELPERS ====================
def normalize_command(line):
    """
    Normaliza qualquer comando para case-insensitive
    """
    replacements = {
        'console.display': 'Console.display',
        'console.input': 'Console.input',
        'console.clear': 'Console.clear',
        'console.back.backspace': 'Console.back.backspace',
        'console.back.enter': 'Console.back.enter',
        'transform.int': 'transform.int',
        'transform.sel': 'transform.sel',
        'wait.frame': 'Wait.frame',
        'wait': 'Wait',
        'stop': 'stop',
        'loop': 'Loop',
        'if': 'If',
        'replace': 'Replace'
    }
    line_lower = line.lower()
    for key in replacements:
        if key in line_lower:
            line_lower = line_lower.replace(key, replacements[key])
    return line_lower

def parse_value(val):
    """
    Converte valor para tipo interno
    """
    if isinstance(val, str):
        val = val.strip()
        if val.isdigit():
            return int(val)
        elif val.lower() == 'true':
            return True
        elif val.lower() == 'false':
            return False
        else:
            return val.strip('"')
    return val

# ==================== CONSOLE ====================
class Console:
    @staticmethod
    def display(valor):
        global command_history
        valor = parse_value(valor)
        print(valor)
        command_history.append(f'Última entrada: {valor}')
        return valor

    @staticmethod
    def input(texto):
        global _input
        texto = parse_value(texto)
        _input = input(str(texto))
        return _input

    @staticmethod
    def clear():
        print("\033[H\033[J", end='')  # Clear terminal

    class back:
        @staticmethod
        def backspace():
            print('\b \b', end='')

        @staticmethod
        def enter():
            print('\r', end='')

# ==================== TRANSFORM ====================
class transform:
    @staticmethod
    def int(expr):
        try:
            return int(float(expr))
        except:
            return 0

    @staticmethod
    def sel(max_val):
        def inner(expr):
            val = parse_value(expr)
            return min(val, max_val)
        return inner

# ==================== WAIT ====================
class Wait:
    @staticmethod
    def frame(frames):
        # Simula pausar por frames (~1 frame = 1/60s)
        time.sleep(frames / 60.0)

    @staticmethod
    def __call__(seconds):
        time.sleep(float(seconds))

# ==================== REPLACE ====================
def Replace(var):
    class Replacer:
        def to(self, value):
            variables[var] = parse_value(value)
    return Replacer()

# ==================== STOP ====================
def stop(var=None):
    global stop_flags
    if var:
        stop_flags[var] = True
    else:
        global running
        running = False

# ==================== IF ====================
def If(cond):
    class Then:
        def then(self, block):
            try:
                result = eval(cond, {}, variables)
                if result:
                    execute_block(block)
            except Exception as e:
                print(f"Erro no If: {e}")
    return Then()

# ==================== LOOP ====================
def Loop(block, loop_id=None):
    global current_loop_id
    if not loop_id:
        loop_id = f'loop_{len(loops)+1}'
    loops[loop_id] = True
    while loops[loop_id] and running:
        current_loop_id = loop_id
        execute_block(block)
        if stop_flags.get(loop_id):
            loops[loop_id] = False
            stop_flags[loop_id] = False

# ==================== EXECUTE BLOCK ====================
def execute_block(block):
    """
    Executa um bloco de comandos JX
    """
    lines = block.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        line = normalize_command(line)
        try:
            if line.startswith('Console.display'):
                content = line[line.find('(')+1:line.rfind(')')]
                Console.display(content)
            elif line.startswith('Console.input'):
                content = line[line.find('(')+1:line.rfind(')')]
                Console.input(content)
            elif line.startswith('Console.clear'):
                Console.clear()
            elif line.startswith('Console.back.backspace'):
                Console.back.backspace()
            elif line.startswith('Console.back.enter'):
                Console.back.enter()
            elif line.startswith('transform.int'):
                content = line[line.find('(')+1:line.rfind(')')]
                transform.int(content)
            elif line.startswith('transform.sel'):
                idx1 = line.find('(')
                idx2 = line.find(')')
                max_val = int(line[idx1+1:idx2])
                expr = line[line.rfind('(')+1:line.rfind(')')]
                transform.sel(max_val)(expr)
            elif line.startswith('Wait.frame'):
                frames = int(line[line.find('(')+1:line.rfind(')')])
                Wait.frame(frames)
            elif line.startswith('Wait'):
                seconds = float(line[line.find('(')+1:line.rfind(')')])
                Wait(seconds)
            elif line.startswith('Replace'):
                idx1 = line.find('(')
                idx2 = line.find(')')
                var = line[idx1+1:idx2]
                value = line.split('to')[-1].strip().strip('"')
                Replace(var).to(value)
            elif line.startswith('stop'):
                stop()
            elif line.startswith('Loop'):
                idx1 = line.find('{')
                idx2 = line.rfind('}')
                block_content = line[idx1+1:idx2]
                Loop(block_content)
            elif line.startswith('If'):
                idx_then = line.find('then')
                cond = line[3:idx_then].strip()
                block_content = line[line.find('{')+1:line.rfind('}')]
                If(cond).then(block_content)
            else:
                # Avalia expressões simples
                eval(line, {}, variables)
        except Exception as e:
            print(f"Erro: {e}")

# ==================== MAIN LOOP ====================
def JX_main_loop():
    print("=== JX0.1 Interpreter Rodando (sem input.detect) ===")
    while running:
        try:
            cmd = input("JX> ").strip()
            command_history.append(cmd)
            execute_block(cmd)
        except KeyboardInterrupt:
            print("\nSaindo do JX...")
            break
        except Exception as e:
            print(f"Erro: {e}")

# ==================== START INTERPRETER ====================
if __name__ == "__main__":
    JX_main_loop()
