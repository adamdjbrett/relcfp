#!/bin/bash

XML_FILE="feed.xml"
JSON_FILE="_data/feed.json"

hash_file() {
    local file_path="$1"
    openssl md5 "$file_path" | awk '{ print $2 }'
}

compare_files_by_hash() {
    local file1_path="$1"
    local file2_path="$2"
    local hash1=$(hash_file "$file1_path")
    local hash2=$(hash_file "$file2_path")
    
    if [ "$hash1" == "$hash2" ]; then
        return 0  # Files are identical
    else
        return 1  # Files are different
    fi
}

# Function to validate JSON
validate_json() {
    python3 - <<END
import json
import sys

try:
    json.loads(sys.stdin.read())
    print("Valid JSON")
    sys.exit(0)
except ValueError as e:
    print(f"Invalid JSON: {e}")
    sys.exit(1)
END
}

# Read XML file and convert to JSON
convert_xml_to_json() {
    python3 - <<END
import xmltodict
import json
import sys

xml_file_path = sys.argv[1]
json_file_path = sys.argv[2]

try:
    with open(xml_file_path, 'r') as xml_file:
        xml_data = xml_file.read()
        xml_dict = xmltodict.parse(xml_data)
        json_data = json.dumps(xml_dict, indent=4)
        with open(json_file_path, 'w') as json_file:
            json_file.write(json_data)
    print("Conversion successful")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
END
}

# Backup current feed.xml
cp $XML_FILE old_feed.xml

wget -O feed.xml 'https://input.relcfp.com/feed.xml'
sed -i 's/<!\[CDATA\[//g' feed.xml
sed -i 's/]]>//g' feed.xml
sed -i 's/<br>/<br\/>/g' feed.xml
sed -i 's/<hr>/<hr\/>/g' feed.xml

# Compare the old and new feed files
if compare_files_by_hash "old_feed.xml" "$XML_FILE"; then
    echo "Files are identical"
    rm old_feed.xml
    exit 0
else
    echo "Files are different"
    rm old_feed.xml

    convert_xml_to_json "$XML_FILE" "$JSON_FILE"

    # Validate JSON
    if cat "$JSON_FILE" | validate_json; then
        echo "JSON is valid"
    else
        echo "JSON is invalid"
    fi
    exit 1
fi
