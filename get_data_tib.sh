wget --recursive --no-parent "https://buddhanexus.net/json/tib/"
mkdir data/tib/
find buddhanexus.net/json/tib/ -name "*json.gz" -exec cp "{}" data/tib \;
rm -rf buddhanexus.net
