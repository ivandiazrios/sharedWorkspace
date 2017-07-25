from StringIO import StringIO
from PlistWriter import PlistWriter

class Writer:
    def write(self, value, initial_indent=0):
        self.output = StringIO()
        self.initial_indent = initial_indent

        self._write(value)

        return self.output.getvalue()

    def writeListItems(self, items, initial_indent=0):
        self.output = StringIO()
        self.initial_indent = initial_indent

        for item in items:
            self.write_indent()
            self._write(item)
            self.output.write(",\n")

        return self.output.getvalue()

    def writeKeyValue(self, key, value, initial_indent=0):
        self.output = StringIO()
        self.initial_indent = initial_indent

        self.write_indent()
        self._write(key)
        self.output.write(" = ")
        self._write(value)
        self.output.write(";\n")

        return self.output.getvalue()

    def _write(self, value):
        writer = PlistWriter(self.output)
        writer.write(value, initialIndent=self.initial_indent)

    def write_indent(self):
        self.output.write("\t" * self.initial_indent)