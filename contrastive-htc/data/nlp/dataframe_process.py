import pandas as pd

# reading the annotations
def read_annotations(annotations_path):
    with open(annotations_path, 'r') as file:
        content = file.read().split("\n")
    
    # getting data into the list
    data_annotations_list = []
    for i in content:
        data_annotations_list.append(i.split("\t"))
    
    # print(data_list)
        
    # getting data into a dataframe
    data = pd.DataFrame(data_annotations_list, columns = ["file_name", "narrative", "subnarrative"])
    
    # dropping last empty row
    data = data[:-1]
    data
    return data

# reading the files in the same order
def read_files(dataframe, file_path):
    data = dataframe
    data_text_list = []
    for i in dataframe["file_name"]:
        file_name = file_path + i
        with open(file_name, 'r') as file:
            data_text_list.append(file.read())
            # print(file.read())
    data["text"] = data_text_list
    return data
    



# functions for extracting the narratives into proper format
def is_CC_URW(text):
    if "CC" in text:
        return ["CC"]
    if "URW" in text: 
        return ["URW"]
    if "CC" in text and "URW" in text:
        return ["CC", "URW"]
    else:
        return ["Other"]

def remove_backslash(text):
    text = text.replace("/", " or ")
    return text

def create_label_path(text):
    label_path = text.replace(": ", "/")
    return label_path

def drop_other(text):
    return text.replace("/Other", "")

def add_top(text):
    new_list = []
    for i in text:
        i = "Top/" + i
        new_list.append(i)
    return new_list

def get_data(path_annotations, path_files):
    data_annotations = read_annotations(path_annotations)
    data = read_files(data_annotations, path_files)

    # remove backslash
    data["subnarrative"] = data["subnarrative"].apply(lambda text: remove_backslash(text))
    # create the subnarrative format
    data["subnarrative"] = data["subnarrative"].apply(lambda text: create_label_path(text))
    # replace /Other with empty string
    data["subnarrative"] = data["subnarrative"].apply(lambda text: drop_other(text))
    # getting a list with separate paths to all subnarratives
    data["subnarrative_list"] = data["subnarrative"].apply(lambda text: text.split(";"))
    # add the "Top/" part at the front
    data["subnarrative_list"] = data["subnarrative_list"].apply(lambda text_list: add_top(text_list))
    data

    return data
    


