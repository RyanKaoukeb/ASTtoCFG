from ASTtoCFGVisitor import ASTtoCFGVisitor
from deadcodeVisitor import DeadcodeVisitor
from code_analysis import CFGReader, ASTReader
cfgreader = CFGReader()
astreader = ASTReader()
# ast = astreader.read_ast("../part_1/while/while.php.ast.json")
# ast = astreader.read_ast(
#     "../while_continue_break/while_continue_break.php.ast.json")
ast = astreader.read_ast("../part_1/if/if.php.ast.json")

atcV = ASTtoCFGVisitor()
cfg = atcV.visit(ast)

#cfg = cfgreader.read_cfg("../part_2/code_mort/example3.php.cfg.json")
cfg.show(filename="if.cfg.dot")
dcv = DeadcodeVisitor()

dcv.visit(cfg)
dcv.visit_def(ast)
