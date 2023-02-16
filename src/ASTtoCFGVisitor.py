# This is an example of a visitor to create a CFG
# You can start from it if you don't know how to start


from code_analysis import ASTException, CFG, AST


class ASTtoCFGVisitor:
    def __init__(self):
        self.ast = None
        self.cfg = CFG()
        self.iNextNode = 0
        self.while_statements = [[], []]  # [break, continue]

    def get_new_node(self) -> int:
        self.iNextNode += 1
        return self.iNextNode

    def visit(self, ast: AST):
        self.ast = ast
        self.cfg = CFG()
        print(f"Visit AST from file {self.ast.get_filename()}")
        self.visit_ROOT()
        return self.cfg

    def visit_ROOT(self):
        ctx = {}
        entryNodeId = self.get_new_node()
        stopNodeId = self.get_new_node()
        rootAST = self.ast.get_root()
        self.cfg.set_root(entryNodeId)

        self.cfg.set_type(entryNodeId, "Entry")
        self.cfg.set_image(entryNodeId, "main")
        self.cfg.set_type(stopNodeId, "Exit")

        ctx['parent'] = entryNodeId
        ctx['scope'] = entryNodeId
        ctx['stopId'] = stopNodeId

        

        if self.ast.get_type(rootAST) == "Start":
            self.cfg.set_node_ptr(rootAST, entryNodeId)

        self.visit_node(rootAST, ctx)
        self.cfg.add_edge(ctx['endId'], stopNodeId)

    # chain nodes

    def visit_BREAK_CONTINUE(self, ast_node_id: int, ctx: dict) -> int:
        cfg_node = self.get_new_node()
        self.cfg.set_node_ptr(ast_node_id, cfg_node)
        self.cfg.set_type(cfg_node, self.ast.get_type(ast_node_id))
        self.cfg.set_image(cfg_node, self.ast.get_image(ast_node_id))
        print("debug: ", ctx["parent"], " ", cfg_node)
        self.cfg.add_edge(ctx["parent"], cfg_node)
        ctx["endId"] = cfg_node

        if self.ast.get_type(ast_node_id) == "Break":
            self.while_statements[0].append(cfg_node)
        else:
            self.while_statements[1].append(cfg_node)

        return cfg_node

    def visit_WHILE(self, ast_node_id: int, ctx: dict) -> int:
        cfg_node = self.get_new_node()
        self.cfg.set_node_ptr(ast_node_id, cfg_node)
        self.cfg.set_type(cfg_node, self.ast.get_type(ast_node_id))
        self.cfg.set_image(cfg_node, self.ast.get_image(ast_node_id))
        self.cfg.add_edge(ctx["parent"], cfg_node)
        condition_node = 0
        ctx["endId"] = cfg_node

        new_ctx = dict(ctx)
        new_ctx["parent"] = cfg_node
        for child_id in self.ast.get_children(ast_node_id):
            self.visit_node(child_id, new_ctx)

            if self.ast.get_type(child_id) == "Condition":
                condition_node = child_id

            if new_ctx["endId"] is not None:
                new_ctx["parent"] = new_ctx["endId"]
        ctx["endId"] = new_ctx["endId"]

        self.cfg.add_edge(ctx["endId"], cfg_node)

        node_end = self.get_new_node()
        self.cfg.set_type(node_end, "WhileEnd")
        self.cfg.add_edge(condition_node, node_end)

        ctx["endId"] = node_end

        for jump in self.while_statements[0]:
            chi = self.cfg.get_any_children(jump)
            for c in chi:
                self.cfg.remove_edge(jump, c)
            self.cfg.add_edge(jump, node_end)
        for jump in self.while_statements[1]:
            chi = self.cfg.get_any_children(jump)
            for c in chi:
                self.cfg.remove_edge(jump, c)
            self.cfg.add_edge(jump, cfg_node)

        self.while_statements = [[], []]

        return cfg_node

    # If fonction
    def visit_IF(self, ast_node_id: int, ctx: dict) -> int:

        # Custom IF block
        cfg_node_IF = self.get_new_node()
        self.cfg.set_node_ptr(ast_node_id, cfg_node_IF)
        self.cfg.set_type(cfg_node_IF, "If")
        self.cfg.add_edge(ctx["parent"], cfg_node_IF)

        # We close the call
        cfg_node_endIF = self.get_new_node()
        self.cfg.set_type(cfg_node_endIF, "IfEnd")

        ctx["endId"] = cfg_node_IF
        new_ctx = dict(ctx)
        new_ctx["parent"] = cfg_node_IF
        index = 0
        for idx, child_id in enumerate(self.ast.get_children(ast_node_id)):
            if self.ast.get_type(child_id) == "Condition":
                for subchild_id in self.ast.get_children(child_id):
                    self.visit_node(subchild_id, new_ctx)
                    new_ctx["parent"] = new_ctx["endId"]
                # Condition
                cfg_node_cond = self.get_new_node()
                self.cfg.set_type(cfg_node_cond, "Condition")
                self.cfg.add_edge(new_ctx["endId"], cfg_node_cond)
                new_ctx["parent"] = cfg_node_cond
            elif idx == 1:
                index = 1
                for subchild_id in self.ast.get_children(child_id):
                    self.visit_node(subchild_id, new_ctx)
                    new_ctx["endTrue"] = new_ctx["endId"]
                cfg_node_argument = self.get_new_node()
                self.cfg.set_type(cfg_node_argument, "Argument")
                self.cfg.add_edge(new_ctx["endId"], cfg_node_argument)
                self.cfg.add_edge(cfg_node_argument, cfg_node_endIF)

            elif idx == 2:
                index = 2
                for subchild_id in self.ast.get_children(child_id):
                    self.visit_node(subchild_id, new_ctx)
                    new_ctx["endFalse"] = new_ctx["endId"]
                cfg_node_argument = self.get_new_node()
                self.cfg.set_type(cfg_node_argument, "Argument")
                self.cfg.add_edge(new_ctx["endFalse"], cfg_node_argument)
                self.cfg.add_edge(cfg_node_argument, cfg_node_endIF)

        if index == 1:
            self.cfg.add_edge(cfg_node_cond, cfg_node_endIF)

        ctx["endId"] = cfg_node_endIF

    def visit_FUNCTION(self, ast_node_id: int, ctx: dict) -> int:
        cfg_node = self.get_new_node()
        self.cfg.set_node_ptr(ast_node_id, cfg_node)
        self.cfg.set_type(cfg_node, self.ast.get_type(ast_node_id))
        self.cfg.set_image(cfg_node, self.ast.get_image(ast_node_id))
        self.cfg.add_edge(ctx["parent"], cfg_node)

        ctx["endId"] = cfg_node

        new_ctx = dict(ctx)
        new_ctx["parent"] = cfg_node
        for child_id in self.ast.get_children(ast_node_id):
            self.visit_node(child_id, new_ctx)
            if new_ctx["endId"] is not None:
                new_ctx["parent"] = new_ctx["endId"]
        ctx["endId"] = new_ctx["endId"]

        node_arg = self.get_new_node()
        node_begin = self.get_new_node()
        node_end = self.get_new_node()
        node_return = self.get_new_node()

        self.cfg.set_type(node_arg, "Argument")
        self.cfg.set_type(node_begin, "CallBegin")
        self.cfg.set_type(node_end, "CallEnd")
        self.cfg.set_type(node_return, "RetValue")
        self.cfg.set_image(node_begin, self.ast.get_image(ast_node_id))
        self.cfg.set_image(node_end, self.ast.get_image(ast_node_id))

        self.cfg.add_edge(ctx["endId"], node_arg)
        self.cfg.add_edge(node_arg, node_begin)
        self.cfg.set_call(node_begin, node_end)
        self.cfg.add_edge(node_end, node_return)
        ctx["endId"] = node_return
        return cfg_node

    def visit_GENERIC(self, ast_node_id: int, ctx: dict) -> int:
        cfg_node = self.get_new_node()
        self.cfg.set_node_ptr(ast_node_id, cfg_node)
        self.cfg.set_type(cfg_node, self.ast.get_type(ast_node_id))
        self.cfg.set_image(cfg_node, self.ast.get_image(ast_node_id))
        self.cfg.add_edge(ctx["parent"], cfg_node)

        ctx["endId"] = cfg_node

        new_ctx = dict(ctx)  # clone ctx
        new_ctx["parent"] = cfg_node
        for child_id in self.ast.get_children(ast_node_id):
            self.visit_node(child_id, new_ctx)
            new_ctx["parent"] = new_ctx["endId"]
        ctx["endId"] = new_ctx["endId"]

        return cfg_node

    def visit_GENERIC_BLOCK(self, ast_node_id: int, ctx: dict):
        new_ctx = dict(ctx)  # clone ctx
        for child_id in self.ast.get_children(ast_node_id):
            self.visit_node(child_id, new_ctx)
            new_ctx["parent"] = new_ctx["endId"]
        ctx["endId"] = new_ctx["endId"]

        return None

    def visit_BINOP(self, ast_node_id: int, ctx: dict) -> int:
        # Create BinOP node
        cfg_node = self.get_new_node()
        self.cfg.set_node_ptr(ast_node_id, cfg_node)
        self.cfg.set_type(cfg_node, self.ast.get_type(ast_node_id))
        self.cfg.set_image(cfg_node, self.ast.get_image(ast_node_id))

        # Visit right child
        new_ctx = dict(ctx)  # clone ctx
        self.visit_node(self.ast.get_children(ast_node_id)[1], new_ctx)
        right = new_ctx['endId']

        # Visit right left
        new_ctx = dict(ctx)  # clone ctx
        new_ctx["parent"] = right
        self.visit_node(self.ast.get_children(ast_node_id)[0], new_ctx)
        left = new_ctx['endId']

        # Link left child with BinOp
        self.cfg.add_edge(left, cfg_node)

        ctx["endId"] = cfg_node
        return cfg_node

    def visit_node(self, ast_node_id: int, ctx: dict):
        cur_type = self.ast.get_type(ast_node_id)
        if cur_type is None:
            raise ASTException("Missing type in a node")

        if cur_type in ["BinOP", "RelOP", "LogicOP"]:
            self.visit_BINOP(ast_node_id, ctx)
        elif cur_type == "Break" or cur_type == "Continue":
            self.visit_BREAK_CONTINUE(ast_node_id, ctx)
        elif cur_type == "While":
            self.visit_WHILE(ast_node_id, ctx)
        elif cur_type == "IfThenElseStatement" or cur_type == "IfThenStatement":
            self.visit_IF(ast_node_id, ctx)
        elif cur_type == "FunctionCall":
            self.visit_FUNCTION(ast_node_id, ctx)
        elif cur_type in ["Block", "Start"]:
            self.visit_GENERIC_BLOCK(ast_node_id, ctx)
        elif cur_type in ["PLACEHOLDER"]:  # Node to ignore
            self.visit_passthrough(ast_node_id, ctx)
        else:
            self.visit_GENERIC(ast_node_id, ctx)

    def visit_passthrough(self, ast_node_id: int, ctx: dict):
        for child_id in self.ast.get_children(ast_node_id):
            self.visit_node(child_id, ctx)
