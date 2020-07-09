from lark import Transformer


class CodeGenerator(Transformer):

    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)
        self.mips_code = ""

        # stores (var_name, var_obj)
        self.symbol_table = {}

        self.type_tmp = None

    def write_code(self, code_line):
        self.mips_code = self.mips_code + "\n" + code_line

    def variable_declare(self, args):
        variable_name = args[0].children[1].value
        variable = Variable()
        if self.type_tmp == None:
            raise Exception()
        variable.type = self.type_tmp
        self.type_tmp = None
        self.symbol_table[variable_name] = variable

    def int_variable(self, args):
        self.type_tmp = "int"
        return args

    def print(self, args):
        variable_name = (args[0].children[0].children[0].children[0].children[0].children[0].children[0]
                         .children[0].children[0].children[0].children[0].children[0].children[0].children[0].value)
        
        variable = self.symbol_table.get(variable_name)

        if variable.type == "int":
            self.write_code("""
                li $v0, 1
                move $a0, {0}
                syscall     
            """.format(variable.register_name))


class Variable:
    def __init__(self):
        super().__init__()
        self.type = None
        self.value = None
        self.address = None
        self.register_name = None
