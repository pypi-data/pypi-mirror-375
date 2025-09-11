from softdata import load, clean, split

def test_iris_flow():
    df = load("iris")
    dfc = clean(df)
    Xtr, Xval, Xte, y = split(dfc, target="target")
    assert len(Xtr) > 0 and len(Xval) > 0 and len(Xte) > 0
    assert set(y.keys()) == {"train","val","test"}
