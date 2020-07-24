import sys
import getopt
from lark import Lark, UnexpectedInput
from CodeGenerator import CodeGenerator

grammar = open("grammar.lark", "r")
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

    tree = parser.parse(
        """
    
    void func2(int y){
        y = y + 1;
        print(y);
    }
    void func1 (int a){
        print(a);
        func2(a);
    }
    int main(){
        int x;
        x = 90;
        func1(x);
        print(x);
    }
    """
    )

    # print(tree.pretty())

    print("---------------------------------------\nsymbol table: ")
    for var in codeGen.symbol_table.keys():
        var = codeGen.symbol_table[var]
        print(
            "name: {}, offset: {}, size: {}".format(
                var.name, var.address_offset, var.size
            )
        )

    print("---------------------------------------\nMIPS:")
    print(codeGen.mips_code)


if __name__ == "__main__":
    main(sys.argv[1:])
