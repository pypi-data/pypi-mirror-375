import impmagic

@impmagic.loader(
    {'module': 'os'},
    {'module': 'glob'},
    {'module': 'app.display', 'submodule': ['logs']},
)
def remove_unlisted_files(base_dir, paths_to_keep):
    # Normaliser les chemins (en absolu)
    paths_to_keep_abs = {os.path.abspath(os.path.join(base_dir, p)) for p in paths_to_keep}

    # Lister tous les fichiers dans base_dir récursivement
    all_files = glob.glob(os.path.join(base_dir, '**'), recursive=True)
    all_files = [f for f in all_files if os.path.isfile(f)]
    all_files = [p.replace('\\', '/') for p in all_files]

    # Supprimer ceux qui ne sont pas dans paths_to_keep
    for file_path in all_files:
        abs_path = os.path.abspath(file_path)
        if abs_path not in paths_to_keep_abs:
            logs(f"{os.path.expanduser(file_path)} supprimé", force=True)
            os.remove(abs_path)



import os
import hashlib
from collections import defaultdict
from app.display import build_tree_from_dict

def build_diff_tree(base_path, remote_tree):
    local_files = {}
    for root, _, files in os.walk(base_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_path).replace('\\', '/')
            with open(full_path, 'rb') as f:
                local_files[rel_path] = hashlib.sha256(f.read()).hexdigest()

    remote_map = {f["name"].replace('\\', '/'): f["content_hash"] for f in remote_tree}
    all_paths = set(local_files) | set(remote_map)

    diff = {}
    for path in sorted(all_paths):
        if path in local_files and path in remote_map:
            if local_files[path] == remote_map[path]:
                diff[path] = "OK"
            else:
                diff[path] = "UPDATE"
        elif path in local_files:
            diff[path] = "DELETE"
        else:
            diff[path] = "NEW"

    return build_tree_from_dict(diff)

def build_tree_view(diff_map):
    tree = defaultdict(list)
    for path, status in diff_map.items():
        parts = path.split('/')
        for i in range(1, len(parts)):
            folder = '/'.join(parts[:i])
            tree[folder].append(None)
        tree[path] = status

    printed = set()
    lines = []

    def print_branch(prefix, path_parts):
        full_path = '/'.join(path_parts)
        entries = {k for k in tree if k.startswith(full_path + '/') and k.count('/') == len(path_parts)}
        files = sorted(e for e in entries if tree[e] != None)
        folders = sorted(e for e in entries if tree[e] == None)
        for i, item in enumerate(folders + files):
            connector = '└── ' if i == len(folders + files) - 1 else '├── '
            label = item.split('/')[-1]
            status = f" [{tree[item]}]" if tree[item] else ''
            lines.append(f"{prefix}{connector}{label}{status}")
            if tree[item] is None:
                print_branch(prefix + ('    ' if i == len(folders + files) - 1 else '│   '), item.split('/'))

    print_branch("", [])
    return '\n'.join(lines)