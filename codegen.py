class Codegen():
    def __init__(self):
        self.ss = []
        self.break_s = []
        self.pb = []
        self.i = 0
        self.st = {}
        self.current_available_address = 508

    def code_gen(self, action, lexeme):
        if action == "#pid":
            if lexeme not in ["main", "output"]:
                addr = str(self.findaddr(lexeme))
                # print(lexeme, addr)
                self.ss.append(addr)
        elif action == "#assign_initial_var":
            self.add_and_increment_pb(generate_3address_code('ASSIGN', '#0', self.ss.pop()))

        elif action == "#pnum":
            # just put number in stack
            self.ss.append("#" + str(lexeme))
        elif action == "#assign":
            t1 = self.ss.pop()
            t2 = self.ss.pop()
            self.add_and_increment_pb(generate_3address_code('ASSIGN', t1, t2))
        elif action == "#psymbol":
            self.ss.append(lexeme)
        elif action == "#addsub":
            t1 = self.ss.pop()
            t2 = self.ss.pop()
            t3 = self.ss.pop()
            temp_addr = self.gettemp()
            if t2 == "+":
                self.add_and_increment_pb(generate_3address_code('ADD', t3, t1, temp_addr))
            else:
                self.add_and_increment_pb(generate_3address_code('SUB', t3, t1, temp_addr))
            self.ss.append(temp_addr)

        elif action == "#call_out":
            t1 = self.ss.pop()
            self.add_and_increment_pb(generate_3address_code('PRINT', t1))
        elif action == "#mult":
            t1 = self.ss.pop()
            t2 = self.ss.pop()
            temp_addr = self.gettemp()
            self.add_and_increment_pb(generate_3address_code('MULT', t1, t2, temp_addr))
            self.ss.append(temp_addr)
        elif action == "#array":
            t1 = self.ss.pop()
            size = int(lexeme)
            self.current_available_address += 4 * (size - 1)
            self.add_and_increment_pb(generate_3address_code('ASSIGN', "#0", t1))
        elif action == "#index":
            idx = self.ss.pop()
            offset = self.ss.pop()
            temp_addr = self.gettemp()
            self.add_and_increment_pb(generate_3address_code('MULT', idx, '#4', temp_addr))
            self.add_and_increment_pb(generate_3address_code('ADD', '#' + offset, temp_addr, temp_addr))
            self.ss.append("@" + temp_addr)
        elif action == "#LT" or action == "#EQ":
            self.ss.append(action[1:])
        elif action == "#cmp":
            second = self.ss.pop()
            op = self.ss.pop()
            first = self.ss.pop()
            temp_addr = self.gettemp()
            self.add_and_increment_pb(generate_3address_code(op, first, second, temp_addr))
            self.ss.append(temp_addr)
        elif action == "#label":
            self.ss.append(self.i)
        elif action == "#rep_jpf":
            cmp_res = self.ss.pop()
            dest = self.ss.pop()
            self.add_and_increment_pb(generate_3address_code('JPF', cmp_res, dest))
            if self.break_s:
                to_break = self.break_s.pop()
                self.pb[to_break] = generate_3address_code('JP', self.i)
        elif action == "#break":
            self.break_s.append(self.i)
            self.pb.append('')
            self.i += 1
        elif action == '#save':
            self.ss.append(self.i)
            self.pb.append('')
            self.i += 1
        elif action == '#jpf_save':
            pb_idx = self.ss.pop()
            jump_cnd = self.ss.pop()
            self.pb[int(pb_idx)] = generate_3address_code('JPF', jump_cnd, self.i + 1)
            self.ss.append(self.i)
            self.pb.append('')
            self.i += 1
        elif action == '#jp':
            pb_idx = self.ss.pop()
            self.pb[int(pb_idx)] = generate_3address_code('JP', str(self.i))
        else:
            print("ridiiiiiiii")

    def findaddr(self, inp):
        if inp not in self.st.keys():
            self.st[inp] = self.current_available_address
            self.current_available_address += 4
        return self.st[inp]

    def gettemp(self):
        addr = self.current_available_address
        self.current_available_address += 4
        return str(addr)

    def add_and_increment_pb(self, code):
        self.pb.append(code)
        self.i += 1


def generate_3address_code(op, operand1, operand2=' ', operand3=' '):
    return "(" + op + ", " + str(operand1) + ", " + str(operand2) + ", " + str(operand3) + " )"
