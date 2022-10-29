## OnSet Wiki to Json Converted
### This is a converted version of the OnSet Wiki to Json format.

This is useful for:
- Creating type definitions for Lua or Teal
- Creating snippets for VSCode, Sublime Text, etc.

## Usage
```sh
    python .\main.py [args]

    -g --generate : overwrite/generate the json api
    -t --threads : set the thread count (Note: categories will not work if it's higher than 1). Default is 1, takes around 150s with 1 thread and 44s with 4
    -p --prettify : prettify the json. Default is true
```

**Note:** I've rarely ever touch Python so the threading isn't the best, at least it works.