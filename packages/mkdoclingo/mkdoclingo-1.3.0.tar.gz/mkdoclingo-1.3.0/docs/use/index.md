---
icon: "material/rocket-launch"
---

# Usage

To use the extension just write the following code inside your documentation
and *mkdoclingo* will render the corresponding documentation in that place.

!!! example

    ```
    ::: relative-path-to-file.lp
        handler: asp
        options:
            ...
    ```

-  `relative-path-to-file.lp` is a relative path to an ASP encoding from the project root
-  `handler: asp` indicates that *mkdoclingo* will be used
-  `options` customize each section that can be included.


## Configuration options
- `encodings` See [**Encodings** section](../reference/sections/encodings)
- `predicate-table` See [**Predicate table** section](../reference/sections/predicate-table)
- `glossary` See [**Glossary** section](../reference/sections/glossary)
- `dependency-graph` See [**Dependency graph** section](../reference/sections/dependency-graph)
- `start-level` The initial markdown level. By default is `1`



<!-- ## TODO: Things to document

- Predicate docs
    - One predicate definiton per block comment

- How to customize your mkdocs material to get a nice layout for the table

- Comments of code are ignored in the encoding content. Make sure whatever is after your comment is not parsable by clingo if you want to show it -->
