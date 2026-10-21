import b
#from b import x, spam
import sys
#b.spam('gumby')

#print(x)

print(f"Path: {sys.path}")

# This allows you to reference variable in another module.
# Trying to reference x directly, like print(x), will result in an error.
print(b.x)

# This is commonly used. This runs when the script is executed directly.
# So if we imported this and ran it from another file, this part would
# not execute.
if __name__ == '__main__':
    b.spam('gumby')