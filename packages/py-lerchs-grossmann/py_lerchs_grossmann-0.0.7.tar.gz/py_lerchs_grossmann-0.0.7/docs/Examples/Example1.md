# Basic Example

this is a basic example how to use the `py-lerchs-grossmann` package to obtain optimum pit in a block model.

## Block Model

The block model must have the next columns `id` and `value`, to the well performing of the package.

## Arc dataframe

The Arc Dataframe is a table where is the conections or arcs between the blocks, it is because to mine a block, we must have to mine the blocks upside.

```python
import pandas as pd
import py_lerchs_grossmann as plg

# Definir los datos de bloques y arcos
    df_y = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "x": [1, 2, 3, 4, 5, 2, 3, 4, 3],
            "y": [1, 1, 1, 1, 1, 1, 1, 1, 1],
            "z": [3, 3, 3, 3, 3, 2, 2, 2, 1],
            "value": [-1, -1, -1, -1, -1, -1, -1, 3, 5],
        }
    )

    df_arc = pd.DataFrame(
        {
            "start": [6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9],
            "end": [1, 2, 3, 2, 3, 4, 3, 4, 5, 6, 7, 8],
        }
    )

    df_pit = main(df_y, df_arc, True)
```
