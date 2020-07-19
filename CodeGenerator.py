from lark import Transformer
from lark.lexer import Lexer, Token


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
        # for generating label names
        self.label_count = 0

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
        print("Variable Declared type {0}, name {1}".format(
            self.type_tmp, variable_name))

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
            variable.address_offset = offset if offset % variable.size == 0 else offset + \
                (variable.size - variable.size % offset)
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
        # print("[readLine]")
        # print(args)
        var = self.create_variable(
            "string", "readline" + str(CodeGenerator.tmp_var_id_read))
        CodeGenerator.tmp_var_id_read += 1
        t = self.get_a_free_t_register()
        self.write_code("""
li $v0, 9;
li $a0, 16384;
syscall
li $t{}, {};
sw $v0, frame_pointer($t{})
move $a0, $v0;
li $v0, 8
li $a1, 16384
syscall
        """.format(t, var.address_offset, t))
        # act as a new variable in rest of the tree
        return [Token('IDENT', var.name)]

    def get_a_free_t_register(self):
        for i in range(10):
            if not self.t_registers[i]:
                return i
        print("Not Enough Regsiter to Use!")
        exit(4)

    def assignment_calculated(self, args):
        # print("assignment calculated")
        # print(args)
        left_value = args[0]
        right_value = args[1]
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        if isinstance(right_value, Register):
            self.write_code("""
move $t{}, ${};
            """.format(t1, right_value.type + str(right_value.number)))
            if right_value.type == "t":
                self.t_registers[right_value.number] = False
        elif isinstance(right_value, Immediate):
            self.write_code("""
li $t{}, {};
            """.format(t1, right_value.value))
        else:
            self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(t1, right_value.address_offset, t1, t1))
        if isinstance(left_value, Register):
            self.write_code("""
move ${}, $t{};
            """.format(left_value.type + str(left_value.number), t1))
            if left_value.type == "t":
                self.t_registers[left_value.number] = False
        else:
            t2 = self.get_a_free_t_register()
            self.write_code("""
li $t{}, {};
sw $t{}, frame_pointer($t{});
            """.format(t2, left_value.address_offset, t1, t2))
        self.t_registers[t1] = False

        # return something for nested equalities
        return args[0] # after assignment, the left value will be returned for other assignment (nested)

    def lvalue_calculated(self, args):
        # print("lvalue calculated")
        # print(args)
        return args[0]

    def identifier_in_expression(self, args):
        # print("ident: {0}".format(args[0].value))
        return args[0]

    '''
    Expressions
    '''

    def token_to_var(self, args):
        # print("high prior: ")
        # print(args)
        try:
            child = args[0]
            if isinstance(child, Token) and child.type == 'IDENT':
                return self.symbol_table[child.value]
            elif isinstance(child, Immediate):
                return args[0]
            else:
                pass  # other expressions
        except Exception:
            print("Exception in token to var.")
            exit(4)
        return args

    def minus(self, args):
        # print("minus:")
        # print(args)
        var = args[0].children[0]
        if isinstance(var, Variable):
            if var.type == "int":
                t1 = self.get_a_free_t_register()
                self.t_registers[t1] = True
                t2 = self.get_a_free_t_register()
                self.write_code("""
li $t{}, -1;
li $t{}, {};
lw $t{}, frame_pointer($t{});
mult $t{}, $t{};
mflo $t{};
                """.format(t1, t2, var.address_offset, t2, t2, t1, t2, t1))
                return Register("t", t1)
            # other types
        elif isinstance(var, Immediate):
            var.value = -1 * var.value
            return var
        else:
            pass  # other expressions
        return args

    def multiply(self, args):
        # print("multiply")
        # print(args)
        try:
            opr1 = args[0]
            opr2 = args[1]
            t1 = self.get_a_free_t_register()
            self.t_registers[t1] = True
            t2 = self.get_a_free_t_register()
            if isinstance(opr1, Variable):
                if opr1.type == "int":
                    self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(t1, opr1.address_offset, t1, t1))
                else:
                    pass  # type checking
            elif isinstance(opr1, Immediate):
                self.write_code("""
li $t{}, {};
                """.format(t1, opr1.value))
            elif isinstance(opr1, Register):
                self.write_code("""
move $t{}, ${};
                """.format(t1, opr1.type + str(opr1.number)))
            else:
                pass  # other things
            if isinstance(opr2, Variable):
                if opr2.type == "int":
                    self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(t2, opr2.address_offset, t2, t2))
                else:
                    pass  # type checking
            elif isinstance(opr2, Immediate):
                self.write_code("""
li $t{}, {};
                """.format(t2, opr2.value))
            elif isinstance(opr2, Register):
                self.write_code("""
move $t{}, ${};
                """.format(t2, opr2.type + str(opr2.number)))
            else:
                pass  # other things

            self.write_code("""
mult $t{}, $t{};
mflo $t{};
            """.format(t1, t2, t1))
            return Register("t", t1)
        except Exception:
            print("Error in multiply")
            exit(4)
        return args

    def divide(self, args):
        # print("divide")
        # print(args)
        try:
            opr1 = args[0]
            opr2 = args[1]
            t1 = self.get_a_free_t_register()
            self.t_registers[t1] = True
            t2 = self.get_a_free_t_register()
            if isinstance(opr1, Variable):
                if opr1.type == "int":
                    self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(t1, opr1.address_offset, t1, t1))
                else:
                    pass  # type checking
            elif isinstance(opr1, Immediate):
                self.write_code("""
li $t{}, {};
                """.format(t1, opr1.value))
            elif isinstance(opr1, Register):
                self.write_code("""
move $t{}, ${};
                """.format(t1, opr1.type + str(opr1.number)))
            else:
                pass  # other things
            if isinstance(opr2, Variable):
                if opr2.type == "int":
                    self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(t2, opr2.address_offset, t2, t2))
                else:
                    pass  # type checking
            elif isinstance(opr2, Immediate):
                self.write_code("""
li $t{}, {};
                """.format(t2, opr2.value))
            elif isinstance(opr2, Register):
                self.write_code("""
move $t{}, ${};
                """.format(t2, opr2.type + str(opr2.number)))
            else:
                pass  # other things

            self.write_code("""
div $t{}, $t{};
mflo $t{};
            """.format(t1, t2, t1))
            return Register("t", t1)
        except Exception:
            print("Error in DIvide")
            exit(4)
        return args

    def mod(self, args):
        # print("mod")
        # print(args)
        try:
            opr1 = args[0]
            opr2 = args[1]
            t1 = self.get_a_free_t_register()
            self.t_registers[t1] = True
            t2 = self.get_a_free_t_register()
            if isinstance(opr1, Variable):
                if opr1.type == "int":
                    self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(t1, opr1.address_offset, t1, t1))
                else:
                    pass  # type checking
            elif isinstance(opr1, Immediate):
                self.write_code("""
li $t{}, {};
                """.format(t1, opr1.value))
            elif isinstance(opr1, Register):
                self.write_code("""
move $t{}, ${};
                """.format(t1, opr1.type + str(opr1.number)))
            else:
                pass  # other things
            if isinstance(opr2, Variable):
                if opr2.type == "int":
                    self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(t2, opr2.address_offset, t2, t2))
                else:
                    pass  # type checking
            elif isinstance(opr2, Immediate):
                self.write_code("""
li $t{}, {};
                """.format(t2, opr2.value))
            elif isinstance(opr2, Register):
                self.write_code("""
move $t{}, ${};
                """.format(t2, opr2.type + str(opr2.number)))
            else:
                pass  # other things

            self.write_code("""
div $t{}, $t{};
mfhi $t{};
            """.format(t1, t2, t1))
            return Register("t", t1)
        except Exception:
            print("Error in MOD")
            exit(4)
        return args

    def not_statement(self, args):
        # todo
        return args

    def pass_one_operand_calculation(self, args):
        # print("one opr")
        # print(args)
        return args[0]

    def pass_math_expr2(self, args):
        return args[0]

    def pass_math_expr1(self, args):
        return args[0]

    def add(self, args):
        # print("add")
        # print(args)
        opr1 = args[0]
        opr2 = args[1]
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        if isinstance(opr1, Register):
            self.write_code("""
move $t{}, ${};
            """.format(t1, opr1.type + str(opr1.number)))
            if opr1.type == "t":
                self.t_registers[opr1.number] = False
        elif isinstance(opr1, Variable):
            self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(t1, opr1.address_offset, t1, t1))
        elif isinstance(opr1, Immediate):
            self.write_code("""
li $t{}, {};
            """.format(t1, opr1.value))
        else:
            pass  # other types
        if isinstance(opr2, Register):
            self.write_code("""
move $t{}, ${};
            """.format(t2, opr2.type + str(opr2.number)))
            if opr2.type == "t":
                self.t_registers[opr2.number] = False
        elif isinstance(opr2, Variable):
            self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(t2, opr2.address_offset, t2, t2))
        elif isinstance(opr2, Immediate):
            self.write_code("""
li $t{}, {};
            """.format(t2, opr2.value))
        else:
            pass  # other types
        self.write_code("""
add $t{}, $t{}, $t{}
        """.format(t1, t1, t2))

        return Register("t", t1)

    def sub(self, args):
        # print("minus")
        # print(args)
        opr1 = args[0]
        opr2 = args[1]
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        if isinstance(opr1, Register):
            self.write_code("""
move $t{}, ${};
            """.format(t1, opr1.type + str(opr1.number)))
            if opr1.type == "t":
                self.t_registers[opr1.number] = False
        elif isinstance(opr1, Variable):
            self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(t1, opr1.address_offset, t1, t1))
        elif isinstance(opr1, Immediate):
            self.write_code("""
li $t{}, {};
            """.format(t1, opr1.value))
        else:
            pass  # other types
        if isinstance(opr2, Register):
            self.write_code("""
move $t{}, ${};
            """.format(t2, opr2.type + str(opr2.number)))
            if opr2.type == "t":
                self.t_registers[opr2.number] = False
        elif isinstance(opr2, Variable):
            self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(t2, opr2.address_offset, t2, t2))
        elif isinstance(opr2, Immediate):
            self.write_code("""
li $t{}, {};
            """.format(t2, opr2.value))
        else:
            pass  # other types
        self.write_code("""
sub $t{}. $t{}, $t{}
        """.format(t1, t1, t2))

        return Register("t", t1)

    def write_conditional_expr(self, opr1, opr2):
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        if isinstance(opr1, Register):
            self.write_code("""
move $t{}, ${};
            """.format(t1, opr1.type + str(opr1.number)))
            if opr1.type == "t":
                self.t_registers[opr1.number] = False
        elif isinstance(opr1, Variable):
            self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(t1, opr1.address_offset, t1, t1))
        elif isinstance(opr1, Immediate):
            self.write_code("""
li $t{}, {};
            """.format(t1, opr1.value))
        else:
            pass  # other types
        if isinstance(opr2, Register):
            self.write_code("""
move $t{}, ${};
            """.format(t2, opr2.type + str(opr2.number)))
            if opr2.type == "t":
                self.t_registers[opr2.number] = False
        elif isinstance(opr2, Variable):
            self.write_code("""
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(t2, opr2.address_offset, t2, t2))
        elif isinstance(opr2, Immediate):
            self.write_code("""
li $t{}, {};
            """.format(t2, opr2.value))
        else:
            pass  # other types

        return (Register('t', t1), Register('t', t2))

    def get_new_label(self):
        self.label_count += 1
        return "label{}".format(self.label_count)

    def map_condition_to_boolian(self, t_reg, label):
        out_label = self.get_new_label()
        self.write_code("""
add $t{}, zero, zero;
b {};
{}:
addi $t{}, zero, 1;
{}:
        """.format(t_reg.number, out_label, label, t_reg.number, out_label))

    def handle_condition(self, left_opr, right_opr, branch_instruction):
        t1, t2 = self.write_conditional_expr(left_opr, right_opr)
        label = self.get_new_label()
        self.write_code("""
{} $t{}, $t{}, {};
        """.format(branch_instruction, t1.number, t2.number, label))
        self.map_condition_to_boolian(t1, label)
        return t1

    def less_than(self, args):
        # print(args, 'less')
        t1 = self.handle_condition(args[0], args[1], 'blt')
        return t1

    def less_equal(self, args):
        t1 = self.handle_condition(args[0], args[1], 'ble')
        return t1

    def grater_than(self, args):
        t1 = self.handle_condition(args[0], args[1], 'bgt')
        return t1

    def grater_equal(self, args):
        t1 = self.handle_condition(args[0], args[1], 'bge')
        return t1

    def equal(self, args):
        t1 = self.handle_condition(args[0], args[1], 'be')
        return t1

    def not_equal(self, args):
        t1 = self.handle_condition(args[0], args[1], 'bne')
        return t1

    def and_logic(self, args):
        pass

    def or_logic(self, args):
        pass

    def if_expr(self, args):
        print(args, 'if_expr')
        result_register = args[0]
        end_if_stmt_label = Label('label1')         # generate label
        self.write_code("""
ble $t{}, zero, {}:
        """.format(result_register.number, end_if_stmt_label.name))
        return end_if_stmt_label

    def if_stmt(self, args):
        print('if_stmt', args[0].name)
        end_if_stmt_label = args[0]
        end_if_else_label = Label('lable_out')  # todo: generate lable
        self.write_code("""
b {} ;
{}:
        """.format(end_if_else_label.name, end_if_stmt_label.name))
        return end_if_else_label

    def pass_if(self, args):
        print(args, 'pass_if')
        end_if_else_label = args[0]
        self.write_code("""
{}:
        """.format(end_if_else_label.name))

    def pass_compare(self, args):
        # print(args[0].value)
        return args[0]

    def pass_equality(self, args):
        return args[0]

    def stmt_block(self, args):
        # print(args, 'stmt_block')
        return args

    def pass_stmt(self, args):
        # print(args, 'pass_stmt')
        return args

    def pass_logic(self, args):
        return args[0]

    def pass_assignment(self, args):
        # print("pass assign")
        # print(args)
        return args[0]

    def constant_operand(self, args):
        # print("constant operands")
        # print(args)
        if isinstance(args[0], Token) and args[0].type == "NUMBER":
            return Immediate(args[0].value)
        return args

    def pass_constant(self, args):
        # print("pass constants")
        # print(args)
        return args[0].children[0]

    def call_action(self, args):
        # print("call")
        # print(args)
        return args[0]

    # [Tree(math_expr_1, [Tree(math_expr_2, [<CodeGenerator.Variable object at 0x000001B9FBB3B308>])]), Tree(math_expr_2, [<CodeGenerator.Variable object at 0x000001B9FBB3B548>])]
    # [Tree(math_expr_1, [Tree(math_expr_2, [<CodeGenerator.Variable object at 0x000001F904ADA708>])]), <CodeGenerator.Register object at 0x000001F904ADAB48>]
    
    def paranthes_action(self, args):
        # print("paranethesis")
        # print(args)
        return args[0]


    '''
    Print
    '''

    def exp_to_actual(self, args):
        # print("exp to actual")
        # print(args)
        return args[0]

    def exp_calculated(self, args):
        # print("exp calculated")
        # print(args)
        return args[0]

    def print(self, args):
        # print("print")
        # print(args)
        if isinstance(args[0], Variable):
            if args[0].type == "int":
                self.write_code("""
li $v0, 1;
li $a0, {};
lw $a0, frame_pointer($a0);
syscall
                """.format(args[0].address_offset))
            elif args[0].type == "string":
                pass
            elif args[0].type == "double":
                pass
            elif args[0].type == "bool":
                pass
            else:
                pass  # other types
        else:
            pass  # other types
        return args


class Variable:
    def __init__(self):
        super().__init__()
        self.name = None
        self.type = None
        self.value = None
        self.address_offset = None   # address from the start of frame pointer
        self.size = None  # in bytes

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

    def __str__(self):
        return "Variable({})".format(self.name)

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


class Register:
    def __init__(self, typ, number):
        self.type = typ  # s, v, a, t
        self.number = number


class Immediate:
    def __init__(self, value):
        self.value = value


class Label:
    def __init__(self, name):
        self.name = name
