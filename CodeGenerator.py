from lark import Transformer, Tree
from lark.lexer import Lexer, Token
from ObjectOrientedCodeGen import ObjectOrientedCodeGen
import uuid


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
        # $f registers. $f[i] is being used <==> self.f_regsiters[i] = True
        self.f_registers = [False for i in range(32)]
        # last local variable
        self.last_var_in_fp = None
        # for generating label names
        self.label_count = 0
        # for generating double name
        self.tmp_double_count = 0
        # for loop
        self.expr_started = False
        self.expr_tokens = []
        # object oriented code generator
        self.oo_gen = ObjectOrientedCodeGen(self)

    def write_code(self, code_line):
        self.mips_code = self.mips_code + "\n" + code_line

    """
    Initialization
    """

    def create_data_segment(self):
        self.write_code(
            """
.data
frame_pointer:  .space  1000
true_const:     .asciiz "true"
false_const:    .asciiz "false"

.text
main:
        """
        )

    """
    Variable declaration
    """

    def variable_declare(self, args):
        # print("var_declare", args)
        variable_name = args[0].children[1].value

        if variable_name in self.symbol_table.keys():
            print("Variable with name {} already exists".format(variable_name))
            exit(4)

        # debug
        # print(
        #     "Variable Declared type {0}, name {1}".format(self.type_tmp, variable_name)
        # )

        if self.type_tmp == None:
            print("Type of Variable {} unknown".format(variable_name))
            exit(4)

        self.create_variable(self.type_tmp, variable_name)
        self.type_tmp = None
        return Result()

    """
    Create a variable in Memory and add to Symbol Table
    """

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
            variable.address_offset = (
                offset
                if offset % variable.size == 0
                else offset + (variable.size - offset % variable.size)
            )
        self.last_var_in_fp = variable
        if variable.address_offset + variable.size > 1000:
            print("Local Variables are more than frame size!")
            exit(4)
        self.symbol_table[var_name] = variable
        return variable

    """
    Getting the type of declared variable
    """

    def int_variable_declaraion(self, args):
        self.type_tmp = "int"
        return "int"

    def double_variable_declaration(self, args):
        self.type_tmp = "double"
        return "double"

    def bool_variable_declaration(self, args):
        self.type_tmp = "bool"
        return "bool"

    def string_variable_declaration(self, args):
        self.type_tmp = "string"
        return "string"

    """
    Read from console
    """

    def read_line(self, args):
        # print("[readLine]")
        # print(args)
        var = self.create_variable(
            "string", "readline" + str(CodeGenerator.tmp_var_id_read)
        )
        CodeGenerator.tmp_var_id_read += 1
        t = self.get_a_free_t_register()
        var.write_code(
            """
li $v0, 9;
li $a0, 16384;
syscall
li $t{}, {};
sw $v0, frame_pointer($t{})
move $a0, $v0;
li $v0, 8
li $a1, 16384
syscall
        """.format(
                t, var.address_offset, t
            )
        )
        # act as a new variable in rest of the tree
        return [Token("IDENT", var.name)]

    """
    Get a not used Register of Type 't'
    """

    def get_a_free_t_register(self):
        for i in range(10):
            if not self.t_registers[i]:
                return i
        print("Not Enough Regsiter to Use!")
        exit(4)

    def get_a_free_f_register(self):
        for i in range(0, 32, 2):
            if not self.f_registers[i]:
                return i
        print("Not Enough Regsiter to Use!")
        exit(4)

    """
    After 'left_value = right_value' calculated 
    """

    def append_code(self, current_code, new_code):
        return current_code + "\n" + new_code

    def type_checking_for_assignment(self, l_opr, r_opr):
        if l_opr.type != r_opr.type:
            print(
                "invalid type {} and {} for assignment".format(l_opr.type, r_opr.type)
            )
            exit(4)

    def code_for_loading_int_reg(self, t_reg, _int):
        code = """
move $t{}, ${};
                """.format(
            t_reg, _int.kind + str(_int.number)
        )

        return code

    def code_for_loading_int_Imm(self, t_reg, _Imm):
        code = """
li $t{}, {};
            """.format(
            t_reg, _Imm.value
        )

        return code

    def code_for_moveing_int_var(self, t_reg, var):
        code = """
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(
            t_reg, var.address_offset, t_reg, t_reg
        )

        return code

    def handle_double_assignment(self, left_opr, right_opr):

        f1 = self.get_a_free_f_register()
        t1 = self.get_a_free_t_register()
        code = ""
        if isinstance(right_opr, Variable):
            if right_opr.address_offset == None:
                code = self.append_code(
                    code,
                    """
li.d $f{}, {};
                    """.format(
                        f1, right_opr.value
                    ),
                )
            else:
                code = self.append_code(
                    code,
                    """
li $t{}, {};
l.d $f{}, frame_pointer($t{})
                    """.format(
                        t1, right_opr.address_offset, f1, t1
                    ),
                )
        # double register
        else:
            f1 = right_opr.number
        code = self.append_code(
            code,
            """
li $t{}, {};
s.d $f{}, frame_pointer($t{});
                """.format(
                t1, left_opr.address_offset, f1, t1
            ),
        )
        return code

    def assignment_calculated(self, args):
        # print("assignment calculated")
        # print(args)
        left_value = args[0]
        right_value = args[1]

        self.type_checking_for_assignment(left_value, right_value)

        if left_value.type == "double":
            code = right_value.code
            assign_code = self.handle_double_assignment(left_value, right_value)
            code = self.append_code(code, assign_code)
            # args[0].write_code(code)
            result = Result()
            result.code = code
            return result

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True

        current_code = right_value.code
        right_code = ""

        # right
        if isinstance(right_value, Register):
            if right_value.type == "int" or right_value.type == "bool":
                right_code = self.code_for_loading_int_reg(t1, right_value)

            # now right register can be free
            if right_value.kind == "t":
                self.t_registers[right_value.number] = False

        elif isinstance(right_value, Immediate):
            right_code = self.code_for_loading_int_Imm(t1, right_value)

        elif isinstance(right_value, Variable):
            # int or bool
            right_code = self.code_for_moveing_int_var(t1, right_value)

        current_code = self.append_code(current_code, right_code)

        # left
        if isinstance(left_value, Register):
            current_code = self.append_code(  # ?????????????
                current_code,
                """
    move ${}, $t{};
                """.format(
                    left_value.type + str(left_value.number), t1
                ),
            )

            # free left_value register
            self.t_registers[left_value.number] = False
        else:
            if left_value.type == "int":
                t2 = self.get_a_free_t_register()
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
sw $t{}, frame_pointer($t{});
                """.format(
                        t2, left_value.address_offset, t1, t2
                    ),
                )
            elif left_value.type == "bool":
                t2 = self.get_a_free_t_register()
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
sb $t{}, frame_pointer($t{});
                """.format(
                        t2, left_value.address_offset, t1, t2
                    ),
                )
            else:
                # other types
                pass
        self.t_registers[t1] = False

        # add this generated code
        # args[0].write_code(current_code)
        result = Result()
        result.code = current_code
        # return something for nested equalities
        return result  # after assignment, the left value will be returned for other assignment (nested)

    """
    Check if a Variable, Register or Immediate is 'bool'
    """

    def lvalue_calculated(self, args):
        # print("lvalue calculated")
        # print(args)
        return args[0]

    def pass_bool(self, args):
        print("bool", args)
        return args[0]

    def identifier_in_expression(self, args):
        print("ident: {0}".format(args[0].value))
        return args[0]

    """
    Expressions
    """

    def token_to_var(self, args):
        # print("high prior: ")
        # print(args)

        try:
            child = args[0]
            if isinstance(child, Token) and child.type == "IDENT":
                return self.symbol_table[child.value]
            elif isinstance(child, Variable) and child.type == "double":
                return child
            else:
                pass  # other expressions
        except Exception:
            print("Exception in token to var.")
            exit(4)

        return args[0]

    def type_checking_for_minus(self, opr):
        if opr.type != "int" and opr.type != "double":
            print("type of {} is invalid for -".format(opr.type))
            exit(4)

    def minus(self, args):
        print("minus:")
        print(args)

        self.type_checking_for_minus(args[0])

        var = args[0]
        if isinstance(var, Variable):
            if var.type == "int":
                current_code = ""
                t1 = self.get_a_free_t_register()
                self.t_registers[t1] = True
                t2 = self.get_a_free_t_register()
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, -1;
li $t{}, {};
lw $t{}, frame_pointer($t{});
mult $t{}, $t{};
mflo $t{};
                """.format(
                        t1, t2, var.address_offset, t2, t2, t1, t2, t1
                    ),
                )
                reg = Register("int", "t", t1)
                reg.write_code(current_code)
                return reg
            # other types
        elif isinstance(var, Immediate):
            var.value = -1 * int(var.value)
            return var
        else:
            pass  # other expressions
        return args

    def multiply(self, args):
        # print("multiply")
        # print(args)
        current_code = ""
        opr1 = args[0]
        opr2 = args[1]

        self.check_type_for_math_expr(opr1, opr2, "*")

        if opr1.type == "double":
            return self.double_operation(opr1, opr2, "mul")

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        if isinstance(opr1, Variable):
            if opr1.type == "int":
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(
                        t1, opr1.address_offset, t1, t1
                    ),
                )
            else:
                pass  # type checking
        elif isinstance(opr1, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
                """.format(
                    t1, opr1.value
                ),
            )
        elif isinstance(opr1, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
                """.format(
                    t1, opr1.type + str(opr1.number)
                ),
            )
        else:
            pass  # other things
        if isinstance(opr2, Variable):
            if opr2.type == "int":
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(
                        t2, opr2.address_offset, t2, t2
                    ),
                )
            else:
                pass  # type checking
        elif isinstance(opr2, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
                """.format(
                    t2, opr2.value
                ),
            )
        elif isinstance(opr2, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
                """.format(
                    t2, opr2.type + str(opr2.number)
                ),
            )
        else:
            pass  # other things
        current_code = self.append_code(
            current_code,
            """
mult $t{}, $t{};
mflo $t{};
            """.format(
                t1, t2, t1
            ),
        )
        reg = Register(opr1.type, "t", t1)
        reg.write_code(current_code)
        return reg

    def divide(self, args):
        print("divide")
        print(args)
        current_code = ""
        opr1 = args[0]
        opr2 = args[1]

        self.check_type_for_math_expr(opr1, opr2, "/")

        if opr1.type == "double":
            return self.double_operation(opr1, opr2, "div")

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()

        if isinstance(opr1, Variable):
            if opr1.type == "int":
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(
                        t1, opr1.address_offset, t1, t1
                    ),
                )
            else:
                pass  # type checking
        elif isinstance(opr1, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t1, opr1.value
                ),
            )
        elif isinstance(opr1, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t1, opr1.type + str(opr1.number)
                ),
            )
        else:
            pass  # other things
        if isinstance(opr2, Variable):
            if opr2.type == "int":
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
lw $t{}, frame_pointer($t{});
                """.format(
                        t2, opr2.address_offset, t2, t2
                    ),
                )
            else:
                pass  # type checking
        elif isinstance(opr2, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t2, opr2.value
                ),
            )
        elif isinstance(opr2, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t2, opr2.type + str(opr2.number)
                ),
            )
        else:
            pass  # other things

        current_code = self.append_code(
            current_code,
            """
div $t{}, $t{};
mflo $t{};
        """.format(
                t1, t2, t1
            ),
        )
        reg = Register(opr1.type, "t", t1)
        reg.write_code(current_code)
        return reg

    def mod(self, args):
        # print("mod")
        # print(args)
        current_code = ""
        opr1 = args[0]
        opr2 = args[1]

        self.check_type_for_math_expr(opr1, opr2, "%")

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        if isinstance(opr1, Variable):
            if opr1.type == "int":
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(
                        t1, opr1.address_offset, t1, t1
                    ),
                )
            else:
                pass  # type checking
        elif isinstance(opr1, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
                """.format(
                    t1, opr1.value
                ),
            )
        elif isinstance(opr1, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
                """.format(
                    t1, opr1.type + str(opr1.number)
                ),
            )
        else:
            pass  # other things
        if isinstance(opr2, Variable):
            if opr2.type == "int":
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
lw $t{}, frame_pointer($t{});
                    """.format(
                        t2, opr2.address_offset, t2, t2
                    ),
                )
            else:
                pass  # type checking
        elif isinstance(opr2, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
                """.format(
                    t2, opr2.value
                ),
            )
        elif isinstance(opr2, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
                """.format(
                    t2, opr2.type + str(opr2.number)
                ),
            )
        else:
            pass  # other things

        current_code = self.append_code(
            current_code,
            """
div $t{}, $t{};
mfhi $t{};
            """.format(
                t1, t2, t1
            ),
        )
        reg = Register(opr1.type, "t", t1)
        reg.write_code(current_code)
        return reg

    def not_statement(self, args):
        print("not statement")
        print(args)

        self.type_checking_for_logical_expr(args[0], args[0], "!")

        if isinstance(args[0], Variable):
            current_code = ""
            t1 = self.get_a_free_t_register()
            self.t_registers[t1] = True
            lbl1 = self.get_new_label().name
            lbl2 = self.get_new_label().name
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
lb $t{}, frame_pointer($t{});
beq $t{}, $zero, {};
move $t{}, $zero;
j {};
{}:
li $t{}, 1;
{}:
             """.format(
                    t1,
                    args[0].address_offset,
                    t1,
                    t1,
                    t1,
                    lbl1,
                    t1,
                    lbl2,
                    lbl1,
                    t1,
                    lbl2,
                ),
            )
            reg = Register("bool", "t", t1)
            reg.write_code(current_code)
            return reg

        elif isinstance(args[0], Immediate):
            args[0].value = 0 if args[0].value == 1 else 1
        elif isinstance(args[0], Register):
            current_code = ""
            t1 = self.get_a_free_t_register()
            lbl1 = self.get_new_label().name
            lbl2 = self.get_new_label().name
            current_code = self.append_code(
                current_code,
                """
beq ${}, $zero, {};
move ${}, $zero;
j {};
{}:
li ${}, 1;
{}:
                """.format(
                    args[0].type + str(args[0].number),
                    lbl1,
                    args[0].type + str(args[0].number),
                    lbl2,
                    lbl1,
                    args[0].type + str(args[0].number),
                    lbl2,
                ),
            )
            args[0].write_code(current_code)
        return args[0]

    def pass_one_operand_calculation(self, args):
        # print("one opr")
        # print(args)
        return args[0]

    def pass_math_expr2(self, args):
        return args[0]

    def pass_math_expr1(self, args):
        return args[0]

    def double_operation(self, opr1, opr2, instruction):
        f1 = self.get_a_free_f_register()
        self.f_registers[f1] = True
        # self.f_registers[f1 + 1] = True
        f2 = self.get_a_free_f_register()
        current_code = ""
        current_code = self.append_code(
            current_code,
            """
li.d $f{}, {};
li.d $f{}, {};
{}.d $f{}, $f{}, $f{} 
            """.format(
                f1, opr1.value, f2, opr2.value, instruction, f1, f1, f2
            ),
        )
        reg = Register("double", "f", f1)
        reg.write_code(current_code)
        return reg

    def add(self, args):
        print("add")
        print(args)
        opr1 = args[0]
        opr2 = args[1]

        # type checking
        self.check_type_for_math_expr(opr1, opr2, "add")

        if opr1.type == "double":
            reg = self.double_operation(opr1, opr2, "add")
            return reg
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        current_code = ""
        if isinstance(opr1, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t1, opr1.type + str(opr1.number)
                ),
            )
            if opr1.type == "t":
                self.t_registers[opr1.number] = False
        elif isinstance(opr1, Variable):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(
                    t1, opr1.address_offset, t1, t1
                ),
            )
        elif isinstance(opr1, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t1, opr1.value
                ),
            )
        else:
            pass  # other types
        if isinstance(opr2, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t2, opr2.type + str(opr2.number)
                ),
            )
            if opr2.type == "t":
                self.t_registers[opr2.number] = False
        elif isinstance(opr2, Variable):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(
                    t2, opr2.address_offset, t2, t2
                ),
            )
        elif isinstance(opr2, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t2, opr2.value
                ),
            )
        else:
            pass  # other types
        current_code = self.append_code(
            current_code,
            """
add $t{}, $t{}, $t{}
        """.format(
                t1, t1, t2
            ),
        )
        reg = Register("int", "t", t1)
        reg.write_code(current_code)

        return reg

    def check_type_for_math_expr(self, opr1, opr2, instruction):
        if opr1.type != opr2.type:
            print(
                "invalid type {} and {} for {}".format(
                    opr1.type, opr2.type, instruction
                )
            )
            exit(4)
        if opr1.type != "int" and opr1.type != "double":
            print("math expr (+,-,*,/,%) for {} are not allowed".format(opr1.type))
            exit(4)

    def sub(self, args):
        print("sub")
        print(args)

        opr1 = args[0]
        opr2 = args[1]
        self.check_type_for_math_expr(opr1, opr2, "sub")

        if opr1.type == "double":
            return self.double_operation(opr1, opr2, "sub")

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        current_code = ""
        if isinstance(opr1, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t1, opr1.type + str(opr1.number)
                ),
            )
            if opr1.type == "t":
                self.t_registers[opr1.number] = False
        elif isinstance(opr1, Variable):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(
                    t1, opr1.address_offset, t1, t1
                ),
            )
        elif isinstance(opr1, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t1, opr1.value
                ),
            )
        else:
            pass  # other types
        if isinstance(opr2, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t2, opr2.type + str(opr2.number)
                ),
            )
            if opr2.type == "t":
                self.t_registers[opr2.number] = False
        elif isinstance(opr2, Variable):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(
                    t2, opr2.address_offset, t2, t2
                ),
            )
        elif isinstance(opr2, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t2, opr2.value
                ),
            )
        else:
            pass  # other types
        current_code = self.append_code(
            current_code,
            """
sub $t{}, $t{}, $t{}
        """.format(
                t1, t1, t2
            ),
        )
        reg = Register("int", "t", t1)
        reg.write_code(current_code)

        return reg

    """
    Conditional Part
    """

    def write_conditional_expr(self, opr1, opr2):
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        self.t_registers[t2] = True
        current_code = ""
        if isinstance(opr1, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t1, opr1.type + str(opr1.number)
                ),
            )
            if opr1.type == "t":
                self.t_registers[opr1.number] = False
        elif isinstance(opr1, Variable):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(
                    t1, opr1.address_offset, t1, t1
                ),
            )
        elif isinstance(opr1, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t1, opr1.value
                ),
            )
        else:
            pass  # other types
        if isinstance(opr2, Register):
            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t2, opr2.type + str(opr2.number)
                ),
            )
            if opr2.type == "t":
                self.t_registers[opr2.number] = False
        elif isinstance(opr2, Variable):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(
                    t2, opr2.address_offset, t2, t2
                ),
            )
        elif isinstance(opr2, Immediate):
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t2, opr2.value
                ),
            )
        else:
            pass  # other types

        reg = Register("int", "t", t1)
        reg.write_code(current_code)
        return (reg, Register("int", "t", t2))

    """
    Get A new Label
    """

    def get_new_label(self):
        self.label_count += 1
        return Label("label{}".format(self.label_count))

    def map_condition_to_boolian(self, t_reg, label):
        out_label = self.get_new_label()
        current_code = ""
        current_code = self.append_code(
            current_code,
            """
add $t{}, $zero, $zero;
b {};
{}:
addi $t{}, $zero, 1;
{}:
        """.format(
                t_reg.number, out_label.name, label.name, t_reg.number, out_label.name
            ),
        )
        t_reg.write_code(current_code)

    def type_checking_for_compare_expr(self, left_opr, right_opr, instruction):
        if left_opr.type != right_opr.type:
            print(
                "type of {} and {} are different".format(left_opr.type, right_opr.type)
            )
            exit(4)
        if left_opr.type != "int" and left_opr.type != "double":
            print("invalid type of {} for {}".format(left_opr.type, instruction))
            exit(4)

    def type_checking_for_equality_expr(self, left_opr, right_opr, instruction):
        if left_opr.type != right_opr.type:
            print(
                "type of {} and {} are different".format(left_opr.type, right_opr.type)
            )
            exit(4)

        if left_opr.type == "string":
            pass  # todo: handle type checking for string

    def handle_condition(self, left_opr, right_opr, inst):
        if left_opr.type == "double":
            return self.handle_condition_for_double(left_opr, right_opr, inst)

        _map = {
            "<": "blt",
            ">": "bgt",
            "<=": "ble",
            ">=": "bge",
            "==": "beq",
            "!=": "bne",
        }
        t1, t2 = self.write_conditional_expr(left_opr, right_opr)
        label = self.get_new_label()
        current_code = ""
        current_code = self.append_code(
            current_code,
            """
{} $t{}, $t{}, {};
        
        """.format(
                _map[inst], t1.number, t2.number, label.name
            ),
        )

        t1.write_code(current_code)
        self.map_condition_to_boolian(t1, label)
        self.t_registers[t2.number] = False
        t1.type = "bool"
        return t1

    def load_double_to_reg(self, opr):
        f1 = self.get_a_free_f_register()
        self.f_registers[f1] = True
        t1 = self.get_a_free_t_register()
        code = ""
        if isinstance(opr, Variable):
            if opr.address_offset == None:
                code = self.append_code(
                    code,
                    """
li.d $f{}, {};
                    """.format(
                        f1, opr.value
                    ),
                )
            else:
                code = self.append_code(
                    code,
                    """
li $t{}, {};
s.d $f{}, frame_pointer($t{})
                    """.format(
                        t1, opr.address_offset, f1, t1
                    ),
                )
        # double register
        else:
            f1 = opr.number
        reg = Register("double", "f", f1)
        reg.write_code(code)
        return reg

    def handle_condition_for_double(self, left_opr, right_opr, inst):
        _map = {
            "<": "c.lt.d",
            ">": "c.lt.d",
            "<=": "c.le.d",
            ">=": "c.le.d",
            "==": "c.eq.d",
            "!=": "c.eq.d",
        }

        left_reg = self.load_double_to_reg(left_opr)
        right_reg = self.load_double_to_reg(right_opr)

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True

        code = self.append_code(left_reg.code, right_reg.code)

        one_label = self.get_new_label()
        out_label = self.get_new_label()

        if inst == "<" or inst == "<=" or inst == "==":
            code = self.append_code(
                code,
                """
{} $f{}, $f{};
bc1t {}
            """.format(
                    _map[inst], left_reg.number, right_reg.number, one_label.name
                ),
            )
        else:
            code = self.append_code(
                code,
                """
{} $f{}, $f{};
bc1f {}
            """.format(
                    _map[inst], left_reg.number, right_reg.number, one_label.name
                ),
            )
        code = self.append_code(
            code,
            """
add $t{}, $zero, $zero;
b {};
{}:
addi $t{}, $zero, 1;
{}:
        """.format(
                t1, out_label.name, one_label.name, t1, out_label.name,
            ),
        )
        reg = Register("bool", "t", t1)
        reg.write_code(code)
        return reg

    def less_than(self, args):
        self.type_checking_for_compare_expr(args[0], args[1], "<")
        t1 = self.handle_condition(args[0], args[1], "<")
        return t1

    def less_equal(self, args):
        self.type_checking_for_compare_expr(args[0], args[1], "<=")
        t1 = self.handle_condition(args[0], args[1], "<=")
        return t1

    def grater_than(self, args):
        self.type_checking_for_compare_expr(args[0], args[1], ">")
        t1 = self.handle_condition(args[0], args[1], ">")
        return t1

    def grater_equal(self, args):
        self.type_checking_for_compare_expr(args[0], args[1], ">=")
        t1 = self.handle_condition(args[0], args[1], ">=")
        return t1

    def equal(self, args):
        self.type_checking_for_equality_expr(args[0], args[1], "==")
        t1 = self.handle_condition(args[0], args[1], "==")
        return t1

    def not_equal(self, args):
        self.type_checking_for_equality_expr(args[0], args[1], "!=")
        t1 = self.handle_condition(args[0], args[1], "!=")
        return t1

    def type_checking_for_logical_expr(self, left_opr, right_opr, instruction):
        if left_opr.type != "bool":
            print("invalid type of {} for {}".format(left_opr.type, instruction))
            exit(4)
        if right_opr.type != "bool":
            print("invalid type of {} for {}".format(right_opr.type, instruction))
            exit(4)

    def and_logic(self, args):
        # print(args, "and_logic")
        t1 = args[0]
        t2 = args[1]
        current_code = ""

        self.type_checking_for_logical_expr(t1, t2, "&&")

        if isinstance(t1, Register) and isinstance(t2, Register):
            current_code = self.append_code(
                current_code,
                """
and $t{}, $t{}, $t{};
            """.format(
                    t1.number, t1.number, t2.number
                ),
            )
            self.t_registers[t2.number] = False
            t1.is_bool = True
            t1.write_code(current_code)
            return t1
        else:
            pass  # other types
        return args[0]

    def or_logic(self, args):
        # print(args, 'or_logic')
        t1 = args[0]
        t2 = args[1]
        current_code = ""

        self.type_checking_for_logical_expr(t1, t2, "||")

        if isinstance(t1, Register) and isinstance(t2, Register):
            current_code = self.append_code(
                current_code,
                """
or $t{}, $t{}, $t{};
            """.format(
                    t1.number, t1.number, t2.number
                ),
            )
            self.t_registers[t2.number] = False
            t1.is_bool = True
            t1.write_code(current_code)
            return t1
        else:
            pass  # other possible types
        return args[0]

    def _if(self, args):
        # print("_if", args)
        expr_result_reg = args[0]
        end_if_stmt_label = self.get_new_label()
        end_if_else_label = self.get_new_label()
        current_code = ""
        current_code = self.append_code(current_code, expr_result_reg.code)
        current_code = self.append_code(
            current_code,
            """
beq $t{}, $zero, {};
        """.format(
                expr_result_reg.number, end_if_stmt_label.name
            ),
        )
        if_stmt = args[1]
        for child in if_stmt.children:
            current_code = self.append_code(current_code, child.code)
        current_code = self.append_code(
            current_code,
            """
b {};
{}:
        """.format(
                end_if_else_label.name, end_if_stmt_label.name
            ),
        )
        if len(args) == 3:
            else_stmt = args[2]
        for child in else_stmt.children:
            current_code = self.append_code(current_code, child.code)
        current_code = self.append_code(
            current_code,
            """
{}:
        """.format(
                end_if_else_label.name
            ),
        )
        result = Result()
        result.write_code(current_code)
        return result

    def false_expression(self, args):
        # if self.expr_started:
        #     self.expr_started = False
        #     tkn = self.expr_tokens[-1]
        #     self.mips_code = self.mips_code.replace("#" + tkn, "\n")
        return args

    def get_label_to_expr_token(self, token):
        lbl = self.get_new_label()
        self.mips_code = self.mips_code.replace(
            "#" + str(token), "{}:\n".format(lbl.name)
        )
        return lbl

    def _for(self, args):
        condition_label = self.get_new_label()
        end_label = self.get_new_label()
        current_code = ""
        if len(args) == 4 or (len(args) == 3 and isinstance(args[1], Register)):
            current_code = self.append_code(current_code, args[0].code)
        current_code = self.append_code(
            current_code, """
{}:
                """.format(condition_label.name)
        )

        if len(args) == 4 or len(args) == 2 or (len(args) == 3 and isinstance(args[1], Register)):
            current_code = self.append_code(current_code, args[1].code)
            current_code = self.append_code(
                current_code, """
beq $t{},$zero,{};
                            """.format(args[1].number, end_label.name)
            )
        else:
            # print(args[0].code)
            current_code = self.append_code(current_code, args[0].code)
            current_code = self.append_code(
                current_code, """
beq $t{},$zero,{};
                            """.format(args[0].number, end_label.name)
            )
        if isinstance(args[len(args) - 1], Tree):
            print(args[len(args) - 1].children[0].code)
            current_code = self.append_code(
                current_code, args[len(args) - 1].children[0].code)
        else:
            print("not handled")

        if len(args) == 4:
            current_code = self.append_code(current_code, args[2].code)
        elif len(args) == 3 and isinstance(args[0], Register):
            current_code = self.append_code(current_code, args[1].code)
        current_code = self.append_code(
            current_code, """
j {};
{}:
                """.format(condition_label.name, end_label.name)
        )
        result = Result()
        result.write_code(current_code)
        return result

    def pass_compare(self, args):
        # print(args[0].value)
        return args[0]

    def pass_equality(self, args):
        return args[0]

    def stmt_block(self, args):
        # print("stmt_block")
        # print(args)
        code = ""
        for result in args:
            if isinstance(result, Tree):
                for child in result.children:
                    code = self.append_code(code, child.code)
            else:
                code = self.append_code(code, result.code)
        result = Result()
        result.code = code
        return result

    def pass_stmt(self, args):
        # print(args, 'pass_stmt')
        return args

    def pass_logic(self, args):
        return args[0]

    def pass_assignment(self, args):
        # print("pass assign")
        # print(args)
        return args[0]

    """
    There is a Constant operand in Expression
    """

    def generate_name_for_double(self):
        self.tmp_double_count += 1
        return "double{}".format(self.tmp_double_count)

    def calculate_value_of_double(self, val):
        val = val.lower()
        if "e" in val:
            mantis, exponent = val.lower().split("e")
            if exponent[0] == "+":
                exponent = int(exponent)
            else:
                exponent = -int(exponent)
            val = float(mantis) * 10 ** exponent
            return val
        else:
            return float(val)

    def constant_operand(self, args):
        # print("constant operands")
        # print(args)
        if isinstance(args[0], Token):
            if args[0].type == "INT":
                return Immediate(args[0].value, "int")
            elif args[0].type == "DOUBLE":
                var = Variable()
                var.type = "double"
                # var = self.create_variable("double", self.generate_name_for_double())
                var.value = self.calculate_value_of_double(args[0].value)
                return var
            elif args[0].type == "BOOL":
                imm = Immediate(1 if args[0].value == "true" else 0, "bool")
                return imm
        return args

    def pass_constant(self, args):
        # print("pass constants", args)
        # print(args[0].children[0])
        return args[0].children[0]

    def call_action(self, args):
        # print("call")
        # print(args)
        return args[0]

    def paranthes_action(self, args):
        # print("paranethesis")
        # print(args)

        # start of expression
        #         if not self.expr_started:
        #             self.expr_started = True
        #             tkn = str(uuid.uuid4())
        #             self.expr_tokens.append(tkn)
        #             self.write_code("""
        # #{}
        #             """.format(tkn))

        return args[0]

    """
    Print
    """

    def exp_to_actual(self, args):
        # print("exp to actual")
        # print(args)
        return args[0]

    def exp_calculated(self, args):
        # print("exp calculated")
        # print(args)
        # print("exp_calculated:")
        # print(args[0].code)
        return args[0]

    def end_of_expr(self, args):
        #         if self.expr_started:
        #             self.write_code("""
        # #{}
        #             """.format(self.expr_tokens[-1]))
        #         self.expr_started = False
        return args[0]

    def print(self, args):
        # print("print")
        # print(args)
        current_code = args[0].code

        if isinstance(args[0], Variable):
            if args[0].type == "int":
                current_code = self.append_code(
                    current_code,
                    """
li $v0, 1;
li $a0, {};
lw $a0, frame_pointer($a0);
syscall
                """.format(
                        args[0].address_offset
                    ),
                )
            elif args[0].type == "string":
                pass
            elif args[0].type == "double":
                if args[0].address_offset == None:
                    current_code = self.append_code(
                        current_code,
                        """
li $v0, 3;
li.d $f12, {};
syscall
                """.format(
                            args[0].value
                        ),
                    )
                else:
                    t1 = self.get_a_free_t_register()
                    current_code = self.append_code(
                        current_code,
                        """
li $v0, 3;
li $t{}, {};
l.d $f12, frame_pointer($t{});
syscall
                """.format(
                            t1, args[0].address_offset, t1
                        ),
                    )
            elif args[0].type == "bool":
                t1 = self.get_a_free_t_register()
                lbl = self.get_new_label().name
                lbl2 = self.get_new_label().name
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
lb $t{}, frame_pointer($t{});
li $v0, 4;
beq $t{}, $zero, {};
la $a0, true_const;
j {};
{}:
la $a0, false_const;
{}:
syscall
                """.format(
                        t1, args[0].address_offset, t1, t1, t1, lbl, lbl2, lbl, lbl2
                    ),
                )
            else:
                pass  # other types
        elif isinstance(args[0], Register):
            if args[0].type == "bool":
                lbl1 = self.get_new_label().name
                lbl2 = self.get_new_label().name
                current_code = self.append_code(
                    current_code,
                    """
li $v0, 4;
beq ${}, $zero, {};
la $a0, true_const;
j {};
{}:
la $a0, false_const;
{}:
syscall
                """.format(
                        args[0].type + str(args[0].number), lbl1, lbl2, lbl1, lbl2
                    ),
                )
            elif args[0].type == "double":
                current_code = self.append_code(
                    current_code,
                    """
li $v0, 3;
mov.d $f12, $f{};
syscall
                """.format(
                        args[0].number
                    ),
                )

            elif args[0].type == "int":
                current_code = self.append_code(
                    current_code,
                    """
li $v0, 1;
move $a0, $t{};
syscall
                """.format(
                        args[0].number
                    ),
                )

            else:
                pass
                # other types in Register
        elif isinstance(args[0], Immediate):
            if args[0].is_bool:
                pass  # todo
            else:
                current_code = self.append_code(
                    current_code,
                    """
li $v0, 1;
li $a0, {};
syscall
                """.format(
                        args[0].value
                    ),
                )
        else:
            pass  # other types
        result = Result()
        result.write_code(current_code)
        return result

    """
    Methods from second code generator
    """

    def non_void_func_declare(self, args):
        return self.oo_gen.non_void_func_declare(args)

    def void_func_declare(self, args):
        return self.oo_gen.void_func_declare(args)

    def read_integer(self, args):
        print("read integer", args)
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        code = """
li $v0, 5;
syscall
move $t{}, $v0;
        """.format(
            t1
        )
        reg = Register("int", "t", t1)
        reg.write_code(code)
        return reg


"""
Other Classes
"""


class Result:
    def __init__(self):
        self.code = ""

    def write_code(self, code):
        self.code += "\n" + code


class Variable(Result):
    def __init__(self):
        super().__init__()
        self.name = None
        self.type = None
        self.value = None
        self.address_offset = None  # address from the start of frame pointer
        self.size = None  # in bytes

    def calc_size(self):
        if self.type == "int":
            self.size = 4
        if self.type == "bool":
            self.size = 1
        if self.type == "string":
            self.size = 4  # address of string
        if self.type == "double":
            self.size = 8
        # var type is an object

    def __str__(self):
        return "Variable name: {}, type: {}, value: {}, size: {}".format(
            self.name, self.type, self.value, self.size
        )

    def __repr__(self):
        return "Variable name: {}, type: {}, value: {}, size: {}".format(
            self.name, self.type, self.value, self.size
        )


class Register(Result):
    def __init__(self, _type, kind, number):
        super().__init__()
        self.type = _type  # int, string, boolian, double
        self.kind = kind  # s, v, a, t
        self.number = number
        # self.is_bool = False
        self.is_reference = False  # later

    def __str__(self):
        return "register type:{}, kind: {}, number: {}".format(
            self.type, self.kind, self.number
        )

    def __repr__(self):
        return "register type:{}, kind: {}, number: {}".format(
            self.type, self.kind, self.number
        )


class Immediate(Result):
    def __init__(self, value, _type):
        super().__init__()
        self.value = value
        self.type = _type

    def __repr__(self):
        return "Immediate value: {}".format(self.value)


class Label:
    def __init__(self, name):
        self.name = name


class Array(Variable):
    def __init__(self):
        super().__init__()
