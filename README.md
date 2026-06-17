# OrbScript Programming Language

A clean, readable scripting language designed for automation, bots, and web applications.

## Quick Start

### Installation

**Windows:**
```batch 
install.bat```

**Linux/Mac/termux**

```
chmod +x install.sh
./install.sh
```

```
pip install orbscript
```

**Run It**
```
orbscript run hello.orb
```

**Run directly**
```
orbscript run -c 'say "Hello World"'
```


# Run a source file
orbscript run program.orb

# Compile to bytecode
orbscript compile program.orb -o program.orbc

# Execute bytecode
orbscript exec program.orbc

# Run multiple files
orbscript run file1.orb file2.orb

# Interactive mode
orbscript run

# Verbose output
orbscript run program.orb -v