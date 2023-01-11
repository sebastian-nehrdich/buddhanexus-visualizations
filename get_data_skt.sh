wget --recursive --no-parent "https://buddhanexus.net/json/skt/"
mkdir data/skt/
find buddhanexus.net/json/skt/ -name "*json.gz" -exec cp "{}" data/skt \;
rm -rf buddhanexus.net
