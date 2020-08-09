import pytest

from pyzem.swc import swc

def test_swc_node():
  tn = swc.SwcNode()
  assert tn.is_virtual()

if __name__ == "__main__":
    args = ['-s', '--tb=native', '--pyargs', 'pyzem.tests.test_swc']
    pytest.main(args)
