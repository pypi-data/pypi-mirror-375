from softdata import load, clean, split

def main():
    df = load("iris")
    print("Loaded:", df.shape, list(df.columns)[:5], "...")
    df = clean(df)
    Xtr, Xval, Xte, y = split(df, target="target")
    print("Splits:", Xtr.shape, Xval.shape, Xte.shape)
    print("y train unique:", y["train"].nunique())

if __name__ == "__main__":
    main()
