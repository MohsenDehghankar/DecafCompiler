from lark import Transformer, Tree
from lark.lexer import Lexer, Token
import CodeGenerator


class ArrayCodeGen:
    tmp_var_id_read = 1

    def __init__(self, main_code_gen):
        self.main_code_gen = main_code_gen

    def new_array(self, args):
        # print("new array", args)
        _type = args[1] + "[]"
        arr_len = int(args[0].value)
        var = self.main_code_gen.create_variable(
            _type, "new_array" + str(ArrayCodeGen.tmp_var_id_read), True
        )
        arr_size = (arr_len + 1) * var.size  # first position used for arr.len
        if arr_len == 0:
            arr_size = 0
        t1 = self.main_code_gen.get_a_free_t_register()
        code = """
li $a0, {};
li $v0, 9;
syscall
li $t{} , {};
sw $t{}, 0($v0);
li $t{}, {}
sw $v0, frame_pointer($t{})
        """.format(
            arr_size, t1, arr_len, t1, t1, var.address_offset, t1
        )
        var.write_code(code)
        return var

    def type_checking_for_arr_access(self, args):
        if args[1].type != "int":
            print("index for access to array should be int")
            exit(4)
        if int(args[1].value) < 0:
            print("index should >= zero")
            exit(4)
        arr_name = args[0]
        if (
            isinstance(self.main_code_gen.symbol_table[arr_name], CodeGenerator.Array)
            == False
        ):
            print("{} is not array object".format(arr_name))
            exit(4)

    def access_to_array(self, args):
        print("access to array", args)
        self.type_checking_for_arr_access(args)
        arr_name = args[0]
        index = int(args[1].value)

        arr = self.main_code_gen.symbol_table[arr_name]
        t1 = self.main_code_gen.get_a_free_t_register()
        self.main_code_gen.t_registers[t1] = True
        # TODO: lb for bool and load for double
        code = """
li $t{}, {};
lw $t{}, frame_pointer($t{});
addi $t{}, $t{}, {};
        """.format(
            t1, arr.address_offset, t1, t1, t1, t1, (index + 1) * arr.size
        )
        output_type = arr.type.split("[]")[0]  # int[][] -> int
        reg = CodeGenerator.Register(output_type, "t", t1)
        reg.is_reference = True
        reg.write_code(code)

        return reg

    def arr_length(self, args):
        print("arr.length()", args)
        return args
