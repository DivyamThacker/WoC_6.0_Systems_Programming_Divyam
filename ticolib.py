import argparse, os , sys ,datetime, hashlib ,json

argparser = argparse.ArgumentParser(description="This is the Main program that tracks your files :)")
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "init": cmd_init(args)
        case "add" : cmd_add(args)
        case "status" : cmd_status(args)
        case "commit" : cmd_commit(args)
        case "rmcommit":  cmd_rmcommit(args)
        case "rmadd" : cmd_rmadd(args)
        case "push" : cmd_push(args)
        case "create_user": cmd_create_user(args)
        case "set_user": cmd_set_user(args)
        case _ : print("Bad Command")

argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")

argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository.")

argsp = argsubparsers.add_parser("add", help="Track all the files in the current directories and sub directories")    

argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="from where to add all the new files to tracking")

def cmd_init(args):
    directory_path = args.path
    paths = [".tico",".tico/branches",".tico/objects", ".tico/branches/main"]
    for path in paths:
        # if directory_path != ".":
        path = os.path.join(directory_path,path)
        if not os.path.exists(path):
            os.mkdir(path)
    if os.path.exists(file_path = ".tico/branches/main/commits.json"):
        print("Root Commit Already Exists!")
        return        
    create_root_commit()
    file_paths = ["added.json", "index.json", "users.txt"]
    for file_path in file_paths:
        file_path = os.path.join(directory_path,".tico/branches/main", file_path)
        if os.path.exists(file_path):
            print("File already exists!")
        else:
            with open(file_path, "w") as file:
                 file.write("{}")
            create_user(directory_path) 
            
argsp = argsubparsers.add_parser("set_user", help="set the current user")
argsp.add_argument("username", help="Username of the current user")                
                
def cmd_set_user(args):
    file_path = ".tico/branches/main/users.txt"
    if not os.path.exists(file_path):
        print("You need to initialize tico with 'tico init' command before performing this action")
        return 
    username = args.username
    with open(file_path, "r") as file:  
        lines = file.readlines()
        
    for line in lines:
        words = line.split()  # Split the line into words
        if  words and words[-1] == username:  # Check if the last word is equal to username
            lines.pop()
            lines.append(f"Current User: {username}")
            with open(file_path, "w") as file:  # Open the file in write mode ("w")
                file.writelines(lines)  # Write all lines from the list
            return  # Exit the loop once the name is found
    print("No Such Users Exist, you first need to create the user using 'tico create_user' command")
        
        
        
                
def create_user(directory_path=".", username=None):
    file_path = ".tico/branches/main/users.txt"
    file_path=os.path.join(directory_path, file_path)
    if username==None:
        username = input("Set the username as .. ")
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")  # Output: 2024-01-23 14:25:30
    timestamp = now.timestamp()  # Output (example): 1690546730.0
    with open(file_path, "r") as file:  
        lines = file.readlines()
    if len(lines) > 1:
        lines.pop()
        
    lines.append(f"{formatted_datetime} {timestamp} {username}")   
    lines.append(f"\nCurrent User: {username}")   
    with open(file_path, "w") as file:  # Open in append mode ("a")
        for line in lines:
            file.write(line)
        
        
argsp = argsubparsers.add_parser("create_user", help="create a new user")
argsp.add_argument("username", help="Username of the current user")

def cmd_create_user(args):
    username = args.username
    file_path = ".tico/branches/main/users.txt"
    # file_path=os.path.join(directory_path, file_path)
    if not os.path.exists(file_path):
        print("You need to initialize tico with 'tico init' command before performing this action")
        return
    with open(file_path, "r") as file:  
        lines = file.readlines()
        
    for line in lines:
        words = line.split()  # Split the line into words
        if words and words[-1] == username:  # Check if the last word is equal to username
            print("This user aldready exists.")
            return  # Exit the function if the name is found
    create_user(".", username)
    
    
    
                    
def add_file_to_tracking(filepath, valid_json_files):
    try:
        with open(filepath, "rb") as file:
            content = file.read()
            hash_object = hashlib.md5(content)
            md5_hash = hash_object.hexdigest()

        for json_file in valid_json_files:
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)

                # Update the dictionary with the new key-value pair
                data.update({filepath: md5_hash})

                with open(json_file, "w") as file:
                    json.dump(data, file, indent=4)
                    print(f"Successfully added '{filepath}' and hash to '{json_file}'")

            except Exception as e:
                print(f"Error writing to '{json_file}': {e}")

    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
    

def cmd_add(args):
    valid_json_files = [".tico/branches/main/index.json", ".tico/branches/main/added.json"]
    data = None
    if os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for filename in files:
                filepath = os.path.join(root, filename)
                add_file_to_tracking(filepath, valid_json_files)
    else:
        filepath = args.path
        add_file_to_tracking(filepath, valid_json_files)

argsp = argsubparsers.add_parser("status", help="Check the status of all the files in your directory")    

argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="for which directory do you want to check the status of files")
        
def cmd_status(args):
    untracked_files = []
    modified_files=[]
    deleted_files=[]
    all_files=[]
    directory_path = args.path
    with open(".tico/branches/main/index.json", "r") as file:
        json_content = json.load(file)
    for root, _, files in os.walk(directory_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                if not filepath or not filepath[2].isalpha():
                    continue
                filepath = filepath[2:]
                all_files.append(filepath)
                with open(filepath, "rb") as file:
                    file_content = file.read()
                    hash_object = hashlib.md5(file_content)
                    md5_hash = hash_object.hexdigest()
                if filepath not in json_content.keys():
                    untracked_files.append(filepath)
                if filepath in json_content.keys() and json_content[filepath] != md5_hash:
                    modified_files.append(filepath)
    for filepath in json_content.keys():
        if filepath not in all_files:
            deleted_files.append(filepath)
    for filepath in untracked_files:
        print(f"Untracked file:   {filepath}")
                                        
    for filepath in modified_files:
        print(f"Modified file:    {filepath}") 
                                       
    for filepath in deleted_files:
        print(f"Deleted file:     {filepath}")
        
    # for filepath in all_files:
    #     print(f"All file:   {filepath}")
    return untracked_files, modified_files, deleted_files, all_files                                    

argsp= argsubparsers.add_parser("commit", help="Commit the added changes.")

argsp.add_argument("-m", dest="messageFlag", action="store_true", help="specify it if you want to write message for the commit")
argsp.add_argument("message",default="",help="specify message for the commit")


def get_current_author(directory_path="."):
    file_path = os.path.join(directory_path, ".tico", "branches", "main","users.txt")
    if not os.path.exists(file_path):
        print("You first need to run 'tico init' command")
        return
    with open(file_path, "r") as file:
        lines = file.readlines()
    return lines[-1].split()[-1]    

class Commit:
    def __init__(self, message, author, parent=None):
        self.message = message
        self.author = author
        self.parent = parent
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Capture creation time
        self.files = {}  # Store a dictionary of changed files and their contents

    def add_files(self, json_file_path = ".tico/branches/main/index.json"): #adds tracked files that are in index.json
        with open(json_file_path, "r") as f:
            all_files = json.load(f)
            all_files =  list(all_files.keys())
        files = {}    
        for file in all_files:
            files[file] = self.read_file(file)
        self.files = files     

    def read_file(self, file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return content    
        
    def get_commit_info(self):
        return f"Message: {self.message}\nAuthor: {self.author}\nTimestamp: {self.timestamp}"

    # Simplified method to simulate creating a new commit based on changes
    def create_child_commit(self, message, author):
        child = Commit(message, author, parent=self)
        return child

    def __dict__(self):
        return {"message": self.message, "author": self.author, "parent":self.parent, "timestamp":self.timestamp,
                "files":self.files}
        
def create_root_commit():
    message="This is the root commit of main branch"
    author=get_current_author()
    file_path = ".tico/branches/main/commits.json"
    commit = Commit(message, author)
    data = commit.__dict__()
    md5_hash = hashlib.md5()
    md5_hash.update(str(commit).encode())  # Encode as bytes for hashing
    hashed_value = md5_hash.hexdigest()
    my_dict = {}
    my_dict[hashed_value] = data
    with open(file_path, 'w') as f:
        json.dump(my_dict, f, indent=4)
    

def get_last_commit():
    file_path = ".tico/branches/main/commits.json"
    if not os.path.exists(file_path):
        print("Root Commit does not exists")
        return
    with open(file_path, "r") as file:
        data = json.load(file)
        last_commit  = list(data.keys())[-1]
    return last_commit

def empty_tracked_files():
    file_paths = [".tico/branches/main/added.json", ".tico/branches/main/index.json"]
    for file_path in file_paths:
        with open(file_path, "w") as f:
            f.write("{}")
 
def cmd_commit(args):
    file_path = ".tico/branches/main/commits.json"
    if not args.messageFlag:
        message = input("Please Enter the a short description of this commit... ")
    else:    
        message = args.message
    author = get_current_author()
    parent = get_last_commit()    
    commit  = Commit(message,author,parent)
    commit.add_files()
    data = commit.__dict__()
    md5_hash = hashlib.md5()
    md5_hash.update(str(commit).encode())  # Encode as bytes for hashing
    hashed_value = md5_hash.hexdigest()
    with open(file_path, "r") as file:
        my_dict = json.load(file)
    
    my_dict[hashed_value] = data
    with open(file_path, 'w') as f:
        json.dump(my_dict, f, indent=4)
    empty_tracked_files() # Empty the tracking files in index.json after commiting them
        
        
argsp=  argsubparsers.add_parser("rmcommit", help="remove specified or last commit")
argsp.add_argument("--hash", dest="hash",action="store",   nargs="?", help="Specify the hash of the commit that you want to delete")   

    
def cmd_rmcommit(args):
    file_path=".tico/branches/main/commits.json"
    flag=None
    with open (file_path, "r") as file:
        content = json.load(file)
        last_key = list(content.keys())[-1]
    if args.hash:
        hash = args.hash
        parent_hash = content[hash]["parent"]
        for key, value in content.items():
            if key==hash:
                flag=1
            if flag==1:
                value["parent"] = parent_hash    
        del content[hash]
    else :    
        del content[last_key]
    with open (file_path, "w") as file:    
        json.dump(content,file, indent=4)     
        
argsp = argsubparsers.add_parser("rmadd", help="Remove the file or directory from tracking")
argsp.add_argument("file_path", default=".", help="specify the path of file or directory that you want to untrack")

def rmadd(filepath):
    json_file_path=".tico/branches/main/index.json"
    with open(json_file_path, "r") as f:
        my_dict = json.load(f)
    if filepath in my_dict:    
        del my_dict[filepath]
    else: print(f"{filepath} is already an untracked file or it doesn't exists")    
    with open(json_file_path, "w") as f:
        json.dump(my_dict, f, indent=4)

def cmd_rmadd(args):
    file_path=args.file_path
    if os.path.isdir(file_path):
        for root, _ , files in os.walk(file_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                filepath = filepath[2:]
                rmadd(filepath)
    else:
        rmadd(file_path)

argsp = argsubparsers.add_parser("push", help="Push all the files in the last commit into your destination folder")
argsp.add_argument("directory_path", help="Specify the destination folder of the files in the commit")

def cmd_push(args):
    directory_path = args.directory_path
    json_file_path = ".tico/branches/main/commits.json"
    with open(json_file_path, "r") as f:
        content = json.load(f)
    last_key = list(content.keys())[-1]
    last_value = content[last_key]
    for file_path, file_content in last_value["files"].items():
        path = os.path.join(directory_path, file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(file_content) 