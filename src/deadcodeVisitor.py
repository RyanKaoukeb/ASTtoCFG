
from code_analysis import CFG, CFGException


class DeadcodeVisitor:
    def __init__(self):
        self.cfg = None
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

        return self.deadcode
