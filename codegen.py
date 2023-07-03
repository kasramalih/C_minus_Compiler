class Codegen:
    def __init__(self):
        self.ss = []
        self.break_s = []
        self.pb = []
        self.i = 0
        self.st = {}
        self.current_available_address = 3000
        self.current_indirect_address = 500
        self.stack_pointer = '5000'
        self.add_and_increment_pb(generate_3address_code('ASSIGN', '#10000', self.stack_pointer))
        self.add_and_increment_pb(generate_3address_code('ASSIGN', '#0', '0'))
        self.semantic_errors = []
        self.scope = 0
        # scope, add, iadd, type, start of  func, return add, return val, no.arg, params
        self.st['output'] = [0, self.current_available_address - 8, self.current_indirect_address - 4, 'void', None,
                             None, None, 1, [['int', 504]]]
        self.st['main'] = [0, self.current_available_address - 16, self.current_indirect_address - 12, 'void', 0,
                           0, 0, 0, [['int', 504]]]
        self.iter_s = []
        self.fst = []
        self.globals_finish_i = 0
        self.globals_done = False

    def code_gen(self, action, lexeme, line_no):
        # TODO Test case 5: Add return action for voids.
        # TODO Test case 8: ?????
        # TODO Test case 12: ?????
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
            if self.ss:
                if self.ss[-1] == '#assign':
                    self.ss.pop()
                    self.ss.pop()
                elif isinstance(self.ss[-1], str) and self.ss[-1][0] == '#':
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
            if not self.globals_done:
                self.globals_done = True
                self.globals_finish_i = self.i
                self.pb.append('')
                self.i += 1
            function_lexeme_address = self.ss.pop()
            function_lexeme = self.ss.pop()
            if function_lexeme == "main":
                self.pb[self.globals_finish_i] = generate_3address_code('JP', str(self.i))
            return_type = self.ss.pop()
            no_args = 0
            if function_lexeme != 'main':
                return_address = self.gettemp()
                return_val = self.gettemp()
                self.fst.append((return_address, return_val))
                self.st[function_lexeme] = [self.scope, function_lexeme_address[1:], return_type, self.i,
                                            return_address,
                                            return_val, no_args, []]
            else:
                self.fst.append((0, 0))
            self.scope = 1
            self.ss.append(function_lexeme)

        elif action == '#scope_out':
            # print('----------------------------------')
            # for k, v in list(self.st.items()):
            #     print(k, '\t:\t', v)
            for k, v in list(self.st.items()):
                if v[0] == self.scope:
                    del self.st[k]
            self.scope = 0
            ra, rv = self.fst.pop()
            if self.ss[-1] != 'main':
                self.add_and_increment_pb(generate_3address_code('JP', '@' + str(ra)))
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
            # self.add_and_increment_pb(generate_3address_code('PRINT', '#5555555'))
            func_addr = self.ss.pop()
            func_name = ''
            top = self.ss[-1]
            top_1 = ''
            try:
                top_1 = self.ss[-2]
            except IndexError:
                pass
            for k in self.st.keys():
                if str(self.st[k][1]) == str(func_addr[1:]):
                    func_name = k
                    self.ss.append(k)
            self.ss.append(0)
            if func_name == 'output':
                return
            vars_cnt = 2
            t = str(self.gettemp())
            t_add = str(self.gettemp())
            self.add_and_increment_pb(generate_3address_code('ASSIGN', '#8', t))
            decrease_pointer = self.i
            self.add_and_increment_pb('')
            self.add_and_increment_pb('')
            t_temp = self.gettemp()
            self.add_and_increment_pb(generate_3address_code('ADD', '#4', self.stack_pointer, t_temp))
            t_temp_temp = self.gettemp()
            self.add_and_increment_pb(generate_3address_code('ASSIGN', '#0', t_temp_temp))
            self.add_and_increment_pb(
                generate_3address_code('ASSIGN', top_1 if top == '+' else t_temp_temp,
                                       '@' + t_temp))
            # self.add_and_increment_pb(generate_3address_code('PRINT', '#888888'))
            # self.add_and_increment_pb(generate_3address_code('PRINT', '#' + str(top_1 if top == '+' else t_temp_temp)))
            # self.add_and_increment_pb(generate_3address_code('PRINT', t_temp))
            # self.add_and_increment_pb(generate_3address_code('PRINT', '@' + t_temp))
            # self.add_and_increment_pb(generate_3address_code('PRINT', '#88888'))
            for k in self.st.keys():
                if self.st[k][0] == 1:
                    vars_cnt += 1
                    # self.add_and_increment_pb(generate_3address_code('PRINT', '#33333333'))
                    self.add_and_increment_pb(generate_3address_code('ADD', t, str(self.stack_pointer), t_add))
                    self.add_and_increment_pb(generate_3address_code('ASSIGN', '@' + str(self.st[k][1]), '@' + t_add))
                    # self.add_and_increment_pb(generate_3address_code('PRINT', str(self.st[k][1])))
                    # self.add_and_increment_pb(generate_3address_code('PRINT', '@' + t_add))
                    # self.add_and_increment_pb(generate_3address_code('PRINT', t_add))
                    self.add_and_increment_pb(generate_3address_code('ADD', '#4', t, t))
                    # self.add_and_increment_pb(generate_3address_code('PRINT', '#33333333'))
            self.pb[decrease_pointer] = generate_3address_code('MULT', '#4', '#' + str(vars_cnt), t_add)
            self.pb[decrease_pointer + 1] = generate_3address_code('SUB', str(self.stack_pointer), t_add,
                                                                   str(self.stack_pointer))
            # self.add_and_increment_pb(generate_3address_code('PRINT', '#5555555'))

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
                    self.add_and_increment_pb(
                        generate_3address_code('ASSIGN', '#' + str(self.st[func_name][-1][cnt - 1][2]),
                                               self.st[func_name][-1][cnt - 1][1][1:]))
                    self.add_and_increment_pb(generate_3address_code('ASSIGN', arg, self.st[func_name][-1][cnt - 1][1]))
            self.ss.append(cnt)
        elif action == "#check_count":
            total = self.ss.pop()
            func_name = self.ss.pop()
            if func_name == 'output':
                return
            # scope, add, type, start of  func, return add, return val, no.arg, params

            # assign return address
            # self.add_and_increment_pb(generate_3address_code('PRINT', '#444444444'))
            self.add_and_increment_pb(
                generate_3address_code('ASSIGN', self.fst[-1][0], '@' + str(self.stack_pointer)))
            self.add_and_increment_pb(generate_3address_code('ASSIGN', '#' + str(self.i + 2), self.st[func_name][-4]))
            # self.add_and_increment_pb(generate_3address_code('PRINT', '#444444444'))
            # self.add_and_increment_pb(generate_3address_code('PRINT', self.st[func_name][-4]))
            # self.add_and_increment_pb(generate_3address_code('PRINT', '@' + str(self.stack_pointer)))
            # self.add_and_increment_pb(generate_3address_code('PRINT', str(self.stack_pointer)))
            # self.add_and_increment_pb(generate_3address_code('PRINT', '#444444444'))

            # jump to start of function
            self.add_and_increment_pb(generate_3address_code('JP', self.st[func_name][3]))
            if self.st[func_name][2] == 'int':
                t_return = str(self.gettemp())
                self.add_and_increment_pb(generate_3address_code('ASSIGN', self.st[func_name][-3], t_return))
                self.ss.append(t_return)
                # self.add_and_increment_pb(generate_3address_code('PRINT', '#999999'))
                # self.add_and_increment_pb(generate_3address_code('PRINT', '#' + str(self.st[func_name][-3])))
                # self.add_and_increment_pb(generate_3address_code('PRINT', t_return))
            self.retrieve_values()
        elif action == "#pop_return":
            val = self.ss.pop()
            ra, rv = self.fst[-1]
            self.add_and_increment_pb(generate_3address_code('ASSIGN', val, rv))
            self.add_and_increment_pb(generate_3address_code('JP', '@' + str(ra)))
        elif action == '#return':
            ra, rv = self.fst[-1]
            self.add_and_increment_pb(generate_3address_code('JP', '@' + str(ra)))

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

    def retrieve_values(self):
        t = self.gettemp()
        t_add = self.gettemp()
        vars_cnt = 2
        # self.add_and_increment_pb(generate_3address_code('PRINT', '#1111111'))
        self.add_and_increment_pb(
            generate_3address_code('ASSIGN', '@' + str(self.stack_pointer), str(self.fst[-1][0])))
        # self.add_and_increment_pb(generate_3address_code('PRINT', str(self.stack_pointer)))
        # self.add_and_increment_pb(generate_3address_code('PRINT', '@' + str(self.stack_pointer)))
        # self.add_and_increment_pb(generate_3address_code('PRINT', '#' + str(self.fst[-1][0])))
        # self.add_and_increment_pb(generate_3address_code('PRINT', '#2222222'))
        t_temp = self.gettemp()
        self.add_and_increment_pb(generate_3address_code('ADD', '#4', self.stack_pointer, t_temp))
        tttttt = self.gettemp()
        self.add_and_increment_pb(
            generate_3address_code('ASSIGN', '@' + t_temp,
                                   str(self.ss[-3]) if isinstance(self.ss[-1], int) or self.ss[-1].isnumeric() and
                                                       self.ss[-2] == '+' else tttttt))
        # self.add_and_increment_pb(generate_3address_code('PRINT', '#77777'))
        # self.add_and_increment_pb(generate_3address_code('PRINT',
        #                                                  '#' + self.ss[-3] if self.ss[-1].isnumeric() and self.ss[
        #                                                      -2] == '+' else '#' + str(tttttt)))
        # self.add_and_increment_pb(
        #     generate_3address_code('PRINT', self.ss[-3] if self.ss[-1].isnumeric() and self.ss[-2] == '+' else tttttt))
        # self.add_and_increment_pb(generate_3address_code('PRINT', t_temp))
        # self.add_and_increment_pb(generate_3address_code('PRINT', '#77777'))

        self.add_and_increment_pb(generate_3address_code('ASSIGN', '#8', t))
        for k in self.st.keys():
            if self.st[k][0] == 1:
                vars_cnt += 1
                self.add_and_increment_pb(generate_3address_code('ADD', t, str(self.stack_pointer), t_add))
                self.add_and_increment_pb(generate_3address_code('ASSIGN', '@' + t_add, '@' + str(self.st[k][1])))
                # self.add_and_increment_pb(generate_3address_code('PRINT', t_add))
                # self.add_and_increment_pb(generate_3address_code('PRINT', '@' + t_add))
                # self.add_and_increment_pb(generate_3address_code('PRINT', '@' + str(self.st[k][1])))
                # self.add_and_increment_pb(generate_3address_code('PRINT', str(self.st[k][1])))
                # self.add_and_increment_pb(generate_3address_code('PRINT', '#222222222'))
                self.add_and_increment_pb(generate_3address_code('ADD', '#4', t, t))
        self.add_and_increment_pb(generate_3address_code('MULT', '#4', '#' + str(vars_cnt), t))
        self.add_and_increment_pb(generate_3address_code('ADD', str(self.stack_pointer), t,
                                                         str(self.stack_pointer)))
        # self.add_and_increment_pb(generate_3address_code('PRINT', '#1111111111'))


def generate_3address_code(op, operand1, operand2=' ', operand3=' '):
    return "(" + op + ", " + str(operand1) + ", " + str(operand2) + ", " + str(operand3) + " )"
