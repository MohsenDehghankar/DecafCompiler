from lark import Transformer

class CodeGenerator(Transformer):

    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)
        self.mips_code = ""

    def test(self, args):
        pass



    

