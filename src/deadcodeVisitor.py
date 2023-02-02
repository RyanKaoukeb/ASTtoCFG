
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
        stack.append(cfg.get_root())
        while len(stack) > 0:
            node = stack.pop()
            if node not in self.alivecode:
                self.alivecode.append(node)
                for child in self.cfg.get_children(node):
                    stack.append(child)

        for node in self.allcode:
            if node not in self.alivecode:
                self.deadcode.append(node)

        return self.deadcode
