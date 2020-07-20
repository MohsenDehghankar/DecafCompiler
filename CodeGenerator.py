from lark import Transformer, Tree
from lark.lexer import Lexer, Token
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
        # last local variable
        self.last_var_in_fp = None
        # for generating label names
        self.label_count = 0
        # for loop
        self.expr_started = False
        self.expr_tokens = []

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
        variable_name = args[0].children[1].value

        if variable_name in self.symbol_table.keys():
            print("Variable with name {} already exists".format(variable_name))
            exit(4)

        # debug
        print(
            "Variable Declared type {0}, name {1}".format(self.type_tmp, variable_name)
        )

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
                else offset + (variable.size - variable.size % offset)
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

    """
    After 'left_value = right_value' calculated 
    """

    def append_code(self, current_code, new_code):
        return current_code + "\n" + new_code

    def assignment_calculated(self, args):
        # print("assignment calculated")
        # print(args)
        left_value = args[0]
        right_value = args[1]
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True

        current_code = ""
        # right
        if isinstance(right_value, Register):
            # check bool
            if right_value.is_bool and not self.is_bool(left_value):
                print("BOOL assignment to non BOOL.")
                exit(4)

            current_code = self.append_code(
                current_code,
                """
move $t{}, ${};
            """.format(
                    t1, right_value.type + str(right_value.number)
                ),
            )
            if right_value.type == "t":
                self.t_registers[right_value.number] = False
        elif isinstance(right_value, Immediate):
            # check bool
            if right_value.is_bool and not self.is_bool(left_value):
                print("BOOL assignment to non BOOL.")
                exit(4)

            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
            """.format(
                    t1, right_value.value
                ),
            )
        else:
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
lw $t{}, frame_pointer($t{});
            """.format(
                    t1, right_value.address_offset, t1, t1
                ),
            )

        # left
        if isinstance(left_value, Register):
            current_code = self.append_code(
                current_code,
                """
move ${}, $t{};
            """.format(
                    left_value.type + str(left_value.number), t1
                ),
            )

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
                if not self.is_bool(right_value):
                    print("Wrong assignment to BOOL variable")
                    exit(4)

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
        args[0].write_code(current_code)

        # return something for nested equalities
        return args[
            0
        ]  # after assignment, the left value will be returned for other assignment (nested)

    """
    Check if a Variable, Register or Immediate is 'bool'
    """

    def is_bool(self, var_or_reg):
        # check if the Variable or Register or Immediate is bool
        if isinstance(var_or_reg, Variable) and var_or_reg.type == "bool":
            return True
        elif (
            isinstance(var_or_reg, Immediate) or isinstance(var_or_reg, Register)
        ) and var_or_reg.is_bool:
            return True
        return False

    def lvalue_calculated(self, args):
        # print("lvalue calculated")
        # print(args)
        return args[0]

    def identifier_in_expression(self, args):
        # print("ident: {0}".format(args[0].value))
        return args[0]

    """
    Expressions
    """

    def token_to_var(self, args):
        # print("high prior: ")
        # print(args)

        # start of expression
        #         if not self.expr_started:
        #             self.expr_started = True
        #             tkn = str(uuid.uuid4())
        #             self.expr_tokens.append(tkn)
        #             self.write_code("""
        # #{}
        #             """.format(tkn))

        try:
            child = args[0]
            if isinstance(child, Token) and child.type == "IDENT":
                return self.symbol_table[child.value]
            else:
                pass  # other expressions
        except Exception:
            print("Exception in token to var.")
            exit(4)

        return args[0]

    def minus(self, args):
        # print("minus:")
        # print(args)
        var = args[0].children[0]
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
                reg = Register("t", t1)
                reg.write_code(current_code)
                return reg
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
            current_code = ""
            opr1 = args[0]
            opr2 = args[1]
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
            reg = Register("t", t1)
            reg.write_code(current_code)
            return reg
        except Exception:
            print("Error in multiply")
            exit(4)
        return args

    def divide(self, args):
        # print("divide")
        # print(args)
        try:
            current_code = ""
            opr1 = args[0]
            opr2 = args[1]
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
            reg = Register("t", t1)
            reg.write_code(current_code)
            return reg
        except Exception:
            print("Error in DIvide")
            exit(4)
        return args

    def mod(self, args):
        # print("mod")
        # print(args)
        try:
            current_code = ""
            opr1 = args[0]
            opr2 = args[1]
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
            reg = Register("t", t1)
            reg.write_code(current_code)
            return reg
        except Exception:
            print("Error in MOD")
            exit(4)
        return args

    def not_statement(self, args):
        # print("not statement")
        # print(args)
        if isinstance(args[0], Variable):
            if args[0].type == "bool":
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
                reg = Register("t", t1)
                reg.is_bool = True
                reg.write_code(current_code)
                return reg
            else:
                print("! is for boolean only.")
                exit(4)
        elif isinstance(args[0], Immediate):
            if args[0].is_bool:
                args[0].value = 0 if args[0].value == 1 else 1
            else:
                print("! is for boolean only.")
                exit(4)
        elif isinstance(args[0], Register):
            current_code = ""
            if args[0].is_bool:
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
            else:
                print("! is for boolean only.")
                exit(4)
        return args[0]

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
        reg = Register("t", t1)
        reg.write_code(current_code)

        return reg

    def sub(self, args):
        # print("minus")
        # print(args)
        opr1 = args[0]
        opr2 = args[1]
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
sub $t{}. $t{}, $t{}
        """.format(
                t1, t1, t2
            ),
        )
        reg = Register("t", t1)
        reg.write_code(current_code)

        return reg

    """
    Conditional Part
    """

    def write_conditional_expr(self, opr1, opr2):
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

        reg = Register("t", t1)
        reg.write_code(current_code)
        return (reg, Register("t", t2))

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

    def handle_condition(self, left_opr, right_opr, branch_instruction):
        t1, t2 = self.write_conditional_expr(left_opr, right_opr)
        label = self.get_new_label()
        current_code = ""
        current_code = self.append_code(
            current_code,
            """
{} $t{}, $t{}, {};
        
        """.format(
                branch_instruction, t1.number, t2.number, label.name
            ),
        )

        t1.write_code(current_code)
        self.map_condition_to_boolian(t1, label)
        self.t_registers[t2.number] = False
        t1.is_bool = True
        return t1

    def less_than(self, args):
        # print(args, 'less')
        t1 = self.handle_condition(args[0], args[1], "blt")
        return t1

    def less_equal(self, args):
        t1 = self.handle_condition(args[0], args[1], "ble")
        return t1

    def grater_than(self, args):
        t1 = self.handle_condition(args[0], args[1], "bgt")
        return t1

    def grater_equal(self, args):
        t1 = self.handle_condition(args[0], args[1], "bge")
        return t1

    def equal(self, args):
        t1 = self.handle_condition(args[0], args[1], "beq")
        return t1

    def not_equal(self, args):
        t1 = self.handle_condition(args[0], args[1], "bne")
        return t1

    def and_logic(self, args):
        # print(args, "and_logic")
        t1 = args[0]
        t2 = args[1]
        current_code = ""
        if not (self.is_bool(t1) or self.is_bool(t2)):
            print("|| should be used for bool type")
            exit(4)
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
        if not (self.is_bool(t1) or self.is_bool(t2)):
            print("|| should be used for bool type")
            exit(4)
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
        print("for")
        print(args)
        result_code = ""
        for_lablel = self.get_new_label()
        # print(for_lablel.name)
        end_label = self.get_new_label()
        # print(end_label.name)
        condition = args[1].number
        # print(condition)

        # check availability
        if isinstance(args[0], Tree):
            if len(args[0].children) == 0:
                pass  # handle when we don't have first expr
        elif len(args[0]) == 0:
            pass  # handle when we don't have first expr
        if isinstance(args[2], Tree):
            if len(args[2].children) == 0:
                pass  # handle when we don't have second expr
        elif len(args[2]) == 0:
            pass  # handle when we don't have second expr

        # We do have both exprs
        # todo
        # label for condition
        condition_label = self.get_label_to_expr_token(condition_part_token)
        # label for part
        step_label = self.get_label_to_expr_token(step_part_token)

        # TODO:body (stmt tree) should be here
        current_code = self.append_code(
            current_code,
            """
{}:
beq $t{},$zero,{}
#body should be inserted here
j {}
{}:
        """.format(
                for_lablel.name,
                condition,
                end_label.name,
                for_lablel.name,
                end_label.name,
            ),
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
        print("stmt_block")
        print(args)
        for result in args:
            if isinstance(result, Tree):
                for child in result.children:
                    self.write_code(child.code)
            else:
                self.write_code(result.code)
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

    """
    There is a Constant operand in Expression
    """

    def constant_operand(self, args):
        # print("constant operands")
        # print(args)
        if isinstance(args[0], Token):
            if args[0].type == "NUMBER":
                return Immediate(args[0].value)
            elif args[0].type == "BOOL":
                imm = Immediate(1 if args[0].value == "true" else 0)
                imm.is_bool = True
                return imm
        return args

    def pass_constant(self, args):
        # print("pass constants")
        # print(args)
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
        print("exp calculated")
        print(args)
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
        current_code = ""
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
                pass
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
            if args[0].is_bool:
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
        return "Variable({})".format(self.name)


class Register(Result):
    def __init__(self, typ, number):
        super().__init__()
        self.type = typ  # s, v, a, t
        self.number = number
        self.is_bool = False
        self.is_reference = False  # later


class Immediate(Result):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.is_bool = False


class Label:
    def __init__(self, name):
        self.name = name


class Array(Variable):
    def __init__(self):
        super().__init__()
