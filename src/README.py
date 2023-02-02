from ASTtoCFGVisitor import ASTtoCFGVisitor
from code_analysis import CFGReader, ASTReader
cfgreader = CFGReader()
astreader = ASTReader()
ast = astreader.read_ast("../part_1/functioncall/functioncall.php.ast.json")

atcV = ASTtoCFGVisitor()
cfg = atcV.visit(ast)

cfg.show(filename="function.cfg.dot")
