# Generated from CBBsdl.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .CBBsdlParser import CBBsdlParser
else:
    from CBBsdlParser import CBBsdlParser

# This class defines a complete listener for a parse tree produced by CBBsdlParser.
class CBBsdlListener(ParseTreeListener):

    # Enter a parse tree produced by CBBsdlParser#bsdl.
    def enterBsdl(self, ctx:CBBsdlParser.BsdlContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#bsdl.
    def exitBsdl(self, ctx:CBBsdlParser.BsdlContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#entity.
    def enterEntity(self, ctx:CBBsdlParser.EntityContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#entity.
    def exitEntity(self, ctx:CBBsdlParser.EntityContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#entity_name.
    def enterEntity_name(self, ctx:CBBsdlParser.Entity_nameContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#entity_name.
    def exitEntity_name(self, ctx:CBBsdlParser.Entity_nameContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#body.
    def enterBody(self, ctx:CBBsdlParser.BodyContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#body.
    def exitBody(self, ctx:CBBsdlParser.BodyContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#generic_phys_pin_map.
    def enterGeneric_phys_pin_map(self, ctx:CBBsdlParser.Generic_phys_pin_mapContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#generic_phys_pin_map.
    def exitGeneric_phys_pin_map(self, ctx:CBBsdlParser.Generic_phys_pin_mapContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#phys_pin_map_name.
    def enterPhys_pin_map_name(self, ctx:CBBsdlParser.Phys_pin_map_nameContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#phys_pin_map_name.
    def exitPhys_pin_map_name(self, ctx:CBBsdlParser.Phys_pin_map_nameContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#attr_bsr_len.
    def enterAttr_bsr_len(self, ctx:CBBsdlParser.Attr_bsr_lenContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#attr_bsr_len.
    def exitAttr_bsr_len(self, ctx:CBBsdlParser.Attr_bsr_lenContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#bsr_len.
    def enterBsr_len(self, ctx:CBBsdlParser.Bsr_lenContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#bsr_len.
    def exitBsr_len(self, ctx:CBBsdlParser.Bsr_lenContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#log_port_desc.
    def enterLog_port_desc(self, ctx:CBBsdlParser.Log_port_descContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#log_port_desc.
    def exitLog_port_desc(self, ctx:CBBsdlParser.Log_port_descContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#port_def.
    def enterPort_def(self, ctx:CBBsdlParser.Port_defContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#port_def.
    def exitPort_def(self, ctx:CBBsdlParser.Port_defContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#port_name.
    def enterPort_name(self, ctx:CBBsdlParser.Port_nameContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#port_name.
    def exitPort_name(self, ctx:CBBsdlParser.Port_nameContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#port_function.
    def enterPort_function(self, ctx:CBBsdlParser.Port_functionContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#port_function.
    def exitPort_function(self, ctx:CBBsdlParser.Port_functionContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#port_type.
    def enterPort_type(self, ctx:CBBsdlParser.Port_typeContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#port_type.
    def exitPort_type(self, ctx:CBBsdlParser.Port_typeContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#bit.
    def enterBit(self, ctx:CBBsdlParser.BitContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#bit.
    def exitBit(self, ctx:CBBsdlParser.BitContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#bit_vector.
    def enterBit_vector(self, ctx:CBBsdlParser.Bit_vectorContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#bit_vector.
    def exitBit_vector(self, ctx:CBBsdlParser.Bit_vectorContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#attr_bsr.
    def enterAttr_bsr(self, ctx:CBBsdlParser.Attr_bsrContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#attr_bsr.
    def exitAttr_bsr(self, ctx:CBBsdlParser.Attr_bsrContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#bsr_def.
    def enterBsr_def(self, ctx:CBBsdlParser.Bsr_defContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#bsr_def.
    def exitBsr_def(self, ctx:CBBsdlParser.Bsr_defContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#data_cell.
    def enterData_cell(self, ctx:CBBsdlParser.Data_cellContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#data_cell.
    def exitData_cell(self, ctx:CBBsdlParser.Data_cellContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#bsr_cell0.
    def enterBsr_cell0(self, ctx:CBBsdlParser.Bsr_cell0Context):
        pass

    # Exit a parse tree produced by CBBsdlParser#bsr_cell0.
    def exitBsr_cell0(self, ctx:CBBsdlParser.Bsr_cell0Context):
        pass


    # Enter a parse tree produced by CBBsdlParser#bsr_cell1.
    def enterBsr_cell1(self, ctx:CBBsdlParser.Bsr_cell1Context):
        pass

    # Exit a parse tree produced by CBBsdlParser#bsr_cell1.
    def exitBsr_cell1(self, ctx:CBBsdlParser.Bsr_cell1Context):
        pass


    # Enter a parse tree produced by CBBsdlParser#cell_type.
    def enterCell_type(self, ctx:CBBsdlParser.Cell_typeContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#cell_type.
    def exitCell_type(self, ctx:CBBsdlParser.Cell_typeContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#cell_desc.
    def enterCell_desc(self, ctx:CBBsdlParser.Cell_descContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#cell_desc.
    def exitCell_desc(self, ctx:CBBsdlParser.Cell_descContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#cell_func.
    def enterCell_func(self, ctx:CBBsdlParser.Cell_funcContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#cell_func.
    def exitCell_func(self, ctx:CBBsdlParser.Cell_funcContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#cell_val.
    def enterCell_val(self, ctx:CBBsdlParser.Cell_valContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#cell_val.
    def exitCell_val(self, ctx:CBBsdlParser.Cell_valContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#ctrl_cell.
    def enterCtrl_cell(self, ctx:CBBsdlParser.Ctrl_cellContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#ctrl_cell.
    def exitCtrl_cell(self, ctx:CBBsdlParser.Ctrl_cellContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#disval.
    def enterDisval(self, ctx:CBBsdlParser.DisvalContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#disval.
    def exitDisval(self, ctx:CBBsdlParser.DisvalContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#bit_range.
    def enterBit_range(self, ctx:CBBsdlParser.Bit_rangeContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#bit_range.
    def exitBit_range(self, ctx:CBBsdlParser.Bit_rangeContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#undef_part.
    def enterUndef_part(self, ctx:CBBsdlParser.Undef_partContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#undef_part.
    def exitUndef_part(self, ctx:CBBsdlParser.Undef_partContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#number.
    def enterNumber(self, ctx:CBBsdlParser.NumberContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#number.
    def exitNumber(self, ctx:CBBsdlParser.NumberContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#identifier.
    def enterIdentifier(self, ctx:CBBsdlParser.IdentifierContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#identifier.
    def exitIdentifier(self, ctx:CBBsdlParser.IdentifierContext):
        pass


    # Enter a parse tree produced by CBBsdlParser#comment.
    def enterComment(self, ctx:CBBsdlParser.CommentContext):
        pass

    # Exit a parse tree produced by CBBsdlParser#comment.
    def exitComment(self, ctx:CBBsdlParser.CommentContext):
        pass



del CBBsdlParser