wget --recursive --no-parent "https://buddhanexus.net/json/pli/"
mkdir data/pli/
find buddhanexus.net/json/pli/ -name "*json.gz" -exec cp "{}" data/pli \;
#rm -rf buddhanexus.net
