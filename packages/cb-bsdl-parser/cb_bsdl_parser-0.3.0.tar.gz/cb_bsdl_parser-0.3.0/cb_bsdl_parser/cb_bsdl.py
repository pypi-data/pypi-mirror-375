from collections import OrderedDict
from antlr4 import *
from cb_bsdl_parser.CBBsdlLexer import CBBsdlLexer
from cb_bsdl_parser.CBBsdlParser import CBBsdlParser


class CBBsdl():
    def __init__(self, bsdl_file, check_bsr=True, verbose=False):

        self.bsdl_file = bsdl_file
        self.check_bsr = check_bsr
        self.verbose = verbose

        with open(self.bsdl_file, 'r') as file:
            input_text = file.read()

        lexer = CBBsdlLexer(InputStream(input_text))
        stream = CommonTokenStream(lexer)
        parser = CBBsdlParser(stream)

        self.tree = parser.bsdl()


        if self.check_entity_name() != True:
            raise ValueError("Entity name is not present or malformed in the BSDL content.")

        if self.check_bsr:
            if self.check_bsr_length() != True:
                raise ValueError("BSR length is not present or inconsistent in the BSDL content.")

        self.build_bsr_content()
        self.compile_bsr_ctrl_cells()


    def check_entity_name(self):
        """Checks if the entity name is present in the BSDL content."""
        if len(self.tree.entity().entity_name()) != 2:
            raise ValueError("Entity name is not present or malformed in the BSDL content.")

        if self.tree.entity().entity_name()[0].getText() != \
            self.tree.entity().entity_name()[1].getText():
            raise ValueError("Entity name is not correct the BSDL content.")

        return True

    def check_bsr_length(self):
        """Checks if the BSR length is present in the BSDL content."""


        attr_bsr_len0 = self.get_bsr_len()
        attr_bsr_len1 = len(self.tree.entity().body().attr_bsr()[0].bsr_def())

        if self.verbose:
            print(f'attr_bsr_len0: {attr_bsr_len0}, attr_bsr_len1: {attr_bsr_len1}')

        if attr_bsr_len0 != attr_bsr_len1:
            raise ValueError("BSR length not consistent.")

        return True


    def get_entity_name(self):
        """Extracts the entity name from the BSDL content."""
        return self.tree.entity().entity_name()[0].getText()

    def get_physical_pin_map(self):
        """Extracts the physical pin map from the BSDL content."""
        return self.tree.entity().body().generic_phys_pin_map()[0].phys_pin_map_name().getText()

    def get_bsr_len(self):
        """Extracts the BSR length from the BSDL content."""
        return int(self.tree.entity().body().attr_bsr_len()[0].bsr_len().getText())

    def build_bsr_content(self):
        """Builds the BSR content from the BSDL tree."""

        self.bsr = {}

        for i in range(self.get_bsr_len()):
            bsr_def = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].getText()

            data_cell = int(self.tree.entity().body().attr_bsr()[0].bsr_def()[i].data_cell().getText())

            if self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell0() is not None:
                cell_type = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell0().cell_type().getText()
                if self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell0().cell_desc() is not None:
                    cell_desc = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell0().cell_desc().getText()
                else:
                    cell_desc = '*'

                cell_func = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell0().cell_func().getText()
                cell_val = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell0().cell_val().getText()
                ctrl_cell = 0
                disval = 0

            elif self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell1() is not None:
                cell_type = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell1().cell_type().getText()
                if self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell1().cell_desc() is not None:
                    cell_desc = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell1().cell_desc().getText()
                else:
                    cell_desc = '*'

                cell_func = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell1().cell_func().getText()
                cell_val = self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell1().cell_val().getText()
                ctrl_cell = int(self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell1().ctrl_cell().getText())
                disval = int(self.tree.entity().body().attr_bsr()[0].bsr_def()[i].bsr_cell1().disval().getText())

            else:
                data_cell = 0
                cell_type = 'undef'
                cell_desc = 'undef'
                cell_func = 'undef'
                cell_val = 'undef'
                ctrl_cell = 0
                disval = 0


            bsr_cell = {
                'data_cell': data_cell,
                'cell_type': cell_type,
                'cell_desc': cell_desc,
                'cell_func': cell_func,
                'cell_val': cell_val,
                'ctrl_cell': ctrl_cell,
                'disval': disval
            }


            if cell_desc == '*':
                cell_desc = f'cell_{data_cell}'

            if cell_func.upper() in ['INPUT', 'OBSERVE_ONLY']:
                key_a = 'in'
            elif cell_func.upper() in ['OUTPUT', 'OUTPUT2', 'OUTPUT3']:
                key_a = 'out'
            elif cell_func.upper() in ['CONTROL']:
                key_a = 'ctrl'
            elif cell_func.upper() in ['INTERNAL']:
                key_a = ''
            else:
                key_a = ''
                print(f'Warning: cell_func {cell_func} not recognized for cell_desc {cell_desc}')

            if key_a != '':
                key = f'{cell_desc}_{key_a}'
            else:
                key = cell_desc


            self.bsr[key] = bsr_cell


    def compile_bsr_ctrl_cells(self):
        """Compiles control cells from the BSR content."""

        # print('')
        # print('BSR content:')
        # for pin_desc, cell in self.bsr.items():
        #     print(f'  {pin_desc}: {cell}')

        for i in range(len(self.bsr)):
            cell_desc = list(self.bsr.keys())[i]
            cell = self.bsr[cell_desc]

            ctrl_cell_used = 0

            if cell_desc.endswith('_out'):
                if self.verbose:
                    print(f'Control cell found: {cell_desc}, data_cell: {cell['data_cell']} ctrl_cell: {cell['ctrl_cell']}   ', end='')

                for key, ccell in self.bsr.items():
                    if ccell['ctrl_cell'] != '' and int(ccell['ctrl_cell']) == int(cell['ctrl_cell']):
                        ctrl_cell_used += 1
                        if self.verbose:
                            print(f'  {key} has ctrl_cell {ccell['ctrl_cell']}')

                if ctrl_cell_used == 1:
                    new_key_ctrl_cell = f'{cell['cell_desc']}_ctrl'
                    old_key_ctrl_cell = f'cell_{cell['ctrl_cell']}_ctrl'



                    if self.verbose:
                        print(f'modify key: {old_key_ctrl_cell} -> {new_key_ctrl_cell}  ')

                    if int(cell['data_cell']) != int(cell['ctrl_cell']):
                        self.bsr[new_key_ctrl_cell] = self.bsr.pop(old_key_ctrl_cell)
                    else:
                        print(f'Warning: {cell['cell_desc']} does not have a separate ctrl_cell')


        # Sort the BSR content by data_cell
        self.bsr = OrderedDict(sorted(self.bsr.items(), key=lambda t: t[1]['data_cell']))

    def get_bsr(self):
        """Returns the BSR content."""
        return self.bsr


    def print_bsr_table(self):
        """Prints the BSDL BSR content information."""
        print(f'BSDL file: {self.bsdl_file}')
        print(f'Entity name: {self.get_entity_name()}')
        print(f'Physical pin map: {self.get_physical_pin_map()}')
        print(f'BSR length: {self.get_bsr_len()}')
        print('BSR content:')
        for bsr_cell in self.bsr.keys():

            if self.bsr[bsr_cell]['cell_func'] != 'internal':
                print(f'  {bsr_cell:10s} '\
                      f'{self.bsr[bsr_cell]['data_cell']:3d}   '\
                      f'type: {self.bsr[bsr_cell]['cell_type']:4s}   '\
                      f'desc: {self.bsr[bsr_cell]['cell_desc']:6s}   '\
                      f'func: {self.bsr[bsr_cell]['cell_func']:9s}   '\
                      f'val: {self.bsr[bsr_cell]['cell_val']:1s}   '\
                      f'ctrl_cell: {self.bsr[bsr_cell]['ctrl_cell']:3d}')


    def get_bsr_data_cell(self, cell_desc):
        """Returns the cell number for a given cell description."""
        if cell_desc in self.bsr:
            return self.bsr[cell_desc]['data_cell']
        else:
            raise ValueError(f"Cell description {cell_desc} not found in BSR content.")

    def get_bsr_cell_type(self, cell_desc):
        """Returns the cell type for a given cell description."""
        if cell_desc in self.bsr:
            return self.bsr[cell_desc]['cell_type']
        else:
            raise ValueError(f"Cell description {cell_desc} not found in BSR content.")

    def get_bsr_cell_desc(self, cell_desc):
        """Returns the cell description for a given cell description."""
        if cell_desc in self.bsr:
            return self.bsr[cell_desc]['cell_desc']
        else:
            raise ValueError(f"Cell description {cell_desc} not found in BSR content.")

    def get_bsr_cell_func(self, cell_desc):
        """Returns the cell function for a given cell description."""
        if cell_desc in self.bsr:
            return self.bsr[cell_desc]['cell_func']
        else:
            raise ValueError(f"Cell description {cell_desc} not found in BSR content.")

    def get_bsr_cell_val(self, cell_desc):
        """Returns the cell value for a given cell description."""
        if cell_desc in self.bsr:
            return self.bsr[cell_desc]['cell_val']
        else:
            raise ValueError(f"Cell description {cell_desc} not found in BSR content.")

    def get_bsr_ctrl_cell(self, cell_desc):
        """Returns the control cell for a given cell description."""
        if cell_desc in self.bsr:
            return self.bsr[cell_desc]['ctrl_cell']
        else:
            raise ValueError(f"Cell description {cell_desc} not found in BSR content.")

    def get_bsr_disval(self, cell_desc):
        """Returns the disable value for a given cell description."""
        if cell_desc in self.bsr:
            return self.bsr[cell_desc]['disval']
        else:
            raise ValueError(f"Cell description {cell_desc} not found in BSR content.")