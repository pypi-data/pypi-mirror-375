# NAME

kera — Fill template files with structured data

# SYNOPSIS

**kera** *plate_files*... *data_files*...

# OPTIONS

-o, \--out-dir
:   The directory in which to write all files.  Defaults to the current
    directory.

# INSTALL

kera can be installed using the pip package manager, where it is available
under the name [kera][].

To install just the executable command line interface, I would use [pipx][]:

```
pipx install kera
```

To install it as a library, use [pip][] and a [venv][].

# DESCRIPTION

This program takes a collection of template files, a collection of data files,
and then uses the data to fill placeholder "slots" in the templates.  Each
individual data file produces an output for each individual template file.

To represent a simple slot in a template file, surround it in double hashes:

```
= ##title##
by ##name## on ##date##

##content##
```

And provide the data in your format of choice:

```json
{
    "title": "kera",
    "name": "C Wiebe",
    "date": "JAN 01 1970",
    "content": "Fill template files with structured data."
}
```

This results in:

```typ
= kera
by C Wiebe on JAN 01 1970

Fill template files with structured data.
```

## GLOSSARY

plate file
:   A file containing a template; optionally can have the extension .plate

data file
:   A file containing structured data; can be either a JSON file or a YAML file

slot
:   A string in a plate file that will be replaced with data from a data file

key
:   The identifier used to select which value from a data file is used to fill
    any given slot; the key in a key / value pair

conditional slot
:   A slot that has a condition attached to it

collection slot
:   A slot whose key points to a collection of nested data

## AS AN EXECUTABLE

The executable version of kera has the name `kera` and takes any number of
filenames as its arguments.

Template files can have the extension `.plate`, but any file that isn't a data
file will be read as a template by default.  Supported data filetypes are:

- JSON
- YAML

If you want to use a data file as a template file, it *must* have the `.plate`
extension, e.g. `.json.plate`.

The default filename of the filled template is the name of the data file (minus
extension), an underscore, and the name of the template file (with extension,
minus `.plate` if present).  These output files can be redirected to a
different directory with the `--out` option.

As an example:

```
$ ls
> 123.sql 456.sql.plate abc.json def.yml
$ kera --out output 123.sql 456.sql.plate abc.json def.yml
$ ls output
> abc_123.sql abc_456.sql def_123.sql def_456.sql
```

## AS A LIBRARY

The library version of kera has the name `kera` and provides one function:

```py
process(plate: str, data: dict[str, any]) -> str
```

This function takes a `plate` (a string containing the template text whose
slots will be filled) and a `data` (a dictionary containing the key / value
pairs that will be used to populate the template).  The function will fill
all the template slots using the data and then returns the populated template
string.

As a simple example:

```py
import kera

plate = "Hello, ##name##!"
data = {
    "name": "World",
}

result = kera.process(plate, data)
print(result)
#> Hello, World!
```

## CONDITIONAL SLOTS

kera supports additional types of slots that introduce additional
functionality.  Conditional slots (analogous to if statements) can be
represented as such:

```
##[ condition ]{{ if true }}{{ if false (optional) }}
```

The condition is simply a key found in the data, and it is true if the value of
the key is truthy according to Python.  If the key is not found, it is
automatically false.  The "body" of the conditional slot is treated the same as
the rest of the text; you can include other slots inside it and nest slots as
much as you wish.

An example of conditional slots in use:

```
<div class="profile">
    <h3>##name##</h3>
    <ul class="inline">
        ##[pronouns]{{ <li>##pronouns##</li> }}
        ##[language]{{ <li>##language##</li> }}
        ##[join-date]{{ <li>Joined ##join-date##</li> }}
    </ul>
    ##[desc]{{
        ##desc##
    }}{{
        <p>No bio provided.</p>
    }}
</div>
```

With this, you can process both full profiles:

```yaml
name: Scofflaw Saxwulf
pronouns: he/him
language: ENG | FIN
join-date: AUG 23 2025
desc: <p>INSERT INTERESTING BIO HERE</p>
```

```html
<div class="profile">
    <h3>Scofflaw Saxwulf</h3>
    <ul class="inline">
        <li>he/him</li>
        <li>ENG | FIN</li>
        <li>Joined AUG 23 2025</li>
    </ul>
    <p>INSERT INTERESTING BIO HERE</p>
</div>
```

And partial profiles:

```yaml
name: Lusaka Hernesto
pronouns: she/her
```

```html
<div class="profile">
    <h3>Lusaka Hernesto</h3>
    <ul class="inline">
        <li>she/her</li>
        
        
    </ul>
    <p>No bio provided.</p>
</div>
```

## COLLECTION SLOTS

Collection slots (analogous to for loops) are represented as:

```
##collection{{ body for each collection member }}
```

In a collection body, the "scope" that contains available keys is not the
original data, but rather the keys nested inside the collection key.  This
is easier shown than explained:

```yaml
table: Person
joins:
  - table: Place
    alias: a
    join-on: addressId

  - table: Place
    alias: w
    join-on: workAddressId

  - table: Job
    alias: j
    join-on: workId
```

```
SELECT  *
FROM    ##table##
##joins{{
    JOIN    ##table## ##alias## ON ##join-on## = ##alias##.id
}};
```

```sql
SELECT  *
FROM    Person
JOIN    Place a ON addressId = a.id
JOIN    Place w ON workAddressId = w.id
JOIN    Job j ON workId = j.id;
```

By default each member of the collection is joined with a newline, but you
can alter this by providing a join string before the collection body that is
surrounded by parenthesis:

```yaml
table: Record
columns:
  - name: create_date
    type: DATE

  - name: update_date
    type: DATE

  - name: id
    type: INTEGER

  - name: content
    type: TEXT
```

```
CREATE PROCEDURE insert_into_##table##
( ##columns(\n, ){{
    p_##name## IN ##type##
  }}
)
BEGIN

    INSERT
    INTO    ##table##
            ( ##columns(\n            , ){{
                ##name##
              }}
            )
    VALUES  ( ##columns(\n            , ){{
                p_##name##
              }}
            );

END insert_into_##table##;
```

```sql
CREATE PROCEDURE insert_into_Record
( p_create_date IN DATE
, p_update_date IN DATE
, p_id IN INTEGER
, p_content IN TEXT
)
BEGIN

    INSERT
    INTO    Record
            ( create_date
            , update_date
            , id
            , content
            )
    VALUES  ( p_create_date
            , p_update_date
            , p_id
            , p_content
            );

END insert_into_Record;
```

## APPENDIX

### ACCESSING NESTED VALUES

Say you have a nested object like so:

```json
{
    "parent": {
        "child": "value"
    }
}
```

In these instances, the values within the nested object can be accessed using
dot notation, e.g. `##parent.child##`.

### OVERRIDING DEFAULT NAMES

The default name of an output file produced by the executable can be overriden
by including the key `_out_file` in the data file, where the value of
`_out_file` is the name of the resulting file.  If that data file is used with
multiple plate files, it will result in the same name each time.

# RETURN CODES

0
:   Code execution was successful.

1
:   Unable to create or find the given output directory.

# BUGS

1.  If a key in YAML is made up of numbers and only numbers, the YAML parser
    will store it as an integer, which won't be resolved properly when kera
    tries to retrieve it as a string.  To prevent this, surround such keys with
    double quotes:

    ```yaml
    # bad:
    1: this won't be resolved
    # good:
    "1": this WILL be resolved
    ```

# SEE ALSO

-   [Source code][source]
-   [Online README][kera]
-   [CHANGELOG][changelog]

[pipx]: https://github.com/pypa/pipx
[pip]: https://pypi.org/project/pip/
[venv]: https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments
[kera]: https://ctwiebe23.github.io/kera
[source]: https://github.com/ctwiebe23/kera
[changelog]: https://ctwiebe23.github.io/kera/changelog
