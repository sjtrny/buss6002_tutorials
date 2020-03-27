import nbformat
import nbconvert
from nbconvert import HTMLExporter
import yaml
import os
import shutil
import re

html_exporter = HTMLExporter()
writer = nbconvert.writers.FilesWriter()

manifest_f = open("manifest", "r")
paths = manifest_f.read().splitlines()
manifest_f.close()

index_data_list = []

usrpl = "\_"

for path in paths:
    full_path = f"{path}/resources.yaml"
    
    try:
        path_f = open(full_path, "r")
        print(f"found {full_path}")
    except:
        print(f"Path not found: {full_path}")
        continue
    
    index_data = {}
    
    # Load the folder resources data
    path_resources_dict = yaml.load(path_f)
    path_f.close()
    
    index_data['name'] = path_resources_dict['name']
    index_data['notebooks'] = {}
    index_data['assets'] = {}
    
    folder_name = path.split("/")[-1]
    
    # Clear old folder
    if os.path.exists(f"{folder_name}"):
        shutil.rmtree(f"{folder_name}")
    os.mkdir(f"{folder_name}")
    
    # Convert and write notebooks
    for notebook_name, notebook_path in path_resources_dict["notebooks"].items():
        notebook = nbformat.read(f"{path}/{notebook_path}", as_version=nbformat.NO_CONVERT)
        (body, resources) = html_exporter.from_notebook_node(notebook)
        writer.write(body, resources, f"{folder_name}/{notebook_path}")
        
        index_data['notebooks'][notebook_name] = f"{folder_name}/{notebook_path}"

        # Copy notebook
        shutil.copyfile(f"{path}/{notebook_path}", f"{folder_name}/{notebook_path}")
    
    # Copy assets
    for asset_path in path_resources_dict["assets"]:
        # If asset is folder
        if os.path.isdir(f"{path}/{asset_path}"):
            shutil.copytree(f"{path}/{asset_path}", f"{folder_name}/{asset_path}")
        # else is a file
        else:
            shutil.copyfile(f"{path}/{asset_path}", f"{folder_name}/{asset_path}")
            index_data['assets'][asset_path] = f"{folder_name}/{asset_path}"
        
    index_data_list.append(index_data)
    
# Create index
index_f = open("index.md", "w")

for index_data in index_data_list:
    
    index_f.writelines("\n")
    index_f.writelines(f"### {index_data['name']}\n")
    for nb_name, nb_path in index_data['notebooks'].items():
        index_f.writelines(f"- [{nb_name}]({nb_path}.html) ([notebook]({nb_path}))\n")
    
    if len(index_data['assets']) > 0:
        index_f.writelines("- Resources\n")
        for asset_name, asset_path in index_data['assets'].items():
            index_f.writelines(f"  - [{asset_name.replace('_', usrpl)}]({asset_path})\n")

index_f.close()
