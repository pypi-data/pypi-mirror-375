This package provides magics for using GenSQL inside of a jupyter notebook. Queries are wrapped into a Pandas dataframe.

Requires 24 or later installed an in `PATH`. (Java 17 _might_ work).

Usage:

First load the package and the extension:

```
import gensql_magics
%load_ext gensql_magics
```

Then you can use it in its own cells:

```
%%gensql -d db.edn
SELECT * FROM data LIMIT 10
```

Valid options are:

* `-d` The model database, defaults to `db.edn`.
* `-o` Jupyter variable to bind output to.
* `-l` Query language, `permissive` or `strict`, defaults to `permissive`.

## Building

Make sure you have the git repo checked out recursively (including submodules).
Then, make sure to run the `prebuild.sh` script before building with uv.

```
git clone --recursive https://github.com/LeifAndersen/GenSQL.magics/
./prebuild.sh
uv build
```