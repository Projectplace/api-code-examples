import math
import os.path
import argh
import requests
import requests_oauthlib


APPLICATION_KEY = 'REDACTED'
APPLICATION_SECRET = 'REDACTED'
ACCESS_TOKEN_KEY = 'REDACTED'
ACCESS_TOKEN_SECRET = 'REDACTED'
API_ENDPOINT = 'https://api.projectplace.com'


oauth1 = requests_oauthlib.OAuth1(
    client_key=APPLICATION_KEY,
    client_secret=APPLICATION_SECRET,
    resource_owner_key=ACCESS_TOKEN_KEY,
    resource_owner_secret=ACCESS_TOKEN_SECRET
)


class ProjectToDownload:
    def __init__(self, _id, name, size_bytes):
        self.id = _id
        self.name = name
        self.space_used = self._convert_size(size_bytes)

    @classmethod
    def _convert_size(cls, size_bytes):
        """ Returns approx size """
        if size_bytes == 0:
            return "0 B"

        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1000, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])


def _fetch_archived_projects_info(limit=100, row_number=0):
    """
    Paginate through all archived projects in the account. Returns a list populated with instances of
    `ProjectToDownload`-objects.
    """
    request_body = {
        'sort_by': '+creation_date',
        'filter': {
            'archive_status': [1]
        },
        'limit': limit
    }
    if row_number:
        request_body.update({'row_number': row_number})

    r = requests.post(f'{API_ENDPOINT}/2/account/projects', json=request_body, auth=oauth1)

    response_json = r.json()

    archived_projects = [ProjectToDownload(r['id'], r['name'], r['space_used']) for r in response_json]
    if len(response_json) == limit:
        archived_projects += _fetch_archived_projects_info(limit=limit, row_number=row_number + limit)

    if not row_number:
        print(f'Finished fetching information about {len(archived_projects)} archived workspaces')

    return archived_projects


def _project_file_exists(project_id, path=None):
    """
    Checks if a workspace has already been downloaded - by looking for zip files in the designated path
    that start with the ID of the workspace in question.

    If it finds a file it returns the name of the file.
    """
    try:
        return [f for f in os.listdir(path) if f.endswith('.zip') and f.startswith(f'{project_id}-')].pop()
    except IndexError:
        return False


def _download_archived_projects(archived_projects, path=None):
    """
    For each archived workspace.

    1. Check if it has already been downloaded to `path` - if so skip it and print information
    2. If not already downloaded - initiate the export job on the ProjectPlace servers
    3. Once the export job has finished - we can fetch the zip-file that now resides on the ProjectPlace
       server.
    """
    n = 0
    total_count = len(archived_projects)
    for archived_project in archived_projects:
        n += 1
        if filename := _project_file_exists(archived_project.id, path=path):
            print(
                f'{n}/{len(archived_projects)} Already downloaded "{archived_project.name}" '
                f'({archived_project.space_used}). Delete {os.path.join(path, filename)} to re-download.',
            )
            continue

        print(
            f'{n}/{total_count} Starting remote export job for "{archived_project.name}" '
            f'({archived_project.space_used})'
        )
        export_id = _trigger_project_export(archived_project.id)
        export_result = _await_export(archived_project.id, export_id)
        if export_result:
            print(
                f'{n}/{total_count} Downloading "{archived_project.name}" ({archived_project.space_used})'
            )
            _download_export(
                archived_project.id, export_result['download_name'], export_result['download_uri'], path=path
            )
        else:
            print(
                f'{n}/{total_count} Failed to complete export of "{archived_project.name}"'
            )


def _trigger_project_export(project_id: int):
    """
    Triggers ProjectPlace to start the job of zipping the workspace.
    """
    response = requests.post(
        f'{API_ENDPOINT}/1/projects/{project_id}/exports',
        json={"include_documents": True, "include_all_document_versions": True, "include_plan": True,
              "include_plan_attachments": True, "include_boards": True, "include_card_attachments": True,
              "include_archived_boards": True, "include_conversations": True, "include_conversation_attachments": True,
              "include_issues_2": True, "include_issues_2_attachments": True},
        auth=oauth1
    )

    if response.status_code == 200:
        eid = response.json()
        assert isinstance(eid, int)
        return eid

    raise RuntimeError('For some reason could not initialize export job')


def _await_export(project_id, export_id):
    """
    Polls the export status API to check whether it is done yet or not. To be nice to the server we have a sleep of
    5 seconds between each check (a really big project can take a very long time to export).
    Once the job is done - this function returns a dict containing the following information:
        * the ID of the job (eid)
        * started_at - an ISO timestamp signifying when the job was started
        * finished_at - an ISO timestamp signifying when the job was finished
        * done - a bool which is True if the job has completed
        * download_url - the URL to invoke (with an API call) in order to download the zip-file
        * download_name - A suggested name of the file once you've downloaded it, consisting of the project name
          and the started_at timestamp
    :param project_id: int, the ID of the project
    :param export_id: int, the ID of the export job
    :return: dict
    """
    import time
    export_done = False

    while not export_done:
        time.sleep(5)
        export_result = requests.get(
            f'{API_ENDPOINT}/1/projects/{project_id}/exports/{export_id}', auth=oauth1
        )

        if not export_result.status_code == 200:
            return False

        if export_result.json()['done']:
            return export_result.json()


def _download_export(project_id, download_name, download_uri, path=None):
    """
    Downloads the zip file representing exported data from the workspace. It is important to write to disk as
    the response is coming in. The file may be many gigabytes big and if we would wait for the entire
    response to resolve before writing to disk we may very well end up out of memory.
    """
    download_name = f'{project_id}-{download_name}'
    file_path = download_name

    if path is not None:
        file_path = os.path.join(path, file_path)

    with requests.get(download_uri, auth=oauth1, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as fp:
            for chunk in r.iter_content(chunk_size=8192):
                fp.write(chunk)


def _delete_archived_projects(archived_projects, path=None):
    """
    Deletes archived workspaces - but as a safety measure refuses to delete them unless there is a zip file in the
    path that seems to match an export.
    """
    n = 0
    total_count = len(archived_projects)
    print(f'Deleting archived workspaces')
    for archived_project in archived_projects:
        n += 1
        if not _project_file_exists(archived_project.id, path=path):
            print(f'{n}/{total_count} Skipping deletion of {archived_project.id} {archived_project.name} since it '
                  f'does not appear to have been downloaded')
            continue

        r = requests.delete(
            f'{API_ENDPOINT}/1/projects/{archived_project.id}', auth=oauth1
        )
        if r.status_code != 200:
            print(f'{n}/{total_count} Failed to delete {archived_project.id} - {archived_project.name}')

        else:
            print(f'{n}/{total_count} Deleted {archived_project.id} - {archived_project.name}')


@argh.arg(
    '-d', '--purge-after-download',
    help='Flag to signify that the script should delete archived workspaces after successfully having downloaded them.'
)
@argh.arg(
    '-p', '--path', default=None, type=str,
    help='Path to directory where download should end up - if unspecified current directory will be used'
)
def download_archived_projects(purge_after_download=False, path=None):
    """
    This is the entry point of the script.
    """
    if path is not None:
        assert os.path.isdir(path) is True  # Abort if path is not a valid directory

    archived_projects = _fetch_archived_projects_info()

    _download_archived_projects(archived_projects, path=path)

    if purge_after_download:
        _delete_archived_projects(archived_projects, path=path)


if __name__ == '__main__':
    argh.dispatch_command(download_archived_projects)
