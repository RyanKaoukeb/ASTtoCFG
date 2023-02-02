from ASTtoCFGVisitor import ASTtoCFGVisitor
from code_analysis import CFGReader, ASTReader
cfgreader = CFGReader()
astreader = ASTReader()
#ast = astreader.read_ast("../part_1/while/while.php.ast.json")
ast2 = astreader.read_ast("../part_1/if/if.php.ast.json")
atcV = ASTtoCFGVisitor()
#cfg = atcV.visit(ast)
cfg2 = atcV.visit(ast2)

#cfg.show(filename="function.cfg.dot")
cfg2.show(filename="functionif.cfg.dot")