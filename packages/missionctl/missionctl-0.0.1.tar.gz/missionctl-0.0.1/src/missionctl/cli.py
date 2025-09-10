import getpass

def cli():
    msg = f'Running missionctl as {getpass.getuser()}.'
    print(msg)
    print('You have mistakenly installed https://pypi.org/project/missionctl/.  This generally is caused by a misconfiguration of pip.  Please closely follow the instructions at https://missioncloudinc.atlassian.net/wiki/x/MgBzBQ')


if __name__ == '__main__':
    cli()
