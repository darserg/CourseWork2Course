import generator
# Tests for generator
code_gen = generator.Generator()

print("Only numbers:", code_gen.generate_numbers())
print("Only characters of latin:", code_gen.generate_chars())
print("Complex code", code_gen.complex_code())
