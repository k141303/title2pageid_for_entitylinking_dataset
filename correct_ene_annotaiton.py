import os
import glob
import argparse

from data_utils import Title2Pageid, DataUtils

TARGET_ATTRIBUTE_PATH = "./data/target_attribute_linkjp_210315.csv"

def load_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("annotation_file_dir", type=str)
    parser.add_argument("output_dir", type=str)
    return parser.parse_args()

if __name__ == '__main__':
    target_attributes = DataUtils.Csv.load(TARGET_ATTRIBUTE_PATH, "utf-8-sig")
    target_attributes = {category:set(attr.strip() for attr in attributes.split("、")) for _, category, attributes in target_attributes}

    args = load_arg()

    os.makedirs(args.output_dir, exist_ok=True)

    ignored_attributes = set()
    for target in glob.glob(os.path.join(args.annotation_file_dir, "*.json")):
        if "_for_view.json" in target:
            continue

        category, _ = os.path.splitext(os.path.basename(target))

        data = DataUtils.JsonL.load(target)
        new_data = []
        for d in data:
            if d["attribute"] not in target_attributes[category]:
                ignored_attributes.add((category, d["attribute"]))
                continue

            new_data.append(d)

        DataUtils.JsonL.save(
            os.path.join(args.output_dir, f"{category}.json"),
            new_data
        )
        DataUtils.JsonL.save_for_view(
            os.path.join(args.output_dir, f"{category}_for_view.json"),
            new_data
        )

    print(ignored_attributes)
