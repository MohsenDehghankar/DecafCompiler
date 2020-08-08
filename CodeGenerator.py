from lark import Transformer, Tree
from lark.lexer import Lexer, Token
from ObjectOrientedCodeGen import ObjectOrientedCodeGen
from ArrayCodeGen import ArrayCodeGen
import uuid
from ObjectOrientedCodeGen import SymbolTable, ClassMetaData


class CodeGenerator(Transformer):
    tmp_var_id_read = 1000

    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)
        self.mips_code = ""
        # stores (var_name, var_obj)
        self.symbol_table = None
        # symbol_tables['function_name']['var_name'] is instance of Variable
        # this is the main symbol_table
        self.symbol_tables = []
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
        # object oriented code generator
        self.oo_gen = ObjectOrientedCodeGen(self)
        # last declared function
        self.func_type_tmp = None
        self.current_function_name = "7777global7777"
        # previous parser code generator
        self.previous_pass = None
        # is first pass
        self.first_pass = False
        # array code generator
        self.arr_cgen = ArrayCodeGen(self)
        # previous code generator (prev pass)
        self.prev_code_gen = None
        # class declaration started
        self.is_in_class = False
        self.class_name = ""
        self.break_label = None


    def write_code(self, code_line):
        self.mips_code = self.mips_code + "\n" + code_line

    """
    Initialization
    """

    def create_data_segment(self):
        self.write_code(
            """
.data
frame_pointer:  .space  10000
global_pointer: .space  10000
input:          .space  16384
true_const:     .asciiz "true"
false_const:    .asciiz "false"
end_of_string:  .byte   0
newline:        .asciiz "\\n"

.text
main:
la $s0, frame_pointer;
la $s1, global_pointer;
        """
        )

    """
    Variable declaration
    """

    def variable_declare(self, args):
        # print("var_declare", args)

        variable_name = args[0].children[1].value

        if self.is_in_class and not self.oo_gen.func_start:
            if "[]" in self.type_tmp:
                self.create_class_field(variable_name, True, self.type_tmp)
            else:
                self.create_class_field(variable_name, False, self.type_tmp)
            return Result()


        if variable_name in self.symbol_table.variables.keys():
            print("Variable with name {} already exists".format(variable_name))
            exit(4)

        if self.type_tmp == None:
            print("Type of Variable {} unknown".format(variable_name))
            exit(4)

        if "[]" in self.type_tmp:
            self.create_variable(self.type_tmp, variable_name, True)
        elif not self.type_tmp in ["bool", "int", "string", "double"]:
            self.create_variable(self.type_tmp, variable_name, True, is_obj = True)
        else:
            self.create_variable(self.type_tmp, variable_name, False)
        self.type_tmp = None
        return Result()

    """
    Create a variable in Memory and add to Symbol Table
    """

    def create_variable(self, var_type, var_name, is_ref=False, is_obj = False):
        # dynamic allocation
        variable = None

        if "[]" in var_type:
            variable = Array()
        else:
            variable = Variable()

        variable.type = var_type
        variable.name = var_name
        variable.is_reference = is_ref
        variable.calc_size()
        if self.current_function_name == "7777global7777":
            variable.is_global = True

        self.get_last_variable_in_frame()
        if self.last_var_in_fp == None:
            variable.address_offset = 8
        else:
            offset = self.last_var_in_fp.address_offset + self.last_var_in_fp.size
            # memory alignment
            variable.address_offset = (
                offset
                if offset % variable.size == 0
                else offset + (variable.size - offset % variable.size)
            )
        self.last_var_in_fp = variable
        if variable.address_offset + variable.size > 10000:
            print("Local Variables are more than frame size!")
            exit(4)
        self.symbol_table.variables[var_name] = variable
        return variable


    def create_class_field(self, field_name, is_ref, var_type):
        variable = None
        if "[]" in var_type:
            variable = Array()
        else:
            variable = Variable()
        variable.type = var_type
        variable.name = field_name
        variable.is_reference = is_ref
        variable.calc_size()

        # print("var size: {}, {}".format(variable.size, variable.is_reference))

        clss = self.oo_gen.classes[self.class_name]
        if clss.last_var == None:
            variable.class_offset = 0
        else:
            offset = clss.last_var.size + clss.last_var.class_offset
            variable.class_offset = (
                offset
                if offset % variable.size == 0
                else offset + (variable.size - offset % variable.size)
            )
        clss.last_var = variable
        # variable.address_offset = variable.class_offset

        self.symbol_table.variables[field_name] = variable
        if self.first_pass:
            self.oo_gen.classes[self.class_name].fields.append(variable)

        

    def get_last_variable_in_frame(self):
        max_a = 0
        last = None
        sym_tbl_tmp = self.symbol_table
        fnc_name = sym_tbl_tmp.function_name

        # search in first pass generated symbol tables
        # if not self.first_pass:
        #     sym_tbl_tmp = self.get_symbol_table_from_last_pass(sym_tbl_tmp.name)

        # search in all blocks for the function
        while sym_tbl_tmp.function_name == fnc_name:
            for var in sym_tbl_tmp.variables.keys():
                if sym_tbl_tmp.variables[var].address_offset >= max_a:
                    max_a = sym_tbl_tmp.variables[var].address_offset
                    last = sym_tbl_tmp.variables[var]
            sym_tbl_tmp = sym_tbl_tmp.parent
            if sym_tbl_tmp is None:
                break

        self.last_var_in_fp = last
        if last is None:
            var = Variable()
            var.address_offset = 8
            var.size = 0
            self.last_var_in_fp = var

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

    def void_function_declaration(self, args):
        self.type_tmp = "void"
        return "void"

    def save_function_type(self, args):
        self.func_type_tmp = self.type_tmp
        self.type_tmp = None

    def array_variable_declaration(self, args):
        # print("array_declaration", args)
        self.type_tmp = "{}[]".format(args[0])
        return self.type_tmp

    def class_type_def(self, args):
        # print("class type def")
        # print(args)
        self.type_tmp = args[0].value
        return args[0].value

    

    """
    Read from console
    """

    def read_line(self, args):
        # print("ReadLine")
        # print(args)
        t0 = self.get_a_free_t_register()
        self.t_registers[t0] = True
        counter = self.get_a_free_t_register()
        self.t_registers[counter] = True
        t2 = self.get_a_free_t_register()
        self.t_registers[t2] = True
        enter = self.get_a_free_t_register()
        new_line = self.get_new_label()
        end = self.get_new_label()
        reg = Register("string", "t", t0)
        reg.write_code(
            """
la $a0, input
li $v0, 8
li $a1, 16384
syscall
addi $t{}, $t{}, 0
{}:
lb $t{}, ($a0)
lb $t{}, newline
beq $t{}, $t{}, {}
addi $a0, $a0, 1
b {}   
{}:
sb $zero, ($a0)
la $a0, input
move $t{},$a0
        """.format(
                counter,
                counter,
                new_line.name,
                t2,
                enter,
                t2,
                enter,
                end.name,
                new_line.name,
                end.name,
                t0,
            )
        )
        self.t_registers[counter] = False
        self.t_registers[t2] = False
        return reg

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

    def code_for_loading_string_Imm(self, reg, str):
        # print("calculate string")
        # print("str is :::::", str)
        # print(reg)
        code = """
li $v0, 9;
li $a0, {};
syscall
        """.format(
            len(str.value) + 1
        )

        for i in range(len(str.value) + 1):
            if i == len(str.value):
                code = self.append_code(
                    code,
                    """
lb $a0,end_of_string;
sb $a0,{}($v0);
                            """.format(
                        i
                    ),
                )
            else:
                code = self.append_code(
                    code,
                    """
li $a0,'{}';
sb $a0,{}($v0);
                            """.format(
                        str.value[i], i
                    ),
                )
        code = self.append_code(
            code,
            """
move $t{}, $v0;
        """.format(
                reg
            ),
        )

        return code

    def code_for_loading_int_var(self, t_reg, var):
        code = """
li $t{}, {};
add $t{}, $t{}, $s{};
lw $t{}, ($t{});
            """.format(
            t_reg,
            var.address_offset,
            t_reg,
            t_reg,
            1 if var.is_global else 0,
            t_reg,
            t_reg,
        )

        return code

    def code_for_loading_bool_var(self, t_reg, var):
        code = """
li $t{}, {};
add $t{}, $t{}, $s{};
lb $t{}, ($t{});
            """.format(
            t_reg,
            var.address_offset,
            t_reg,
            t_reg,
            1 if var.is_global else 0,
            t_reg,
            t_reg,
        )

        return code

    def code_for_loading_int_ref_reg(self, t_reg, reg):
        code = """
lw $t{}, ($t{});
        """.format(
            t_reg, reg.number
        )
        return code

    def code_for_loading_string_ref_reg(self, t_reg, reg):
        code = """
move $t{},$t{};
        """.format(
            t_reg, reg.number
        )
        return code

    def code_for_loading_double_ref_reg(self, f_reg, reg):
        code = """
l.d $f{}, ($t{});
            """.format(
            f_reg, reg.number
        )
        return code

    def code_for_loading_bool_ref_reg(self, t_reg, reg):
        code = """
lb $t{}, ($t{});
        """.format(
            t_reg, reg.number
        )
        return code

    def code_for_loading_ref_var(self, t_reg, var):
        code = """


        """.format()

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
add $t{}, $t{}, $s{};
l.d $f{}, ($t{})
                    """.format(
                        t1,
                        right_opr.address_offset,
                        t1,
                        t1,
                        1 if right_opr.is_global else 0,
                        f1,
                        t1,
                    ),
                )
        # double register
        elif isinstance(right_opr, Register):
            if right_opr.is_reference == True:
                code = self.append_code(
                    code,
                    """
l.d $f{}, ($t{});
                    """.format(
                        f1, right_opr.number
                    ),
                )
            else:
                f1 = right_opr.number

        if left_opr.is_reference == True:
            code = self.append_code(
                code,
                """
s.d $f{}, ($t{});
                    """.format(
                    f1, left_opr.number
                ),
            )
        else:
            code = self.append_code(
                code,
                """
li $t{}, {};
add $t{}, $t{}, $s{};
s.d $f{}, ($t{});
                """.format(
                    t1,
                    left_opr.address_offset,
                    t1,
                    t1,
                    1 if left_opr.is_global else 0,
                    f1,
                    t1,
                ),
            )

        return code

    def assignment_calculated(self, args):
        print("assignment calculated")
        print(args)

        left_value = args[0]
        right_value = args[1]

        if self.first_pass:
            return Result()

        # print("right value code: {}: " + right_value.code)

        self.type_checking_for_assignment(left_value, right_value)


        if left_value.type == "double":
            code = self.append_code(right_value.code, left_value.code)
            assign_code = self.handle_double_assignment(left_value, right_value)
            code = self.append_code(code, assign_code)
            # args[0].write_code(code)
            result = Result()
            result.code = code
            return result

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        # print("THE NEW REGISTER IS : ", t1)
        current_code = self.append_code(right_value.code, left_value.code)
        right_code = ""

        # right
        if isinstance(right_value, Register):
            if right_value.type == "int" or right_value.type == "string":
                if right_value.is_reference == True:
                    right_code = self.code_for_loading_int_ref_reg(t1, right_value)
                else:
                    print("IS ENTERING HERE")
                    if right_value.type == "string":
                        right_code = """
move $v0,$t{};
                """.format(
                            right_value.number
                        )
                    else:
                        right_code = self.code_for_loading_int_reg(t1, right_value)

            elif right_value.type == "bool":
                if right_value.is_reference == True:
                    right_code = self.code_for_loading_bool_ref_reg(t1, right_value)
                else:
                    right_code = self.code_for_loading_int_reg(t1, right_value)
            elif right_value.is_reference:
                # obj it is
                right_code = self.code_for_loading_int_reg(t1, right_value)


            # now right register can be free
            if right_value.kind == "t":
                self.t_registers[right_value.number] = False

        elif isinstance(right_value, Immediate):
            if right_value.type == "string":
                right_code = self.code_for_loading_string_Imm(t1, right_value)
            else:
                right_code = self.code_for_loading_int_Imm(t1, right_value)

        elif isinstance(right_value, Variable):
            if right_value.type == "int":
                right_code = self.code_for_loading_int_var(t1, right_value)
            elif right_value.type == "bool":
                right_code = self.code_for_loading_bool_var(t1, right_value)

        current_code = self.append_code(current_code, right_code)

        # left
        if isinstance(left_value, Register):
            if left_value.is_obj:
                t = self.get_a_free_t_register()
                t3 = left_value.number

                fld = self.oo_gen.classes[left_value.cls_nm].get_field(left_value.fld_nm)

                current_code += """
li $t{}, {};
add $t{}, $t{}, $s0;
lw $t{}, ($t{});
# now address of obj is in $t{}
li $t{}, {};
add $t{}, $t{}, $t{};
# now $t{} has fld offset
sw $t{}, ($t{});
                """.format(
                    t,
                    left_value.var.address_offset,
                    t,
                    t,
                    t,
                    t,
                    t,
                    t3,
                    fld.class_offset,
                    t3,
                    t3,
                    t,
                    t3,
                    t1,
                    t3
                )


            elif left_value.is_reference == True:
                current_code = self.append_code(
                    current_code,
                    """
sw $t{}, ($t{});
                    """.format(
                        t1, left_value.number
                    ),
                )
            else:
                current_code = self.append_code(  # ?????????????
                    current_code,
                    """
move ${}, $t{};
                    """.format(
                        left_value.kind + str(left_value.number), t1
                    ),
                )
            # TODO: handle other types

            # free left_value register
            self.t_registers[left_value.number] = False
        else:
            if left_value.is_reference:
                current_code = self.append_code(
                    current_code, self.store_ref_var(left_value, t1)
                )

            elif left_value.type == "int":
                t2 = self.get_a_free_t_register()
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
add $t{}, $t{}, $s{};
sw $t{}, ($t{});
                """.format(
                        t2,
                        left_value.address_offset,
                        t2,
                        t2,
                        1 if left_value.is_global else 0,
                        t1,
                        t2,
                    ),
                )
            elif left_value.type == "string":
                t2 = self.get_a_free_t_register()
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
add $t{}, $t{}, $s{};
sw $v0, ($t{});
                    """.format(
                        t2,
                        left_value.address_offset,
                        t2,
                        t2,
                        1 if left_value.is_global else 0,
                        t2,
                    ),
                )
            elif left_value.type == "bool":
                t2 = self.get_a_free_t_register()
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, {};
add $t{}, $t{}, $s{};
sb $t{}, ($t{});
                """.format(
                        t2,
                        left_value.address_offset,
                        t2,
                        t2,
                        1 if left_value.is_global else 0,
                        t1,
                        t2,
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

    def store_ref_reg(self, reg, new_val):  # x[2] = 3, x[2] = 3.2, x[2] = true
        code = ""
        if reg.type == "int":
            code = """
sw $t{}, ($t{});
                """.format(
                new_val, reg.number
            )
        elif reg.type == "bool":
            code = """
sb $t{}, ($t{});
                """.format(
                new_val, reg.number
            )

        return code

    def store_ref_var(self, var, new_ref):  # x = newArray(4, int)
        t2 = self.get_a_free_t_register()
        code = """
li $t{}, {};
add $t{}, $t{}, $s{};
sw $t{}, ($t{});
                """.format(
            t2, var.address_offset, t2, t2, 1 if var.is_global else 0, new_ref, t2
        )
        return code

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
        # print("ident: {0}".format(args[0].value))
        return args[0]

    """
    Expressions
    """

    def token_to_var(self, args):
        # print("high prior: ")
        # print(args)

        types = ["int", "bool", "double", "string"]

        try:
            child = args[0]
            if isinstance(child, Token) and child.type == "IDENT":

                if child.value in types:  # when identifier is a reserved token
                    return child.value

                # search in all symbol table stack
                sym_tbl = self.symbol_table

                while sym_tbl:
                    # print("sym: {}: {}".format(sym_tbl.function_name, sym_tbl.variables))
                    # print(child.value)
                    if child.value in sym_tbl.variables.keys():
                        v = sym_tbl.variables[child.value]
                        if v.address_offset == None and self.is_in_class:
                            return self.method_call([Token("IDENT", "this"), child])
                        return sym_tbl.variables[child.value]

                    if not self.first_pass:
                        # from last pass symbol
                        last_pass_sym = self.get_symbol_table_from_last_pass(
                            sym_tbl.name
                        )
                        if last_pass_sym and (
                            child.value in last_pass_sym.variables.keys()
                        ):
                            v = last_pass_sym.variables[child.value]
                            if v.address_offset == None and self.is_in_class:
                                return self.method_call([Token("IDENT", "this"), child])
                            return last_pass_sym.variables[child.value]

                    sym_tbl = sym_tbl.parent

                if self.first_pass:
                    reg = Register("int", "t", 0)
                    reg.code = ""
                    return reg

                print("Variable Not Exists!")
                exit(4)

            elif isinstance(child, Variable) and child.type == "double":
                return child
            elif isinstance(child, Register):
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
        # print("minus:")
        # print(args)

        if self.first_pass:
            # not important what the code is
            reg = Register("int", "t", 0)
            reg.code = ""
            return reg

        self.type_checking_for_minus(args[0])

        var = args[0]
        if isinstance(var, Variable):
            if var.type == "int":
                current_code = var.code
                t1 = self.get_a_free_t_register()
                self.t_registers[t1] = True
                t2 = self.get_a_free_t_register()
                current_code = self.append_code(
                    current_code,
                    """
li $t{}, -1;
li $t{}, {};
add $t{}, $t{}, $s{};
lw $t{}, ($t{});
mult $t{}, $t{};
mflo $t{};
                """.format(
                        t1,
                        t2,
                        var.address_offset,
                        t2,
                        t2,
                        1 if var.is_global else 0,
                        t2,
                        t2,
                        t1,
                        t2,
                        t1,
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

    def code_for_loading_opr(self, t_reg, opr):
        # opr type should be int or bool
        code = ""
        if isinstance(opr, Variable):
            if opr.type == "bool":
                code = self.append_code(
                    code, self.code_for_loading_bool_var(t_reg, opr)
                )
            else:
                code = self.append_code(code, self.code_for_loading_int_var(t_reg, opr))

        elif isinstance(opr, Immediate):
            code = self.append_code(
                code,
                """
li $t{}, {};
                """.format(
                    t_reg, opr.value
                ),
            )
        elif isinstance(opr, Register):
            if opr.is_reference == True:
                if opr.type == "int":
                    code = self.append_code(
                        code, self.code_for_loading_int_ref_reg(t_reg, opr)
                    )
                elif opr.type == "bool":
                    code = self.append_code(
                        code, self.code_for_loading_bool_ref_reg(t_reg, opr)
                    )
            else:
                code = self.append_code(
                    code,
                    """
move $t{}, ${};
                """.format(
                        t_reg, opr.kind + str(opr.number)
                    ),
                )
        return code

    def multiply(self, args):
        # print("multiply")
        # print(args)
        opr1 = args[0]
        opr2 = args[1]

        if self.first_pass:
            # not important what the code is
            reg = Register("int", "t", 0)
            reg.code = ""
            return reg

        current_code = ""
        current_code = opr1.code + "\n" + opr2.code

        self.check_type_for_math_expr(opr1, opr2, "*")

        if opr1.type == "double":
            return self.double_operation(opr1, opr2, "mul")

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()

        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t1, opr1)
        )
        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t2, opr2)
        )

        current_code = self.append_code(
            current_code,
            """
mult $t{}, $t{};
mflo $t{};
            """.format(
                t1, t2, t1
            ),
        )

        # todo debug
        if isinstance(opr1, Register) and opr1.kind == "t":
            self.t_registers[opr1.number] = False
        if isinstance(opr2, Register) and opr2.kind == "t":
            self.t_registers[opr2.number] = False

        reg = Register(opr1.type, "t", t1)
        reg.write_code(current_code)
        return reg

    def divide(self, args):
        # print("divide")
        # print(args)
        current_code = ""

        if self.first_pass:
            # not important what the code is
            reg = Register("int", "t", 0)
            reg.code = ""
            return reg

        opr1 = args[0]
        opr2 = args[1]
        current_code = opr1.code + "\n" + opr2.code

        self.check_type_for_math_expr(opr1, opr2, "/")

        if opr1.type == "double":
            return self.double_operation(opr1, opr2, "div")

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()

        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t1, opr1)
        )
        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t2, opr2)
        )

        current_code = self.append_code(
            current_code,
            """
div $t{}, $t{};
mflo $t{};
        """.format(
                t1, t2, t1
            ),
        )

        # todo debug
        if isinstance(opr1, Register) and opr1.kind == "t":
            self.t_registers[opr1.number] = False
        if isinstance(opr2, Register) and opr2.kind == "t":
            self.t_registers[opr2.number] = False

        reg = Register(opr1.type, "t", t1)
        reg.write_code(current_code)
        return reg

    def mod(self, args):
        # print("mod")
        # print(args)

        if self.first_pass:
            # not important what the code is
            reg = Register("int", "t", 0)
            reg.code = ""
            return reg


        current_code = ""
        opr1 = args[0]
        opr2 = args[1]
        current_code = opr1.code + "\n" + opr2.code

        self.check_type_for_math_expr(opr1, opr2, "%")

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()

        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t1, opr1)
        )
        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t2, opr2)
        )

        current_code = self.append_code(
            current_code,
            """
div $t{}, $t{};
mfhi $t{};
            """.format(
                t1, t2, t1
            ),
        )

        # todo debug
        if isinstance(opr1, Register) and opr1.kind == "t":
            self.t_registers[opr1.number] = False
        if isinstance(opr2, Register) and opr2.kind == "t":
            self.t_registers[opr2.number] = False

        reg = Register(opr1.type, "t", t1)
        reg.write_code(current_code)
        return reg

    def not_statement(self, args):
        # print("not statement")
        # print(args)

        if self.first_pass:
            # not important what the code is
            reg = Register("int", "t", 0)
            reg.code = ""
            return reg

        self.type_checking_for_logical_expr(args[0], args[0], "!")

        if isinstance(args[0], Variable):
            current_code = args[0].code
            t1 = self.get_a_free_t_register()
            self.t_registers[t1] = True
            lbl1 = self.get_new_label().name
            lbl2 = self.get_new_label().name
            current_code = self.append_code(
                current_code,
                """
li $t{}, {};
add $t{}, $t{}, $s{};
lb $t{}, ($t{});
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
                    1 if args[0].is_global else 0,
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
                    args[0].kind + str(args[0].number),
                    lbl1,
                    args[0].kind + str(args[0].number),
                    lbl2,
                    lbl1,
                    args[0].kind + str(args[0].number),
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
        f1 = self.load_double_to_reg(opr1)
        f2 = self.load_double_to_reg(opr2)
        current_code = self.append_code(f1.code, f2.code)

        current_code = self.append_code(
            current_code,
            """
{}.d $f{}, $f{}, $f{}
            """.format(
                instruction, f1.number, f1.number, f2.number
            ),
        )
        reg = Register("double", "f", f1.number)
        reg.write_code(current_code)
        return reg

    def add(self, args):
        # print("add")
        # print(args)
        opr1 = args[0]
        opr2 = args[1]
        current_code = opr1.code + "\n" + opr2.code

        if self.first_pass:
            # not important what the code is
            reg = Register("int", "t", 0)
            reg.code = ""
            return reg

        # type checking
        self.check_type_for_math_expr(opr1, opr2, "add")

        if opr1.type == "double":
            reg = self.double_operation(opr1, opr2, "add")
            return reg
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()

        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t1, opr1)
        )
        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t2, opr2)
        )

        current_code = self.append_code(
            current_code,
            """
add $t{}, $t{}, $t{}
        """.format(
                t1, t1, t2
            ),
        )

        # todo debug
        if isinstance(opr1, Register) and opr1.kind == "t":
            self.t_registers[opr1.number] = False
        if isinstance(opr2, Register) and opr2.kind == "t":
            self.t_registers[opr2.number] = False

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
            if self.first_pass:
                return
            print("math expr (+,-,*,/,%) for {} are not allowed".format(opr1.type))
            exit(4)

    def sub(self, args):
        # print("sub")
        # print(args)

        if self.first_pass:
            # not important what the code is
            reg = Register("int", "t", 0)
            reg.code = ""
            return reg

        opr1 = args[0]
        opr2 = args[1]
        self.check_type_for_math_expr(opr1, opr2, "sub")

        if opr1.type == "double":
            return self.double_operation(opr1, opr2, "sub")

        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        current_code = ""
        current_code = opr1.code + "\n" + opr2.code

        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t1, opr1)
        )
        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t2, opr2)
        )

        current_code = self.append_code(
            current_code,
            """
sub $t{}, $t{}, $t{}
        """.format(
                t1, t1, t2
            ),
        )

        # todo debug
        if isinstance(opr1, Register) and opr1.kind == "t":
            self.t_registers[opr1.number] = False
        if isinstance(opr2, Register) and opr2.kind == "t":
            self.t_registers[opr2.number] = False

        reg = Register("int", "t", t1)
        reg.write_code(current_code)

        return reg

    """
    Conditional Part
    """

    def write_conditional_expr(self, opr1, opr2):
        # print(opr1, opr2, "aaaaaaaaaaa")
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        t2 = self.get_a_free_t_register()
        self.t_registers[t2] = True
        current_code = ""

        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t1, opr1)
        )
        current_code = self.append_code(
            current_code, self.code_for_loading_opr(t2, opr2)
        )

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

        # if left_opr.type == "string":
        #     pass  # todo: handle type checking for string

    def handle_condition(self, left_opr, right_opr, inst):

        current_code = ""
        current_code += left_opr.code + "\n" + right_opr.code

        if left_opr.type == "double":
            return self.handle_condition_for_double(left_opr, right_opr, inst)

        if left_opr.type == "string":
            return self.handle_condition_for_string(left_opr, right_opr, inst)

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

        t1.code = current_code + "\n" + t1.code
        t1.code += (
            "\n"
            + """
{} $t{}, $t{}, {};
        
        """.format(
                _map[inst], t1.number, t2.number, label.name
            )
        )

        # t1.write_code(current_code)
        self.map_condition_to_boolian(t1, label)
        self.t_registers[t2.number] = False
        t1.type = "bool"
        return t1

    def load_double_to_reg(self, opr):
        f1 = self.get_a_free_f_register()
        self.f_registers[f1] = True
        t1 = self.get_a_free_t_register()
        code = opr.code
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
add $t{}, $t{}, $s{};
l.d $f{}, ($t{})
                    """.format(
                        t1,
                        opr.address_offset,
                        t1,
                        t1,
                        1 if opr.is_global else 0,
                        f1,
                        t1,
                    ),
                )
        elif isinstance(opr, Register):
            if opr.is_reference == True:
                code = self.append_code(
                    code, self.code_for_loading_double_ref_reg(f1, opr)
                )
            else:
                f1 = opr.number
        reg = Register("double", "f", f1)
        reg.write_code(code)
        return reg

    def load_string_to_reg(self, opr):
        # print("loading string here")
        register = self.get_a_free_t_register()
        self.t_registers[register] = True
        code = ""
        if isinstance(opr, Variable):
            # print("it has address offset")
            code = self.append_code(
                code,
                """
li $t{}, {};
add $t{}, $t{}, $s{};
lw $t{}, ($t{});
            """.format(
                    register,
                    opr.address_offset,
                    register,
                    register,
                    1 if opr.is_global else 0,
                    register,
                    register,
                ),
            )

        if isinstance(opr, Immediate):
            print("is instance immediate")

        reg = Register("string", "t", register)
        reg.write_code(code)
        return reg

    def handle_condition_for_string(self, left_opr, right_opr, inst):
        # print("operands are : ")
        # print(left_opr)
        # print(right_opr)
        right_reg = None
        left_reg = None
        if isinstance(right_opr, Variable):
            right_reg = self.load_string_to_reg(right_opr)
        elif isinstance(right_opr, Immediate):
            reg = self.get_a_free_t_register()
            self.t_registers[reg] = True
            right_reg = Register("string", "t", reg)
            right_reg.code = self.code_for_loading_string_Imm(reg, right_opr)
        elif isinstance(right_opr, Register):
            reg = self.get_a_free_t_register()
            self.t_registers[reg] = True
            right_reg = Register("string", "t", reg)
            right_reg.code = self.code_for_loading_string_ref_reg(reg, right_opr)

        if isinstance(left_opr, Variable):
            left_reg = self.load_string_to_reg(left_opr)
        elif isinstance(left_opr, Immediate):
            reg = self.get_a_free_t_register()
            self.t_registers[reg] = True
            left_reg = Register("string", "t", reg)
            left_reg.code = self.code_for_loading_string_Imm(reg, left_opr)
        elif isinstance(left_opr, Register):
            reg = self.get_a_free_t_register()
            self.t_registers[reg] = True
            left_reg = Register("string", "t", reg)
            left_reg.code = self.code_for_loading_string_ref_reg(reg, left_opr)
        code = self.append_code(left_opr.code, right_opr.code)
        code = self.append_code(code, left_reg.code)
        code = self.append_code(code, right_reg.code)

        result = self.get_a_free_t_register()
        self.t_registers[result] = True
        t0 = self.get_a_free_t_register()
        self.t_registers[t0] = True
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True

        loop = self.get_new_label()
        loop_end = self.get_new_label()
        not_equal = self.get_new_label()
        end = self.get_new_label()
        equal = self.get_new_label()

        eq = 0
        neq = 0

        if inst == "==":
            eq = 1
            neq = 0
        elif inst == "!=":
            print("instruction is not equal")
            eq = 0
            neq = 1
        else:
            pass

        code = self.append_code(
            code,
            """
li $t{}, 0
{}:
lb $t{}, 0($t{})
lb $t{}, 0($t{})
add $t{}, $t{}, 1
add $t{}, $t{}, 1
beqz $t{}, {}
beqz $t{}, {}
bne $t{}, $t{}, {}
beq $t{}, $t{}, {}
{}:
li $t{}, {}
j {}
{}:
li $t{}, {}
j {}
{}:
beq $t{}, $t{}, {}
{}:
                """.format(
                result,
                loop.name,
                t0,
                right_reg.number,
                t1,
                left_reg.number,
                right_reg.number,
                right_reg.number,
                left_reg.number,
                left_reg.number,
                t0,
                loop_end.name,
                t1,
                loop_end.name,
                t0,
                t1,
                not_equal.name,
                t0,
                t1,
                loop.name,
                not_equal.name,
                result,
                neq,
                end.name,
                equal.name,
                result,
                eq,
                end.name,
                loop_end.name,
                t0,
                t1,
                equal.name,
                end.name,
            ),
        )
        self.t_registers[left_reg.number] = False
        self.t_registers[right_reg.number] = False
        self.t_registers[t0] = False
        self.t_registers[t1] = False
        if isinstance(left_opr, Immediate):
            self.t_registers[right_reg.number] = False
        if isinstance(left_opr, Immediate):
            self.t_registers[left_reg.number] = False
        reg = Register("bool", "t", result)
        reg.code = code
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

        if self.first_pass:
            # not important what the code is
            reg = Register("bool", "t", 0)
            reg.code = ""
            return reg

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
            t1.type = "bool"
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

        if self.first_pass:
            # not important what the code is
            reg = Register("bool", "t", 0)
            reg.code = ""
            return reg

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
            t1.type = "bool"
            t1.write_code(current_code)
            return t1
        else:
            pass  # other possible types
        return args[0]

    def _if(self, args):
        print("_if", args)
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
        if isinstance(if_stmt, Result):
            current_code += if_stmt.code
        else:
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
            current_code,
            """
{}:
                    """.format(
                condition_label.name
            ),
        )

        if (
            len(args) == 4
            or len(args) == 2
            or (len(args) == 3 and isinstance(args[1], Register))
        ):
            current_code = self.append_code(current_code, args[1].code)
            current_code = self.append_code(
                current_code,
                """
beq ${}{},$zero,{};
                                """.format(
                    args[1].kind, args[1].number, end_label.name
                ),
            )
        else:
            # print(args[0].code)
            current_code = self.append_code(current_code, args[0].code)
            current_code = self.append_code(
                current_code,
                """
beq ${}{},$zero,{};
                                """.format(
                    args[0].kind, args[0].number, end_label.name
                ),
            )
        if isinstance(args[len(args) - 1], Tree):
            # print(args[len(args) - 1].children[0].code)
            current_code = self.append_code(
                current_code, args[len(args) - 1].children[0].code
            )
        else:
            print("not handled")

        if len(args) == 4:
            current_code = self.append_code(current_code, args[2].code)
        elif len(args) == 3 and isinstance(args[0], Register):
            current_code = self.append_code(current_code, args[1].code)
        current_code = self.append_code(
            current_code,
            """
j {};
{}:
                    """.format(
                condition_label.name, end_label.name
            ),
        )
        if self.break_label is not None:
            current_code = self.append_code(
                current_code,
                """
{}:
            """.format(
                    self.break_label.name
                ),
            )
            self.break_label = None
        result = Result()
        result.write_code(current_code)
        return result

    def _while(self, args):
        # print("while")
        # print(args)
        # print(args[1].children[0].code)
        current_code = ""
        loop_lable = self.get_new_label()
        end_lable = self.get_new_label()
        current_code = self.append_code(
            current_code,
            """
{}:
            """.format(
                loop_lable.name
            ),
        )
        current_code = self.append_code(current_code, args[0].code)
        current_code = self.append_code(
            current_code,
            """
beq ${}{},$zero,{};
            """.format(
                args[0].kind, args[0].number, end_lable.name
            ),
        )
        if isinstance(args[1], Tree):
            current_code = self.append_code(current_code, args[1].children[0].code)
        else:
            print("not handled")
        current_code = self.append_code(
            current_code,
            """
j {};
{}:
            """.format(
                loop_lable.name, end_lable.name
            ),
        )
        if self.break_label is not None:
            current_code = self.append_code(
                current_code,
                """
{}:
                                            """.format(
                    self.break_label.name
                ),
            )
            self.break_label = None
        result = Result()
        result.write_code(current_code)
        return result

    def pass_compare(self, args):
        # print(args[0].value)
        return args[0]

    def pass_equality(self, args):
        return args[0]

    def end_block(self, args):
        # print("stmt_block")
        # print(args)
        code = ""
        for result in args:
            if result is None:
                continue
            if isinstance(result, Tree):
                for child in result.children:
                    code = self.append_code(code, child.code)
            else:
                code = self.append_code(code, result.code)
        result = Result()
        result.code = code

        # used when going to a new function

        #
        self.symbol_table = self.symbol_table.parent
        self.symbol_tables.append(self.symbol_table)

        return result

    def start_block(self, args):
        self.oo_gen.start_block()

    # --------------------------------------------

    def pass_stmt(self, args):
        # print(args, 'pass_stmt')
        re = Result()
        code = ""
        label = self.get_new_label()
        code = self.append_code(
            code,
            """
j {};
        """.format(
                label.name
            ),
        )
        re.code = code
        self.break_label = label
        return re

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
            elif args[0].type == "STRING_CONSTANT":
                return Immediate(args[0].value[1 : len(args[0].value) - 1], "string")
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

    def prevent_tree_generation_for_actual(self, args):
        # print("prevent_tree_generation_for_actual")
        # print(args)
        if isinstance(args[0], list):
            args = args[0] + [args[1]]
        # print(args)
        return args

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

    def _print(self, args):
        # print("print")
        # print(args)
        current_code = ""

        if not isinstance(args[0], list):
            args[0] = [args[0]]

        for inp in args[0]:
            current_code += "\n" + inp.code
            if isinstance(inp, Variable):
                if inp.type == "int":
                    current_code = self.append_code(
                        current_code,
                        """
li $v0, 1;
li $a0, {};
add $a0, $a0, $s{};
lw $a0, ($a0);
syscall
                    """.format(
                            inp.address_offset, 1 if inp.is_global else 0
                        ),
                    )
                elif inp.type == "string":
                    current_code = self.append_code(
                        current_code,
                        """
li $v0, 4;
li $a0, {};
add $a0, $a0, $s{};
lw $a0, ($a0);
syscall
                    """.format(
                            inp.address_offset, 1 if inp.is_global else 0
                        ),
                    )
                elif inp.type == "double":
                    if inp.address_offset == None:
                        current_code = self.append_code(
                            current_code,
                            """
li $v0, 2;
li.d $f12, {};
cvt.s.d $f12, $f12
syscall
	                """.format(
                                inp.value
                            ),
                        )
                    else:
                        t1 = self.get_a_free_t_register()
                        current_code = self.append_code(
                            current_code,
                            """
li $v0, 2;
li $t{}, {};
add $t{}, $t{}, $s{};
l.d $f12, ($t{});
cvt.s.d $f12, $f12
syscall
	                """.format(
                                t1,
                                inp.address_offset,
                                t1,
                                t1,
                                1 if inp.is_global else 0,
                                t1,
                            ),
                        )
                elif inp.type == "bool":
                    t1 = self.get_a_free_t_register()
                    lbl = self.get_new_label().name
                    lbl2 = self.get_new_label().name
                    current_code = self.append_code(
                        current_code,
                        """
li $t{}, {};
add $t{}, $t{}, $s{};
lb $t{}, ($t{});
li $v0, 4;
beq $t{}, $zero, {};
la $a0, true_const;
j {};
{}:
la $a0, false_const;
{}:
syscall
                    """.format(
                            t1,
                            inp.address_offset,
                            t1,
                            t1,
                            1 if inp.is_global else 0,
                            t1,
                            t1,
                            t1,
                            lbl,
                            lbl2,
                            lbl,
                            lbl2,
                        ),
                    )
                else:
                    pass  # other types
            elif isinstance(inp, Register):

                # todo debug
                if isinstance(inp, Register) and inp.kind == "t":
                    if inp.type == "string":
                        current_code = self.append_code(
                            current_code,
                            """
move $a0,$t{};
li $v0, 4;
syscall
                            """.format(
                                inp.number
                            ),
                        )
                    self.t_registers[inp.number] = False

                if inp.type == "bool":
                    lbl1 = self.get_new_label().name
                    lbl2 = self.get_new_label().name
                    reg = inp.kind + str(inp.number)
                    if inp.is_reference == True:
                        current_code = self.append_code(
                            current_code,
                            """
lw ${}, (${})
beq ${}, $zero, {};
la $a0, true_const;
j {};
{}:
la $a0, false_const;
{}:
li $v0, 4;
syscall
                        """.format(
                                reg, reg, reg, lbl1, lbl2, lbl1, lbl2
                            ),
                        )
                    else:
                        current_code = self.append_code(
                            current_code,
                            """
beq ${}, $zero, {};
la $a0, true_const;
j {};
{}:
la $a0, false_const;
{}:
li $v0, 4;
syscall
                    """.format(
                                inp.kind + str(inp.number), lbl1, lbl2, lbl1, lbl2
                            ),
                        )

                elif inp.type == "double":
                    if inp.is_reference == True:
                        current_code = self.append_code(
                            current_code,
                            """
li $v0, 2;
l.d $f12, ($t{});
cvt.s.d $f12, $f12
syscall
	                """.format(
                                inp.number
                            ),
                        )
                    else:
                        current_code = self.append_code(
                            current_code,
                            """
li $v0, 2;
mov.d $f12, $f{};
cvt.s.d $f12, $f12
syscall
                    """.format(
                                inp.number
                            ),
                        )

                elif inp.type == "int":
                    if inp.is_reference == True:
                        current_code = self.append_code(
                            current_code,
                            """
li $v0, 1;
lw $a0, ($t{});
syscall
                        """.format(
                                inp.number
                            ),
                        )
                    else:

                        current_code = self.append_code(
                            current_code,
                            """
li $v0, 1;
move $a0, $t{};
syscall
                        """.format(
                                inp.number
                            ),
                        )

                elif inp.type == "string":
                    if inp.is_reference == True:
                        current_code = self.append_code(
                            current_code,
                            """
li $v0, 4;
lw $a0, ($t{});
syscall
                    """.format(
                                inp.number
                            ),
                        )
                    else:  # func return
                        current_code = self.append_code(
                            current_code,
                            """
move $a0, $v0;
li $v0, 4;
syscall
                    """,
                        )

            elif isinstance(inp, Immediate):
                if inp.type == "bool":
                    pass  # todo
                if inp.type == "string":
                    current_code = self.append_code(
                        current_code,
                        """
    li $v0, 9;
    li $a0, {};
    syscall
                                """.format(
                            len(inp.value) + 1
                        ),
                    )
                    for i in range(len(inp.value) + 1):
                        if i == len(inp.value):
                            current_code = self.append_code(
                                current_code,
                                """
    lb $a0,end_of_string;
    sb $a0,{}($v0);
                                """.format(
                                    i
                                ),
                            )
                        else:
                            current_code = self.append_code(
                                current_code,
                                """
    li $a0,'{}';
    sb $a0,{}($v0);
                                """.format(
                                    inp.value[i], i
                                ),
                            )
                    current_code = self.append_code(
                        current_code,
                        """
    move $a0, $v0;
    li $v0, 4;
    syscall
                        """,
                    )
                else:
                    current_code = self.append_code(
                        current_code,
                        """
    li $v0, 1;
    li $a0, {};
    syscall
                    """.format(
                            inp.value
                        ),
                    )
            else:
                pass  # other types
        result = Result()

        # newline after print
        current_code = (
            current_code
            + "\n"
            + """
li $v0, 4;
la $a0, newline;
syscall
        """
        )
        result.write_code(current_code)
        return result

    """
    Methods from second code generator
    """

    def non_void_func_declare(self, args):
        return self.oo_gen.non_void_func_declare(args)

    def void_func_declare(self, args):
        return self.oo_gen.void_func_declare(args)

    def func_declare(self, args):
        return self.oo_gen.func_declare(args)

    def formal_reduce(self, args):
        return self.oo_gen.formal_reduce(args)

    def return_from_func(self, args):
        return self.oo_gen.return_from_func(args)

    def add_codes(self, args):
        return self.oo_gen.add_codes(args)

    def function_call(self, args):
        return self.oo_gen.function_call(args)

    def method_call(self, args):
        # print("method call")
        # print(args)

        var = self.token_to_var([args[0]])
        if isinstance(var, Array) and args[1].value == "length":
            return self.arr_cgen.arr_length(var)
        
        if len(args) == 2:
            # field call
            return self.oo_gen.field_call(args)
        else:
            return self.oo_gen.mtd_call(args)

    """
    Read Integer
    """

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
    array methods
    """

    def new_array(self, args):
        return self.arr_cgen.new_array(args)

    def access_to_array(self, args):
        print("access")
        print(args)
        return self.arr_cgen.access_to_array(args)

    """
    Previous Code Generator for multi pass
    """

    def set_last_code_gen(self, prev_code_gen):
        self.previous_pass = prev_code_gen
        # move all function calls to new code generator
        self.oo_gen.last_pass_functions = prev_code_gen.oo_gen.functions
        # move symbol tables (move every thing from last pass)
        self.prev_code_gen = prev_code_gen

    def get_symbol_table_from_last_pass(self, sym_id):
        for sym in self.prev_code_gen.symbol_tables:
            if sym.name == sym_id:
                return sym
        return None

    """
    Global Variable
    """

    def global_var_declare(self, args):
        return Result()

    def function_name(self, args):
        # print("function name")
        # print(args[0])
        self.current_function_name = args[0]
        return args[0]

    """
    Class
    """

    def class_declare(self, args):
        return self.oo_gen.class_declare(args)

    def class_dec_finished(self, args):
        # no need to generate code
        self.is_in_class = False
        self.class_name = ""
        return Result()

    def start_class_dec(self, args):
        # print("start class")
        # print(args)
        self.is_in_class = True 
        self.class_name = args[0].value
        # add new class to list
        clss = ClassMetaData()
        clss.name = self.class_name
        if self.first_pass:
            self.oo_gen.classes[clss.name] = clss
        return args[0]

    def method_declare(self, args):
        return self.oo_gen.method_declare(args)

    def create_object(self, args):
        return self.oo_gen.create_object(args)

    """
    Convert
    """

    def itod(self, args):
        print("itod", args[0])
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        opr = args[0]
        code = opr.code
        code = self.append_code(code, self.code_for_loading_opr(t1, opr))
        f1 = self.get_a_free_f_register()
        self.f_registers[f1] = True
        code = self.append_code(
            code,
            """
li $v0, 9;
li $a0, 8;
syscall
sw $t{}, ($v0);
l.d $f{}, ($v0);
cvt.d.w $f{}, $f{};
        """.format(
                t1, f1, f1, f1
            ),
        )
        self.t_registers[t1] = False
        reg = Register("double", "f", f1)
        reg.write_code(code)
        return reg

    def dtoi(self, args):
        print("dtoi", args[0])
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        opr = args[0]
        f1 = self.load_double_to_reg(opr)
        code = self.append_code(opr.code, f1.code)
        code = self.append_code(
            code,
            """
li $v0, 9;
li $a0, 8;
syscall
cvt.w.d $f{}, $f{};
s.d $f{}, ($v0);
lw $t{}, ($v0);
        """.format(
                t1, f1.number, f1.number, f1.number
            ),
        )
        self.f_registers[f1.number] = False
        reg = Register("int", "t", t1)
        reg.write_code(code)
        return reg

    def itob(self, args):
        print("itob", args[0])
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        label = self.get_new_label()
        opr = args[0]
        code = self.append_code(opr.code, self.code_for_loading_opr(t1, opr))
        code = self.append_code(
            code,
            """
beq $t{}, $zero, {};
li $t{}, 1;
{}:
        """.format(
                t1, label.name, t1, label.name
            ),
        )
        reg = Register("bool", "t", t1)
        reg.write_code(code)
        return reg

    def btoi(self, args):
        print("btoi", args[0])
        t1 = self.get_a_free_t_register()
        self.t_registers[t1] = True
        opr = args[0]
        code = self.append_code(opr.code, self.code_for_loading_opr(t1, opr))
        reg = Register("int", "t", t1)
        reg.write_code(code)
        return reg



"""
Other Classes
"""


class Result:
    def __init__(self):
        self.code = ""
        # When going to another function
        self.symbol_table = None

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
        self.is_reference = False
        self.is_global = False
        self.class_offset = None

    def calc_size(self):
        if self.is_reference == True:
            self.size = 4
        else:
            if self.type == "int":
                self.size = 4
            elif self.type == "bool":
                self.size = 1
            elif self.type == "string":
                self.size = 4  # address of string
            elif self.type == "double":
                self.size = 8
            else:
                self.size = 4
        if "[]" in self.type:
            self.size = 4
            self.is_reference = True

        # var type is an object

    def __str__(self):
        return "Variable name: {}, type: {}, value: {}, size: {}, is_reference: {}".format(
            self.name, self.type, self.value, self.size, self.is_reference
        )

    def __repr__(self):
        return "Variable name: {}, type: {}, value: {}, size: {}, is_reference: {}".format(
            self.name, self.type, self.value, self.size, self.is_reference
        )


class Register(Result):
    def __init__(self, _type, kind, number):
        super().__init__()
        self.type = _type  # int, string, boolian, double
        self.kind = kind  # s, v, a, t
        self.number = number
        # self.is_bool = False
        self.is_reference = False  # later
        
        self.is_obj = False
        self.cls_nm = None
        self.fld_nm = None
        self.var = None
        self.addr_register = None

    def __str__(self):
        return "register type:{}, kind: {}, number: {}, is_ref: {}".format(
            self.type, self.kind, self.number, self.is_reference
        )

    def __repr__(self):
        return "register type:{}, kind: {}, number: {},  is_ref: {}".format(
            self.type, self.kind, self.number, self.is_reference
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

    def __str__(self):
        return "Array name: {}, type: {}, value: {}, size: {}, is_reference: {}".format(
            self.name, self.type, self.value, self.size, self.is_reference
        )

    def __repr__(self):
        return "Array name: {}, type: {}, value: {}, size: {}, is_reference: {}".format(
            self.name, self.type, self.value, self.size, self.is_reference
        )
