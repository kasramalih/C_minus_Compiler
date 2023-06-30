class Codegen:
    def __init__(self):
        self.func_name = ''
        self.ss = []
        self.break_s = []
        self.pb = ["(ASSIGN, #4, 0,   )", "(JP, 2,  ,   )"]
        self.i = 2
        self.st = {}
        self.current_available_address = 508
        self.semantic_errors = []
        self.scope = 0
        self.count_arg = 0
        self.arg_list = []

    def code_gen(self, action, lexeme, line_no):
        if action == "#pid":
            if lexeme != "output":
                addr = str(self.findaddr(lexeme))
                # print(lexeme, addr)
                self.ss.append(addr)
            elif lexeme == 'main':  # for illegal type error only
                self.ss.pop()
                self.ss.pop()
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
        elif action == '#void_check_type_save':
            self.ss.append(lexeme)
        elif action == '#void_check_name_save':
            self.ss.append(lexeme)
        elif action == '#void_check':
            id = self.ss.pop()
            type = self.ss.pop()
            if type == 'void':
                self.semantic_errors.append(f"#{line_no - 1}: Semantic Error! Illegal type of void for '{id}'.")
        elif action == '#defined_check':  # checks for definition of variables only
            if lexeme not in self.st.keys() and lexeme != 'output':
                self.semantic_errors.append(f"#{line_no}: Semantic Error! '{lexeme}' is not defined.")
            pass
        elif action == '#scope_in':
            function_lexeme_address = self.ss.pop()
            function_lexeme = self.ss.pop()
            return_type = self.ss.pop()
            no_args = 0
            self.st[function_lexeme] = [self.scope, function_lexeme_address, return_type, self.i, no_args, []]
            self.scope = 1
            self.ss.append(function_lexeme)
            """On this action:
                1- create pointer to a new symbol table for the function's scope
                2- set return type (already in stack, may need to remove the #ignore_void_check action) 
                in global symbol table
                3- set jump address in global symbol table
                4- change current symbol table to the new one
            """
        elif action == '#scope_out':
            print('ALL VARS IN SCOPE:\n-----------------------------')
            for k in self.st.keys():
                print(k, self.st[k])
            for k, v in list(self.st.items()):
                if v[0] == self.scope:
                    del self.st[k]
            self.scope = 0
            print("---------------------\n AFTER SCOPE:\n------------------------")
            for k in self.st.keys():
                print(k, self.st[k])
            print('-----------------------------')
            self.ss.pop()
            """On this action:
                1- change current symbol table to global
                2- set number of arguments in global symbol table
                (may need a new action for this after param declarations)
            """
        elif action == '#param_first':
            address = self.ss.pop()
            function_lexeme = self.ss[-1]
            self.st[function_lexeme][-2] += 1
            self.st[function_lexeme][-1].append(['int', address])
        elif action == '#param':
            param = self.ss.pop()
            param_lexeme = self.ss.pop()
            type = self.ss.pop()
            function_lexeme = self.ss[-1]
            self.st[function_lexeme][-2] += 1
            self.st[function_lexeme][-1].append([type, param])
            """On this action:
                1- added type, name, reg, index of param into symbol table
                2- update total number of params(can be handled in stack)
            """
        elif action == '#arr_param':
            function_lexeme = self.ss[-1]
            self.st[function_lexeme][-1][-1][0] = 'array'
            for k in self.st.keys():
                if str(self.st[k][1]) == str(self.st[function_lexeme][-1][-1][1]):
                    self.st[k].append('array')
            """On this action:
                1- added type, name, reg, index of param into symbol table
                2- update total number of arguments(can be handled in stack)
            """
        elif action == '#check_arg':
            # TODO
            """On this action:
                1- check for type match
                In next phase we also need to assign value to registers
            """
        elif action == 'check_invoke_out':
            # TODO
            """On this action:
                1- check total number of args
            """
        elif action == "#count_arg":
            self.arg_list.append(self.ss.pop())
            if self.count_arg == 0:
                func_addr = self.ss.pop()
                for k in self.st.keys():
                    if self.st[k][1] == func_addr:
                        self.func_name = k
            self.count_arg += 1

            print('------0-------', self.func_name, self.arg_list[self.count_arg - 1])
            arg_type = 'int'
            for k in self.st.keys():
                if str(self.st[k][1]) == str(self.arg_list[self.count_arg - 1]):
                    try:
                        arg_type = self.st[k][2]
                    except:
                        arg_type = 'int'

            if self.st[self.func_name][-1][self.count_arg - 1][0] != arg_type:
                self.semantic_errors.append(
                    f"#{line_no}: Semantic Error! Mismatch in type of argument '{self.count_arg}' of '{self.func_name}'. Expected '{self.st[self.func_name][-1][self.count_arg - 1][0]}' but got '{arg_type}' instead")
                # 16: Semantic Error! Mismatch in type of argument 1 of 'sum1array'. Expected 'array' but got 'int' instead.
        elif action == "#check_count":
            # need return address
            self.ss.append(self.gettemp())
            if self.count_arg != self.st[self.func_name][-2]:
                self.semantic_errors.append(
                    f"#{line_no}: Semantic Error!  Mismatch in numbers of arguments of '{self.func_name}'.")
            self.func_name = ''
            self.count_arg = 0
        else:
            print("ridiiiiiiii")

    def findaddr(self, inp):
        if inp not in self.st.keys():
            print('-----------------------------findaddr', inp, self.ss)
            self.st[inp] = [self.scope, self.current_available_address]
            self.current_available_address += 4
        return self.st[inp][1]

    def gettemp(self):
        addr = self.current_available_address
        self.current_available_address += 4
        return str(addr)

    def add_and_increment_pb(self, code):
        self.pb.append(code)
        self.i += 1


def generate_3address_code(op, operand1, operand2=' ', operand3=' '):
    return "(" + op + ", " + str(operand1) + ", " + str(operand2) + ", " + str(operand3) + " )"
