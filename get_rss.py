import hashlib
import json
import os
import re
import requests
import xmltodict
import sys

XML_FILE = "feed.xml"
JSON_FILE = "_data/feed.json"
OLD_XML_FILE = "old_feed.xml"


def hash_file(file_path):
    """Compute MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def compare_files_by_hash(file1_path, file2_path):
    """Compare files by their MD5 hash."""
    hash1 = hash_file(file1_path)
    hash2 = hash_file(file2_path)
    return hash1 == hash2


def validate_json(json_data):
    """Validate JSON format."""
    try:
        json.loads(json_data)
        print("Valid JSON")
        return True
    except ValueError as e:
        print(f"Invalid JSON: {e}")
        return False


def convert_xml_to_json(xml_file_path, json_file_path):
    """Convert XML to JSON using xmltodict."""
    try:
        with open(xml_file_path, "r") as xml_file:
            xml_data = xml_file.read()
            xml_dict = xmltodict.parse(xml_data)
            json_data = json.dumps(xml_dict, indent=4)
            with open(json_file_path, "w") as json_file:
                json_file.write(json_data)
        print("Conversion successful")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    # Backup current feed.xml
    if os.path.exists(XML_FILE):
        os.rename(XML_FILE, OLD_XML_FILE)

    # Download new feed.xml
    url = "https://input.relcfp.com/feed.xml"
    response = requests.get(url)
    if response.status_code == 200:
        with open(XML_FILE, "w") as file:
            file.write(response.text)

    # Perform text replacements
    with open(XML_FILE, "r+") as file:
        xml_content = file.read()
        xml_content = re.sub(r"<!\[CDATA\[", "", xml_content)
        xml_content = re.sub(r"\]\]>", "", xml_content)
        xml_content = re.sub(r"<br>", "<br/>", xml_content)
        xml_content = re.sub(r"<hr>", "<hr/>", xml_content)
        file.seek(0)
        file.write(xml_content)
        file.truncate()

    # Compare the old and new feed files
    if compare_files_by_hash(OLD_XML_FILE, XML_FILE):
        print("Files are identical")
        os.remove(OLD_XML_FILE)
        # Comment below line if running locally
        sys.stdout.write(f"::set-output name=content_changed::false\n")

    else:
        print("Files are different")
        os.remove(OLD_XML_FILE)
        # Comment below line if running locally
        sys.stdout.write(f"::set-output name=content_changed::true\n")
        if convert_xml_to_json(XML_FILE, JSON_FILE):
            # Validate JSON
            with open(JSON_FILE, "r") as json_file:
                json_data = json_file.read()
                if validate_json(json_data):
                    print("JSON is valid")
                else:
                    print("JSON is invalid")
        else:
            print("Failed to convert")


if __name__ == "__main__":
    main()
