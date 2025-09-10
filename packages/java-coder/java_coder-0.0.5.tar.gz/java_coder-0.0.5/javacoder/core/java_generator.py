import javalang
from javalang.tree import *
from javalang.parser import JavaSyntaxError

from javacoder.utils.converter import is_collection
from javacoder.utils.log import error


class JavaCodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.code_lines = []
        self.current_line = ""
        self.type_stack = []
        self.success = True

    def stack(self, type):
        self.type_stack.append(type)

    def pop(self):
        self.type_stack.pop()

    def peek(self):
        if not len(self.type_stack) > 0:
            return None
        return self.type_stack[-1]

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level = max(0, self.indent_level - 1)

    def add(self, text):
        self.current_line += text

    def newline(self):
        if self.current_line:
            indent = " " * (4 * self.indent_level)
            self.code_lines.append(indent + self.current_line)
            self.current_line = ""

    def new_empty_line(self):
        self.newline()
        self.code_lines.append('')

    def generate_document(self, node):
        if hasattr(node, 'documentation') and node.documentation:
            if type(node.documentation) == str:
                self.add(node.documentation)
                self.newline()
            else:
                self.generate(node.documentation)

    def generate(self, node):
        """主生成方法，根据节点类型分发处理"""
        method_name = f"visit_{type(node).__name__}"
        if hasattr(self, method_name):
            getattr(self, method_name)(node)
        else:
            # 默认处理：打印节点类型和位置
            self.add(f"/* UNHANDLED NODE: {type(node).__name__} */")
            error(f"/* UNHANDLED NODE: {type(node).__name__} */")
            self.success = False

    def get_code(self):
        """返回生成的完整代码"""
        self.newline()  # 确保最后一行被添加
        return "\n".join(self.code_lines)

    def start_new_line(self):
        """另起一行"""
        self.new_empty_line()

    # 以下是具体节点类型的处理方法
    # --------------------------------------------------

    # def visit_str(self, str):
    #     if str:
    #         self.add(str)

    def visit_CompilationUnit(self, node):
        if node.package:
            self.generate(node.package)
            self.newline()
            # self.newline()
            # self.start_new_line()
            self.start_new_line()

        if node.imports:
            for import_decl in node.imports:
                self.generate(import_decl)
                self.newline()
            self.start_new_line()
        # if node.imports and len(node.imports)>0:
        #     self.start_new_line()

        for type_decl in node.types:
            self.generate(type_decl)
            # self.newline()
            self.start_new_line()

    def visit_PackageDeclaration(self, node):
        self.add(f"package {node.name};")

    def visit_Import(self, node):
        static = "static " if node.static else ""
        wildcard = ".*" if node.wildcard else ""
        self.add(f"import {static}{node.path}{wildcard};")

    def visit_ClassDeclaration(self, node):
        """处理类声明，添加注解支持"""
        self.stack('class[{}]'.format(node.name))

        # document
        if node.documentation:
            if type(node.documentation) == str:
                self.add(node.documentation)
                self.newline()
            else:
                self.generate(node.documentation)
        # 处理类注解
        self._process_annotations(node.annotations)

        # 类修饰符
        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        self.add(f"class {node.name}")

        # 泛型参数
        if node.type_parameters:
            self.add("<")
            for i, param in enumerate(node.type_parameters):
                if i > 0:
                    self.add(", ")
                self.generate(param)
            self.add(">")

        # 继承
        if node.extends:
            self.add(" extends ")
            self.generate(node.extends)

        # 实现接口
        if node.implements:
            self.add(" implements ")
            for i, impl in enumerate(node.implements):
                if i > 0:
                    self.add(", ")
                self.generate(impl)

        self.add(" {")
        self.newline()
        self.indent()

        # 类体内容
        for i, body_item in enumerate(node.body):
            if i > 0:
                self.start_new_line()
            self.generate(body_item)
            if type(body_item) == FieldDeclaration:
                self.add(';')
            # self.newline()

        self.dedent()
        self.add("}")

        self.pop()

    def visit_InterfaceDeclaration(self, node):
        """处理类声明，添加注解支持"""
        self.stack('interface[{}]'.format(node.name))
        # document
        if node.documentation:
            if type(node.documentation) == str:
                self.add(node.documentation)
                self.newline()
            else:
                self.generate(node.documentation)
        # 处理类注解
        self._process_annotations(node.annotations)

        # 类修饰符
        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        self.add(f"interface {node.name}")

        # 泛型参数
        if node.type_parameters:
            self.add("<")
            for i, param in enumerate(node.type_parameters):
                if i > 0:
                    self.add(", ")
                self.generate(param)
            self.add(">")

        # 继承
        if node.extends:
            self.add(" extends ")
            for i, impl in enumerate(node.extends):
                if i > 0:
                    self.add(", ")
                self.generate(impl)

        self.add(" {")
        self.newline()
        self.indent()

        # 类体内容
        for body_item in node.body:
            self.generate(body_item)
            self.newline()

        self.dedent()
        self.add("}")

        self.pop()

    def visit_FieldDeclaration(self, node):
        """处理字段声明，添加注解支持"""
        # 处理字段注解
        self._process_annotations(node.annotations)

        # 字段修饰符
        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        # 类型
        self.generate(node.type)
        self.add(" ")

        # 声明器列表
        for i, decl in enumerate(node.declarators):
            if i > 0:
                self.add(", ")
            self.generate(decl)

        # self.add(";")

    def visit_VariableDeclarator(self, node):
        self.add(node.name)
        if node.initializer:
            self.add(" = ")
            self.generate(node.initializer)

    def visit_MethodDeclaration(self, node):
        """处理方法声明，添加注解支持"""
        self.generate_document(node)
        # 处理方法注解
        self._process_annotations(node.annotations)

        # 方法修饰符
        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        # 类型参数
        if node.type_parameters:
            self.add("<")
            for i, param in enumerate(node.type_parameters):
                if i > 0:
                    self.add(", ")
                self.generate(param)
            self.add("> ")

        # 返回类型
        if node.return_type:
            self.generate(node.return_type)
        else:
            self.add("void")

        self.add(f" {node.name}(")

        # 参数列表
        if node.parameters:
            for i, param in enumerate(node.parameters):
                if i > 0:
                    self.add(", ")
                self.generate(param)

        self.add(")")

        # 抛出异常
        if node.throws:
            self.add(" throws ")
            for i, exc in enumerate(node.throws):
                if i > 0:
                    self.add(", ")
                if type(exc) == str:
                    self.add(exc)
                else:
                    self.generate(exc)

        # 方法体
        if node.body:
            self.add(" {")
            self.newline()
            self.indent()

            for stmt in node.body:
                self.generate(stmt)
                if len(self.current_line) > 0 and not self.current_line[-1] in (';', '}'):
                    self.add(';')
                self.newline()

            self.dedent()
            self.add("}")
        elif 'abstract' in node.modifiers or (self.peek() and str(self.peek()).startswith('interface')):
            self.add(";")  # 抽象方法
        else:
            self.add(" {")
            self.newline()
            self.add("}")

    def visit_ConstructorDeclaration(self, node):
        # 方法修饰符
        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        # 类型参数
        if node.type_parameters:
            self.add("<")
            for i, param in enumerate(node.type_parameters):
                if i > 0:
                    self.add(", ")
                self.generate(param)
            self.add("> ")

        # 返回类型
        # if node.return_type:
        #     self.generate(node.return_type)
        # else:
        #     self.add("void")

        self.add(f"{node.name}(")

        # 参数列表
        if node.parameters:
            for i, param in enumerate(node.parameters):
                if i > 0:
                    self.add(", ")
                self.generate(param)

        self.add(")")

        # 抛出异常
        if node.throws:
            self.add(" throws ")
            for i, exc in enumerate(node.throws):
                if i > 0:
                    self.add(", ")
                self.generate(exc)

        # 方法体
        if node.body:
            self.add(" {")
            self.newline()
            self.indent()

            for stmt in node.body:
                self.generate(stmt)
                if len(self.current_line) > 0 and not self.current_line[-1] in (';', '}'):
                    self.add(';')
                self.newline()

            self.dedent()
            self.add("}")
        elif 'abstract' in node.modifiers or (self.peek() and str(self.peek()).startswith('interface')):
            self.add(";")  # 抽象方法
        else:
            self.add(" {")
            self.newline()
            self.add("}")

    def visit_FormalParameter(self, node):
        """处理参数声明，添加注解支持"""
        # 处理参数注解
        self._process_annotations(node.annotations)

        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        self.generate(node.type)
        self.add(" ")
        if node.varargs:
            self.add("...")
        self.add(node.name)

    def visit_BlockStatement(self, node):
        if isinstance(node.statements, LocalVariableDeclaration):
            self.generate(node.statements)
        elif isinstance(node.statements, Statement):
            self.generate(node.statements)
        elif is_collection(node.statements):
            for statement in node.statements:
                self.generate(statement)
                if len(self.current_line) > 0 and not self.current_line[-1] in (';', '}'):
                    self.add(';')
                self.newline()
        else:
            self.add(f"/* UNHANDLED BLOCK: {type(node.statements).__name__} */")
            error(f"/* UNHANDLED BLOCK: {type(node.statements).__name__} */")
            self.success = False

    def visit_LocalVariableDeclaration(self, node):
        """处理局部变量声明，添加注解支持"""
        # 处理局部变量注解
        self._process_annotations(node.annotations)

        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        self.generate(node.type)
        self.add(" ")

        for i, decl in enumerate(node.declarators):
            if i > 0:
                self.add(", ")
            self.generate(decl)

        self.add(";")

    def visit_ReturnStatement(self, node):
        self.add("return")
        if node.expression:
            self.add(" ")
            self.generate(node.expression)
        self.add(";")

    def visit_IfStatement(self, node):
        self.add("if (")
        self.generate(node.condition)
        self.add(") {")
        self.newline()
        self.indent()

        self.generate(node.then_statement)
        self.newline()

        self.dedent()
        self.add("}")

        if node.else_statement:
            self.add(" else {")
            self.newline()
            self.indent()

            self.generate(node.else_statement)
            self.newline()

            self.dedent()
            self.add("}")

    def visit_BasicType(self, node):
        self.add(node.name)
        if node.dimensions and len(node.dimensions) > 0:
            self.add('[')
            for i, dimension in enumerate(node.dimensions):
                if dimension == None:
                    continue
                if i > 0:
                    self.add(', ')
                self.add(str(dimension))
            self.add(']')

    def visit_ReferenceType(self, node):
        if node.arguments:
            self.add(node.name)
            self.add("<")
            for i, arg in enumerate(node.arguments):
                if i > 0:
                    self.add(", ")
                self.generate(arg)
            self.add(">")
        else:
            self.add(node.name)

    def visit_Literal(self, node):
        if node.value is None:
            self.add('null')
        elif isinstance(node.value, bool):
            self.add("true" if node.value else "false")
        elif isinstance(node.value, str):
            # null 解析问题 ,数字转换问题
            self.add(f"{node.value}")
            # if (node.value.startswith('"') and node.value.endswith('"')):
            #     self.add(f"{node.value}")
            # else:
            #     self.add(f"\"{node.value}\"")
        else:
            self.add(str(node.value))

    def visit_MethodInvocation(self, node):
        if node.qualifier:
            if type(node.qualifier) == str:
                self.add(node.qualifier)
            else:
                self.generate(node.qualifier)
            self.add(".")
        if node.type_arguments:
            self.add("<")
            for i, arg in enumerate(node.type_arguments):
                if i > 0:
                    self.add(", ")
                self.generate(arg)
            self.add(">")
        self.add(f"{node.member}(")
        if node.arguments:
            for i, arg in enumerate(node.arguments):
                if i > 0:
                    self.add(", ")
                self.generate(arg)
        self.add(")")

        if node.selectors:
            for selector in node.selectors:
                if type(selector) == ArraySelector:
                    self.generate(selector)
                else:
                    self.add('.')
                    self.generate(selector)

    def visit_Assignment(self, node):
        self.generate(node.expressionl)
        self.add(f" {node.type} ")
        self.generate(node.value)
        self.add(";")

    def visit_StatementExpression(self, node):
        # self.generate(node.label)
        self.generate(node.expression)

    def visit_This(self, node):
        # self.generate(node.label)
        if node.qualifier:
            if type(node.qualifier) == str:
                self.add(node.qualifier)
            else:
                self.generate(node.qualifier)
            self.add(".")
        self.add(f"this.")
        for member in node.selectors:
            self.generate(member)

    def visit_Annotation(self, node):
        """处理单个注解使用"""
        self.add(f"@{node.name}")

        # 处理注解参数
        if node.element:
            self.add("(")
            if isinstance(node.element, list):
                # 多个键值对参数
                for i, element in enumerate(node.element):
                    if i > 0:
                        self.add(", ")
                    self.generate(element)
            else:
                # 单个值参数
                self.generate(node.element)
            self.add(")")

    def visit_AnnotationDeclaration(self, node):
        """处理注解类型声明"""
        if node.documentation:
            self.generate(node.documentation)
        # 处理类注解
        self._process_annotations(node.annotations)
        # 注解修饰符
        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        self.add(f"@interface {node.name} ")

        # 注解体
        self.add("{")
        self.newline()
        self.indent()

        # 处理注解成员
        for member in node.body:
            self.generate(member)
            self.newline()

        self.dedent()
        self.add("}")

    def visit_AnnotationMember(self, node):
        """处理注解成员声明"""
        # 成员类型
        self.generate(node.type)
        self.add(f" {node.name}()")

        # 默认值
        if node.default:
            self.add(" default ")
            self.generate(node.default)

        self.add(";")

    def visit_ElementValuePair(self, node):
        """处理注解键值对"""
        self.add(f"{node.name} = ")
        self.generate(node.value)

    def visit_MemberReference(self, node):
        """处理注解中的成员引用"""
        if node.qualifier:
            if type(node.qualifier) == str:
                self.add(node.qualifier)
            else:
                self.generate(node.qualifier)
            self.add(".")

        if node.prefix_operators:
            for operator in node.prefix_operators:
                if type(operator) == str:
                    self.add(operator)
                else:
                    self.generate(operator)

        self.add(node.member)

        if node.postfix_operators:
            for operator in node.postfix_operators:
                if type(operator) == str:
                    self.add(operator)
                else:
                    self.generate(operator)

    # ====================== 在声明节点中添加注解支持 ======================

    def _process_annotations(self, annotations):
        """通用注解处理方法"""
        if annotations:
            for annotation in annotations:
                self.generate(annotation)
                self.newline()

    # ====================== 高级注解特性支持 ======================

    def visit_AnnotationMethod(self, node):
        """处理注解方法声明（在注解类型内部）"""
        # 注解方法返回值类型
        self.generate_document(node)

        self._process_annotations(node.annotations)

        self.generate(node.return_type)
        self.add(f" {node.name}()")

        # 默认值
        if node.default:
            self.add(" default ")
            self.generate(node.default)

        self.add(";")

    def visit_MarkerAnnotation(self, node):
        """处理标记注解（无参数）"""
        self.add(f"@{node.name}")

    def visit_SingleElementAnnotation(self, node):
        """处理单元素注解"""
        self.add(f"@{node.name}(")
        self.generate(node.value)
        self.add(")")

    # 可以继续添加更多节点类型的处理方法...
    def visit_Documented(self, node):
        self.add("/**\n")
        self.add('\n'.join([" * " + s for s in str(node.documentation).split("\n")]))
        self.add("\n */\n")

    def visit_LambdaExpression(self, node):
        self.add("(")
        for i, parameter in enumerate(node.parameters):
            if i > 0:
                self.add(', ')
            self.generate(parameter)
        self.add(") -> ")
        if is_collection(node.body):
            self.add("{")
            self.newline()
            self.indent()
            for expression in node.body:
                self.generate(expression)
                if len(self.current_line) > 0 and not self.current_line[-1] in (';', '}'):
                    self.add(';')
                self.newline()
            self.dedent()
            self.newline()
            self.add("}")
        else:
            self.generate(node.body)

    def visit_EnumDeclaration(self, node):
        """处理类声明，添加注解支持"""

        # document
        if node.documentation:
            # 兼容javalang document 解析成字符串
            if type(node.documentation) == str:
                self.add(node.documentation)
                self.newline()
            else:
                self.generate(node.documentation)
        # 处理类注解
        self._process_annotations(node.annotations)

        # 类修饰符
        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        self.add(f"enum {node.name}")

        # 实现接口
        if node.implements:
            self.add(" implements ")
            for i, impl in enumerate(node.implements):
                if i > 0:
                    self.add(", ")
                self.generate(impl)

        self.add(" {")
        self.newline()
        self.indent()

        # 类体内容
        # javalang 解析body问题处理，只解析第一个
        # for body_item in node.body:
        if type(node.body[0]) == tuple:
            self.generate(node.body[0][1])
            self.newline()
        else:
            for body_item in node.body:
                self.generate(body_item)
                if type(body_item) == FieldDeclaration:
                    self.add(';')
                self.newline()
        # if type(node.body[0][1]) == FieldDeclaration:
        #     self.add(';')
        # self.newline()
        # break

        self.dedent()
        self.add("}")

    def visit_EnumBody(self, node):
        if node.constants:
            for i, constant in enumerate(node.constants):
                if i > 0:
                    self.add(',')
                    self.newline()
                self.generate(constant)
            self.add(';')
            self.newline()

        if node.declarations:
            for declaration in node.declarations:
                self.generate(declaration)
                if type(declaration) == FieldDeclaration:
                    self.add(';')
                self.newline()

    def visit_EnumConstantDeclaration(self, node):
        # document
        if node.documentation:
            # 兼容javalang document 解析成字符串
            if type(node.documentation) == str:
                self.add(node.documentation)
                self.newline()
            else:
                self.generate(node.documentation)

        if node.modifiers:
            self.add(" ".join(node.modifiers) + " ")

        self.add(node.name)

        if node.arguments:
            self.add('(')
            for i, argument in enumerate(node.arguments):
                if i > 0:
                    self.add(', ')
                self.generate(argument)
            self.add(')')

    def visit_ArrayInitializer(self, node):
        self.add('{')
        for i, initializer in enumerate(node.initializers):
            if i > 0:
                self.add(', ')
            self.generate(initializer)
        self.add('}')

    def visit_ElementArrayValue(self, node):
        self.add('{')
        for i, value in enumerate(node.values):
            if i > 0:
                self.add(', ')
            self.generate(value)
        self.add('}')

    def visit_ClassReference(self, node):
        self.generate(node.type)
        self.add('.class')

    def visit_ClassCreator(self, node):
        self.add('new ')
        self.generate(node.type)
        self.add('(')
        for i, argument in enumerate(node.arguments):
            if i > 0:
                self.add(', ')
            self.generate(argument)
        self.add(')')

    def visit_BinaryOperation(self, node):
        self.generate(node.operandl)
        self.add(f' {node.operator} ')
        self.generate(node.operandr)

    def visit_TypeArgument(self, node):
        self.generate(node.type)

    def visit_Cast(self, node):
        self.add('(')
        self.generate(node.type)
        self.add(')')
        self.generate(node.expression)

    def visit_InferredFormalParameter(self, node):
        self.add(node.name)

    def visit_ForStatement(self, node):
        self.add('for (')
        self.generate(node.control)
        self.add(') {')

        self.newline()
        self.indent()
        self.generate(node.body)
        self.dedent()

        self.newline()
        self.add('}')

    def visit_ForControl(self, node):
        self.generate(node.init)
        self.add('; ')
        self.generate(node.condition)
        self.add('; ')
        for i, statement in enumerate(node.update):
            if i > 0:
                self.add(', ')
            self.generate(statement)

    def visit_TryStatement(self, node):
        self.add('try {')
        self.newline()
        self.indent()

        for b in node.block:
            self.generate(b)
            self.newline()
        self.dedent()
        self.add('} ')
        for catch in node.catches:
            self.generate(catch)

            self.newline()

        if node.finally_block:
            self.generate(node.finally_block)

    def visit_VariableDeclaration(self, node):
        if node.modifiers and len(node.modifiers) > 0:
            self.add(' '.join(node.modifiers))

        self._process_annotations(node.annotations)

        self.generate(node.type)
        self.add(' ')

        for declarator in node.declarators:
            self.generate(declarator)

    def visit_CatchClause(self, node):
        self.add('catch (')
        self.generate(node.parameter)
        self.add(') {')
        self.newline()
        self.indent()

        for b in node.block:
            self.generate(b)
            if len(self.current_line) > 0 and not self.current_line[-1] in (';', '}'):
                self.add(';')
            self.newline()
        self.dedent()
        self.newline()
        self.add('}')

    def visit_CatchClauseParameter(self, node):
        for i, t in enumerate(node.types):
            if i > 0:
                self.add(' | ')
            if type(t) == str:
                self.add(t)
            else:
                self.generate(t)

        self.add(' ')
        self.add(node.name)

    def visit_ThrowStatement(self, node):
        self.add('throw ')
        self.generate(node.expression)
        if len(self.current_line) > 0 and not self.current_line[-1] in (';', '}'):
            self.add(';')

    def visit_MethodReference(self, node):
        self.generate(node.expression)
        self.add('::')
        self.generate(node.method)

    def visit_TernaryExpression(self, node):
        self.generate(node.condition)
        self.add(' ? ')
        self.generate(node.if_true)
        self.add(' : ')
        self.generate(node.if_false)

    def visit_EnhancedForControl(self, node):
        self.generate(node.var)
        self.add(' : ')
        self.generate(node.iterable)

    def visit_BreakStatement(self, node):
        self.add('break;')

    def visit_ArrayCreator(self, node):
        self.add('new ')

        # if node.qualifier:
        #     if is_collection(node.qualifier):
        #         self.add(' '.join(node.qualifier))
        #     else:
        #         self.add(node.qualifier)

        self.generate(node.type)
        self.add('[')
        if node.dimensions and len(node.dimensions) > 0:
            for i, dimension in enumerate(node.dimensions):
                if i > 0:
                    self.add(', ')
                self.generate(dimension)
        self.add(']')

    def visit_ContinueStatement(self, node):
        self.add('continue;')

    def visit_TypeParameter(self, node):
        self.add(node.name)
        if node.extends:
            self.add(' extends ')
            self.generate(node.extends)

    def visit_WhileStatement(self, node):
        self.add('while (')
        self.generate(node.condition)
        self.add(') {')

        self.newline()
        self.indent()
        self.generate(node.body)
        self.dedent()
        self.add('}')

    def visit_DoStatement(self, node):
        self.add('do {')
        self.newline()
        self.indent()
        self.generate(node.body)
        self.newline()
        self.dedent()
        self.add('} while (')
        self.generate(node.condition)
        self.add(')')

    def visit_SuperMethodInvocation(self, node):
        self.add(f'super.{node.member}')
        self.add('(')
        for i, argument in enumerate(node.arguments):
            if i > 0:
                self.add(', ')
            self.generate(argument)
        self.add(')')

    def visit_NoneType(self, node):
        self.add('?')

    def visit_SwitchStatement(self, node):
        self.add('switch (')
        self.generate(node.expression)
        self.add(') {')
        self.newline()

        for case in node.cases:
            self.indent()
            self.generate(case)
            self.dedent()

        self.add('}')

    def visit_SwitchStatementCase(self, node):
        if node.case and len(node.case) > 0:
            for i in node.case:
                self.add(f'case {i}:')
                self.newline()
        else:
            self.add('default:')
            self.newline()
        self.indent()
        for statement in node.statements:
            self.generate(statement)
            self.newline()
        self.dedent()

    def visit_SuperConstructorInvocation(self, node):
        self.add('super(')
        for i, argument in enumerate(node.arguments):
            if i > 0:
                self.add(', ')
            self.generate(argument)
        self.add(')')

    def visit_ConstantDeclaration(self, node):
        if node.documentation:
            if type(node.documentation) == str:
                self.add(node.documentation)
            else:
                self.generate(node.documentation)
            self.newline()

        if node.modifiers:
            self.add(' '.join(node.modifiers))
        self.generate(node.type)
        self.add(' ')

        for i, declarator in enumerate(node.declarators):
            if i > 0:
                self.add(', ')
            self.generate(declarator)

        if len(self.current_line) > 0 and not self.current_line[-1] in (';', '}'):
            self.add(';')

    def visit_VoidClassReference(self, node):
        self.add('void.class')

    def visit_ExplicitConstructorInvocation(self, node):
        self.add('this(')
        for i, argument in enumerate(node.arguments):
            if i > 0:
                self.add(', ')
            self.generate(argument)
        self.add(')')

    def visit_ArraySelector(self, node):
        if type(node.index) == str:
            self.add(f'[{node.index}]')
        else:
            self.add('[')
            self.generate(node.index)
            self.add(']')


def ast_to_source(java_code):
    """将Java代码解析为AST，然后转换回源码"""
    try:
        # 解析Java代码生成AST
        tree = javalang.parse.parse(java_code)
        print(tree.types[0].body)

        # 创建代码生成器
        generator = JavaCodeGenerator()

        # 生成代码
        generator.generate(tree)

        return generator.get_code()

    except JavaSyntaxError as e:
        print(f"语法错误: {e.description} 位置: {e.at}")
        return None


# 示例用法
if __name__ == "__main__":
    java_source = """
    package com.example;
    import java.util.List;
    public class Calculator {
        private int value;
        public Calculator(int initialValue) {
            this.value = initialValue;
        }
        public int add(int number) {
            value += number;
            return value;
        }
        public int getValue() {
            return value;
        }
        public void helloWorld(){
            System.out.println("hello");
        }
    }
    """

    # 将AST转换回源码
    regenerated_code = ast_to_source(java_source)

    if regenerated_code:
        print("生成的Java代码:")
        print(regenerated_code)

        # 可选：比较原始代码和生成代码
        print("\n原始代码和生成代码是否相同:", java_source.strip() == regenerated_code.strip())
