import os
import shutil

def remove_egg_info_recursively(root="."):
    """
    Recursively remove all directories ending with `.egg-info` starting from `root`.
    """
    for dirpath, dirnames, _ in os.walk(root):
        # Make a copy of dirnames because we may modify it while iterating
        for dirname in dirnames[:]:
            if dirname.endswith(".egg-info"):
                full_path = os.path.join(dirpath, dirname)
                print(f"Removing {full_path}/ ...")
                shutil.rmtree(full_path)
                # remove from dirnames so os.walk doesn't descend into it
                dirnames.remove(dirname)


def clean_build_dirs():
    """
    Remove build artifact directories if they exist:
    - dist/
    - any *.egg-info directory
    """
    # Always check 'dist'
    if os.path.exists("dist"):
        print("Removing dist/ ...")
        shutil.rmtree("dist")
    else:
        print("dist/ not found, skipping.")

    remove_egg_info_recursively()


if __name__ == "__main__":
    clean_build_dirs()


'''
# python -m build

# twine upload --repository testpypi dist/*


# Make a small commit (even just updating a comment)
git add .
git config --global --add safe.directory E:/GitHub/hijri-datetime
git add .
git commit -m "Bump version for new release"

# Rebuild - this will create a version like 0.0.1.dev1+g1234567
python -m build

git tag v0.2.0
git push origin v0.2.0
python -m build
twine upload dist/*

# 5. Install development dependencies
pip install -e ".[dev]"

# 6. Set up pre-commit hooks
pre-commit install

# 7. Run initial tests
pytest

# 8. Build the package
python -m build

# 9. Check the package
twine check dist/*



'''
