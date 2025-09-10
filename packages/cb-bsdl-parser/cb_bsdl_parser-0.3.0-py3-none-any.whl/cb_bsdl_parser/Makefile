

# tools
E := @echo


all: generate_parser


gramar_files = CBBsdl.g4 \
			   CBBsdlLexer.g4

antlr4_files = CBBsdlParser.py CBBsdlLexer.py CBBsdlListener.py \
			   CBBsdl.tokens  CBBsdl.interp \
			   CBBsdlLexer.tokens CBBsdlLexer.interp \
			   .antlr


generate_parser: $(antlr4_files)


$(antlr4_files): $(gramar_files)
	$(E) "Generating python code from ANTLR grammar files..."
	@antlr4 -Dlanguage=Python3 $(gramar_files)


clean:
	$(E) "Cleaning up generated files..."
	@rm -rf $(antlr4_files)
	@rm -rf __pycache__
	@rm -rf */__pycache__