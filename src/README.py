from ASTtoCFGVisitor import ASTtoCFGVisitor
from deadcodeVisitor import DeadcodeVisitor
from code_analysis import CFGReader, ASTReader
cfgreader = CFGReader()
astreader = ASTReader()
ast = astreader.read_ast("../part_1/functioncall/functioncall.php.ast.json")

atcV = ASTtoCFGVisitor()
cfg = atcV.visit(ast)

cfg = cfgreader.read_cfg("../part_2/code_mort/example1.php.cfg.json")
cfg.show(filename="test.cfg.dot")

dcv = DeadcodeVisitor()

print(dcv.visit(cfg))
