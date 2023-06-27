class Codegen():
    def __init__(self):
        self.ss = []
        self.pb = {}
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
            self.pb[self.i] = "(ASSIGN, #0, " + str(self.ss.pop()) + ",\t)"
            # print(self.pb[self.i])
            self.i += 1

        elif action == "#pnum":
            # just put number in stack
            self.ss.append("#" + str(lexeme))
        elif action == "#assign":
            t1 = str(self.ss.pop())
            t2 = str(self.ss.pop())
            self.pb[self.i] = "(ASSIGN, " + t1 + ", " + t2 + ",\t)"
            # print(self.pb[self.i])
            self.i += 1
        elif action == "#psymbol":
            self.ss.append(lexeme)
        elif action == "#addsub":
            t1 = self.ss.pop()
            t2 = self.ss.pop()
            t3 = self.ss.pop()
            temp_addr = str(self.gettemp())
            if t2 == "+":
                self.pb[self.i] = "(ADD, " + t3 + ", " + t1 + ", " + temp_addr + " )"
            else:
                self.pb[self.i] = "(SUB, " + t3 + ", " + t1 + ", " + temp_addr + " )"
            self.ss.append(temp_addr)
            # print(self.pb[self.i])
            self.i += 1

        elif action == "#call_out":
            t1 = self.ss.pop()
            self.pb[self.i] = "(PRINT, " + t1 + ",\t,\t)"
            # print(self.pb[self.i])
            self.i += 1

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
        return addr
