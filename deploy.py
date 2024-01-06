import urllib.request
import subprocess


def add_version():
    path = 'document/en/ps5/index.html'
    with open(path, 'r') as file:
        content = file.read()

    version_index = content.find('<b id="version">')

    if version_index != -1:
        closing_b_index = content.find('</b>', version_index)
        version_opening_tag_end_index = version_index + len('<b id="version">')

        if closing_b_index != -1:
            commit_count = get_commit_count()

            if commit_count is None:
                print('Error couldnt get commit count.')
                return
            updated_content = content[:version_opening_tag_end_index] + \
                ' | v1.04 | v1.' + commit_count + content[closing_b_index:]

            with open(path, 'w') as file:
                file.write(updated_content)
            print(f'File {path} updated successfully.')
        else:
            print('error couldnt find closing tag.')
    else:
        print('Error couldnt find version tag.')


def get_commit_count():
    url = 'https://api.github.com/repos/idlesauce/PS5-Exploit-Host/commits?per_page=1&page=1'
    response = urllib.request.urlopen(url)
    headers = response.info()
    link_header = headers.get('Link', '')

    links_split = link_header.split('<')

    print(link_header)
    print(len(links_split))

    if not len(links_split) == 3:
        return None

    start_index = links_split[2].find('&page=')
    end_index = links_split[2].find('>', start_index)

    if start_index != -1 and end_index != -1:
        result = links_split[2][start_index + len('&page='):end_index]
        return result
    else:
        return None


if __name__ == '__main__':
    add_version()
    subprocess.run(["python", "appcache_manifest_generator.py", "-cf"])
