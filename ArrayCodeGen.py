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
add $t{}, $t{}, $s{};
sw $v0, ($t{})
lw $t{}, ($t{})
        """.format(
            arr_size,
            t1,
            arr_len,
            t1,
            t1,
            var.address_offset,
            t1,
            t1,
            1 if var.is_global else 0,
            t1,
            t1,
            t1,
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
        # if (
        #     isinstance(self.main_code_gen.symbol_table[arr_name], CodeGenerator.Array)
        #     == False
        # ):
        #     print("{} is not array object".format(arr_name))
        #     exit(4)

    def get_output_type(self, arr_type):
        return arr_type[0 : len(arr_type) - 2]

    def access_to_array(self, args):
        print("access to array", args)
        self.type_checking_for_arr_access(args)
        arr_name = args[0]
        index = int(args[1].value)

        if isinstance(arr_name, Token):
            # arr = self.main_code_gen.symbol_table.variables[arr_name.value]
            arr = self.main_code_gen.token_to_var([arr_name])
            t1 = self.main_code_gen.get_a_free_t_register()
            self.main_code_gen.t_registers[t1] = True
            code = """
li $t{}, {};
add $t{}, $t{}, $s{}
lw $t{}, ($t{});
addi $t{}, $t{}, {};
            """.format(
                t1,
                arr.address_offset,
                t1,
                t1,
                1 if arr.is_global else 0,
                t1,
                t1,
                t1,
                t1,
                (index + 1) * self.calc_size_of_index(arr.type),
            )
            output_type = self.get_output_type(arr.type)  # int[][] -> int[]
            reg = CodeGenerator.Register(output_type, "t", t1)
            reg.is_reference = True
            reg.write_code(code)
            return reg
        elif isinstance(arr_name, CodeGenerator.Register):  #   x[2][3]
            reg = arr_name
            t1 = self.main_code_gen.get_a_free_t_register()
            self.main_code_gen.t_registers[t1] = True
            code = self.main_code_gen.append_code(
                reg.code,
                """
lw $t{}, ($t{});
addi $t{}, $t{}, {};
            """.format(
                    t1,
                    reg.number,
                    t1,
                    t1,
                    (index + 1) * self.calc_size_of_index(reg.type),
                ),
            )
            output_type = self.get_output_type(reg.type)  # int[][] -> int[]
            reg = CodeGenerator.Register(output_type, "t", t1)
            reg.is_reference = True
            reg.write_code(code)
            return reg

    def calc_size_of_index(self, _type):
        size = 0
        if "[][]" in _type:
            size = 4
            return size
        else:
            if "int" in _type:
                size = 4
            if "bool" in _type:
                size = 1
            if "string" in _type:
                size = 4  # address of string
            if "double" in _type:
                size = 8
        return size

    def arr_length(self, arr):
        print("arr.length()", arr)
        t1 = self.main_code_gen.get_a_free_t_register()
        self.main_code_gen.t_registers[t1] = True
        code = """
li $t{}, {};
add $t{}, $t{}, $s{};
lw $t{}, ($t{});
lw $t{}, ($t{});
            """.format(
            t1, arr.address_offset, t1, t1, 1 if arr.is_global else 0, t1, t1, t1, t1
        )
        reg = CodeGenerator.Register("int", "t", t1)
        reg.write_code(code)
        return reg
