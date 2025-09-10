import shutil
import os
from .g_Log import Log
import filecmp

def _init(src_dir=None, 
          dst_dir=None,
          overwrite=False,
          log=Log()):
    
    src_dirs=[]

    filedir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(filedir, 'template')
    src_dirs.append(src_dir)
    
    if src_dir is not None:
        src_dirs.append(src_dir)

    if dst_dir is None:
        home_dir = os.path.expanduser("~")              # /home/username or /Users/username
        dst_dir = os.path.join(home_dir, ".genomicshelper")
    
    log.write('Copying new templates and headers to directory : {}'.format(dst_dir))   
    
    if not os.path.exists(dst_dir):
        log.write('Not existing... Creating : {}'.format(dst_dir))   
        os.makedirs(dst_dir)
    
    # Loop through files in source
    copied_list=[]
    for src_dir in src_dirs:
        log.write('Copying from directory : {}'.format(src_dir))
        for filename in os.listdir(src_dir):
            if filename[-4:]==".tmp" or filename[-7:]==".header":
                src_file = os.path.join(src_dir, filename)
                dst_file = os.path.join(dst_dir, filename)
                
                if  overwrite==True:
                    log.write(f'Copying {filename}')
                    shutil.copy2(src_file, dst_file)  # copy2 preserves metadata
                    copied_list.append(src_file)      
                else:
                    # Only copy files (skip directories)
                    if not os.path.exists(dst_file):  # skip if exists
                        log.write(f'Copying {filename}')
                        shutil.copy2(src_file, dst_file)  # copy2 preserves metadata
                        copied_list.append(src_file)       
                    else:
                        if os.path.exists(dst_file):
                            if filecmp.cmp(src_file, dst_file, shallow=False):
                                #log.warning(f'Skipping {filename} (same file)')
                                pass
                            else:
                                log.write(f'Copying {filename}')
                                shutil.copy2(src_file, dst_file)  # copy2 preserves metadata
                                copied_list.append(src_file)
                        else:
                            log.warning(f'Skipping {filename} (already exists)')
                    
    log.write('Copied {} new templates and headers.'.format(len(copied_list)))