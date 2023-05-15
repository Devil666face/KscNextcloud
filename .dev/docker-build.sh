#/bin/bash
REPO_NAME="${PWD##*/}"
REPO_NAME_LOWER="$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')"
# function check_or_install() {
# 	if dpkg -s $1; then
# 		echo "$1 alredy install"
# 	else
# 		sudo apt update && sudo apt-get install $1 -y
# 	fi
# }

# check_or_install "make"
# check_or_install "gcc"
# check_or_install "patchelf"
# check_or_install "ccache"
docker build . -t $REPO_NAME_LOWER
docker run --rm -v $PWD/dist:/$REPO_NAME/dist --name $REPO_NAME_LOWER-build $REPO_NAME_LOWER
rm -rf main.dist main.build main.onefile-build