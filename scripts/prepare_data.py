import pandas as pd
import os
from sklearn.model_selection import train_test_split

# -----------------------------------------------------
# 📂 Define paths
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "processed.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")

# -----------------------------------------------------
# 🧠 Function to check dataset
# -----------------------------------------------------
def quick_check(df):
    print(f"\n✅ File loaded successfully! Total rows: {len(df):,}")
    print("\n📊 Columns available:", df.columns.tolist())
    print("\n🔍 Sample rows:\n", df.head(10))
    print("\n🚫 Missing values check:\n", df.isnull().sum())

    if not {"FEN", "Move"}.issubset(df.columns):
        print("\n⚠️ Columns missing! Ensure your CSV has at least 'FEN' and 'Move' columns.")
    else:
        print("\n✅ Dataset is properly structured!")

# -----------------------------------------------------
# ✂️ Split data into Train/Test sets
# -----------------------------------------------------
def split_dataset():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Dataset not found at: {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)
    quick_check(df)

    # Split dataset (80% training, 20% testing)
    train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)

    # Save both files
    train_path = os.path.join(OUTPUT_DIR, "train_data.csv")
    test_path = os.path.join(OUTPUT_DIR, "test_data.csv")

    train_data.to_csv(train_path, index=False)
    test_data.to_csv(test_path, index=False)

    print("\n📁 Split complete:")
    print(f"  ➤ Training samples: {len(train_data)} → saved at {train_path}")
    print(f"  ➤ Testing samples:  {len(test_data)} → saved at {test_path}")

# -----------------------------------------------------
# 🚀 Main
# -----------------------------------------------------
if __name__ == "__main__":
    split_dataset()
