from IPython.core.magic import magics_class, Magics, cell_magic, register_cell_magic
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from io import StringIO

import pandas as pd
import subprocess

from importlib import resources

@magics_class
class GenSQLMagics(Magics):
    @magic_arguments()
    @argument("-d", "--db", help="Database used for the GenSQL query")
    @argument("-o", "--out", help="Variable to bind the output to")
    @argument("-l", "--language", help="permissive | strict")
    @cell_magic
    def gensql(self, line, cell):
        args = parse_argstring(self.gensql, line)
        db = args.db or "db.edn"
        lang = args.language or "permissive"
        query = cell.strip()
        with resources.path(__package__, "gensql.jar") as gensql_jar:
            result = subprocess.run(["java", "-jar", gensql_jar,
                                    "-d", db, "-l", lang,
                                    "-o", "csv", "-e", query],
                                    capture_output=True, text=True, check=True)
            data = pd.read_csv(StringIO(result.stdout))
            if args.out:
                self.shell.user_ns[args.out] = data
            return data
