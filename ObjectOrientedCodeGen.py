from lark import Transformer, Tree
from lark.lexer import Lexer, Token

class ObjectOrientedCodeGen:
    def __init__(self, main_code_gen):
        self.main_code_gen = main_code_gen

    def non_void_func_declare(self, args):
        print("non void function")
        print(args)
        func_return_type = args[0]
        if isinstance(args[1], Token) and args[1].type == 'IDENT':
            function_name = args[1].value
        else:
            print("Error in Function Declaration!")
            exit(4)

        input_parameters = args[2].children
        function_body = args[3]         # type = Result
        

        return args

    def void_func_declare(self, args):
        pass