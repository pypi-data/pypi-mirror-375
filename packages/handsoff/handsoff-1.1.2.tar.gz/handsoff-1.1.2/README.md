# Handsoff

Automatic file transfer with `scp` `UNIX` command.

# Installation

It's on `pip` server.

```bash
pip install handsoff
```

# Usage Examples

## In terminal

### Set

```bash
handsoff set user=MovingJu port=22 host=localhost client="README.md" server="Target_dir"
```

or you can simply define these attributes in .env file and recall env file.

```env
HOST = "localhost"
PORT = "22"
USER = "MovingJu"
```

```bash
handsoff set env="handsoff.env"
```

### Push or Pull

```bash
handsoff (push/pull) ^`client` ^`server`
```

> ^ is optional.

## In python code

```python
import handsoff

my_computer_1 = handsoff.Commands({
    "env" : "handsoff.env"
})

my_computer_1.push()
my_computer_1.pull("src/*", "~/Documents")
```