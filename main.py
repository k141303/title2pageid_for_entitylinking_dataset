import os
import glob
import argparse

from data_utils import Title2Pageid, DataUtils

TITLES_PATH = "./data/jawiki-20190120-titles.json"
REDIRECTS_PATH = "./data/jawiki-20190120-redirects.json"
TARGET_ATTRIBUTE_PATH = "./data/target_attribute_linkjp_210315.csv"

PATCH = {
    ("2957349", 37, 54, 37, 56) :"楊播",
    ("418969", 137, 123, 137, 137): "板東英二金曜生BAN BAN",
    ("2920111", 46, 787, 46, 790): "安西慎太郎",
    ("2760818", 42, 130, 42, 139): "夜と血のカンケイ。"
}

def load_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("annotation_file_dir", type=str)
    parser.add_argument("output_dir", type=str)
    return parser.parse_args()

if __name__ == '__main__':
    target_attributes = DataUtils.Csv.load(TARGET_ATTRIBUTE_PATH, "utf-8-sig")
    target_attributes = {category:set(attr.strip() for attr in attributes.split("、")) for _, category, attributes in target_attributes}

    title2pageid = Title2Pageid(TITLES_PATH, REDIRECTS_PATH)

    args = load_arg()

    os.makedirs(args.output_dir, exist_ok=True)

    error = []
    ignored_attributes = set()
    for target in glob.glob(os.path.join(args.annotation_file_dir, "*.json")):
        if "_for_view.json" in target:
            continue

        category, _ = os.path.splitext(os.path.basename(target))

        data = DataUtils.JsonL.load(target)
        new_data = []
        for d in data:
            title, *_ = d["link_title"].split("#")

            pageid = title2pageid.convert(title)
            if pageid is None:
                offset = d["html_offset"]
                title = PATCH.get((d["page_id"], offset["start"]["line_id"], offset["start"]["offset"], offset["end"]["line_id"], offset["end"]["offset"]))
                if title is None:
                    assert False, d
                pageid = title2pageid.convert(title)
                if pageid is None:
                    error.append(d)
                    continue

            del d["link_title"]
            d["link_page_id"] = str(pageid)

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

    DataUtils.JsonL.save("error.json", error)
    print(ignored_attributes)
