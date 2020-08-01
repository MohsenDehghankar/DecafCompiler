from lark import Transformer, Tree
from lark.lexer import Lexer, Token
import CodeGenerator



class ObjectOrientedCodeGen:
    def __init__(self, main_code_gen):
        self.main_code_gen = main_code_gen
        # saving parameters for function
        self.current_function_signiture = []
        # all functions
        self.functions = {}
        # last pass functions
        self.last_pass_functions = {}
        # return value of last defined functin
        self.return_value = None

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
        args[4].code += """
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

        # generate code if 'main'
# =======
#        input_parameters = args[2].children
#        function_body = args[3]  # type = Result
#
#        # generate code
# >>>>>>> master
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
        # create symbol table for this function
        self.main_code_gen.symbol_tables[function_name] = function_body.symbol_table
        # clear last symbol table
        self.main_code_gen.symbol_table = {}
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

        # set variables above the frame
        last_offset = 0
        last_size = 0
        for var in args:
            if isinstance(var, Tree):
                variable = CodeGenerator.Variable()
                variable.name = var.children[1].value
                variable.type = var.children[0]
                variable.calc_size()
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

        # show
        # for v in self.current_function_signiture:
        #     print(
        #         "name: {}, type: {}, offset: {}".format(
        #             self.current_function_signiture[v].name,
        #             self.current_function_signiture[v].type,
        #             self.current_function_signiture[v].address_offset,
        #         )
        #     )

        return args

    def return_from_func(self, args):
        # print("return")
        # print(args)
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
            if isinstance(result, CodeGenerator.Variable):
                # print(result.type)
                # print(self.main_code_gen.func_type_tmp)
                if self.main_code_gen.func_type_tmp == result.type:
                    # if type is double, return value is in $f0
                    # other wise the return value is in $v0
                    if result.type == "double":
                        code = """
lw $ra, 4($s0);
l.d $f0, {}($s0);
lw $s0, ($s0)
jr $ra;
                        """.format(
                            result.address_offset
                        )
                    else:
                        code = """
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
            else:
                pass  # todo other types
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
        return args

    """
    Call a Function
    """

    def function_call(self, args):
        print("function_call")
        print(args)
        
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

        # ---------
        print("function {} call".format(func_name))

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

            code = self.main_code_gen.append_code(
                code,
                """
li $t{}, {};
add $t{}, $t{}, $t{};
            """.format(
                    t2, off, t2, t2, t1
                ),
            )
            # $t2 has the address

            if isinstance(input_var, CodeGenerator.Variable):
                if var.type == "int" or var.type == "string":
                    code = self.main_code_gen.append_code(
                        code,
                        """
lw $t{}, {}($s0);
add $t{}, $t{}, $s0;
sw $t{}, ($t{});
                    """.format(
                            t3, input_var.address_offset, t2, t2, t3, t2
                        ),
                    )
                elif var.type == "bool":
                    code = self.main_code_gen.append_code(
                        code,
                        """
lb $t{}, {}($s0);
add $t{}, $t{}, $s0;
sb $t{}, ($t{});
                    """.format(
                            t3, input_var.address_offset, t2, t2, t3, t2
                        ),
                    )
                elif var.type == "double":
                    code = self.main_code_gen.append_code(
                        code,
                        """
l.d $f{}, {}($s0);
add $t{}, $t{}, $s0;
s.d $f{}, ($t{});
                    """.format(
                            f1, input_var.address_offset, t2, t2, f1, t2
                        ),
                    )
                else:
                    pass  # other types
            elif isinstance(input_var, CodeGenerator.Register):
                if var.type == "int" or var.type == "string":
                    code = self.main_code_gen.append_code(
                        code,
                        """
move $t{}, ${};
add $t{}, $t{}, $s0;
sw $t{}, ($t{});
                    """.format(
                            t3, input_var.kind + str(input_var.number), t2, t2, t3, t2
                        ),
                    )
                elif var.type == "bool":
                    code = self.main_code_gen.append_code(
                        code,
                        """
move $t{}, ${};
add $t{}, $t{}, $s0;
sb $t{}, ($t{});
                    """.format(
                            t3, input_var.kind + str(input_var.number), t2, t2, t3, t2
                        ),
                    )
                else:
                    pass  # other types
            elif isinstance(input_var, CodeGenerator.Immediate):
                pass  # todo: other types

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


class Function:
    def __init__(self, name):
        self.name = name
        self.return_type = None
        self.arguments = None

# =======
#    def void_func_declare(self, args):
#        pass
# >>>>>>> master
