# Stdlib imports
import os
import shutil
import zipfile
import urllib2

def get_results(url, extract_file, working_dir):
    """
    Returns data from specified file inside remote zip archive. Cleans up after self.
    
    Arguments:
    - url: File to download
    - extract_file: Filename to extract from archive
    - working_dir: Directory to create for extraction
    """
    
    def download(url, working_dir):
        """
        Download a file to specified working directory.
        """
        os.mkdir(working_dir)
        
        # Derive local filename from URL
        file_name = url.split('/')[-1]
        
        request = urllib2.Request(url)
        opener = urllib2.build_opener()
        # Set custom user-agent string
        request.add_header('User-Agent', 'kpcc-hancock/1.0 +http://www.scpr.org')
        
        remote_file = opener.open(request)
        local_file = open(os.path.join(working_dir, file_name), 'w')
        local_file.write(remote_file.read())
        local_file.close()
        remote_file.close()
        # Return path of downloaded file
        return os.path.join(working_dir, file_name)
    
    def extract(file_path, extract_file, working_dir):
        """
        Remove a single file from a zip archive
        """
        f = open(file_path, 'r')
        zfobj = zipfile.ZipFile(f)
        for name in zfobj.namelist():
            if name == extract_file:
                outfile = open(os.path.join(working_dir, name), 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
                # Quit searching the zip archive after the file is found
                break
        f.close()
    
    # Download the zip archive and extract the desired file
    extract(download(url, working_dir), extract_file, working_dir)
    
    # Get `file` object for results file
    result_file = open(os.path.join(working_dir, extract_file), 'r')
    response = result_file.read()

    # __Clean up__: Close files & remove working directory
    result_file.close()
    shutil.rmtree(working_dir)
    
    # Return data from result_file
    return response
