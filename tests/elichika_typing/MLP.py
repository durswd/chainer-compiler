import ast, gast
import numpy as np
import pprint
import unittest

from chainer_compiler.elichika.testtools import generate_id2type_from_forward

from testcases.elichika_tests.model.MLP import MLP

class TestMLP(unittest.TestCase):
    def test_MLP(self):
        out_n = 4
        batch_size = 100
        model = MLP(8, out_n)
        v = np.random.rand(batch_size, 3).astype(np.float32)
        w = np.random.randint(out_n, size=batch_size)

        node_type = generate_id2type_from_forward(model, (v, w))

        self.assertEqual(str(node_type[1]), "ndarray(dtype=float32) -> ndarray(dtype=int64) -> Variable(dtype=float32)")	# FunctionDef (line 1)
        self.assertEqual(str(node_type[9]), "NoneType")	# Assign (line 2)
        self.assertEqual(str(node_type[10]), "Variable(dtype=float32)")	# Name (line 2)
        self.assertEqual(str(node_type[12]), "Variable(dtype=float32)")	# Call (line 2)
        self.assertEqual(str(node_type[13]), "Variable(dtype=float32) -> Variable(dtype=float32)")	# Attribute (line 2)
        self.assertEqual(str(node_type[17]), "Variable(dtype=float32)")	# Call (line 2)
        self.assertEqual(str(node_type[18]), "Variable(dtype=float32) -> Variable(dtype=float32)")	# Attribute (line 2)
        self.assertEqual(str(node_type[22]), "ndarray(dtype=float32)")	# Name (line 2)
        self.assertEqual(str(node_type[24]), "NoneType")	# Assign (line 3)
        self.assertEqual(str(node_type[25]), "Variable(dtype=float32)")	# Name (line 3)
        self.assertEqual(str(node_type[27]), "Variable(dtype=float32)")	# Call (line 3)
        self.assertEqual(str(node_type[28]), "Variable(dtype=float32) -> Variable(dtype=float32)")	# Attribute (line 3)
        self.assertEqual(str(node_type[32]), "Variable(dtype=float32)")	# Call (line 3)
        self.assertEqual(str(node_type[33]), "Variable(dtype=float32) -> Variable(dtype=float32)")	# Attribute (line 3)
        self.assertEqual(str(node_type[37]), "Variable(dtype=float32)")	# Name (line 3)
        self.assertEqual(str(node_type[39]), "NoneType")	# Assign (line 4)
        self.assertEqual(str(node_type[40]), "Variable(dtype=float32)")	# Name (line 4)
        self.assertEqual(str(node_type[42]), "Variable(dtype=float32)")	# Call (line 4)
        self.assertEqual(str(node_type[43]), "Variable(dtype=float32) -> Variable(dtype=float32)")	# Attribute (line 4)
        self.assertEqual(str(node_type[47]), "Variable(dtype=float32)")	# Name (line 4)
        self.assertEqual(str(node_type[49]), "NoneType")	# Assign (line 5)
        self.assertEqual(str(node_type[50]), "Variable(dtype=float32)")	# Name (line 5)
        self.assertEqual(str(node_type[52]), "Variable(dtype=float32)")	# Call (line 5)
        self.assertEqual(str(node_type[53]), "Variable(dtype=float32) -> ndarray(dtype=int64) -> Variable(dtype=float32)")	# Attribute (line 5)
        self.assertEqual(str(node_type[57]), "Variable(dtype=float32)")	# Name (line 5)
        self.assertEqual(str(node_type[59]), "ndarray(dtype=int64)")	# Name (line 5)
        self.assertEqual(str(node_type[61]), "Variable(dtype=float32)")	# Return (line 6)
        self.assertEqual(str(node_type[62]), "Variable(dtype=float32)")	# Name (line 6)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
