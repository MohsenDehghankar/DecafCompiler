import sys
import getopt
from lark import Lark, UnexpectedInput
from CodeGenerator import CodeGenerator


grammar = open("grammar.lark", "r")
grammar1 = open("grammar.lark", 'r')

# first pass
first_pass_code_gen = CodeGenerator()
first_pass_code_gen.first_pass = True
parser1 = Lark(grammar1, parser="lalr", transformer=first_pass_code_gen, debug=True)


# second pass
codeGen = CodeGenerator()
parser = Lark(grammar, parser="lalr", transformer=codeGen, debug=True)


def test(decaf_text):
    try:
        parser.parse(decaf_text).pretty()
        return "YES"
    except Exception as e:
        print(e)
        return "NO"


def main(argv):
    # inputfile = ''
    # outputfile = ''
    # try:
    #     opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    # except getopt.GetoptError:
    #     print('main.py -i <inputfile> -o <outputfile>')
    #     sys.exit(2)
    # for opt, arg in opts:
    #     if opt == '-h':
    #         print('test.py -i <inputfile> -o <outputfile>')
    #         sys.exit()
    #     elif opt in ("-i", "--ifile"):
    #         inputfile = arg
    #     elif opt in ("-o", "--ofile"):
    #         outputfile = arg

    # with open("tests/" + inputfile, "r") as input_file:
    #     file_content = input_file.read()
    #     result = test(file_content)
    # with open("out/" + outputfile, "w") as output_file:
    #     output_file.write(result)

    codeGen.create_data_segment()
    # first_pass_code_gen.create_data_segment()

    decaf_code = """
int main(){
    int z;
    int u;
    u = 100 + 1400;
    z = 2 * (5 + 3) * (100 - 1);
    z = z - u;
    print(z + 1);
}
    """


    # first pass
    # try:
    print("--------------first pass------------")
    parser1.parse(decaf_code)
    # except Exception:
        # print("exception in first codeGenerator")
    print("----------end of first pass---------")


    # second pass
    codeGen.set_last_code_gen(first_pass_code_gen)
    tree = parser.parse(decaf_code)

    # print(tree.pretty())

    print("---------------------------------------\nsymbol table: ")
    for var in codeGen.symbol_table.keys():
        var = codeGen.symbol_table[var]
        print(
            "name: {}, offset: {}, size: {}".format(
                var.name, var.address_offset, var.size
            )
        )

    print("---------------------------------------\nMIPS code:")
    print(codeGen.mips_code)


if __name__ == "__main__":
    main(sys.argv[1:])
