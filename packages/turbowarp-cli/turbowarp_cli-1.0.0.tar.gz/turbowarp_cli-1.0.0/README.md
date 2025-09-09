# tw-cli

> Run scratch projects in the terminal

> [!WARNING]
> These install instructions may not be enough if you are
> running a linux distro not directly supported by playright, e.g. arch.
> Make sure you can open chromium with playright with `playwright open` 
> before trying to use tw-cli

- Uses playwright and turbowarp scaffolding
- Supports the turbowarp debugger's log, warn, error and breakpoint blocks.

## Installation

`pip install turbowarp-cli`

<details>
<summary>Bleeding edge:</summary>
1. git clone this repo
2. `pip install -e .`
3. to update, use `git pull`
</details>

## Usage

`twcli run <Project path>`

It only works on project files.

---

If you want to automatically supply inputs to `ask and wait` blocks, use the -i command:

`twcli run .\Project.sb3 -i "hi" "there`

This provides the arguments:
- `hi`
- `there`

If you want to disable headless mode (to see the browser), use `-H`:

`twcli run .\Project.sb3 -i "hi" "there" -H`

If the exit code is 1, a Runtime error will always be raised.
The only way to exit with code 1 is with a breakpoint block.
Otherwise, the program will exit with code 0 when it naturally stops.

If you want to use your own 'error codes'

1. Use the error block. This will print in red but not exit the program
2. Use the breakpoint block

This is ^^ intentional design to keep things simpler.
