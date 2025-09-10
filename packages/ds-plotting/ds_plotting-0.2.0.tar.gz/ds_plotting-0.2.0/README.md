# ds-plotting

## Usage

Let's say you want to plot all data in

```shell
"/Users/YOU/Downloads/set"
```

and there is a file `MyReference.fit` that is your reference, then you can simply run

```shell
uv run src/ds_plotting/main.py                      \
    --crux_common="/PATH/TO/YOUR/crux_common/"  \
    --width=1600                                \
    --height=200                                \
    --rolling_window=1                          \
    --silent=True                               \
    --zero=False                                \
    --folder="/Users/YOU/Downloads/set"         \
    --reference_file="MyReference.fit"          \
    --cleanup=True                              \
;
```

If you have `crux_common` defined in your `~/.wahoofitness.json`, you can skip that argument.
