#sphinx-apidoc --file-insertion-enabled -f -o source ../src tests conf conf.py modules
sphinx-apidoc --ext-intersphinx -f -o source ../src tests conf conf.py modules
make html
rm -rf html
cp -a build/html html
