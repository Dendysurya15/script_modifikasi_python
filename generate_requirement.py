import pkg_resources

installed_packages = pkg_resources.working_set
installed_packages_list = sorted(["{}=={}".format(i.key, i.version) for i in installed_packages])

with open('requirements.txt', 'w') as f:
    for package in installed_packages_list:
        f.write(package + '\n')
