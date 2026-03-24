import psutil

def job_killer(jobName: str):
    # nel caso non ci siano job ma si dia comunque ok
    if jobName == '':
        print('Nessun job da killare.')
        return
    # in questo modo ho nome file intero ma non distinguo le estensioni
    target_filename = jobName+'.'
    print(f'Searching of job {jobName} process in progress...')
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name']
            if name in ('explicit.exe', 'standard.exe'):
                # Get list of open files
                try:
                    open_files = proc.open_files()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue

                for f in open_files:
                    if target_filename in f.path:
                        print('Found process, killing in progress...')
                        proc.kill()
                        print('Job killed successfully.')
                        return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue