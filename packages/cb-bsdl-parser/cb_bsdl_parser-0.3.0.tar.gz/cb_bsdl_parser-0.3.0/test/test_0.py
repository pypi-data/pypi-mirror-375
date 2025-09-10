import pytest
import yaml

from cb_bsdl_parser.cb_bsdl import CBBsdl

my_params = ['i2c', 'spi']

test_params_file = 'test/test_params.yaml'

def get_test_params():
    with open(test_params_file, 'r') as yaml_file:
        params = yaml.safe_load(yaml_file)


    print("Test parameters loaded:")
    for key, value in params.items():
        print(f"{key}: {value}")


    for param in params:
        yield params[param]


class Test_BsdlParser:
    @pytest.fixture(autouse=True, params=get_test_params())
    @classmethod
    def setup_class(self, request):
        "Runs at start/setup of class"
        print(f'Setting up test for file: {request.param['name']}')

        self.bsdl_file = request.param['file_name']
        self.expected_entity_name = request.param['entity_name']
        self.expected_physical_pin_map = request.param['physical_pin_map']

        self.expected_bsr_len = int(request.param['bsr_len'])
        self.check_bsr = request.param.get('check_bsr', True)
        self.expected_bsr_cell = request.param.get('bsr_cell', '')
        self.expected_bsr_data_cell = request.param.get('bsr_data_cell', '')
        self.expected_bsr_cell_type = request.param.get('bsr_cell_type', '')
        self.expected_bsr_cell_desc = request.param.get('bsr_cell_desc', '')
        self.expected_bsr_cell_func = request.param.get('bsr_cell_func', '')
        self.expected_bsr_cell_val = request.param.get('bsr_cell_val', '')
        self.expected_bsr_ctrl_cell = request.param.get('bsr_ctrl_cell', 0)
        self.expected_bsr_disval = request.param.get('bsr_disval', 0)

        self.bdsl = CBBsdl(self.bsdl_file,
                           check_bsr=self.check_bsr)


    @classmethod
    def teardown_class(self):
        "Runs at end/teardown of class"
        pass


    def setup_method(self, method):
        """Called before each test method."""
        pass

    def teardown_method(self, method):
        """Called after each test method."""
        pass

    def test_check_entity_name(self):
        print("Testing entity name check")
        entity_name_check = self.bdsl.check_entity_name()
        assert entity_name_check is True, "Entity name check failed"

    def test_entity_name(self):
        print("Testing entity name extraction")
        entity_name = self.bdsl.get_entity_name()
        print(f'entity_name: {entity_name}')
        assert entity_name == self.expected_entity_name


    def test_physical_pin_map(self):
        print("Testing physical pin map extraction")
        physical_pin_map = self.bdsl.get_physical_pin_map()
        print(f'physical_pin_map: {physical_pin_map}')
        assert physical_pin_map == self.expected_physical_pin_map


    def test_bsr_length(self):
        print("Testing BSR length extraction")
        bsr_len = self.bdsl.get_bsr_len()
        print(f'bsr_length: {bsr_len}')
        assert bsr_len == self.expected_bsr_len, "BSR length does not match expected value"

    def test_bsr(self):
        print("Testing BSR content extraction")
        bsr = self.bdsl.get_bsr()

        # print(bsr)
        print(f'bsr[{self.expected_bsr_cell}: {bsr[self.expected_bsr_cell]}]')

        # bsr_cell = self.bdsl.get_bsr_cell(self.expected_bsr_cell)
        bsr_data_cell = self.bdsl.get_bsr_data_cell(self.expected_bsr_cell)
        bsr_cell_type = self.bdsl.get_bsr_cell_type(self.expected_bsr_cell)
        bsr_cell_desc = self.bdsl.get_bsr_cell_desc(self.expected_bsr_cell)
        bsr_cell_func = self.bdsl.get_bsr_cell_func(self.expected_bsr_cell)
        bsr_cell_val = self.bdsl.get_bsr_cell_val(self.expected_bsr_cell)
        bsr_ctrl_cell = self.bdsl.get_bsr_ctrl_cell(self.expected_bsr_cell)
        bsr_disval = self.bdsl.get_bsr_disval(self.expected_bsr_cell)

        # assert bsr_cell == self.expected_bsr_cell
        assert bsr_data_cell == self.expected_bsr_data_cell
        assert bsr_cell_type == self.expected_bsr_cell_type
        assert bsr_cell_desc == self.expected_bsr_cell_desc
        assert bsr_cell_func == self.expected_bsr_cell_func
        assert bsr_cell_val == self.expected_bsr_cell_val
        if self.expected_bsr_ctrl_cell is not None:
            assert bsr_ctrl_cell == self.expected_bsr_ctrl_cell
            assert bsr_disval == self.expected_bsr_disval