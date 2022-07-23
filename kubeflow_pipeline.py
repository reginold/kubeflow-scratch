import kfp
import kfp.components as comp

# First function
def unzip_files(bucket_zipfile_path : str, 
                output_string : comp.OutputPath(str)) :
    
    import boto3
    import os
    from io import BytesIO
    import zipfile
 
    # Set up connection
    s3_resource = boto3.client('s3')
    path_bucket = "bucket_name" # Change it to your bucket name
    path_to_move_file = "destination_subfolder/" # Change it to your 
                                                 # destination subfolder
    
    # Create local targets
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./unzipped_data", exist_ok=True)
    
    # Download zipfile
    boto3.resource('s3').Object(path_bucket, bucket_zipfile_path).\
                        download_file(Filename="./data/zipfile.zip")
    
    # Unzip
    for zip in os.listdir("./data"):
        with zipfile.ZipFile(os.path.join("./data", zip), 'r') as file:
            file.extractall("./unzipped_data")
    
    # Upload
    for file in os.listdir("./unzipped_data"):
        output_path = path_to_move_file + file
        s3_resource.upload_file(os.path.join("./unzipped_data", file), 
                                path_bucket, output_path)
    
    # Create Artifact : S3 path to last extracted csv file    
    with open(output_string, 'w') as writer:
        writer.write(output_path)
        
# 2nd function
def csv_s3_reader(bucket_name : str, 
                  csv_path : comp.InputPath(str), 
                  sep : str, 
                  decimal : str, 
                  encoding : str, 
                  output_csv:comp.OutputPath('CSV')):
    

    from io import StringIO
    import pandas as pd
    import boto3
    import os
    
    # Set up connection and download file
    with open(csv_path, 'r') as reader:
        line = reader.readline()
        csv_obj = boto3.client('s3').get_object(Bucket=bucket_name, Key=line)
    body = csv_obj['Body']
    csv_string = body.read().decode(encoding)
    
    # Read csv
    df = pd.read_csv(StringIO(csv_string), sep=sep, decimal=decimal, 
                     error_bad_lines=False, encoding=encoding)
    
    df.to_csv(output_csv, index=True, header=True)
    
# Link to your container image
base_img = "public.ecr.aws/f6t4n1w1/public_test:latest" # Change to your registry's URI

# Create first OP
unzip_files_op = kfp.components.create_component_from_func(unzip_files, base_image=base_img) 

# Create second OP
csv_s3_reader_op = kfp.components.create_component_from_func(csv_s3_reader, base_image=base_img) 

@kfp.dsl.pipeline(
    name='Give a name to your pipeline',
    description='Give it a description too'
)
def unzip_and_read_pipeline(
    bucket_zipfile_path, 
    bucket_name,  
    sep, 
    decimal, 
    encoding
):  
    # Call the first OP
    first_task = unzip_files_op(bucket_zipfile_path)
    
    # Call the second OP and pass it the first task's outputs
    second_task = csv_s3_reader_op(bucket_name, 
                                   first_task.outputs['output_string'], 
                                   sep, 
                                   decimal, 
                                   encoding)
