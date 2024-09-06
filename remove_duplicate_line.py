def remove_duplicates(file_name):
    # Read lines from file
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # Find and print duplicates
    duplicates = []
    seen = set()
    for line in lines:
        if line in seen:
            duplicates.append(line.strip())
        else:
            seen.add(line)

    if duplicates:
        print("Duplicate lines found:")
        for line in duplicates:
            print(line)

    # Remove duplicates
    unique_lines = list(seen)

    # Write unique lines back to the file
    with open(file_name, 'w') as file:
        file.writelines(unique_lines)

file_name = '/home/grading/yolov8_script/test.txt'  # Replace 'your_file.txt' with the path to your file

remove_duplicates(file_name)
