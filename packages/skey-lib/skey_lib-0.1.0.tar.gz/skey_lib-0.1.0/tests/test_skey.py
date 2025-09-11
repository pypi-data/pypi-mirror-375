import pytest
from skey.core import SKey

def test_skey_default():
  """should return expeted results."""
  password = "test"
  n = 500
  seed = "fo099804"
  hash = SKey()
  hash.skey(n,seed,password)
  hash.md5()
  print(hash.tolong())
  if hash.tolong() != 7368053831075371624:
      print("expetced tolong: 7368053831075371624 got:", hash.tolong())
  if hash.wordlist() != "CHOW AWE ELAN TOTE TOO PO": 
      print("expected wordlist: CHOW AWE ELAN TOTE TOO PO got: ", hash.wordlist())
