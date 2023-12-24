# Testing your cli app.

The general idea behind Clipstick is populating a pydantic model based on arguments provided by the user of your cli tool.

If you want to test your cli you can do just that: provide arguments and validate whether your model is populated correctly:


```{literalinclude} ../tests/test_simple.py
:lines: -20
```


