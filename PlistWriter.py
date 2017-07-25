class PlistWriter:
    def __init__(self, output_stream):
        self.output = output_stream
        if type(self.output) in (str, unicode):
            self.output= open(self.output, 'w')

    def write(self, plist, **kwargs):
        indent = kwargs.get("indent", 1)
        use_tabs = kwargs.get("tabs", False)
        initialIndent = kwargs.get("initialIndent", 0)
        tabsize = 1 if use_tabs else kwargs.get("tabsize", 4)

        self.indent_str = (" " * tabsize if use_tabs else "\t") * indent
        self.current_indent = initialIndent
        self.write_plist(plist)

    def write_plist(self, plist):
        if isinstance(plist, dict):
            if plist.get("isa", None) in ["PBXFileReference", "PBXBuildFile"]:
                self.write_inline(plist)
            else:
                self.write_dict(plist)
        elif type(plist) == str:
            self.write_str(plist)
        elif type(plist) == list:
            self.write_list(plist)
        elif type(plist) == int:
            self.write_int(plist)

    def write_int(self, n):
        self.output.write("%s" % n)

    def write_indent(self, str):
        self.output.write(self.indent_str * self.current_indent)
        self.output.write(str)

    def write_str(self, str):
        self.output.write(str)

    def write_list(self, array):
        self.output.write("(\n")

        self.current_indent += 1

        for item in array:
            self.write_indent("")
            self.write_plist(item)
            self.output.write(",\n")

        self.current_indent -= 1

        self.write_indent(")")

    def write_inline(self, plist):
        if isinstance(plist, dict):
            self.output.write('{')
            for k,v in plist.iteritems():
                self.write_inline(k)
                self.output.write(" = ")
                self.write_inline(v)
                self.output.write("; ")
            self.output.write('}')
        elif type(plist) == list:
            self.output.write('(')
            for item in plist:
                self.write_inline(item)
                self.output.write(', ')
            self.output.write(')')
        elif type(plist) == str:
            self.write_str(plist)
        elif type(plist) == int:
            self.write_int(plist)

    def write_dict(self, plist):
        self.output.write("{\n")

        self.current_indent += 1

        for k,v in plist.iteritems():
            self.write_indent("%s = " % k)
            self.write_plist(v)
            self.output.write(";\n")

        self.current_indent -= 1

        self.write_indent("}")
