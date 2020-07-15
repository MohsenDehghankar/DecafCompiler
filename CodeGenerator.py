from lark import Transformer


class CodeGenerator(Transformer):

    tmp_var_id_read = 1000

    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)
        self.mips_code = ""
        # stores (var_name, var_obj)
        self.symbol_table = {}
        # last declared type
        self.type_tmp = None
        # needed for multiple assignments in one line: x = y = z
        self.lvalue_stack = []
        # $t registers. $t[i] is being used <==> self.t_regsiters[i] = True
        self.t_registers = [False for i in range(10)]
        # last local variable
        self.last_var_in_fp = None

    def write_code(self, code_line):
        self.mips_code = self.mips_code + "\n" + code_line

    '''
    Initialization
    '''
    def create_data_segment(self):
        self.write_code("""
        .data
        frame_pointer:  .space  1000

        .text
        main:
        """)


    '''
    Variable declaration
    '''
    def variable_declare(self, args):
        variable_name = args[0].children[1].value
        
        if variable_name in self.symbol_table.keys():
            print("Variable with name {} already exists".format(variable_name))
            exit(4)
        
        # debug
        print("Variable Declared type {0}, name {1}".format(self.type_tmp, variable_name))

        if self.type_tmp == None:
            print("Type of Variable {} unknown".format(variable_name))
            exit(4)

        self.create_variable(self.type_tmp, variable_name)
        self.type_tmp = None
        return args

    def create_variable(self, var_type, var_name):
        # dynamic allocation
        variable = Variable()
        variable.type = var_type
        variable.name = var_name
        variable.calc_size()
        if self.last_var_in_fp == None:
            variable.address_offset = 0
        else:
            offset = self.last_var_in_fp.address_offset + self.last_var_in_fp.size
            # memory alignment
            variable.address_offset = offset if offset % variable.size == 0 else offset + (variable.size - variable.size % offset)
        self.last_var_in_fp = variable
        if variable.address_offset + variable.size > 1000:
            print("Local Variables are more than frame size!")
            exit(4)
        self.symbol_table[var_name] = variable
        return variable


    '''
    Getting the type of declared variable
    '''

    def int_variable_declaraion(self, args):
        self.type_tmp = "int"
        return args

    def double_variable_declaration(self, args):
        self.type_tmp = "double"
        return args

    def bool_variable_declaration(self, args):
        self.type_tmp = "bool"
        return args

    def string_variable_declaration(self, args):
        self.type_tmp = "string"
        return args


    '''
    Read from console
    '''
    def read_line(self, args):
        print("[readLine]")
        var = self.create_variable("string", "readline" + str(CodeGenerator.tmp_var_id_read))
        CodeGenerator.tmp_var_id_read += 1
        t = self.get_a_free_t_register()
        if t:
            self.t_registers[t] = True # is being used
            self.write_code("""
            
            """)
        else:
            print("All Registers Are Full!")
            exit(4)
        return args

    def get_a_free_t_register(self):
        for i in range(10):
            if not self.t_registers[i]:
                return i
        print("Not Enough Regsiter to Use!")
        exit(4)

    def assignment_calculated(self, args):
        print("assignment calculated")
        print(args)
        return args


    def lvalue_calculated(self, args):
        print("lvalue calculated")
        self.lvalue_stack.append(args[0])
        return args

    def identifier_in_expression(self, args):
        print("ident: {0}".format(args[0].value))
        return args

    '''
    Test Part
    '''

    # def print(self, args):
    #     variable_name = (args[0].children[0].children[0].children[0].children[0].children[0].children[0]
    #                      .children[0].children[0].children[0].children[0].children[0].children[0].children[0].value)
        
    #     variable = self.symbol_table.get(variable_name)

    #     if variable.type == "int":
    #         self.write_code("""
    #             li $v0, 1
    #             move $a0, {0}
    #             syscall     
    #         """.format(variable.register_name))

    #     return args


class Variable:
    def __init__(self):
        super().__init__()
        self.name = None
        self.type = None
        self.value = None
        self.address_offset = None   # address from the start of frame pointer
        self.size = None # in bytes

    def calc_size(self):
        if self.type == "int":
            self.size = 4
        if self.type == "bool":
            self.size = 1
        if self.type == "string":
            self.size = 4   # address of string
        if self.type == "double":
            self.size = 8
        # var type is an object

    # def generate_declaration_code(self):
    #     if self.type == "int":
    #         return "{0}: .word   0".format(self.name)
    #     if self.type == "bool":
    #         return "{0}: .byte   0".format(self.name)
    #     if self.type == "string":
    #         return "{0}: .asciiz \"\"".format(self.name)
    #     if self.type == "double":
    #         return "{0}: .double 0".format(self.name)
    #     # var type is an object

class Array(Variable):
    def __init__(self):
        super().__init__()
