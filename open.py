import click
import subprocess
import os
import json





def get_root_dir():
    try:
        with open('config.json', 'r') as file:
            
            file_json = json.load(file)

            
            return file_json["ROOT_DIR"]
    except Exception as e:
        raise click.ClickException(f'cannot get root dir error: {e}')

def root_dir_exist():
    try:
        with open('config.json', 'r') as file:
        


            file_json = json.load(file)

            if "ROOT_DIR" in file_json:
                if file_json["ROOT_DIR"] != '':
                    return True
                else:
                    return False
            else:
                return False
    except json.JSONDecodeError:
        return False

    except Exception as e:
        raise click.ClickException(f'cannot check if root dir exists: {e}')

def update_root_path(new_dir):
    try:
        with open('config.json', 'r') as file:

            file_json = json.load(file)

            file_json["ROOT_DIR"] = new_dir
    

        with open('config.json', 'w') as files:

            json.dump(file_json, file, indent=4)

        
    except json.decoder.JSONDecodeError:
        raise click.ClickException('Cannot parse json from config.json')




def config_exist():
    try:
        output = os.path.exists('config.json')
        return output
    except Exception as e:
        raise click.ClickException(f'Cannot check if config.json exists: {e}')


def create_config():
    
    try: 
        # ask for new root path
        new_path = click.prompt('Enter the root path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
    
        # create a new file
        with open('config.json', 'w') as file:
            
            # append new json with the new path
            json.dump({"ROOT_DIR": new_path}, file, indent=4)
    
    except Exception as e:
        raise click.ClickException(f'creating config file error: {e}')

@click.command()
@click.argument('project-path',required=True, type=str)
@click.option('--root-dir', type=click.Path(exists=True, dir_okay=True, file_okay=False), help='update/create a root directory where your project lives')
def cli(project_path,root_dir):
    """Open project in VScode no more find, cd, code. save your directory then open projects directly"""
    
    # Check if config file exists
    if config_exist():

        # (IMPORTANT) checks if root dir exists
        if not root_dir_exist():
            try:
                create_config()
            except:
                raise click.ClickException('Root dir in config does not exist. run the cli again and confirm to automatically reset the config.json file ')

        # get root dir (even if empty)
        ROOT_DIR = get_root_dir() 

        # check if root dir is a valid path
        if not os.path.exists(ROOT_DIR): 
            try:
                new_path = click.prompt('Enter the root path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
                update_root_path(new_path)
            except:
                raise click.ClickException('Root dir in the config file is not a valid path. run the cli again to automatically create the root dir')

        # change root dir if root dir option is present
        if root_dir:
            
            # check if root dir option path exists
            if not os.path.exists(root_dir):
                raise click.ClickException(f'root dir presented is not a valid path')

            # if exist, update config.json
            update_root_path(root_dir)
            
        
        
        #check if rootdir+project is valid
        if not os.path.exists(os.path.join(ROOT_DIR, project_path)):
            raise click.ClickException(f'project path cannot be found. Double check your root dir "{ROOT_DIR}". update via the --root-dir if it is wrong')


        new_path = os.path.join(ROOT_DIR, project_path)

        try:
            subprocess.run(['code', '.'],shell=True, cwd=new_path)
            click.secho('success', fg='green' , bold=True)
            

        except subprocess.CalledProcessError as e:
            click.secho(f"Subprocess failed with exit code {e.returncode}", fg='red')
            click.secho(f"Error output (stderr): {e.stderr}", fg='red')
            click.secho(f"Standard output (stdout): {e.stdout}", fg='red')

            
        
    # if config file dont exist, create a new config file
    else:

        # prompt to create a new config file
        if click.confirm('config.json is not found. do you wish to create a new config.json?'):

            # Create a new config file
        
            create_config()

            click.secho('config successfully created. run the cli again', fg='green')
            
            
                
        # error: there is no config file
        else:
            raise click.ClickException('config.json is not found. run the cli again and confirm to automatically create the config.json file')
    



if __name__ == '__main__':
    cli()