import generator
import string

code_gen = generator.Generator()

print("Only numbers:", code_gen.generate_numbers())
print("Only characters of latin:", code_gen.generate_chars())