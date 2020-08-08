from lark import Transformer, Tree
from lark.lexer import Lexer, Token
import CodeGenerator


class ObjectOrientedCodeGen:
    def __init__(self, main_code_gen):
        # symbol table id
        self.symbol_table_id = 1000

        self.main_code_gen = main_code_gen
        self.main_code_gen.symbol_table = SymbolTable(self.symbol_table_id)
        self.symbol_table_id += 1
        self.main_code_gen.symbol_table.function_name = "7777global7777"
        self.main_code_gen.symbol_tables = [self.main_code_gen.symbol_table]
        # saving parameters for function
        self.current_function_signiture = []
        # all functions
        self.functions = {}
        # last pass functions
        self.last_pass_functions = {}
        # return value of last defined functin
        self.return_value = None
        # function declaration started
        self.func_start = False
        # array of ClassMetaData type
        self.classes = {}
        # class method codes
        self.methods_code = ""

    """
    Function Declaration
    """

    def non_void_func_declare(self, args):
        # print("non void function")
        # print(args)
        return args

    def void_func_declare(self, args):
        # print("void func")
        # print(args)
        args[
            4
        ].code += """
lw $ra, 4($s0);
lw $s0, ($s0)
jr $ra;
        """
        return args

    def func_declare(self, args):
        # print("all functions:")
        # print(args)
        # pass two above reductions
        args = args[0]

        func_return_type = args[0]
        if isinstance(args[1], Token) and args[1].type == "IDENT":
            function_name = args[1].value
        else:
            print("Error in Function Declaration!")
            exit(4)

        input_parameters = args[3]  # array of Trees
        function_body = args[4]  # type = Result

        # remove one symbol table from the stack (for func arguments)
        # print("sym after func {}: {}".format(function_name, self.main_code_gen.symbol_table.name))
        self.main_code_gen.symbol_table = self.main_code_gen.symbol_table.parent
        self.main_code_gen.symbol_tables.append(self.main_code_gen.symbol_table)
        self.func_start = False
        self.main_code_gen.current_function_name = "7777global7777"

        # generate code if 'main'
        if function_name == "main" and func_return_type == "int":
            self.main_code_gen.write_code(
                function_body.code
            )  # main is not being called ?
            # exit
            self.main_code_gen.write_code(
                """
li $v0, 10;
syscall;
            """
            )
            return None

        func = Function(function_name)
        func.arguments = self.current_function_signiture
        func.return_type = func_return_type

        # clear function_signiture
        self.current_function_signiture = []
        # add to function list
        if function_name in self.functions.keys():
            print("This Function Exists!")
            exit(4)

        self.functions[function_name] = func

        # main function code:
        code = ""
        # function label
        code = self.main_code_gen.append_code(code, function_name + ":")
        # store $ra
        code = self.main_code_gen.append_code(
            code,
            """
sw $ra, 4($s0);
        """,
        )
        # statement code
        # print("body")
        # print(function_body.code)
        code = self.main_code_gen.append_code(code, function_body.code)

        result = CodeGenerator.Result()
        result.code = code
        return result

    def formal_reduce(self, args):
        # print("formal reduce....")
        # print(args)

        # flag for start of function declaration
        self.func_start = True

        if self.main_code_gen.is_in_class:
            to = Token("IDENT", "this")
            t = Tree("variable",[self.main_code_gen.class_name, to])
            args = [t] + args
            # args.append(t)

        # set variables above the frame
        last_offset = 0
        last_size = 0
        for var in args:
            if isinstance(var, Tree):
                variable = CodeGenerator.Variable()
                variable.name = var.children[1].value
                variable.type = var.children[0]

                variable.calc_size()
                # print(variable, "aaaaaaaaa")
                new_offset = last_offset - variable.size
                new_offset = -new_offset
                variable.address_offset = (
                    -new_offset
                    if new_offset % variable.size == 0
                    else -1
                    * (new_offset + (variable.size - new_offset % variable.size))
                )
                last_offset = variable.address_offset
                last_size = variable.size
                self.current_function_signiture.append(variable)
        return args

    """ 
    return to $v0
    """

    def return_from_func(self, args):
        print("return")
        print(args)
        expr = args[0].children
        code = ""
        if len(expr) == 0:
            if self.main_code_gen.func_type_tmp == "void":
                code = """
lw $ra, 4($s0);
lw $s0, ($s0)
jr $ra;
                """
                self.main_code_gen.func_type_tmp = None
            else:
                print("Invalid Return Type!")
                exit(4)
        else:
            result = expr[0]
            code = result.code
            if isinstance(result, CodeGenerator.Variable):
                # print(result.type)
                # print(self.main_code_gen.func_type_tmp)
                if self.main_code_gen.func_type_tmp == result.type:
                    # if type is double, return value is in $f0
                    # other wise the return value is in $v0
                    if result.type == "double":
                        code += """
lw $ra, 4($s0);
l.d $f0, {}($s0);
lw $s0, ($s0)
jr $ra;
                        """.format(
                            result.address_offset
                        )
                    else:
                        code += """
lw $ra, 4($s0);
lw $v0, {}($s0);
lw $s0, ($s0)
jr $ra;
                        """.format(
                            result.address_offset
                        )
                    self.main_code_gen.func_type_tmp = None
                else:
                    print("Invalid Return Type!")
                    exit(4)
            elif isinstance(result, CodeGenerator.Register):
                if not self.main_code_gen.func_type_tmp == result.type:
                    print("Invalid return type!")
                    exit(4)
                elif result.type == "double":
                    code += """
lw $ra, 4($s0);
mov.d $f0, $f{};
lw $s0, ($s0);
jr $ra;
                """.format(
                        result.number
                    )
                else:
                    code += """
lw $ra, 4($s0);
move $v0, ${};
lw $s0, ($s0);
jr $ra;
                """.format(
                        result.kind + str(result.number)
                    )
            elif isinstance(result, CodeGenerator.Immediate):
                if not self.main_code_gen.func_type_tmp == result.type:
                    print("Invalid return type!")
                    exit(4)
                if result.type == "string":
                    t1 = self.main_code_gen.get_a_free_t_register()
                    self.main_code_gen.t_registers[t1] = True
                    code = self.main_code_gen.code_for_loading_string_Imm(t1, result)
                    code += """
lw $ra, 4($s0);
move $v0, $t{};
lw $s0, ($s0);
jr $ra;
                    """.format(
                        t1
                    )
                elif result.type == "bool":
                    code += """
lw $ra, 4($s0);
li $v0, {};
lw $s0, ($s0);
jr $ra;
                    """.format(
                        result.value
                    )
                elif result.type == "double":
                    code += """
lw $ra, 4($s0);
li.d $f0, {};
lw $s0, ($s0);
jr $ra;
                    """.format(
                        result.value
                    )
                elif result.type == "int":
                    code += """
lw $ra, 4($s0);
li $v0, {};
lw $s0, ($s0);
jr $ra;
                    """.format(
                        result.value
                    )
            else:
                print("Unknown Type in Return!")
                exit(4)
        result = CodeGenerator.Result()
        result.code = code
        return result

    """
    At Last, Add Generated Codes
    """

    def add_codes(self, args):
        # print("last")
        # print(args)
        for code in args:
            if code:
                self.main_code_gen.write_code(code.code)
        
        self.main_code_gen.write_code(self.methods_code)
        return args

    """
    Call a Function
    """

    def function_call(self, args):
        # print("function_call")
        # print(args)

        if self.main_code_gen.first_pass:
            # not important what the code is
            reg = CodeGenerator.Register("int", "t", 0)
            reg.code = ""
            return reg

        func_name = args[0]
        func_name = func_name.value
        try:
            arguments = args[1].children
        except AttributeError:
            if isinstance(args[1], list):
                arguments = args[1]
            else:
                arguments = [args[1]]
        except IndexError:
            arguments = []

        try:
            func = self.functions[func_name]
        except KeyError:
            try:
                func = self.last_pass_functions[func_name]
            except KeyError:
                if self.main_code_gen.first_pass:
                    # not important what the code is
                    reg = CodeGenerator.Register("int", "t", 0)
                    reg.code = ""
                    return reg
                else:
                    print("function {} not exists".format(func_name))
                    exit(4)

        # check number of inputs
        if len(func.arguments) != len(arguments):
            print("Invalid Parameters Type for Function!")
            exit(4)
        # check type of inputs
        for i in range(len(arguments)):
            if func.arguments[i].type != arguments[i].type:
                print("Invalid Parameter input!")
                exit(4)
        code = ""
        total_param_size = 0
        for par in func.arguments:
            total_param_size += par.size

        self.main_code_gen.get_last_variable_in_frame()
        offset = (
            self.main_code_gen.last_var_in_fp.size
            + self.main_code_gen.last_var_in_fp.address_offset
            + total_param_size
        )
        new_offset = offset if offset % 8 == 0 else (offset + (8 - offset % 8))

        t1 = self.main_code_gen.get_a_free_t_register()
        self.main_code_gen.t_registers[t1] = True
        t2 = self.main_code_gen.get_a_free_t_register()
        self.main_code_gen.t_registers[t2] = True
        t3 = self.main_code_gen.get_a_free_t_register()
        f1 = self.main_code_gen.get_a_free_f_register()

        code = self.main_code_gen.append_code(
            code,
            """
li $t{}, {};
        """.format(
                t1, new_offset
            ),
        )

        for i in range(len(func.arguments)):
            var = func.arguments[i]
            input_var = arguments[i]
            off = var.address_offset

            # add codes of arguments
            code += "\n" + input_var.code

            code = self.main_code_gen.append_code(
                code,
                """
li $t{}, {};
add $t{}, $t{}, $t{};
            """.format(
                    t2, off, t2, t2, t1
                ),
            )
            # $t2 has the address for input parameter

            if isinstance(input_var, CodeGenerator.Variable):
                if (
                    input_var.type == "int"
                    or input_var.type == "string"
                    or input_var.is_reference == True
                ):
                    code = self.main_code_gen.append_code(
                        code,
                        """
lw $t{}, {}($s{});
add $t{}, $t{}, $s{};
sw $t{}, ($t{});
                    """.format(
                            t3,
                            input_var.address_offset,
                            1 if input_var.is_global else 0,
                            t2,
                            t2,
                            1 if input_var.is_global else 0,
                            t3,
                            t2,
                        ),
                    )
                elif input_var.type == "bool":
                    code = self.main_code_gen.append_code(
                        code,
                        """
lb $t{}, {}($s{});
add $t{}, $t{}, $s{};
sb $t{}, ($t{});
                    """.format(
                            t3,
                            input_var.address_offset,
                            1 if input_var.is_global else 0,
                            t2,
                            t2,
                            1 if input_var.is_global else 0,
                            t3,
                            t2,
                        ),
                    )
                elif input_var.type == "double":
                    if input_var.address_offset == None:
                        code = self.main_code_gen.append_code(
                            code,
                            """
li.d $f{}, {};
add $t{}, $t{}, $s{};
s.d $f{}, ($t{});
                    """.format(
                                f1,
                                input_var.value,
                                t2,
                                t2,
                                1 if input_var.is_global else 0,
                                f1,
                                t2,
                            ),
                        )
                    else:
                        code = self.main_code_gen.append_code(
                            code,
                            """
l.d $f{}, {}($s{});
add $t{}, $t{}, $s{};
s.d $f{}, ($t{});
                    """.format(
                                f1,
                                input_var.address_offset,
                                1 if input_var.is_global else 0,
                                t2,
                                t2,
                                1 if input_var.is_global else 0,
                                f1,
                                t2,
                            ),
                        )
                else:
                    pass  # other types
            elif isinstance(input_var, CodeGenerator.Register):
                if input_var.type == "int":
                    if input_var.is_reference == True:
                        code = self.main_code_gen.append_code(
                            code,
                            """
lw $t{}, (${});
add $t{}, $t{}, $s0;
sw $t{}, ($t{});
                    """.format(
                                t3,
                                input_var.kind + str(input_var.number),
                                t2,
                                t2,
                                t3,
                                t2,
                            ),
                        )
                    else:
                        code = self.main_code_gen.append_code(
                            code,
                            """
move $t{}, ${};
add $t{}, $t{}, $s0;
sw $t{}, ($t{});
                    """.format(
                                t3,
                                input_var.kind + str(input_var.number),
                                t2,
                                t2,
                                t3,
                                t2,
                            ),
                        )
                if input_var.type == "string":
                    if input_var.is_reference == True:
                        code = self.main_code_gen.append_code(
                            code,
                            """
lw $t{}, (${});
add $t{}, $t{}, $s0;
sw $t{}, ($t{});
                    """.format(
                                t3,
                                input_var.kind + str(input_var.number),
                                t2,
                                t2,
                                t3,
                                t2,
                            ),
                        )
                    else:
                        code = self.main_code_gen.append_code(
                            code,
                            """
move $t{}, ${};
add $t{}, $t{}, $s0;
sw $t{}, ($t{});
                    """.format(
                                t3,
                                input_var.kind + str(input_var.number),
                                t2,
                                t2,
                                t3,
                                t2,
                            ),
                        )
                elif input_var.type == "bool":
                    if input_var.is_reference == True:
                        code = self.main_code_gen.append_code(
                            code,
                            """
lb $t{}, (${});
add $t{}, $t{}, $s0;
sb $t{}, ($t{});
                    """.format(
                                t3,
                                input_var.kind + str(input_var.number),
                                t2,
                                t2,
                                t3,
                                t2,
                            ),
                        )
                    else:
                        code = self.main_code_gen.append_code(
                            code,
                            """
move $t{}, ${};
add $t{}, $t{}, $s0;
sb $t{}, ($t{});
                    """.format(
                                t3,
                                input_var.kind + str(input_var.number),
                                t2,
                                t2,
                                t3,
                                t2,
                            ),
                        )
                elif input_var.type == "double":
                    if input_var.is_reference == True:
                        code = self.main_code_gen.append_code(
                            code,
                            """
l.d $f{}, (${});
add $t{}, $t{}, $s0;
s.d $t{}, ($t{});
                    """.format(
                                f1,
                                input_var.kind + str(input_var.number),
                                t2,
                                t2,
                                f1,
                                t2,
                            ),
                        )
                    else:
                        code = self.main_code_gen.append_code(
                            code,
                            """
mov.d $f{}, ${};
add $t{}, $t{}, $s0;
s.d $t{}, ($t{});
                    """.format(
                                f1,
                                input_var.kind + str(input_var.number),
                                t2,
                                t2,
                                f1,
                                t2,
                            ),
                        )
                else:
                    pass  # other types
            elif isinstance(input_var, CodeGenerator.Immediate):
                if input_var.type == "int":
                    code += """
li $t{}, {};
add $t{}, $t{}, $s0;
sw $t{}, ($t{});
                    """.format(
                        t3, input_var.value, t2, t2, t3, t2,
                    )
                elif input_var.type == "bool":  # todo check
                    code += """
li $t{}, {};
add $t{}, $t{}, $s0;
sb $t{}, ($t{});
                    """.format(
                        t3, input_var.value, t2, t2, t3, t2,
                    )
                elif input_var.type == "string":
                    code += self.main_code_gen.code_for_loading_string_Imm(
                        t3, input_var
                    )
                    code += """
add $t{}, $t{}, $s0;
sw $t{}, ($t{});
                    """.format(
                        t2, t2, t3, t2
                    )

        self.main_code_gen.t_registers[t1] = False
        self.main_code_gen.t_registers[t2] = False
        # store current fp
        code = (
            code
            + "\n"
            + """
li $t{}, {};
add $t{}, $t{}, $s0;
sw $s0, ($t{});
        """.format(
                t3, new_offset, t3, t3, t3
            )
        )

        # change fp
        code = (
            code
            + "\n"
            + """
move $t{}, $s0;
add $t{}, $t{}, {}
move $s0, $t{};
jal {};
        """.format(
                t3, t3, t3, new_offset, t3, func_name
            )
        )

        # returning from function
        #         code = (
        #             code
        #             + "\n"
        #             + """
        # li $t{}, {};
        # lw $s0, ($t{});
        #         """.format(
        #                 t3, new_offset, t3
        #             )
        #         )

        # get output
        code = (
            code
            + "\n"
            + """
move $t{}, $v0;
        """.format(
                t3
            )
        )

        # use t3 as result holder
        self.main_code_gen.t_registers[t3] = True
        reg = CodeGenerator.Register(func.return_type, "t", t3)
        reg.code = code

        return reg

    def start_block(self):
        # print("start block")

        # function arguments block
        if self.func_start:
            func_args_symbol_table = SymbolTable(self.symbol_table_id)
            self.symbol_table_id += 1
            func_args_symbol_table.function_name = (
                self.main_code_gen.current_function_name
            )
            func_args_symbol_table.parent = self.main_code_gen.symbol_table
            self.main_code_gen.symbol_table = func_args_symbol_table
            self.main_code_gen.symbol_tables.append(func_args_symbol_table)
            for var in self.current_function_signiture:
                func_args_symbol_table.variables[var.name] = var
        # ------------------------

        sym_tbl = SymbolTable(self.symbol_table_id)
        self.symbol_table_id += 1
        sym_tbl.function_name = self.main_code_gen.current_function_name
        sym_tbl.parent = self.main_code_gen.symbol_table
        self.main_code_gen.symbol_tables.append(sym_tbl)
        self.main_code_gen.symbol_table = sym_tbl


    '''
    Classes in Decaf
    '''

    def class_declare(self, args):
        # print("class: ")
        # print(args)

        return args

    def method_declare(self, args):
        # print("method: ")
        # print(args)
        args[0][1].value = self.main_code_gen.class_name + "." + args[0][1].value
        # add name of method
        if self.main_code_gen.first_pass:
            self.classes[self.main_code_gen.class_name].methods.append(args[0][1].value)
        self.methods_code += "\n" + self.func_declare(args).code
        # return args

    def field_call(self, args):
        var_name = args[0].value
        field_name = args[1].value

        # print("var name: {}, field name: {}".format(var_name, field_name))

        if self.main_code_gen.first_pass:
            return CodeGenerator.Register("int", "t", 0)

        variable = self.main_code_gen.token_to_var([args[0]])
        clss = self.classes[variable.type]
        fld = clss.get_field(field_name)

        # write value to t2

        if fld.type == "bool":
            pass    # todo
        elif fld.type == "string":
            pass    # todo
        elif fld.type == "double":
            pass    # todo
        else:   
            # 4 byte fields
            # get field from variable address
            t2 = self.main_code_gen.get_a_free_t_register()
            self.main_code_gen.t_registers[t2] = True
            t1 = self.main_code_gen.get_a_free_t_register()

            code = """
# get address of obj
li $t{}, {};
add $t{}, $t{}, $s0;
lw $t{}, ($t{})

# now $t{} has the address of obj
li $t{}, {};
add $t{}, $t{}, $t{};

# now $t{} has address of field
lw $t{}, ($t{});
# field moved to $t{}
            """.format(
                t1,
                variable.address_offset,
                t1,
                t1,
                t1,
                t1,
                t1,
                t2,
                fld.class_offset,
                t1,
                t1,
                t2,
                t1,
                t2,
                t1,
                t2
            )

        reg = CodeGenerator.Register(fld.type, "t", t2)
        reg.code = code
        reg.is_obj = True
        reg.cls_nm = variable.type
        reg.fld_nm = field_name
        reg.var = variable
        return reg


        
    def create_object(self, args):
        # print("create obj:")
        # print(args)

        if self.main_code_gen.first_pass:
            return CodeGenerator.Register("int", "t", 0)

        cls_name = args[0].value
        clss = self.classes[cls_name]
        t1 = self.main_code_gen.get_a_free_t_register()
        code = """
# create object for {}
li $v0, 9;
li $a0, {};
syscall
# move address to t1
move $t{}, $v0;
        """.format(
            cls_name,
            clss.get_full_size(),
            t1
        )
        self.main_code_gen.t_registers[t1] = True
        reg = CodeGenerator.Register(cls_name, "t", t1)
        reg.is_reference = True
        reg.code = code
        return reg

    def mtd_call(self, args):
        # print("mtd_call")
        # print(args)

        var = self.main_code_gen.token_to_var([args[0]])
        fnc_nm = var.type + "." + args[1].value

        # args[2].append(var)
        if isinstance(args[2], list):
            args[2] = [var] + args[2]
        else:
            args[2] = [var] + [args[2]]

        t = Token("IDENT", fnc_nm)
        args = [t, args[2]]
        return self.function_call(args)

        




class Function:
    def __init__(self, name):
        self.name = name
        self.return_type = None
        self.arguments = None


class SymbolTable:
    id = 0

    def __init__(self, id):
        super().__init__()
        self.variables = {}
        self.parent = None
        self.name = id
        self.function_name = None


# Saves fields and other data about declared classes
class ClassMetaData:

    def __init__(self):
        super().__init__()
        # self.name = ""
        self.fields = []        # list of 'Variable' s with no address
        self.methods = []       # list of 'Strings' of method name. (class.method)
        self.last_var = None

    def get_full_size(self):
        s = 0
        for f in self.fields:
            s += f.size
        return s

    def get_field(self, fild_name):
        for f in self.fields:
            if f.name == fild_name:
                return f



