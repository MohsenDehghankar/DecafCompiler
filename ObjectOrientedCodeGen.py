from lark import Transformer, Tree
from lark.lexer import Lexer, Token
import CodeGenerator


class ObjectOrientedCodeGen:
    def __init__(self, main_code_gen):
        self.main_code_gen = main_code_gen
        # saving parameters for function
        self.current_function_signiture = {}
        # all functions
        self.functions = {}
        # return value of last defined functin
        self.return_value = None

    def non_void_func_declare(self, args):
        # print("non void function")
        # print(args)
        return args

    def void_func_declare(self, args):
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
        if function_name == "main" and func_return_type == "int":
            self.main_code_gen.write_code(function_body.code)  # main is not being called ?
            # exit
            self.main_code_gen.write_code("""
li $v0, 10;
syscall;
            """)
            return None

        # create symbol table for this function
        self.main_code_gen.symbol_tables[function_name] = function_body.symbol_table
        # clear last symbol table
        self.main_code_gen.symbol_table = {}
        # clear function_signiture
        self.current_function_signiture = {}
        # add to function list
        if function_name in self.functions.keys():
            print("This Function Exists!")
            exit(4)

        func = Function(function_name)

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
                self.current_function_signiture[variable.name] = variable

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
jr $ra;
                        """.format(result.address_offset)
                    else:
                        code = """
lw $ra, 4($s0);
lw $v0, {}($s0);
jr $ra;
                        """.format(result.address_offset)
                    self.main_code_gen.func_type_tmp = None
                else:
                    print("Invalid Return Type!")
                    exit(4)
            else:
                pass    # todo other types   
        result = CodeGenerator.Result()
        result.code = code     
        return result

    def add_codes(self, args):
        # print("last")
        # print(args)
        for code in args:
            if code:
                self.main_code_gen.write_code(code.code)
        return args

class Function:
    def __init__(self, name):
        self.name = name

