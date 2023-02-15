
from code_analysis import CFG, CFGException, AST


class DeadcodeVisitor:
    def __init__(self):
        self.cfg = None
        self.ast = None
        self.deadcode = []
        self.alivecode = []
        self.allcode = None

    def visit(self, cfg: CFG):
        self.cfg = cfg
        self.allcode = cfg.get_node_ids()
        stack = []
        entry = self.cfg.get_func_entry_nodes()
        stack.append(self.cfg.get_root())

        for i in entry:
            stack.append(i)
        while len(stack) > 0:
            node = stack.pop()
            if node not in self.alivecode:

                self.alivecode.append(node)
                for child in self.cfg.get_children(node):
                    stack.append(child)
                if self.cfg.get_type(node) == "CallBegin":
                    stack.append(self.cfg.get_call_end(node))

        for node in self.allcode:
            if node not in self.alivecode:
                self.deadcode.append(node)
        print("Deadcode: ", self.deadcode)
        return self.deadcode

    def visit_def(self, ast: AST):
        self.ast = ast
        rootAST = self.ast.get_root()

        fifo = [rootAST]
        func_def = []
        func_call = []

        while len(fifo) > 0:
            node = fifo.pop()
            if self.ast.get_type(node) == "FunctionCall":
                func_call.append(node)
            if self.ast.get_type(node) == "FunctionStatement":
                func_def.append(node)
            for child in self.ast.get_children(node):
                fifo.append(child)

        for node in func_def:
            name = self.ast.get_image(node)
            flag = True
            for call in func_call:
                if self.ast.get_image(call) == name:
                    flag = False
            if flag:
                print("Warning: Function " + name +
                      " is defined but never called")
