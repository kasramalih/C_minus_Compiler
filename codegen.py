class Codegen:
    def __init__(self):
        self.ss = []
        self.break_s = []
        self.pb = []
        self.pb.append('')
        self.i = 1
        self.st = {}
        self.current_available_address = 3000
        self.current_indirect_address = 500
        self.semantic_errors = []
        self.scope = 0
        # scope, add, iadd, type, start of  func, return add, return val, no.arg, params
        self.st['output'] = [0, self.current_available_address - 8, self.current_indirect_address - 4, 'void', None,
                             None, None, 1, [['int', 504]]]
        self.iter_s = []
        self.fst = []

    def code_gen(self, action, lexeme, line_no):
        """
        phase 4:
        1-  Jump to main function on beginning of program - done
        2-  update all 3address codes to indirect memory addressing - done
        3-  on function invocation:
            a. In caller, save arguments into function params - done
            b. In caller, save return address(unique for each function) - done
            d. optional: In caller, save all symbols plus return address of previous environment to stack
            (this is different from SS since it should appear in the final code)
        4- on function return:
            a. In callee, load return address
            b. In callee, load return value(and probably push it into stack)
            c. In callee, jump indirectly to return address
            d. optional: In caller, load all symbols from stack
        """
        if action == "#pid":
            addr, indirect_addr = self.findaddr(lexeme)
            self.ss.append('@' + addr)
        elif action == "#assign_initial_var":
            self.add_and_increment_pb(generate_3address_code('ASSIGN', '#0', self.ss.pop()))
        elif action == "#declare_pid":
            addr, indirect_addr = self.findaddr(lexeme)
            # assign #500, 3000
            self.add_and_increment_pb(generate_3address_code('ASSIGN', '#' + str(indirect_addr), addr))
            self.ss.append('@' + addr)
        elif action == "#assign_initial_var":
            self.add_and_increment_pb(generate_3address_code('ASSIGN', '#0', self.ss.pop()))
        elif action == "#pnum":
            # just put number in stack
            self.ss.append("#" + str(lexeme))
        elif action == "#assign":
            t1 = self.ss.pop()
            if t1 == '#assign':
                t1 = self.ss.pop()
            t2 = self.ss.pop()
            self.add_and_increment_pb(generate_3address_code('ASSIGN', t1, t2))
            self.ss.append(t2)
            self.ss.append('#assign')
        elif action == "#pop_assign":
            if self.ss and self.ss[-1] == '#assign':
                self.ss.pop()
                self.ss.pop()
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
        elif action == "#mult":
            t1 = self.ss.pop()
            t2 = self.ss.pop()
            temp_addr = self.gettemp()
            self.add_and_increment_pb(generate_3address_code('MULT', t1, t2, temp_addr))
            self.ss.append(temp_addr)
        elif action == "#array":
            t1 = self.ss.pop()
            size = int(lexeme)
            self.current_indirect_address += 4 * (size - 1)
            self.add_and_increment_pb(generate_3address_code('ASSIGN', "#0", t1))
        elif action == "#index":
            idx = self.ss.pop()
            offset = self.ss.pop()
            temp_addr = self.gettemp()
            self.add_and_increment_pb(generate_3address_code('MULT', idx, '#4', temp_addr))
            self.add_and_increment_pb(generate_3address_code('ADD', offset[1:], temp_addr, temp_addr))
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
            self.iter_s.append(1)
            self.ss.append(self.i)
        elif action == "#rep_jpf":
            cmp_res = self.ss.pop()
            dest = self.ss.pop()
            self.add_and_increment_pb(generate_3address_code('JPF', cmp_res, dest))
            if self.break_s:
                to_break = self.break_s.pop()
                self.pb[to_break] = generate_3address_code('JP', self.i)
            self.iter_s.pop()
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
            self.ss.pop()
            self.ss.pop()
        elif action == '#scope_in':
            function_lexeme_address = self.ss.pop()
            function_lexeme = self.ss.pop()
            if function_lexeme == "main":
                self.pb[0] = generate_3address_code('JP', str(self.i))
            return_type = self.ss.pop()
            no_args = 0
            return_address = self.gettemp()
            return_val = self.gettemp()
            self.fst.append((return_address, return_val))
            self.st[function_lexeme] = [self.scope, function_lexeme_address[1:], return_type, self.i, return_address,
                                        return_val, no_args, []]
            self.scope = 1
            self.ss.append(function_lexeme)

        elif action == '#scope_out':
            print('----------------------------------')
            for k, v in list(self.st.items()):
                print(k, '\t:\t', v)
            for k, v in list(self.st.items()):
                if v[0] == self.scope:
                    del self.st[k]
            self.scope = 0
            self.fst.pop()

        elif action == '#param_first':
            address = self.ss.pop()
            function_lexeme = self.ss[-1]
            indir_address = None
            self.st[function_lexeme][-2] += 1
            for k in self.st.keys():
                if str(self.st[k][1]) == str(address[1:]):
                    indir_address = self.st[k][2]
            self.st[function_lexeme][-1].append(['int', address, str(indir_address)])
        elif action == '#param':
            param = self.ss.pop()
            param_lexeme = self.ss.pop()
            type = self.ss.pop()
            function_lexeme = self.ss[-1]
            indir_address = None
            self.st[function_lexeme][-2] += 1
            for k in self.st.keys():
                if str(self.st[k][1]) == str(param[1:]):
                    indir_address = self.st[k][2]
            self.st[function_lexeme][-2] += 1
            self.st[function_lexeme][-1].append([type, param, indir_address])
        elif action == '#arr_param':
            function_lexeme = self.ss[-1]
            self.st[function_lexeme][-1][-1][0] = 'array'
        elif action == '#init_arg_check':
            func_addr = self.ss.pop()
            for k in self.st.keys():
                if str(self.st[k][1]) == str(func_addr[1:]):
                    self.ss.append(k)
            self.ss.append(0)
        elif action == "#count_arg":
            arg = self.ss.pop()  # TODO do sth in next phase
            cnt = self.ss.pop()
            func_name = self.ss[-1]
            cnt += 1
            if func_name == 'output':
                self.add_and_increment_pb(generate_3address_code('PRINT', arg))
            else:
                if self.st[func_name][-1][cnt - 1][0] == 'array':
                    self.add_and_increment_pb(
                        generate_3address_code('ASSIGN', arg[1:], self.st[func_name][-1][cnt - 1][1][1:]))
                else:
                    self.add_and_increment_pb(generate_3address_code('ASSIGN', '#' + self.st[func_name][-1][cnt - 1][2],
                                                                     self.st[func_name][-1][cnt - 1][1]))
                    self.add_and_increment_pb(generate_3address_code('ASSIGN', arg, self.st[func_name][-1][cnt - 1][1]))
            self.ss.append(cnt)
        elif action == "#check_count":
            total = self.ss.pop()
            func_name = self.ss.pop()
            if func_name == 'output':
                return
            # scope, add, type, start of  func, return add, return val, no.arg, params

            # assign return address
            self.add_and_increment_pb(generate_3address_code('ASSIGN', str(self.i + 2), self.st[func_name][-4]))
            # jump to start of function
            self.add_and_increment_pb(generate_3address_code('JP', self.st[func_name][3]))
            if self.st[func_name][2] == 'int':
                self.ss.append(self.st[func_name][-3])
        elif action == "#pop_return":
            val = self.ss.pop()
            ra, rv = self.fst[-1]
            self.add_and_increment_pb(generate_3address_code('ASSIGN', val, rv))
            t = self.gettemp()
            self.add_and_increment_pb(generate_3address_code('ASSIGN', '#'+str(ra), t))
            self.add_and_increment_pb(generate_3address_code('JP', '@'+str(t)))
        else:
            print("ridiiiiiiii")

    def findaddr(self, inp):
        if inp not in self.st.keys():
            self.st[inp] = [self.scope, self.current_available_address, self.current_indirect_address]
            self.current_available_address += 4
            self.current_indirect_address += 4
        return str(self.st[inp][1]), str(self.st[inp][2])

    def gettemp(self):
        addr = self.current_available_address
        self.current_available_address += 4
        return str(addr)

    def add_and_increment_pb(self, code):
        self.pb.append(code)
        self.i += 1

    def type_checker(self, address_op1, address_op2, line_no):
        type_op1 = ''
        type_op2 = ''
        for k in self.st.keys():
            if str(self.st[k][1]) == str(address_op1):
                try:
                    type_op1 = self.st[k][3]
                except:
                    type_op1 = 'int'
            if str(self.st[k][1]) == str(address_op2):
                try:
                    type_op2 = self.st[k][3]
                except:
                    type_op2 = 'int'
        if type_op1 == 'array' or type_op2 == 'array':
            self.semantic_errors.append(
                f"#{line_no}: Semantic Error! Type mismatch in operands, Got array instead of int.")
        # 26: Semantic Error! Type mismatch in operands, Got array instead of int.


def generate_3address_code(op, operand1, operand2=' ', operand3=' '):
    return "(" + op + ", " + str(operand1) + ", " + str(operand2) + ", " + str(operand3) + " )"
