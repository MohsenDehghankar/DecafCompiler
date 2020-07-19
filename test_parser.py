import sys
import getopt
from lark import Lark, UnexpectedInput
from CodeGenerator import CodeGenerator

grammar = open("grammar.lark", 'r')
codeGen = CodeGenerator()
parser = Lark(grammar, parser='lalr', transformer=codeGen, debug=True)


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

    print("Parse Tree:")

    # tree = parser.parse("""
    # int main(){
    #     int x;
    #     int y;
    #     x = 10;
    #     y = 20;
    #     x = y + 2 * 8 + x;
    #     Print(x);
    # }
    # """)

    tree = parser.parse("""
    int main(){
        int x;
        x = 3 == 3;
    }
    """)

    # print(tree.pretty())

    # add var declarations
    # codeGen.generate_variable_declaration_codes()

    print("symbol table: ")
    for var in codeGen.symbol_table.keys():
        var = codeGen.symbol_table[var]
        print("name: {}, offset: {}, size: {}".format(
            var.name, var.address_offset, var.size))

    print("MIPS:")
    print(codeGen.mips_code)


if __name__ == "__main__":
    main(sys.argv[1:])
