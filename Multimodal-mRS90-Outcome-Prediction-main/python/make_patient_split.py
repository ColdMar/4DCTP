import argparse
import os
import pickle
import random


def find_patient_ids(datasets_root):
    patient_ids = []
    for name in sorted(os.listdir(datasets_root)):
        patient_dir = os.path.join(datasets_root, name)
        if not os.path.isdir(patient_dir):
            continue
        if os.path.exists(os.path.join(patient_dir, "preprocessed.npz")):
            patient_ids.append(name)
    return patient_ids


def split_ids(patient_ids, train_ratio, val_ratio, seed):
    rng = random.Random(seed)
    ids = patient_ids[:]
    rng.shuffle(ids)

    total = len(ids)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    training = ids[:train_end]
    validation = ids[train_end:val_end]
    testing = ids[val_end:]

    return training, validation, testing


def main():
    parser = argparse.ArgumentParser(description="Create patient split pickle file.")
    parser.add_argument(
        "--datasets-root",
        default="python/datasets",
        help="Directory containing per-patient folders with preprocessed.npz.",
    )
    parser.add_argument(
        "--output",
        default="python/datasets/patient_dictionary.pickle",
        help="Output pickle path.",
    )
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    patient_ids = find_patient_ids(args.datasets_root)
    if not patient_ids:
        print("No patient folders found. Check --datasets-root.")
        return

    training, validation, testing = split_ids(
        patient_ids, args.train_ratio, args.val_ratio, args.seed
    )

    partition = {
        "training": training,
        "validation": validation,
        "testing": testing,
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "wb") as handle:
        pickle.dump(partition, handle)

    print(
        "Saved split:",
        f"training={len(training)}",
        f"validation={len(validation)}",
        f"testing={len(testing)}",
        "->",
        args.output,
    )


if __name__ == "__main__":
    main()
